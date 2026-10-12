import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from replay_paths import configure_path_map, resolve_input


class ReplayPathTests(unittest.TestCase):
    def tearDown(self):
        configure_path_map()

    def test_duplicate_json_keys_are_rejected_and_clear_previous_map(self):
        with tempfile.TemporaryDirectory() as d:
            repo, private = Path(d, "repo"), Path(d, "private")
            repo.mkdir()
            private.mkdir()
            path = Path(d, "map.json")
            valid = {
                "schema_version": 1,
                "prefixes": [
                    {"from": "/old/repo", "to": str(repo)},
                    {"from": "/old/private", "to": str(private)},
                ],
            }
            for duplicate in ('"schema_version":0,', '"prefixes":[],'):
                path.write_text(json.dumps(valid), encoding="utf-8")
                configure_path_map(path, repo)
                path.write_text(
                    "{" + duplicate + json.dumps(valid)[1:], encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    configure_path_map(path, repo)
                self.assertEqual(
                    resolve_input("/old/private/file"), "/old/private/file"
                )

    def test_disjoint_prefixes_and_symlink_containment(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo, private = root / "repo", root / "private"
            repo.mkdir()
            private.mkdir()
            path = root / "map.json"
            prefixes = [
                {"from": "/old/repo", "to": str(repo)},
                {"from": "/old/private", "to": str(private)},
            ]
            path.write_text(json.dumps({"schema_version": 1, "prefixes": prefixes}))
            configure_path_map(path, repo)
            self.assertEqual(
                resolve_input("/old/private/holdout.jsonl"),
                str(private / "holdout.jsonl"),
            )
            self.assertEqual(
                resolve_input("/old/private-sibling/file"), "/old/private-sibling/file"
            )
            (private / "escape").symlink_to(repo, target_is_directory=True)
            for p in ("/old/private/escape/file", str(private / "escape/file")):
                with self.assertRaisesRegex(ValueError, "escapes"):
                    resolve_input(p)
            for bad in (
                [dict(prefixes[0], **{"from": "/old"}), prefixes[1]],
                [prefixes[0], dict(prefixes[1], to=str(repo))],
                [dict(prefixes[0], **{"from": "relative"}), prefixes[1]],
                prefixes[:1],
            ):
                path.write_text(json.dumps({"schema_version": 1, "prefixes": bad}))
                with self.assertRaises(ValueError):
                    configure_path_map(path, repo)
            # Targets may not fall inside any original prefix (double mapping).
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "prefixes": [{"from": str(root), "to": str(repo)}, prefixes[1]],
                    }
                )
            )
            with self.assertRaisesRegex(ValueError, "cross-overlap"):
                configure_path_map(path, repo)
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "prefixes": [{"from": str(repo), "to": str(repo)}, prefixes[1]],
                    }
                )
            )
            configure_path_map(path, repo)
            mapped = resolve_input("/old/private/file")
            self.assertEqual(resolve_input(mapped), mapped)


if __name__ == "__main__":
    unittest.main()
