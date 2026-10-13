"""Allowlisted mirror deployment; use established DSM and DNS administration."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
SKILL = Path.home() / '.codex/skills/williamq-hosting'
SECRET = Path.home() / '.codex/secrets/williamq-hosting.json'
BASE = '/volume2/docker/williamq-glossary'
RELEASE = '20261012-r1'
HOST = 'glossary.williamq.dev'


def api(name, method, **params):
    nas = json.loads(SECRET.read_text(encoding='utf-8-sig'))['nas']
    args = ['/usr/syno/bin/synowebapi', '--exec', 'api=' + name, 'version=1', 'method=' + method]
    args += [k + '=' + json.dumps(v, separators=(',', ':')) for k, v in params.items()]
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', nas['ssh_alias'], "sudo -S -p '' " + shlex.join(args)], input=nas['sudo_password'] + '\n', capture_output=True, text=True, timeout=420)
    if result.returncode:
        raise RuntimeError('DSM API process failed')
    response = json.loads(result.stdout)
    if not response.get('success') or response.get('data', {}).get('err_settings'):
        raise RuntimeError('DSM API rejected ' + name + '/' + method)
    return response.get('data', {})


def command(value):
    result = subprocess.run([sys.executable, str(SKILL / 'scripts/nas_command.py'), '--sudo', '--timeout', '420', value], capture_output=True, text=True, timeout=450)
    response = json.loads(result.stdout)
    if response['exit_code']:
        raise RuntimeError(response['stderr'][-1200:])
    return response['stdout']


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('step', choices=['stage', 'http', 'inspect']); args = parser.parse_args()
    if args.step == 'stage':
        nas = json.loads(SECRET.read_text(encoding='utf-8-sig'))['nas']
        bundle = PROJECT / 'build' / ('glossary-mirror-' + RELEASE + '.tar.gz')
        bundle.parent.mkdir(exist_ok=True)
        names = ['server.py', 'Dockerfile']
        with tarfile.open(bundle, 'w:gz') as archive:
            for name in names: archive.add(ROOT / name, arcname=name)
        # Require a wholly new service directory for this first deployment.
        command('test ! -e ' + BASE + ' && mkdir -p ' + BASE + '/releases/' + RELEASE + ' && chown -R 1026:100 ' + BASE)
        subprocess.run(['scp', '-O', str(bundle), str(ROOT / 'compose.nas.yaml'), nas['ssh_alias'] + ':' + BASE + '/'], check=True, capture_output=True)
        command('tar -xzf ' + BASE + '/' + bundle.name + ' -C ' + BASE + '/releases/' + RELEASE + ' && cp ' + BASE + '/compose.nas.yaml ' + BASE + '/compose.yaml && cd ' + BASE + ' && /usr/local/bin/docker compose build && /usr/local/bin/docker compose up -d')
        container = json.loads(command('/usr/local/bin/docker inspect williamq-glossary-mirror'))[0]
        receipt = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(), release=RELEASE, service_path=BASE, image=container['Config']['Image'], image_id=container['Image'], loopback_port=18195, source_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}, persistent_state='none; content fetched from published GitHub Pages', backup='first deployment; source bundle and pre-change DNS/proxy records retained')
        save('deployment.json', receipt); print(json.dumps(receipt))
    elif args.step == 'http':
        proxies = api('SYNO.Core.AppPortal.ReverseProxy', 'list')['entries']
        before = PROJECT / 'build/hosting-backup/proxies-before.json'
        before.parent.mkdir(parents=True, exist_ok=True)
        if not before.exists(): before.write_text(json.dumps(proxies, indent=2) + '\n', encoding='utf-8')
        assert not any(p['frontend']['fqdn'] == HOST for p in proxies), 'Inspect existing glossary proxy before changing it'
        entry = dict(description='Open AI Glossary mirror HTTP and ACME', frontend=dict(fqdn=HOST, port=80, protocol=0, acl=None), backend=dict(fqdn='127.0.0.1', port=18195, protocol=0), customize_headers=[dict(name='X-Forwarded-Proto', value='http')], proxy_connect_timeout=30, proxy_read_timeout=60, proxy_send_timeout=60, proxy_http_version=1, proxy_intercept_errors=False)
        api('SYNO.Core.AppPortal.ReverseProxy', 'create', entry=entry)
        after = api('SYNO.Core.AppPortal.ReverseProxy', 'list')['entries']
        assert {p['UUID']: p for p in proxies} == {p['UUID']: p for p in after if p['frontend']['fqdn'] != HOST}, 'Unrelated proxy changed'
        target = next(p for p in after if p['frontend']['fqdn'] == HOST)
        save('http-proxy.json', target); print(json.dumps(target))
    else:
        container = json.loads(command('/usr/local/bin/docker inspect williamq-glossary-mirror'))[0]
        print(json.dumps({'status': container['State']['Status'], 'health': container['State'].get('Health', {}).get('Status'), 'ports': container['NetworkSettings']['Ports']}))


if __name__ == '__main__':
    main()
