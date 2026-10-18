import unittest
import io
import threading
from http.server import ThreadingHTTPServer
from unittest.mock import patch, Mock
from urllib.request import Request, urlopen
from server import upstream_url, mirror_location, ORIGIN, Handler


class MirrorTests(unittest.TestCase):
    def test_path_mapping_preserves_links_and_query(self):
        for path in ['/', '/terms/harness.html', '/assets/style.css', '/glossary.pdf', '/BUILD-INFO.json?check=1']:
            self.assertEqual(upstream_url(path), ORIGIN + path)

    def test_no_escape_or_open_proxy(self):
        for path in ['https://example.org/', '//example.org/', '/../other/', '/%2e%2e/other/', '/%252e%252e/other/', '/a/%5c../', '/a/%00b']:
            with self.assertRaises(ValueError, msg=path):
                upstream_url(path)

    def test_redirects_stay_in_glossary(self):
        self.assertEqual(mirror_location(ORIGIN + '/terms/workflow.html'), '/terms/workflow.html')
        self.assertEqual(mirror_location(ORIGIN), '/')
        for location in ['https://example.org/', 'https://williamq96.github.io/other/',
                         'https://williamq96.github.io/plale-lab-glossary/', '//example.org/']:
            with self.assertRaises(ValueError):
                mirror_location(location)

    def test_requests_read_current_upstream_and_do_not_forward_credentials(self):
        body = [b'published-edition-1']
        def response(request, timeout):
            self.assertNotIn('Cookie', request.headers)
            self.assertNotIn('Authorization', request.headers)
            self.assertEqual(request.get_header('Cache-control'), 'no-cache')
            stream = io.BytesIO(body[0])
            stream.code = 200
            stream.headers = {'Content-Type': 'application/json', 'Content-Length': str(len(body[0]))}
            return stream
        opener = Mock(); opener.open.side_effect = response
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with patch('server.build_opener', return_value=opener):
                for edition in [b'published-edition-1', b'published-edition-2']:
                    body[0] = edition
                    request = Request('http://127.0.0.1:' + str(server.server_port) + '/BUILD-INFO.json', headers={'Cookie': 'private', 'Authorization': 'Bearer private'})
                    with urlopen(request, timeout=3) as actual:
                        self.assertEqual(actual.read(), edition)
                        self.assertEqual(actual.headers['Cache-Control'], 'no-store')
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
