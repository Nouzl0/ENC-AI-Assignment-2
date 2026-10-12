"""Real CLIs on deterministic local fixtures; never benchmarks a product."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import load_all_cases, read_csv
from integrity import final_rating_problems
from make_demo_data import SYSTEMS, create_fixture, run_cli


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="czai-pipeline-test-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.work = Path(cls.tmp.name, "fixture")
        with patch.dict(os.environ, PYTHONHASHSEED="1", TZ="UTC"):
            cls.summary = create_fixture(cls.work)

    def test_full_pipeline_and_preconsensus_integrity(self):
        self.assertEqual(self.summary, dict(runs=500, terminal_failures=58, aggregate_rows=35))
        runs = [row for p in sorted((self.work / "runs").glob("*.csv")) for row in read_csv(p)]
        cases = load_all_cases(self.work / "data", self.work / "data/cases_test.jsonl")
        self.assertEqual(final_rating_problems(runs, self.work / "annotation", self.work / "key", cases), [])
        agreement = read_csv(self.work / "results/agreement.csv")
        self.assertTrue(any(r["measure"] == "explicit pairs S2 vs other" and r["kappa"] == "1.000" for r in agreement))
        self.assertTrue(any(r["measure"] == "answer correctness 0-2" and r["kappa"] == "1.000" for r in agreement))
        report = (self.work / "results/report.md").read_text(encoding="utf-8")
        self.assertIn("nikdy podklad nezávislého ratingu ani důkaz S2", report)
        self.assertNotIn("nápověda, pokud", report)
        rows = read_csv(self.work / "results/answer_metrics.csv")
        self.assertTrue(any(r["run_status"] == "completed" and r["first_ok"] == "no" and r["final_ok"] == "yes" for r in rows))
        self.assertEqual(len(read_csv(self.work / "key/blind_key.csv")), 442)
        zero = [r for p in (self.work / "annotation").rglob("pairs_rated.csv") for r in read_csv(p) if r["citation_n"] == "0"]
        self.assertTrue(zero)  # Parser -> export -> human fixture -> score accepts malformed output.
        self.assertTrue(all(r["rating"] == "FAB" for r in zero))
        for p in (self.work / "key/batches").rglob("annotation_batch.json"):
            batch = json.loads(p.read_text())
            self.assertEqual(len(batch["sheets"]), 4)

    def test_seeded_outputs_are_reproducible(self):
        other = Path(self.tmp.name, "repeat-fixture")
        # Each CLI starts in a fresh process with a different hash seed/timezone.
        with patch.dict(os.environ, PYTHONHASHSEED="8675309", TZ="Europe/Prague"):
            create_fixture(other)
        for name in ("metrics.csv", "answer_metrics.csv", "hypotheses.csv", "agreement.csv", "report.md"):
            self.assertEqual((self.work / "results" / name).read_bytes(), (other / "results" / name).read_bytes(), name)
        self.assertEqual(read_csv(self.work / "key/blind_key.csv"), read_csv(other / "key/blind_key.csv"))

    def test_independent_raters_get_equal_inputs_without_automated_hints(self):
        auto = {r["pair_id"]: r for r in read_csv(self.work / "key/pairs_auto_checks.csv")}
        self.assertTrue(auto)
        self.assertIn("auto_suggestion", next(iter(auto.values())))
        for phase in ("dev", "val", "test", "repeat"):
            for kind, identity in (("pairs", "pair_id"), ("answers", "blind_answer_id")):
                first = read_csv(self.work / f"annotation/{phase}/{kind}_to_rate.csv")
                second = read_csv(self.work / f"annotation/{phase}/{kind}_to_rate_rater2.csv")
                self.assertTrue(first and second)
                self.assertEqual(list(first[0]), list(second[0]))
                self.assertFalse(any(k.startswith("auto_") for k in first[0]))
                indexed = {r[identity]: r for r in first}
                for row in second:
                    self.assertEqual(row, indexed[row[identity]])
                if kind == "pairs":
                    self.assertTrue(set(indexed) <= set(auto))

    def score_args(self, out):
        return ("--synthetic", "--runs", self.work / "runs/run_plan_*.csv", "--annotation-dir", self.work / "annotation",
                "--key-dir", self.work / "key", "--data-dir", self.work / "data", "--test-file", self.work / "data/cases_test.jsonl",
                "--prompts-dir", self.work / "prompts", "--out", out, "--systems", ",".join(SYSTEMS), "--focus", "sys_D", "--boot", "20")

    def test_no_overwrite_no_synthetic_final_and_no_double_export(self):
        with self.assertRaises(FileExistsError):
            create_fixture(self.work)
        with self.assertRaisesRegex(RuntimeError, "Refusing to overwrite"):
            run_cli("score.py", *self.score_args(self.work / "results"))
        with self.assertRaisesRegex(RuntimeError, "cannot be combined"):
            run_cli("score.py", *self.score_args(self.work / "forbidden-final"), "--final")
        with self.assertRaisesRegex(RuntimeError, "run already exported"):
            run_cli("check_citations.py", "--synthetic", "--runs", self.work / "runs/run_plan_dev.csv", "--data-dir", self.work / "data",
                    "--test-file", self.work / "data/cases_test.jsonl", "--out-dir", self.work / "duplicate-export",
                    "--key-dir", self.work / "key", "--offline")

    def test_dangling_output_symlinks_are_rejected_before_any_write(self):
        for name in ("metrics.csv", "answer_metrics.csv", "hypotheses.csv", "agreement.csv",
                     "report.md", "scoring_inputs.json", "replay_provenance.json"):
            with self.subTest(output=name):
                out = Path(self.tmp.name, "dangling-" + name)
                out.mkdir()
                target = Path(self.tmp.name, "must-not-exist-" + name)
                (out / name).symlink_to(target)
                self.assertFalse((out / name).exists())
                with self.assertRaisesRegex(RuntimeError, "Refusing to overwrite"):
                    run_cli("score.py", *self.score_args(out))
                self.assertFalse(target.exists())
                self.assertEqual(list(out.iterdir()), [out / name])

    def test_unrated_pair_blocks_scoring_instead_of_improving_precision(self):
        p = self.work / "annotation/dev/pairs_rated.csv"
        original = p.read_bytes()
        try:
            text = p.read_text(encoding="utf-8-sig")
            self.assertIn(",S2,", text)
            p.write_text(text.replace(",S2,", ",,", 1), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unrated or unmatched"):
                run_cli("score.py", *self.score_args(self.work / "unrated"))
            self.assertFalse((self.work / "unrated/report.md").exists())
        finally:
            p.write_bytes(original)

    def test_original_annotation_sheets_cannot_be_silently_rewritten(self):
        p = self.work / "annotation/dev/answers_to_rate.csv"
        original = p.read_bytes()
        try:
            p.write_bytes(original + b"\n")
            runs = [row for path in (self.work / "runs").glob("*.csv") for row in read_csv(path)]
            cases = load_all_cases(self.work / "data", self.work / "data/cases_test.jsonl")
            self.assertTrue(any("original annotation sheet changed" in e for e in final_rating_problems(runs, self.work / "annotation", self.work / "key", cases)))
        finally:
            p.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
