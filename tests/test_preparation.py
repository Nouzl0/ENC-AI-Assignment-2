"""Offline handoff examples and plan sizes, never product measurements."""
import csv
import datetime as dt
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_citations import stratified_sample
from common import load_all_cases, read_csv, sha256_file
from freeze_protocol import gate_matrix_problems
from integrity import source_evidence_problems, timestamp
from make_demo_data import SYSTEMS, make_cases, run_cli
from make_evidence_example import create_example


class PreparationTests(unittest.TestCase):
    def test_cli_utf8_diagnostics_are_decoded_under_ascii_locale(self):
        env = dict(os.environ, LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0",
                   PYTHONIOENCODING="ascii", PYTHONDONTWRITEBYTECODE="1")
        code = """
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from make_demo_data import make_cases, run_cli
with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    make_cases(work)
    path = work / 'data/cases_dev.jsonl'
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    rows[0]['language'] = '\\u010de\\u0161tina'
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\\n' for row in rows), encoding='utf-8')
    try:
        run_cli('validate_cases.py', '--data-dir', work / 'data', '--no-test')
    except RuntimeError as error:
        assert rows[0]['language'] in str(error), str(error)
    else:
        raise AssertionError('invalid language was accepted')
"""
        result = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts")],
                                env=env, capture_output=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("git"), "Git is needed to test checkout byte preservation")
    def test_autocrlf_checkout_preserves_frozen_file_bytes(self):
        """Same commit must retain LF bytes even on a CRLF-configured machine."""
        with tempfile.TemporaryDirectory(prefix="czai-checkout-test-") as directory:
            repo, checkout = Path(directory, "repo"), Path(directory, "checkout")
            checkout.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1")

            def git(*args):
                subprocess.run(["git", "-c", "core.autocrlf=true", *args], cwd=repo,
                               env=env, check=True, capture_output=True, timeout=30)

            repo.mkdir()
            git("-c", "init.defaultBranch=main", "init", "--quiet")
            names = (".gitattributes", "PROTOCOL.md", "annotation/rubric.md",
                     "prompts/P2_structured_cs.txt", "scripts/score.py")
            for name in names:
                target = repo / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            # Auto-detection must leave binary artefacts unchanged too.
            (repo / "binary.bin").write_bytes(b"\x00\r\n\xff\n")
            names += ("binary.bin",)
            git("add", "--", *names)
            git("checkout-index", "--all", "--prefix=" + str(checkout) + os.sep)
            for name in names:
                with self.subTest(file=name):
                    self.assertEqual((repo / name).read_bytes(), (checkout / name).read_bytes())

    def test_filled_demo_evidence_is_complete_but_not_verified(self):
        with tempfile.TemporaryDirectory(prefix="czai-evidence-test-") as directory:
            out = Path(directory, "example")
            output = run_cli("make_evidence_example.py", "--out", out)
            self.assertIn("no human verification or benchmark", output)
            source = read_csv(out / "source_evidence.csv")
            daily = read_csv(out / "run_day_evidence.csv")
            self.assertEqual((len(source), len(daily)), (5, 4))
            for file, template in (("source_evidence.csv", "data/source_evidence_TEMPLATE.csv"),
                                   ("run_day_evidence.csv", "annotation/run_day_evidence_TEMPLATE.csv")):
                with (out / file).open(encoding="utf-8-sig", newline="") as actual, \
                        (ROOT / template).open(encoding="utf-8-sig", newline="") as expected:
                    self.assertEqual(next(csv.reader(actual)), next(csv.reader(expected)))
            cases = {c["task_id"]: c for c in json.loads((out / "reference_units_DEMO.json").read_text(encoding="utf-8"))}
            expected_units = {(c["task_id"], f"{prefix}{i}"): (fact, kind)
                              for c in cases.values()
                              for prefix, field, kind in (("RF", "required_facts", "required"), ("OF", "optional_facts", "optional"))
                              for i, fact in enumerate(c["reference_answer_or_tests"][field], 1)}
            self.assertEqual({(r["task_id"], r["fact_id"]) for r in source}, set(expected_units))
            for row in source:
                self.assertEqual((row["fact_text"], row["reference_kind"]), expected_units[row["task_id"], row["fact_id"]])
                self.assertNotEqual(row["reference_value"], row["fact_text"])
                self.assertEqual(row["valid_as_of"], "2026-01-01")
                self.assertEqual(row["archive_url"], "")
            self.assertEqual({(r["run_date"], r["fact_id"]) for r in daily},
                             {(day, fact) for day in ("2026-01-01", "2026-01-04") for fact in ("RF1", "OF1")})
            self.assertEqual({r["reference_value"] for r in daily if r["fact_id"] == "RF1"}, {"78 měření", "82 měření"})
            self.assertEqual({r["reference_value"] for r in daily if r["fact_id"] == "OF1"}, {"12,34 m", "12,36 m"})
            for row in source + daily:
                self.assertEqual(row["verification_status"], "DEMO_NOT_VERIFIED")
                self.assertIn("nikoli člověk", row["verified_by"])
                self.assertTrue(row["task_id"].startswith("DEMO-"))
                self.assertTrue(row["url"].startswith("https://fixture.invalid/"))
                path = Path(row["snapshot_file"])
                self.assertTrue(path.is_absolute())
                self.assertEqual(path.parent, out)
                self.assertIn("smyšlený zdroj", path.read_text(encoding="utf-8"))
                self.assertEqual(row["snapshot_sha256"], sha256_file(path))
                checked_day = timestamp(row["checked_at"]).astimezone(dt.timezone.utc).date().isoformat()
                self.assertEqual(checked_day, row.get("run_date", row.get("valid_as_of")))
            errors = source_evidence_problems(cases, out / "source_evidence.csv")
            self.assertEqual(len(errors), 5)
            self.assertTrue(all("missing verified evidence" in e for e in errors))
            self.assertFalse(any(out.glob("G*.json")))

    def test_demo_rejects_overwrite_relative_worktree_and_symlink_paths(self):
        with tempfile.TemporaryDirectory(prefix="czai-evidence-path-test-") as directory:
            out = Path(directory, "example")
            self.assertEqual(create_example(out), dict(source_rows=5, run_day_rows=4, verification_status="DEMO_NOT_VERIFIED"))
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            with self.assertRaises(FileExistsError):
                create_example(out)
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
            with self.assertRaisesRegex(ValueError, "absolute"):
                create_example("relative-DEMO")
            forbidden = ROOT / (Path(directory).name + "-forbidden")
            with self.assertRaisesRegex(ValueError, "outside the worktree"):
                create_example(forbidden)
            link = Path(directory, "repo-link")
            link.symlink_to(ROOT, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside the worktree"):
                create_example(link / forbidden.name)
            self.assertFalse(forbidden.exists())

    def test_five_product_lean_plan_and_rater_sample_match_documentation(self):
        with tempfile.TemporaryDirectory(prefix="czai-lean-plan-test-") as directory:
            work = Path(directory)
            make_cases(work)
            prompts = work / "prompts"
            prompts.mkdir()
            for file in (ROOT / "prompts").glob("*.txt"):
                shutil.copy2(file, prompts / file.name)
            # Fictional selection only for testing the plan, not a real P3 winner.
            for lang in ("cs", "en"):
                shutil.copy2(prompts / f"P3B_candidate_{lang}.txt", prompts / f"P3_final_{lang}.txt")
            repeat_ids = [f"DEMO-{i:03d}" for i in range(31, 36)]
            runs = []
            for phase, size in (("dev", 100), ("val", 100), ("test", 150), ("repeat", 50)):
                out = work / "runs" / f"run_plan_{phase}.csv"
                args = ["--synthetic", "--phase", phase, "--data-dir", work / "data",
                        "--test-file", work / "data/cases_test.jsonl", "--prompts-dir", prompts,
                        "--systems", ",".join(SYSTEMS), "--val-candidates", "P3B", "--out", out]
                if phase == "repeat":
                    args += ["--only", ",".join(repeat_ids)]
                run_cli("make_run_plan.py", *args)
                rows = read_csv(out)
                self.assertEqual(len(rows), size)
                self.assertEqual({r["system"] for r in rows}, set(SYSTEMS))
                self.assertTrue(all(r["run_status"] == "planned" for r in rows))
                if phase == "val":
                    self.assertEqual({r["condition"] for r in rows}, {"P2", "P3B"})
                elif phase == "test":
                    self.assertEqual({r["condition"] for r in rows}, {"P1", "P2", "P3"})
                runs.extend(rows)
            cases = load_all_cases(work / "data", work / "data/cases_test.jsonl")
            config = dict(systems=SYSTEMS, val_candidates=["P3B"], repeat_task_ids=repeat_ids)
            self.assertEqual(gate_matrix_problems(runs, cases, config), [])
            self.assertEqual(len(runs), 400)
            # All-completed workload assumption only; there are no fixture answers.
            sample_rows = [dict(blind_answer_id=r["run_id"], _phase=r["phase"], _system=r["system"],
                                _condition=r["condition"]) for r in runs]
            rater2_ids = stratified_sample(sample_rows, .25, random.Random(2026))
            self.assertEqual(len(rater2_ids), 115)
            self.assertEqual(f"{(len(runs) * 10 + len(rater2_ids) * 7) / 60:.1f}", "80.1")
            self.assertFalse((work / "runs/answers").exists())

    def test_p3b_draft_allows_direct_support_and_rounding_in_both_languages(self):
        for lang, terms in (("cs", ("výslovně podporovat", "transparentně", "zaokrouhlení", "výpočtu", "stejnými jednotkami")),
                            ("en", ("explicitly support", "transparently", "rounding", "calculation", "same units"))):
            with self.subTest(language=lang):
                text = (ROOT / f"prompts/P3B_candidate_{lang}.txt").read_text(encoding="utf-8")
                rule = next(line for line in text.splitlines() if line.startswith("9."))
                for term in terms:
                    self.assertIn(term, rule)
                self.assertEqual(text.count("{user_prompt}"), 1)
                self.assertNotIn("CIT-", text)


if __name__ == "__main__":
    unittest.main()
