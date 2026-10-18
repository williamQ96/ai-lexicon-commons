"""A repository rename must update both Pages publication and the live mirror."""
import ast
from pathlib import Path
import sys
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate import REPO


class PublicationTests(unittest.TestCase):
    def test_publication_guard_and_mirror_follow_canonical_repository(self):
        repository = urlsplit(REPO).path.strip('/')
        workflow = (ROOT / '.github/workflows/build-pdf.yml').read_text(encoding='utf-8')
        guard = "github.repository == '" + repository + "'"
        self.assertEqual(workflow.count(guard), 2)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("github.event_name != 'pull_request'", workflow)
        tree = ast.parse((ROOT / 'hosting/server.py').read_text(encoding='utf-8'))
        origin = next(ast.literal_eval(node.value) for node in tree.body
                      if isinstance(node, ast.Assign) and any(
                          isinstance(target, ast.Name) and target.id == 'ORIGIN'
                          for target in node.targets))
        owner, name = repository.split('/')
        self.assertEqual(origin, 'https://' + owner.lower() + '.github.io/' + name)


if __name__ == '__main__':
    unittest.main()
