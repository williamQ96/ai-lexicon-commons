"""Upgrade only the existing public mirror, retaining compose and image rollback."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile

from deploy import BASE, ROOT, PROJECT, command


def inspect():
    return json.loads(command('/usr/local/bin/docker inspect williamq-glossary-mirror'))[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', required=True, help='YYYYMMDD-rN; must be new')
    args = parser.parse_args()
    release = args.release
    assert re.fullmatch(r'\d{8}-r[1-9]\d*', release), 'Invalid release ID'
    day, revision = release.split('-')
    image = 'williamq/glossary-mirror:' + day[:4] + '-' + day[4:6] + '-' + day[6:] + '-' + revision
    stage = BASE + '/releases/' + release
    backup = BASE + '/compose.pre-' + release + '.yaml'
    before = inspect()
    assert before['State']['Running']
    assert before['State'].get('Health', {}).get('Status') == 'healthy', 'Wait for the previous release to become healthy'
    assert before['HostConfig']['PortBindings'] == {'8000/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18195'}]}
    assert before['HostConfig']['ReadonlyRootfs'] and before['Config']['User'] == '1026:100'
    assert all(m['Destination'] == '/acme-challenge' and not m['RW'] for m in before['Mounts'])
    base_image = before['Config']['Image']
    assert re.fullmatch(r'williamq/glossary-mirror:[0-9r-]+', base_image)
    # Pin the retained tag by checking its immutable ID immediately before building.
    assert command('/usr/local/bin/docker image inspect --format ' + shlex.quote('{{.Id}}') + ' ' + shlex.quote(base_image)).strip() == before['Image']
    command('test ! -e ' + shlex.quote(stage) + ' && test ! -e ' + shlex.quote(backup))
    local = PROJECT / 'build' / ('mirror-upgrade-' + release)
    local.mkdir(parents=True, exist_ok=False)
    raw = (ROOT / 'server.py').read_bytes()
    (local / 'server.py').write_bytes(raw)
    (local / 'Dockerfile').write_text('FROM ' + base_image + '\nCOPY server.py /app/server.py\n', encoding='utf-8')
    manifest = {name: hashlib.sha256((local / name).read_bytes()).hexdigest() for name in ('server.py', 'Dockerfile')}
    bundle = local.with_suffix('.tar.gz')
    with tarfile.open(bundle, 'w:gz') as archive:
        for name in manifest:
            archive.add(local / name, arcname=name)
    command('mkdir -p ' + shlex.quote(stage) + ' && chown 1026:100 ' + shlex.quote(stage))
    subprocess.run(['scp', '-O', str(bundle), 'williamq-nas:' + stage + '/release.tar.gz'], check=True, capture_output=True)
    command('tar -xzf ' + shlex.quote(stage + '/release.tar.gz') + ' -C ' + shlex.quote(stage))
    # A compact NAS Python script verifies the bundle and changes only image/build.
    script = '''import hashlib,json,pathlib,subprocess,time
base=pathlib.Path(BASE)
stage=pathlib.Path(STAGE)
manifest=MANIFEST
for name,digest in manifest.items():
    assert hashlib.sha256((stage/name).read_bytes()).hexdigest()==digest
compose=base/'compose.yaml'
old=compose.read_bytes()
text=old.decode('utf-8')
assert text.count('    image: ' + OLD_IMAGE)==1
lines=text.splitlines()
assert sum(line.startswith('    build: ./releases/') for line in lines)==1
new='\\n'.join('    image: '+NEW_IMAGE if line.startswith('    image: ') else '    build: ./releases/'+RELEASE if line.startswith('    build: ./releases/') else line for line in lines)+'\\n'
backup=pathlib.Path(BACKUP)
with backup.open('xb') as out: out.write(old)
docker='/usr/local/bin/docker'
subprocess.run([docker,'build','-t',NEW_IMAGE,str(stage)],check=True,stdout=subprocess.DEVNULL)
assert compose.read_bytes()==old, 'Compose changed during build'
assert subprocess.check_output([docker,'image','inspect','--format','{{.Id}}',OLD_IMAGE],text=True).strip()==OLD_ID
try:
    compose.write_text(new,encoding='utf-8')
    subprocess.run([docker,'compose','-f',str(compose),'up','-d','--no-build','glossary'],check=True,stdout=subprocess.DEVNULL)
    for attempt in range(90):
        current=json.loads(subprocess.check_output([docker,'inspect','williamq-glossary-mirror']))[0]
        if current['State'].get('Health',{}).get('Status')=='healthy': break
        time.sleep(2)
    assert current['State'].get('Health',{}).get('Status')=='healthy', 'New release did not pass its health check within 180 seconds'
    assert current['Config']['Image']==NEW_IMAGE
    assert current['HostConfig']['PortBindings']==OLD_PORTS
    assert current['Mounts']==OLD_MOUNTS
    assert current['HostConfig']['ReadonlyRootfs']
    runtime=subprocess.check_output([docker,'exec','williamq-glossary-mirror','python','-c',"import hashlib;print(hashlib.sha256(open('/app/server.py','rb').read()).hexdigest())"],text=True).strip()
    assert runtime==manifest['server.py']
except Exception:
    compose.write_bytes(old)
    subprocess.run([docker,'compose','-f',str(compose),'up','-d','--no-build','glossary'],check=True,stdout=subprocess.DEVNULL)
    raise
print(json.dumps(dict(image=current['Config']['Image'],image_id=current['Image'],health=current['State']['Health']['Status'],runtime_sha256=runtime)))
'''
    script = ('BASE=' + repr(BASE) + '\nSTAGE=' + repr(stage) + '\nMANIFEST=' + repr(manifest)
        + '\nOLD_IMAGE=' + repr(base_image) + '\nNEW_IMAGE=' + repr(image)
        + '\nRELEASE=' + repr(release) + '\nBACKUP=' + repr(backup)
        + '\nOLD_ID=' + repr(before['Image'])
        + '\nOLD_PORTS=' + repr(before['HostConfig']['PortBindings'])
        + '\nOLD_MOUNTS=' + repr(before['Mounts']) + '\n' + script)
    result = json.loads(command('python3 -c ' + shlex.quote(script)))
    receipt = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(), release=release,
        service_path=BASE, loopback_port=18195, source_sha256=manifest,
        previous_image=base_image, previous_image_id=before['Image'], compose_backup=backup,
        persistent_state='none; content fetched from published GitHub Pages',
        origin='https://williamq96.github.io/ai-lexicon-commons', **result)
    target = ROOT / ('deployment-' + release + '.json')
    with target.open('x', encoding='utf-8') as out:
        json.dump(receipt, out, indent=2); out.write('\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
