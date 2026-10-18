"""Compare public mirror bytes and provenance; optional temporary edge routing."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from http.client import HTTPSConnection
import ipaddress
import json
from pathlib import Path
import re
import socket
import ssl
from urllib.request import Request, urlopen

HOST = 'glossary.williamq.dev'
SOURCE = 'https://williamq96.github.io/open-AI-glossary/'


def fetch_mirror(path, edge_ip=None):
    connection = HTTPSConnection(HOST, timeout=30, context=ssl.create_default_context())
    if edge_ip:
        # Keep the real Host/SNI and normal certificate verification.
        connection._create_connection = lambda address, timeout, source_address: socket.create_connection((edge_ip, address[1]), timeout)
    try:
        connection.request('GET', '/' + path, headers={'User-Agent': 'WilliamQ-Glossary-Verification/1.0'})
        response = connection.getresponse()
        body = response.read(); headers = dict(response.getheaders())
        assert response.status == 200, (path, response.status)
        assert response.getheader('CF-Ray'), 'Expected Cloudflare edge response'
        assert response.getheader('Cache-Control') == 'no-store', path
        return body, headers
    finally:
        connection.close()


def fetch_source(path):
    request = Request(SOURCE + path, headers={'User-Agent': 'WilliamQ-Glossary-Verification/1.0', 'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity'})
    with urlopen(request, timeout=30) as response:
        assert response.status == 200
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edge-ip', help='Temporary routing to a currently verified public edge IP; no DNS settings changed')
    parser.add_argument('--expect-commit')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('validation.json'))
    args = parser.parse_args()
    if args.edge_ip:
        assert ipaddress.ip_address(args.edge_ip).is_global
    paths = ['index.html', 'lab-guide.html', 'build-record.html', 'BUILD-INFO.json', 'PDF-SNAPSHOT.json', 'glossary.pdf', 'assets/style.css', 'assets/search.js', 'assets/fonts/manrope.ttf', 'assets/fonts/newsreader.ttf']
    published = json.loads(fetch_source('BUILD-INFO.json'))
    paths += ['terms/' + term + '.html' for term in published['display_order']]
    def compare(path):
        mirror, headers = fetch_mirror(path, args.edge_ip)
        source = fetch_source(path)
        # The existing zone adds its public analytics beacon to HTML. Compare
        # the glossary bytes after excluding only that observed edge addition.
        normalized = mirror
        if path.endswith('.html'):
            normalized = re.sub(rb'<script\b(?=[^>]*\bsrc="https://static\.cloudflareinsights\.com/)[^>]*\bdata-cf-beacon=[^>]*></script>\r?\n?', b'', mirror)
        assert normalized == source, 'Mirror differs: ' + path
        return path, mirror, {'source_sha256': hashlib.sha256(source).hexdigest(), 'response_sha256': hashlib.sha256(mirror).hexdigest(), 'bytes': len(mirror), 'cf_ray': headers.get('CF-RAY', headers.get('CF-Ray')), 'byte_equal': mirror == source, 'glossary_bytes_equal': True, 'edge_analytics_excluded': normalized != mirror}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(compare, paths))
    bodies = {path: body for path, body, _ in results}
    build = json.loads(bodies['BUILD-INFO.json']); snapshot = json.loads(bodies['PDF-SNAPSHOT.json'])
    assert build['source_commit'] == snapshot['source_commit'] and build['source_sha256'] == snapshot['source_sha256']
    if args.expect_commit: assert build['source_commit'] == args.expect_commit, build['source_commit']
    assert hashlib.sha256(bodies['glossary.pdf']).hexdigest() == snapshot['pdf_sha256']
    receipt = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'hostname': HOST, 'source': SOURCE, 'routing': 'temporary current public edge IP with hostname/SNI verification' if args.edge_ip else 'normal system DNS', 'content_version': build['content_version'], 'source_commit': build['source_commit'], 'source_sha256': build['source_sha256'], 'pdf_sha256': snapshot['pdf_sha256'], 'cloudflare_cache': 'no-store / dynamic', 'resources': {path: check for path, _, check in results}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'resources': len(results), 'version': build['content_version'], 'commit': build['source_commit'], 'glossary_bytes_equal': True, 'html_edge_analytics_excluded': True, 'tls_verified': True}))


if __name__ == '__main__':
    main()
