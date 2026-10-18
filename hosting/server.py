"""Public, fixed-origin mirror of the published glossary; no stored content."""
import json
import os
from pathlib import Path
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOST = 'glossary.williamq.dev'
ORIGIN = 'https://williamq96.github.io/ai-lexicon-commons'


def upstream_url(path):
    parts = urlsplit(path)
    if parts.scheme or parts.netloc or not parts.path.startswith('/'):
        raise ValueError('Only local paths are accepted')
    decoded = parts.path
    for _ in range(4):
        decoded = unquote(decoded)
        if '\\' in decoded or any(p in {'.', '..'} for p in decoded.split('/')):
            raise ValueError('Invalid path')
        if any(ord(c) < 32 or ord(c) == 127 for c in decoded):
            raise ValueError('Invalid path')
    if unquote(decoded) != decoded:
        raise ValueError('Nested encoding is not accepted')
    return ORIGIN + parts.path + ('?' + parts.query if parts.query else '')


def mirror_location(location):
    if location.startswith(ORIGIN + '/'):
        return location[len(ORIGIN):]
    if location == ORIGIN:
        return '/'
    raise ValueError('Unexpected upstream redirect')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = 'WilliamQ-Glossary-Mirror/1.0'

    def reply(self, status, content, mime='text/plain; charset=utf-8', location=None):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if location:
            self.send_header('Location', location)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(content)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        self.connection.settimeout(30)
        host = self.headers.get('Host', '').split(':')[0]
        if host not in {HOST, '127.0.0.1', 'localhost'}:
            self.reply(421, b'Unexpected host\n')
            return
        try:
            target = upstream_url(self.path)
        except ValueError:
            self.reply(400, b'Invalid path\n')
            return
        path = urlsplit(self.path).path
        if path == '/_mirror-health':
            self.reply(200, json.dumps({'status': 'ok', 'origin': ORIGIN, 'mode': 'live-proxy'}).encode(), 'application/json')
            return
        if path.startswith('/.well-known/acme-challenge/'):
            name = path.removeprefix('/.well-known/acme-challenge/')
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', name):
                self.reply(404, b'Not found\n')
                return
            file = Path(os.environ.get('ACME_DIRECTORY', '/acme-challenge')) / name
            if not file.is_file():
                self.reply(404, b'Not found\n')
                return
            self.reply(200, file.read_bytes())
            return
        if self.headers.get('X-Forwarded-Proto') == 'http':
            self.reply(308, b'Use HTTPS\n', location='https://' + HOST + self.path)
            return
        request = Request(target, method=self.command, headers={
            'User-Agent': self.server_version,
            'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
        try:
            try:
                response = build_opener(NoRedirect()).open(request, timeout=20)
            except HTTPError as error:
                response = error
            with response:
                status = response.code
                location = response.headers.get('Location')
                if 300 <= status < 400:
                    self.reply(status, b'Redirect\n', location=mirror_location(location or ''))
                    return
                self.send_response(status)
                for header in ['Content-Type', 'Content-Length', 'ETag', 'Last-Modified', 'Content-Disposition']:
                    value = response.headers.get(header)
                    if value:
                        self.send_header(header, value)
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                if self.command != 'HEAD':
                    while chunk := response.read(65536):
                        self.wfile.write(chunk)
        except (URLError, TimeoutError, ValueError):
            self.reply(502, b'Published glossary temporarily unavailable\n')
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8000'))), Handler).serve_forever()
