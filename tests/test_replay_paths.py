import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from replay_paths import configure_path_map, resolve_input


class ReplayPathTests(unittest.TestCase):
    def tearDown(self):
        configure_path_map()

    def test_disjoint_prefixes_and_symlink_containment(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo, private = root / "repo", root / "private"
            repo.mkdir()
            private.mkdir()
            path = root / "map.json"
            prefixes = [{"from": "/old/repo", "to": str(repo)},
                        {"from": "/old/private", "to": str(private)}]
            path.write_text(json.dumps(dict(schema_version=1, prefixes=prefixes)))
            configure_path_map(path, repo)
            self.assertEqual(resolve_input("/old/private/holdout.jsonl"), str(private / "holdout.jsonl"))
            self.assertEqual(resolve_input("/old/private-sibling/file"), "/old/private-sibling/file")
            (private / "escape").symlink_to(repo, target_is_directory=True)
            for p in ("/old/private/escape/file", str(private / "escape/file")):
                with self.assertRaisesRegex(ValueError, "escapes"):
                    resolve_input(p)
            for bad in ([dict(prefixes[0], **{"from": "/old"}), prefixes[1]],
                        [prefixes[0], dict(prefixes[1], to=str(repo))],
                        [dict(prefixes[0], **{"from": "relative"}), prefixes[1]],
                        prefixes[:1]):
                path.write_text(json.dumps(dict(schema_version=1, prefixes=bad)))
                with self.assertRaises(ValueError):
                    configure_path_map(path, repo)
            # Targets may not fall inside any original prefix (double mapping).
            path.write_text(json.dumps(dict(schema_version=1, prefixes=[
                {"from": str(root), "to": str(repo)}, prefixes[1]])))
            with self.assertRaisesRegex(ValueError, "cross-overlap"):
                configure_path_map(path, repo)
            path.write_text(json.dumps(dict(schema_version=1, prefixes=[
                {"from": str(repo), "to": str(repo)}, prefixes[1]])))
            configure_path_map(path, repo)
            mapped = resolve_input("/old/private/file")
            self.assertEqual(resolve_input(mapped), mapped)


if __name__ == "__main__":
    unittest.main()
