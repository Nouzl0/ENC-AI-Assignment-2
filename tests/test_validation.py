from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CaseValidationTests(unittest.TestCase):
    def test_25_cases_fail_assignment_minimum(self):
        with tempfile.TemporaryDirectory() as directory:
            for split, n in (("dev", 10), ("val", 5), ("test", 10)):
                rows = (ROOT / "data" / f"cases_{split}.jsonl").read_text().splitlines()[:n]
                Path(directory, f"cases_{split}.jsonl").write_text("\n".join(rows) + "\n")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_cases.py"), "--data-dir", directory],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("< 40 required", result.stdout)


if __name__ == "__main__":
    unittest.main()
