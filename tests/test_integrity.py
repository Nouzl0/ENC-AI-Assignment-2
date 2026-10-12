import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_citations
import freeze_protocol
import integrity
import score
from common import load_all_cases, read_csv, sha256_file, write_csv
from freeze_protocol import gate_matrix_problems, prepare_manifest, template
from integrity import (
    bind_plan,
    private_path,
    run_artifact_problems,
    timestamp,
    verify_freeze,
    verify_plans,
    write_json_new,
)
from replay_paths import configure_path_map

ROOT = Path(__file__).resolve().parents[1]


class IntegrityTests(unittest.TestCase):
    def test_private_path_rejects_worktree_and_symlink(self):
        for relative in ("relative-artifact", "../relative-artifact"):
            with self.assertRaisesRegex(ValueError, "absolute"):
                private_path(relative)
        with self.assertRaises(ValueError):
            private_path(str(ROOT / "private/test.jsonl"))
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory, "linked")
            link.symlink_to(ROOT, target_is_directory=True)
            with self.assertRaises(ValueError):
                private_path(str(link / "data/cases_dev.jsonl"))
            self.assertEqual(private_path(directory), str(Path(directory).resolve()))

    def test_default_case_loading_never_opens_test(self):
        cases = load_all_cases()
        self.assertEqual(len(cases), 30)
        self.assertFalse(
            any(
                c["development_validation_test_split"] == "test" for c in cases.values()
            )
        )
        with tempfile.TemporaryDirectory() as directory:
            for split in ("dev", "val"):
                Path(directory, f"cases_{split}.jsonl").write_text(
                    '{"task_id":"duplicate"}\n'
                )
            with self.assertRaises(ValueError):
                load_all_cases(directory)

    def test_public_candidate_check_uses_utf8_even_in_ascii_locale(self):
        """Exercise only public candidates; no private holdout is opened."""
        env = dict(
            os.environ,
            LC_ALL="C",
            PYTHONUTF8="0",
            PYTHONCOERCECLOCALE="0",
            PYTHONDONTWRITEBYTECODE="1",
        )
        code = """
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from integrity import holdout_problems
path = Path(sys.argv[1]).parent / 'data/published_test_candidates.jsonl'
candidate = json.loads(path.read_text(encoding='utf-8').splitlines()[0])
tid = candidate['task_id']
errors = holdout_problems({tid: candidate})
assert f'{tid}: overlaps an exposed dev/val/published candidate {tid}' in errors, errors
"""
        result = subprocess.run(
            [sys.executable, "-c", code, str(ROOT / "scripts")],
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unsigned_gate_and_plain_p3_files_do_not_unlock_test(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "G1.json"))
            write_json_new(p, template("G1"))
            with self.assertRaisesRegex(ValueError, "unsigned"):
                verify_freeze(p, "G1")
            with self.assertRaisesRegex(ValueError, "signed_by"):
                prepare_manifest(template("G2"))

    def test_manifest_and_snapshot_json_keys_cannot_silently_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "ambiguous.json")
            for value in (
                '{"attestations":{},"attestations":{"protocol_approved":true}}',
                '{"tables":{"answers":[],"answers":[{}]}}',
                '{"files":{"/private/a":"first","/private/a":"second"}}',
            ):
                with self.subTest(value=value):
                    path.write_text(value, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        integrity.read_json(path)

    def test_plan_preserves_metadata_but_rejects_prompt_changes_and_dropped_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "plan.csv"))
            rows = [
                {
                    "run_id": "r1",
                    "phase": "dev",
                    "task_id": "DEMO-1",
                    "prompt_text": "original",
                    "answer_file": "a.txt",
                    "run_status": "planned",
                }
            ]
            write_csv(p, rows, list(rows[0]))
            bind_plan(p, read_csv(p), synthetic=True)
            rows[0]["run_status"] = "completed"
            write_csv(p, rows, list(rows[0]))
            verify_plans(p, synthetic=True)
            rows[0]["prompt_text"] = "changed"
            write_csv(p, rows, list(rows[0]))
            with self.assertRaisesRegex(ValueError, "removed/changed"):
                verify_plans(p, synthetic=True)

    def test_generated_numeric_plan_fields_match_csv_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "plan.csv"))
            rows = [
                {
                    "run_id": "r",
                    "seq": 1,
                    "run_index": 1,
                    "phase": "dev",
                    "run_status": "planned",
                }
            ]
            write_csv(p, rows, list(rows[0]))
            bind_plan(p, rows, synthetic=True)
            verify_plans(p, synthetic=True)
            write_csv(p, [], list(rows[0]))
            with self.assertRaises(ValueError):
                verify_plans(p, synthetic=True)

    def test_replacement_requires_same_condition_and_recorded_operator_error(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "plan.csv"))
            original = {
                "run_id": "r1",
                "phase": "dev",
                "condition": "P2",
                "seq": "1",
                "answer_file": "a.txt",
                "run_status": "planned",
                "replacement_run_id": "",
                "replaces_run_id": "",
            }
            fields = list(original)
            write_csv(p, [original], fields)
            bind_plan(p, read_csv(p), synthetic=True)
            original.update(run_status="excluded", replacement_run_id="r1-replacement")
            replacement = dict(
                original,
                run_id="r1-replacement",
                seq="2",
                answer_file="b.txt",
                run_status="completed",
                replaces_run_id="r1",
                replacement_run_id="",
            )
            write_csv(p, [original, replacement], fields)
            verify_plans(p, synthetic=True)
            replacement["condition"] = "P3"
            write_csv(p, [original, replacement], fields)
            with self.assertRaisesRegex(ValueError, "changed the experimental"):
                verify_plans(p, synthetic=True)

    def test_timestamps_ranges_and_artifact_hashes(self):
        with self.assertRaises(ValueError):
            timestamp("2026-10-12 14:03")
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory, "answer.txt")
            p.write_text("synthetic answer")
            row = {
                "run_id": "r",
                "task_id": "DEMO-1",
                "system": "sys_A",
                "condition": "P2",
                "split": "dev",
                "run_index": "1",
                "run_status": "completed",
                "failure_type": "none",
                "first_attempt_ok": "yes",
                "final_attempt_ok": "yes",
                "retries": "0",
                "latency_s": "2",
                "first_attempt_latency_s": "2",
                "datetime_start": "2026-01-01T10:00:00+00:00",
                "datetime_end": "2026-01-01T10:00:02+00:00",
                "model_visible": "unknown",
                "plan_tier": "free",
                "operator": "synthetic operator",
                "manual_intervention": "none",
                "cost_note": "no marginal fee",
                "search_used": "unclear",
                "n_sources_shown": "unknown",
                "turns": "1",
                "tool_calls_visible": "unknown",
                "answer_file": str(p),
                "answer_sha256": sha256_file(p),
                "raw_answer_file": str(p),
                "raw_answer_sha256": sha256_file(p),
                "screenshot_file": str(p),
                "screenshot_sha256": sha256_file(p),
            }
            self.assertEqual(run_artifact_problems(row), [])
            row["turns"] = "-1"
            self.assertTrue(run_artifact_problems(row))
            row["turns"] = "1"
            p.write_text("changed")
            self.assertTrue(
                any("SHA-256 mismatch" in e for e in run_artifact_problems(row))
            )

    def test_exact_matrix_requires_configured_repeat_subset(self):
        config = {
            "systems": ["a", "b", "c", "d"],
            "val_candidates": ["P3A"],
            "repeat_task_ids": ["t1"],
        }
        cases = {
            "d1": {"development_validation_test_split": "dev"},
            "v1": {"development_validation_test_split": "val"},
            "t1": {"development_validation_test_split": "test"},
            "t2": {"development_validation_test_split": "test"},
        }
        runs = []
        for phase, tids, conds, indices in (
            ("dev", ["d1"], ["P2"], [1]),
            ("val", ["v1"], ["P2", "P3A"], [1]),
            ("test", ["t1", "t2"], ["P1", "P2", "P3"], [1]),
            ("repeat", ["t1"], ["P2"], [2, 3]),
        ):
            runs += [
                {
                    "phase": phase,
                    "task_id": t,
                    "condition": c,
                    "system": s,
                    "run_index": str(i),
                    "run_status": "failed",
                }
                for t in tids
                for c in conds
                for s in config["systems"]
                for i in indices
            ]
        self.assertEqual(gate_matrix_problems(runs, cases, config), [])
        self.assertTrue(gate_matrix_problems(runs[:-1], cases, config))
        self.assertTrue(gate_matrix_problems([*runs, runs[-1]], cases, config))

    def test_production_annotation_rejects_unfrozen_alternate_data(self):
        with tempfile.TemporaryDirectory() as directory:
            args = [
                "check_citations.py",
                "--data-dir",
                directory,
                "--out-dir",
                directory + "/annotation",
                "--key-dir",
                directory + "/key",
                "--freeze",
                directory + "/G1.json",
                "--offline",
            ]
            with (
                patch.object(sys, "argv", args),
                patch.object(
                    check_citations, "read_csv_glob", return_value=[{"split": "dev"}]
                ),
                self.assertRaisesRegex(SystemExit, "frozen repository data"),
            ):
                check_citations.main()

    def rating_fixture(self, directory):
        annotation, key = Path(directory, "annotation"), Path(directory, "key")
        annotation.mkdir()
        key.mkdir()
        runs = [
            {
                "run_id": f"r{i}",
                "phase": "dev",
                "system": "sys_A",
                "condition": "P2",
                "task_id": "DEMO-1",
                "run_status": "completed",
                "operator": "operator",
                "datetime_start": "2026-01-01T10:00:00+00:00",
                "datetime_end": "2026-01-01T10:00:02+00:00",
            }
            for i in range(1, 5)
        ]
        keys = [{"blind_answer_id": f"A{i}", "run_id": f"r{i}"} for i in range(1, 5)]
        answers = [
            {
                "blind_answer_id": f"A{i}",
                "correctness": "0",
                "n_claims": "1",
                "n_key_facts": "1",
                "key_facts_supported": "0",
                "key_fact_evidence": "{}",
                "check_minutes": "1",
                "segmentation_reviewed": "yes",
                "acknowledges_uncertainty": "na",
                "rater": "rater1",
            }
            for i in range(1, 5)
        ]
        pairs = [
            {
                "blind_answer_id": f"A{i}",
                "pair_id": f"A{i}-T1-none",
                "claim_id": "T1",
                "claim_text": "synthetic claim",
                "citation_n": "",
                "rating": "",
                "source_tier": "",
                "time_ok": "",
                "rater": "rater1",
            }
            for i in range(1, 5)
        ]
        write_csv(key / "blind_key.csv", keys, list(keys[0]))
        write_json_new(
            key / "batches/batch/annotation_batch.json",
            {"rater2_ids": ["A1"], "sheets": {}},
        )
        for name in ("answers_rated", "answers_rated_rater1"):
            write_csv(annotation / (name + ".csv"), answers, list(answers[0]))
        for name in ("pairs_rated", "pairs_rated_rater1"):
            write_csv(annotation / (name + ".csv"), pairs, list(pairs[0]))
        write_csv(
            annotation / "answers_rated_rater2.csv",
            [dict(answers[0], rater="rater2")],
            list(answers[0]),
        )
        write_csv(
            annotation / "pairs_rated_rater2.csv",
            [dict(pairs[0], rater="rater2")],
            list(pairs[0]),
        )
        cases = {
            "DEMO-1": {
                "reference_valid_as_of": "2026-01-01",
                "reference_answer_or_tests": {
                    "required_facts": ["fact"],
                    "optional_facts": [],
                },
            }
        }
        return annotation, key, runs, cases, answers, pairs

    def test_final_changes_require_audit_even_after_raw_agreement_or_single_rating(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, answers, _ = self.rating_fixture(directory)
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )
            answers[0]["correctness"] = "2"  # Both independent raw ratings were 0.
            answers[1]["correctness"] = "1"  # Only one raw rater; still needs an audit.
            write_csv(annotation / "answers_rated.csv", answers, list(answers[0]))
            errors = integrity.final_rating_problems(runs, annotation, key, cases)
            self.assertTrue(any("A1/correctness" in e for e in errors))
            self.assertTrue(any("A2/correctness" in e for e in errors))
            logs = [
                {
                    "item_id": f"A{i}",
                    "item_type": "answer",
                    "field": "correctness",
                    "rater1_value": "0",
                    "rater2_value": "0" if i == 1 else "",
                    "resolution": str(3 - i),
                    "resolved_by": "adjudicator",
                    "note": "synthetic documented correction",
                }
                for i in (1, 2)
            ]
            write_csv(annotation / "disagreements.csv", logs, list(logs[0]))
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )

    def test_gate_rejects_blank_diagnostics_in_each_independent_answer_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, _ = self.rating_fixture(directory)
            for name in (
                "answers_rated.csv",
                "answers_rated_rater1.csv",
                "answers_rated_rater2.csv",
            ):
                path = annotation / name
                original = path.read_bytes()
                try:
                    rows = read_csv(path)
                    rows[0]["acknowledges_uncertainty"] = ""
                    write_csv(path, rows, list(rows[0]))
                    errors = integrity.final_rating_problems(
                        runs, annotation, key, cases
                    )
                    self.assertTrue(
                        any("acknowledges_uncertainty must" in e for e in errors), name
                    )
                finally:
                    path.write_bytes(original)

    def test_gate_rejects_nonfinite_annotation_times_in_all_answer_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, _ = self.rating_fixture(directory)
            for name in (
                "answers_rated.csv",
                "answers_rated_rater1.csv",
                "answers_rated_rater2.csv",
            ):
                path = annotation / name
                original = path.read_bytes()
                try:
                    for value in ("", "NaN", "inf", "-inf", "-1"):
                        with self.subTest(sheet=name, value=value):
                            rows = read_csv(path)
                            rows[0]["check_minutes"] = value
                            write_csv(path, rows, list(rows[0]))
                            errors = integrity.final_rating_problems(
                                runs, annotation, key, cases
                            )
                            self.assertTrue(
                                any("invalid check_minutes" in e for e in errors),
                                errors,
                            )
                finally:
                    path.write_bytes(original)

    def test_gate_rejects_invalid_rf_counts_and_duplicate_evidence_in_all_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, _ = self.rating_fixture(directory)
            for name in (
                "answers_rated.csv",
                "answers_rated_rater1.csv",
                "answers_rated_rater2.csv",
            ):
                path = annotation / name
                original = path.read_bytes()
                try:
                    for field, value in (
                        ("n_key_facts", "NaN"),
                        ("key_facts_supported", "inf"),
                        ("n_key_facts", "2"),
                        ("key_fact_evidence", '{"RF1":[],"RF1":[]}'),
                    ):
                        with self.subTest(sheet=name, field=field):
                            rows = read_csv(path)
                            rows[0][field] = value
                            write_csv(path, rows, list(rows[0]))
                            errors = integrity.final_rating_problems(
                                runs, annotation, key, cases
                            )
                            self.assertTrue(
                                any(
                                    "key-fact" in e or "required-fact" in e
                                    for e in errors
                                ),
                                errors,
                            )
                finally:
                    path.write_bytes(original)

    def test_gate_rf_evidence_uses_each_raters_own_pairs(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, answers, pairs = self.rating_fixture(
                directory
            )
            source = Path(directory, "source.txt")
            source.write_text(
                "SYNTHETIC source, not verified evidence", encoding="utf-8"
            )
            evidence1 = '{"RF1":["A1-T1-1"]}'
            evidence2 = '{"RF1":["A1-T2-1"]}'
            answers[0].update(key_facts_supported="1", key_fact_evidence=evidence1)
            pairs[0].update(
                pair_id="A1-T1-1",
                citation_n="1",
                rating="S2",
                source_tier="1",
                time_ok="na",
                evidence_url="https://example.invalid/source",
                evidence_checked_at="2026-01-01T10:00:03+00:00",
                evidence_locator="fixture line 1",
                evidence_excerpt="fictional support",
                evidence_snapshot=str(source),
                evidence_sha256=sha256_file(source),
            )
            for name in ("answers_rated", "answers_rated_rater1"):
                write_csv(annotation / (name + ".csv"), answers, list(answers[0]))
            for name in ("pairs_rated", "pairs_rated_rater1"):
                write_csv(annotation / (name + ".csv"), pairs, list(pairs[0]))
            raw2 = dict(
                answers[0],
                key_fact_evidence=evidence2,
                check_minutes="2.5",
                rater="rater2",
            )
            raw2_pair = dict(pairs[0], pair_id="A1-T2-1", claim_id="T2", rater="rater2")
            write_csv(annotation / "answers_rated_rater2.csv", [raw2], list(raw2))
            write_csv(
                annotation / "pairs_rated_rater2.csv", [raw2_pair], list(raw2_pair)
            )
            logs = [
                {
                    "item_id": item,
                    "item_type": kind,
                    "field": field,
                    "rater1_value": left,
                    "rater2_value": right,
                    "resolution": final,
                    "resolved_by": "adjudicator",
                    "note": "synthetic segmentation audit",
                }
                for item, kind, field, left, right, final in (
                    (
                        "A1",
                        "answer",
                        "key_fact_evidence",
                        evidence1,
                        evidence2,
                        evidence1,
                    ),
                    ("A1-T1-1", "pair", "present", "yes", "no", "yes"),
                    ("A1-T2-1", "pair", "present", "no", "yes", "no"),
                )
            ]
            write_csv(annotation / "disagreements.csv", logs, list(logs[0]))
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )

            # A valid S2 in another rater's segmentation cannot support raw2's RF.
            raw2["key_fact_evidence"] = evidence1
            write_csv(annotation / "answers_rated_rater2.csv", [raw2], list(raw2))
            write_csv(annotation / "disagreements.csv", logs[1:], list(logs[0]))
            errors = integrity.final_rating_problems(runs, annotation, key, cases)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("required-fact denominator/evidence invalid", errors[0])

    def test_validation_source_evidence_is_complete_and_checked_before_G2(self):
        with tempfile.TemporaryDirectory() as directory:
            _, key, runs, _, _, pairs = self.rating_fixture(directory)
            runs = [dict(r, phase="val") for r in runs]
            source = Path(directory, "source.txt")
            source.write_text("SYNTHETIC source decision log, not human evidence")
            pairs[0].update(
                citation_n="1",
                rating="S2",
                evidence_url="https://fixture.invalid/source",
                evidence_checked_at="2026-01-01T10:00:03+00:00",
                evidence_locator="fixture line 1",
                evidence_excerpt="fictional support",
                evidence_snapshot=str(source),
                evidence_sha256=sha256_file(source),
            )
            snapshot = {
                "tables": {"key": read_csv(key / "blind_key.csv"), "pairs": pairs}
            }
            signed = timestamp("2026-01-01T12:00:00+00:00")
            self.assertEqual(
                integrity.validation_source_problems(snapshot, runs, signed), []
            )
            for field, value in (
                ("evidence_checked_at", ""),
                ("evidence_checked_at", "2026-01-01T09:59:00+00:00"),
                ("evidence_checked_at", "2026-01-04T10:00:00+00:00"),
                ("evidence_checked_at", "2026-01-09T10:00:00+00:00"),
                ("evidence_locator", ""),
                ("evidence_snapshot", ""),
                ("evidence_sha256", "0" * 64),
            ):
                with self.subTest(field=field, value=value):
                    bad = copy.deepcopy(snapshot)
                    bad["tables"]["pairs"][0][field] = value
                    self.assertTrue(
                        integrity.validation_source_problems(bad, runs, signed)
                    )
            # Dev rows are not validation evidence; uncited rows need no source check.
            snapshot["tables"]["pairs"][0]["citation_n"] = ""
            self.assertEqual(
                integrity.validation_source_problems(snapshot, runs, signed), []
            )

    def test_missing_source_fab_needs_absence_evidence_not_an_invented_url(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, pairs = self.rating_fixture(directory)
            snapshot = Path(directory, "missing-source.txt")
            snapshot.write_text(
                "Synthetic original answer cites [9]; source list only has [1]."
            )
            pairs[0].update(
                pair_id="A1-T1-9",
                citation_n="9",
                rating="FAB",
                url="",
                source_line="",
                source_tier="unknown",
                time_ok="na",
                evidence_url="",
                evidence_checked_at="2026-01-01T10:00:03+00:00",
                evidence_locator="original answer and complete source list",
                evidence_excerpt="Marker [9] has no source entry (synthetic test).",
                evidence_snapshot=str(snapshot),
                evidence_sha256=sha256_file(snapshot),
            )

            def save():
                for name in ("pairs_rated", "pairs_rated_rater1"):
                    write_csv(annotation / (name + ".csv"), pairs, list(pairs[0]))
                write_csv(
                    annotation / "pairs_rated_rater2.csv",
                    [dict(pairs[0], rater="rater2")],
                    list(pairs[0]),
                )

            save()
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )
            for rating, url, line in (
                ("S2", "", ""),
                ("NA", "", ""),
                ("FAB", "https://fixture.invalid", ""),
                ("FAB", "", "[9] named source"),
            ):
                with self.subTest(rating=rating, url=url, line=line):
                    pairs[0].update(rating=rating, url=url, source_line=line)
                    save()
                    self.assertTrue(
                        any(
                            "missing source-decision evidence" in e
                            for e in integrity.final_rating_problems(
                                runs, annotation, key, cases
                            )
                        )
                    )
            pairs[0].update(rating="FAB", url="", source_line="", evidence_excerpt="")
            save()
            self.assertTrue(
                any(
                    "missing source-decision evidence" in e
                    for e in integrity.final_rating_problems(
                        runs, annotation, key, cases
                    )
                )
            )

    def test_run_day_requires_exact_facts_current_utc_date_and_content(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, _ = self.rating_fixture(directory)
            cases["DEMO-1"]["reference_valid_as_of"] = "RUN_DAY"
            cases["DEMO-1"]["reference_answer_or_tests"] = {
                "required_facts": ["indicator", "value and month"],
                "optional_facts": ["comparison"],
            }
            for name in (
                "answers_rated.csv",
                "answers_rated_rater1.csv",
                "answers_rated_rater2.csv",
            ):
                ratings = read_csv(annotation / name)
                for rating in ratings:
                    rating["n_key_facts"] = "2"
                write_csv(annotation / name, ratings, list(ratings[0]))
            snapshot = Path(directory, "source.txt")
            snapshot.write_text("synthetic daily reference")
            rows = [
                {
                    "task_id": "DEMO-1",
                    "run_date": "2026-01-01",
                    "fact_id": fid,
                    "reference_value": "current synthetic fact",
                    "url": "https://example.org",
                    "verified_by": "independent checker",
                    "checked_at": "2026-01-01T10:00:03+00:00",
                    "locator": "fixture",
                    "excerpt_or_summary": "synthetic evidence",
                    "snapshot_file": str(snapshot),
                    "snapshot_sha256": sha256_file(snapshot),
                    "verification_status": "verified",
                }
                for fid in ("RF1", "RF2", "OF1")
            ]
            path = annotation / "run_day_evidence.csv"
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )
            # Offset is converted to UTC; this is still January 1 in UTC.
            rows[0]["checked_at"] = "2026-01-02T00:01:00+02:00"
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(
                integrity.final_rating_problems(runs, annotation, key, cases), []
            )
            rows[0].update(
                checked_at="2020-01-01T10:00:00+00:00", excerpt_or_summary=""
            )
            write_csv(path, rows[:1], list(rows[0]))
            errors = integrity.final_rating_problems(runs, annotation, key, cases)
            self.assertTrue(any("checked on the run date" in e for e in errors))
            self.assertTrue(any("exactly every RF/OF" in e for e in errors))
            rows[0].update(
                checked_at="2026-01-01T10:00:03+00:00",
                excerpt_or_summary="synthetic evidence",
            )
            write_csv(path, [*rows, rows[0]], list(rows[0]))
            self.assertTrue(
                any(
                    "duplicate RUN_DAY" in e
                    for e in integrity.final_rating_problems(
                        runs, annotation, key, cases
                    )
                )
            )

    def make_g1_fixture(self, directory):
        repo = Path(directory, "fixture-repo")
        private = Path(directory, "fixture-private")
        private.mkdir()
        for name in ("data", "scripts", "prompts", "annotation"):
            (repo / name).mkdir(parents=True)
        for name in (
            "PROTOCOL.md",
            "annotation/rubric.md",
            "annotation/calibration.md",
        ):
            (repo / name).write_text("synthetic fixture, not actual research approval")
        # Freeze the real CLI implementation before G1 so relocated subprocesses
        # exercise their own imports/default ROOT, not modules from this checkout.
        for script in (ROOT / "scripts").glob("*.py"):
            shutil.copyfile(script, repo / "scripts" / script.name)
        for name in ("P1_baseline", "P2_structured"):
            for lang in ("cs", "en"):
                (repo / "prompts" / f"{name}_{lang}.txt").write_text(
                    "synthetic {user_prompt}"
                )
        (repo / "data/published_test_candidates.jsonl").write_text("")
        (repo / "data/holdout_blueprint.json").write_bytes(
            (ROOT / "data/holdout_blueprint.json").read_bytes()
        )
        snapshot = private / "source.txt"
        snapshot.write_text("synthetic supporting source")
        evidence = []
        for split, start, count in (("dev", 0, 20), ("val", 20, 10), ("test", 30, 10)):
            cases = []
            for i in range(start, start + count):
                j = i % 10
                c = {
                    "task_id": f"DEMO-{i}",
                    "schema_version": 2,
                    "capability": "citation_accuracy",
                    "task_type": "fact"
                    if j < 5
                    else "primary_source"
                    if j < 8
                    else "synthesis",
                    "difficulty": "easy" if j < 2 else "medium" if j < 7 else "hard",
                    "language": "cs" if j < 5 else "en",
                    "domain": [
                        "veda_zdravi",
                        "pravo",
                        "it",
                        "ekonomika",
                        "historie_kultura",
                    ][j % 5],
                    "development_validation_test_split": split,
                    "user_prompt": f"unique_query_{i} unique_topic_{i} unique_marker_{i}",
                    "context_or_files": [],
                    "expected_properties": ["fact"],
                    "reference_answer_or_tests": {
                        "reference_answer": "fact",
                        "key_facts": ["fact"],
                        "required_facts": ["fact"],
                        "optional_facts": [],
                        "gold_sources": [{"url": "https://example.org"}],
                    },
                    "edge_case_type": "ambiguous" if j < 4 else "none",
                    "evaluation_method": "human",
                    "source_or_provenance": "synthetic fixture",
                    "reference_valid_as_of": "2026-01-01",
                }
                cases.append(c)
                evidence.append(
                    {
                        "task_id": c["task_id"],
                        "fact_id": "RF1",
                        "reference_kind": "required",
                        "fact_text": "fact",
                        "reference_value": "fact",
                        "valid_as_of": "2026-01-01",
                        "verified_by": "synthetic checker",
                        "url": "https://example.org",
                        "locator": "fixture",
                        "excerpt_or_summary": "synthetic source",
                        "checked_at": "2026-01-01T00:00:00+00:00",
                        "snapshot_file": str(snapshot),
                        "snapshot_sha256": sha256_file(snapshot),
                        "verification_status": "verified",
                    }
                )
            path = (
                private / "holdout.jsonl"
                if split == "test"
                else repo / f"data/cases_{split}.jsonl"
            )
            path.write_text("".join(json.dumps(c) + "\n" for c in cases))
        evpath = str(private / "source_evidence.csv")
        write_csv(evpath, evidence, list(evidence[0]))
        pilot = private / "pilot.txt"
        pilot.write_text("synthetic fixture pilot record; no product calls")
        config = template("G1")
        config.update(
            signed_by="synthetic test signer",
            signed_at="2026-01-01T00:00:00+00:00",
            roles={
                "prompt_author": "synthetic author",
                "data_steward": "synthetic steward",
                "reference_checker": "synthetic checker",
            },
        )
        config["attestations"] = dict.fromkeys(config["attestations"], True)
        config["config"]["repeat_task_ids"] = [f"DEMO-{i}" for i in range(30, 40)]
        config["inputs"] = {
            "test_cases": str(private / "holdout.jsonl"),
            "source_evidence": evpath,
            "pilot_record": str(pilot),
        }
        return repo, private, config

    def test_g1_roundtrip_rejects_changed_data_and_unverified_references(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, private, config = self.make_g1_fixture(directory)
            with (
                patch.object(integrity, "ROOT", str(repo)),
                patch.object(freeze_protocol, "ROOT", str(repo)),
            ):
                m = prepare_manifest(config)
                path = str(private / "G1.json")
                write_json_new(path, m)
                self.assertEqual(verify_freeze(path)["gate"], "G1")
                changed = repo / "data/cases_dev.jsonl"
                original = changed.read_bytes()
                changed.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "frozen file changed"):
                    verify_freeze(path)
                changed.write_bytes(original)
                blueprint = repo / "data/holdout_blueprint.json"
                original_blueprint = blueprint.read_bytes()
                blueprint.write_bytes(original_blueprint + b"\n")
                with self.assertRaisesRegex(ValueError, "frozen file changed"):
                    verify_freeze(path)
                blueprint.write_bytes(original_blueprint)
                rows = read_csv(config["inputs"]["source_evidence"])
                rows[0]["verification_status"] = "pending"
                write_csv(config["inputs"]["source_evidence"], rows, list(rows[0]))
                with self.assertRaisesRegex(ValueError, "missing verified evidence"):
                    prepare_manifest(config)
                rows[0].update(
                    verification_status="verified",
                    checked_at="2099-01-01T00:00:00+00:00",
                )
                write_csv(config["inputs"]["source_evidence"], rows, list(rows[0]))
                with self.assertRaisesRegex(
                    ValueError, "G1 signed_at precedes reference verification"
                ):
                    prepare_manifest(config)
                # Same instant as G1 in another timezone is valid, not a future check.
                rows[0]["checked_at"] = "2026-01-01T01:00:00+01:00"
                write_csv(config["inputs"]["source_evidence"], rows, list(rows[0]))
                self.assertEqual(prepare_manifest(config)["gate"], "G1")

    def test_g2_g3_chain_and_failed_runs_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, private, config = self.make_g1_fixture(directory)
            config["config"]["focus"] = (
                "chatgpt"  # Prespecified alternate focus, never chosen from scores.
            )
            for name in ("P3A_candidate", "P3B_candidate", "P3_final"):
                for lang in ("cs", "en"):
                    (repo / "prompts" / f"{name}_{lang}.txt").write_text(
                        "synthetic candidate {user_prompt}"
                    )
            (repo / "prompts/CHANGELOG.md").write_text("synthetic test selection")
            with (
                patch.object(integrity, "ROOT", str(repo)),
                patch.object(freeze_protocol, "ROOT", str(repo)),
            ):
                g1 = str(private / "G1.json")
                write_json_new(g1, prepare_manifest(config))
                log = private / "outage.txt"
                log.write_text("synthetic outage log (not a benchmark result)")
                plans = []
                for phase, start, count, conds, indices in (
                    ("dev", 0, 20, ["P2"], [1]),
                    ("val", 20, 10, ["P2", "P3A", "P3B"], [1]),
                ):
                    rows = self.failed_fixture_rows(
                        repo, log, phase, start, count, conds, indices
                    )
                    p = str(private / f"run_plan_{phase}.csv")
                    write_csv(p, rows, list(rows[0]))
                    bind_plan(p, read_csv(p), g1, prompts_dir=str(repo / "prompts"))
                    plans.append(p)
                annotation, key = private / "annotation", private / "key"
                annotation.mkdir()
                key.mkdir()
                val_result = private / "val-results"
                self.score_fixture(repo, private, g1, val_result)
                metrics_path = str(val_result / "metrics.csv")
                g2config = template("G2")
                g2config.update(
                    parent_path=g1,
                    signed_by="synthetic signer",
                    signed_at="2026-01-02T00:00:00+00:00",
                    selected_candidate="P3A",
                )
                g2config["attestations"] = dict.fromkeys(g2config["attestations"], True)
                g2config["inputs"] = {
                    "selection_record": str(log),
                    "development_analysis": str(log),
                    "validation_metrics": metrics_path,
                    "validation_scoring_inputs": str(
                        val_result / "scoring_inputs.json"
                    ),
                    "validation_plans": [plans[1]],
                }
                self.assert_bad_g2_inputs_rejected(g2config)
                g2 = str(private / "G2.json")
                write_json_new(g2, prepare_manifest(g2config))
                self.assertEqual(verify_freeze(g2)["gate"], "G2")
                for phase, indices in (("test", [1]), ("repeat", [2, 3])):
                    rows = self.failed_fixture_rows(
                        repo,
                        log,
                        phase,
                        30,
                        10,
                        ["P1", "P2", "P3"] if phase == "test" else ["P2"],
                        indices,
                    )
                    p = str(private / f"run_plan_{phase}.csv")
                    write_csv(p, rows, list(rows[0]))
                    bind_plan(p, read_csv(p), g2, prompts_dir=str(repo / "prompts"))
                    plans.append(p)
                g3config = template("G3")
                g3config.update(
                    parent_path=g2,
                    signed_by="synthetic signer",
                    signed_at="2026-01-05T00:00:00+00:00",
                )
                g3config["attestations"] = dict.fromkeys(g3config["attestations"], True)
                g3config["inputs"] = {
                    "run_plans": plans,
                    "annotation_dir": str(annotation),
                    "key_dir": str(key),
                    "deviations_record": str(log),
                }
                g3 = str(private / "G3.json")
                write_json_new(g3, prepare_manifest(g3config))
                self.assertEqual(verify_freeze(g3)["gate"], "G3")
                # Exercise the actual final scoring entry point in the isolated
                # fake repo, never approve gates or create results in the worktree.
                result = private / "final-results"
                argv = [
                    "score.py",
                    "--final",
                    "--freeze",
                    g3,
                    "--runs",
                    str(private / "run_plan_*.csv"),
                    "--annotation-dir",
                    str(annotation),
                    "--key-dir",
                    str(key),
                    "--data-dir",
                    str(repo / "data"),
                    "--prompts-dir",
                    str(repo / "prompts"),
                    "--out",
                    str(result),
                    "--focus",
                    config["config"]["focus"],
                ]
                with (
                    patch.object(score, "ROOT", str(repo)),
                    patch.object(score, "PROMPTS", str(repo / "prompts")),
                    patch.object(sys, "argv", argv),
                ):
                    score.main()
                per_run = read_csv(result / "answer_metrics.csv")
                self.assertEqual(len(per_run), 500)
                self.assertTrue(
                    all(
                        r["run_status"] == "failed" and float(r["precision"]) == 0
                        for r in per_run
                    )
                )
                hypotheses = read_csv(result / "hypotheses.csv")
                self.assertEqual([h["supported"] for h in hypotheses], ["no", "no"])
                self.assertEqual(
                    [h["ci_above_margin"] for h in hypotheses], ["no", "no"]
                )
                self.assertEqual([int(h["n_cases"]) for h in hypotheses], [10, 10])
                self.assertEqual(verify_freeze(g3)["gate"], "G3")
                log.write_text("changed outage artifact")
                with self.assertRaisesRegex(ValueError, "frozen file changed"):
                    verify_freeze(g3)
                log.write_text("synthetic outage log (not a benchmark result)")
                self.assert_relocated_replay(repo, private, argv)

    def score_fixture(self, repo, private, gate, result, final=False):
        argv = [
            "score.py",
            "--freeze",
            str(gate),
            "--runs",
            str(private / "run_plan_*.csv"),
            "--annotation-dir",
            str(private / "annotation"),
            "--key-dir",
            str(private / "key"),
            "--data-dir",
            str(repo / "data"),
            "--prompts-dir",
            str(repo / "prompts"),
            "--out",
            str(result),
            "--focus",
            "chatgpt",
        ] + (["--final"] if final else [])
        with (
            patch.object(score, "ROOT", str(repo)),
            patch.object(score, "PROMPTS", str(repo / "prompts")),
            patch.object(sys, "argv", argv),
        ):
            score.main()
        return argv

    def test_completed_positive_g1_g2_g3_pipeline_and_portable_replay(self):
        """Known local labels, fake gates in a temp repo, zero product/network calls."""
        with tempfile.TemporaryDirectory() as directory:
            repo, private, config = self.make_g1_fixture(directory)
            config["config"]["focus"] = "chatgpt"
            for c in ("P3A", "P3B"):
                for lang in ("cs", "en"):
                    (repo / "prompts" / f"{c}_candidate_{lang}.txt").write_text(
                        f"synthetic {c} {{user_prompt}}"
                    )
            (repo / "prompts/CHANGELOG.md").write_text(
                "SYNTHETIC test, no real dev evidence or winner"
            )
            (private / "annotation").mkdir()
            (private / "key").mkdir()
            source = private / "source.txt"
            source.write_text(
                "SYNTHETIC source: fixture facts 1-9 supported; fact 10 contradicted. Not a factual benchmark."
            )
            # Update the fixture evidence hash BEFORE the fake G1.
            evidence = read_csv(private / "source_evidence.csv")
            for row in evidence:
                row["snapshot_sha256"] = sha256_file(source)
            write_csv(private / "source_evidence.csv", evidence, list(evidence[0]))
            with (
                patch.object(integrity, "ROOT", str(repo)),
                patch.object(freeze_protocol, "ROOT", str(repo)),
            ):
                g1 = str(private / "G1.json")
                write_json_new(g1, prepare_manifest(config))
                plans, expected = [], {}

                def collect_phase(phase, gate):
                    start, count = (
                        (0, 20)
                        if phase == "dev"
                        else (20, 10)
                        if phase == "val"
                        else (30, 10)
                    )
                    conds = (
                        ["P2"]
                        if phase in {"dev", "repeat"}
                        else ["P2", "P3A", "P3B"]
                        if phase == "val"
                        else ["P1", "P2", "P3"]
                    )
                    rows = self.failed_fixture_rows(
                        repo,
                        source,
                        phase,
                        start,
                        count,
                        conds,
                        [2, 3] if phase == "repeat" else [1],
                    )
                    for r in rows:
                        i = int(r["task_id"].split("-")[-1])
                        p2 = (8 + i % 2) if r["system"] == "chatgpt" else 5
                        k = (
                            p2 - (2 + i % 2)
                            if r["condition"] == "P1"
                            else p2
                            if r["condition"] == "P2"
                            else 6
                            if r["condition"] == "P3A"
                            else 9
                        )
                        text = (
                            "ANSWER:\n"
                            + " ".join(
                                f"Fixture fact number {j} is present [1]."
                                for j in range(1, 11)
                            )
                            + "\nSOURCES:\n[1] https://fixture.invalid/source\nCONFIDENCE: synthetic"
                        )
                        answer = private / (r["run_id"] + ".txt")
                        answer.write_text(text)
                        r.update(
                            run_status="completed",
                            failure_type="none",
                            first_attempt_ok="yes",
                            final_attempt_ok="yes",
                            answer_file=str(answer),
                            answer_sha256=sha256_file(answer),
                            raw_answer_file=str(answer),
                            raw_answer_sha256=sha256_file(answer),
                            failure_artifact_file="",
                            failure_artifact_sha256="",
                            search_used="yes",
                            n_sources_shown="1",
                        )
                        expected[r["run_id"]] = k / 10
                    plan = str(private / f"run_plan_{phase}.csv")
                    write_csv(plan, rows, list(rows[0]))
                    bind_plan(
                        plan, read_csv(plan), gate, prompts_dir=str(repo / "prompts")
                    )
                    plans.append(plan)
                    ad = private / "annotation" / phase
                    argv = [
                        "check_citations.py",
                        "--freeze",
                        gate,
                        "--runs",
                        plan,
                        "--data-dir",
                        str(repo / "data"),
                        "--out-dir",
                        str(ad),
                        "--key-dir",
                        str(private / "key"),
                        "--offline",
                        "--salt",
                        "synthetic-positive-fixture",
                    ]
                    with (
                        patch.object(check_citations, "ROOT", str(repo)),
                        patch.object(sys, "argv", argv),
                    ):
                        check_citations.main()
                    keys = {
                        k["blind_answer_id"]: k["run_id"]
                        for k in read_csv(private / "key/blind_key.csv")
                    }
                    for suffix, rater in (
                        ("", "fixture rater1"),
                        ("_rater2", "fixture rater2"),
                    ):
                        pairs = read_csv(ad / f"pairs_to_rate{suffix}.csv")
                        answers = read_csv(ad / f"answers_to_rate{suffix}.csv")
                        support = {}
                        for p in pairs:
                            bid = p["blind_answer_id"]
                            k = round(expected[keys[bid]] * 10)
                            p.update(
                                rating="S2" if int(p["claim_id"][1:]) <= k else "S0",
                                source_tier="1",
                                time_ok="na",
                                rater=rater,
                                evidence_url="https://fixture.invalid/source",
                                evidence_checked_at="2026-01-01T10:00:03+00:00"
                                if phase in {"dev", "val"}
                                else "2026-01-04T10:00:00+00:00",
                                evidence_locator="local fictional fixture",
                                evidence_excerpt="SYNTHETIC predetermined label, not human verification",
                                evidence_snapshot=str(source),
                                evidence_sha256=sha256_file(source),
                            )
                            if p["rating"] == "S2":
                                support.setdefault(bid, p["pair_id"])
                        for a in answers:
                            a.update(
                                correctness="2",
                                n_claims="10",
                                segmentation_reviewed="yes",
                                key_facts_supported="1",
                                key_fact_evidence=json.dumps(
                                    {"RF1": [support[a["blind_answer_id"]]]}
                                ),
                                constraint_results="{}",
                                acknowledges_uncertainty="yes"
                                if int(a["task_id"].split("-")[-1]) % 10 < 4
                                else "na",
                                check_minutes="1",
                                rater=rater,
                                comment="SYNTHETIC fixture only",
                            )
                        for name, values in (("pairs", pairs), ("answers", answers)):
                            write_csv(
                                ad
                                / f"{name}_rated{'_rater2' if suffix else '_rater1'}.csv",
                                values,
                                list(values[0]),
                            )
                            if not suffix:
                                write_csv(
                                    ad / f"{name}_rated.csv", values, list(values[0])
                                )

                collect_phase("dev", g1)
                collect_phase("val", g1)
                val_result = private / "val-results"
                self.score_fixture(repo, private, g1, val_result)
                for lang in ("cs", "en"):
                    shutil.copyfile(
                        repo / "prompts" / f"P3B_candidate_{lang}.txt",
                        repo / "prompts" / f"P3_final_{lang}.txt",
                    )
                g2config = template("G2")
                g2config.update(
                    parent_path=g1,
                    signed_by="synthetic signer",
                    signed_at="2026-01-01T12:00:00+00:00",
                    selected_candidate="P3B",
                )
                g2config["attestations"] = dict.fromkeys(g2config["attestations"], True)
                g2config["inputs"] = {
                    "selection_record": str(source),
                    "development_analysis": str(source),
                    "validation_metrics": str(val_result / "metrics.csv"),
                    "validation_scoring_inputs": str(
                        val_result / "scoring_inputs.json"
                    ),
                    "validation_plans": [plans[1]],
                }
                snapshot_path = val_result / "scoring_inputs.json"
                original_snapshot = snapshot_path.read_bytes()
                valid_manifest = prepare_manifest(g2config)
                snapshot = json.loads(original_snapshot)
                val_ids = {
                    k["blind_answer_id"]
                    for k in snapshot["tables"]["key"]
                    if k["run_id"].startswith("val-")
                }
                bad_pair = next(
                    p
                    for p in snapshot["tables"]["pairs"]
                    if p["blind_answer_id"] in val_ids
                )
                bad_pair["evidence_checked_at"] = "2026-01-04T10:00:00+00:00"
                snapshot_path.write_text(json.dumps(snapshot))
                with self.assertRaisesRegex(
                    ValueError, "signed_at precedes a source decision"
                ):
                    prepare_manifest(g2config)
                # Even a manually rehashed manifest cannot bypass the verify guard.
                valid_manifest["files"][str(snapshot_path)] = sha256_file(snapshot_path)
                bad_gate = private / "tampered-G2.json"
                write_json_new(bad_gate, valid_manifest)
                with self.assertRaisesRegex(
                    ValueError, "signed_at precedes a source decision"
                ):
                    verify_freeze(str(bad_gate))
                snapshot_path.write_bytes(original_snapshot)
                g2 = str(private / "G2.json")
                write_json_new(g2, prepare_manifest(g2config))
                self.assertEqual(
                    verify_freeze(g2)["selection_summary"]["selected_candidate"], "P3B"
                )
                collect_phase("test", g2)
                collect_phase("repeat", g2)
                g3config = template("G3")
                g3config.update(
                    parent_path=g2,
                    signed_by="synthetic signer",
                    signed_at="2026-01-05T00:00:00+00:00",
                )
                g3config["attestations"] = dict.fromkeys(g3config["attestations"], True)
                g3config["inputs"] = {
                    "run_plans": plans,
                    "annotation_dir": str(private / "annotation"),
                    "key_dir": str(private / "key"),
                    "deviations_record": str(source),
                }
                # G3 rejects a post-selection change, even if made in all rating versions.
                val_answers = private / "annotation/val/answers_rated.csv"
                original = val_answers.read_bytes()
                values = read_csv(val_answers)
                values[0]["comment"] = "changed after G2"
                write_csv(val_answers, values, list(values[0]))
                with self.assertRaisesRegex(ValueError, "changed since G2"):
                    prepare_manifest(g3config)
                val_answers.write_bytes(original)
                g3 = str(private / "G3.json")
                write_json_new(g3, prepare_manifest(g3config))
                argv = self.score_fixture(
                    repo, private, g3, private / "final-results", final=True
                )
                actual = read_csv(private / "final-results/answer_metrics.csv")
                self.assertEqual(len(actual), 500)
                for a in actual:
                    self.assertAlmostEqual(float(a["precision"]), expected[a["run_id"]])
                hypotheses = read_csv(private / "final-results/hypotheses.csv")
                self.assertEqual([h["supported"] for h in hypotheses], ["yes", "yes"])
                self.assertAlmostEqual(float(hypotheses[0]["estimate"]), 0.35)
                self.assertAlmostEqual(float(hypotheses[1]["estimate"]), 0.25)
                self.assert_relocated_replay(repo, private, argv)

    def assert_bad_g2_inputs_rejected(self, config):
        path = Path(config["inputs"]["validation_metrics"])
        original = path.read_bytes()
        rows = read_csv(path)
        for precision in ("", "NaN", "inf", "-1", "1.5", "1"):
            bad = copy.deepcopy(rows)
            next(r for r in bad if r["split"] == "val")["precision"] = precision
            write_csv(path, bad, list(rows[0]))
            with self.assertRaisesRegex(ValueError, "precision"):
                prepare_manifest(config)
        write_csv(
            path, [*rows, next(r for r in rows if r["split"] == "val")], list(rows[0])
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            prepare_manifest(config)
        path.write_bytes(original)
        bad = copy.deepcopy(config)
        bad["selected_candidate"] = "P3B"
        with self.assertRaisesRegex(ValueError, "tie rule"):
            prepare_manifest(bad)

    def assert_relocated_replay(self, repo, private, original_argv):
        """Two relocated directories, fresh CLIs, original paths gone, bytes intact."""
        hashes = {
            str(p.relative_to(private)): sha256_file(p)
            for p in private.rglob("*")
            if p.is_file()
        }
        expected = {
            name: (private / "final-results" / name).read_bytes()
            for name in (
                "metrics.csv",
                "answer_metrics.csv",
                "hypotheses.csv",
                "agreement.csv",
                "report.md",
            )
        }
        original_repo, original_private = str(repo), str(private)
        try:
            for index in (1, 2):
                target = private.parent / f"machine-{index}"
                new_repo, new_private = target / "repo", target / "private"
                shutil.copytree(repo, new_repo)
                shutil.copytree(private, new_private)
                shutil.rmtree(repo)
                shutil.rmtree(private)
                mapping = target / "paths.json"
                mapping.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "prefixes": [
                                {"from": original_repo, "to": str(new_repo)},
                                {"from": original_private, "to": str(new_private)},
                            ],
                        }
                    )
                )
                argv = [*list(original_argv), "--path-map", str(mapping)]
                # Exercise actual CLI defaults in the relocated repository.
                for flag in ("--data-dir", "--prompts-dir"):
                    position = argv.index(flag)
                    del argv[position : position + 2]
                out = new_private / f"replay-{index}"
                argv[argv.index("--out") + 1] = str(out)
                env = dict(
                    os.environ,
                    PYTHONDONTWRITEBYTECODE="1",
                    PYTHONHASHSEED=str(index),
                    TZ="UTC" if index == 1 else "Europe/Prague",
                )
                # score verifies its inputs; verify again afterwards to detect
                # newly added unbound files as well as changes to existing bytes.
                for script, args in (
                    ("score.py", argv[1:]),
                    (
                        "freeze_protocol.py",
                        [
                            "--verify",
                            str(new_private / "G3.json"),
                            "--path-map",
                            str(mapping),
                        ],
                    ),
                ):
                    result = subprocess.run(
                        [sys.executable, str(new_repo / "scripts" / script), *args],
                        cwd=target,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )
                for name, value in expected.items():
                    self.assertEqual((out / name).read_bytes(), value, name)
                for name, digest in hashes.items():
                    self.assertEqual(sha256_file(new_private / name), digest, name)
                prov = json.loads((out / "replay_provenance.json").read_text())
                self.assertEqual(
                    prov["parent_g3_sha256"], sha256_file(new_private / "G3.json")
                )
                configure_path_map(mapping, new_repo)
                with patch.object(integrity, "ROOT", str(new_repo)):
                    source = new_private / "source.txt"
                    original = source.read_bytes()
                    source.write_bytes(original + b"tamper")
                    with self.assertRaisesRegex(ValueError, "frozen file changed"):
                        verify_freeze(str(new_private / "G3.json"))
                    source.write_bytes(original)
                repo, private = new_repo, new_private
        finally:
            configure_path_map()

    def failed_fixture_rows(self, repo, log, phase, start, count, conditions, indices):
        rows = []
        split = "test" if phase == "repeat" else phase
        day = "03" if phase == "repeat" else "02" if phase == "test" else "01"
        for i in range(start, start + count):
            for cond in conditions:
                for system in template("G1")["config"]["systems"]:
                    for ri in indices:
                        lang = "cs" if i % 10 < 5 else "en"
                        prompt = {
                            "P1": "P1_baseline",
                            "P2": "P2_structured",
                            "P3": "P3_final",
                            "P3A": "P3A_candidate",
                            "P3B": "P3B_candidate",
                        }[cond] + f"_{lang}.txt"
                        rows.append(
                            {
                                "run_id": f"{phase}-DEMO-{i}-{cond}-{system}-{ri}",
                                "phase": phase,
                                "split": split,
                                "task_id": f"DEMO-{i}",
                                "language": lang,
                                "condition": cond,
                                "system": system,
                                "run_index": str(ri),
                                "prompt_file": prompt,
                                "prompt_sha256": sha256_file(repo / "prompts" / prompt),
                                "run_status": "failed",
                                "failure_type": "product_outage",
                                "first_attempt_ok": "no",
                                "final_attempt_ok": "no",
                                "retries": "0",
                                "latency_s": "2",
                                "first_attempt_latency_s": "2",
                                "datetime_start": f"2026-01-{day}T10:00:00+00:00",
                                "datetime_end": f"2026-01-{day}T10:00:02+00:00",
                                "model_visible": "unknown",
                                "plan_tier": "free",
                                "operator": "synthetic operator",
                                "manual_intervention": "none",
                                "cost_note": "fixture",
                                "search_used": "unclear",
                                "n_sources_shown": "unknown",
                                "turns": "1",
                                "tool_calls_visible": "unknown",
                                "screenshot_file": str(log),
                                "screenshot_sha256": sha256_file(log),
                                "failure_artifact_file": str(log),
                                "failure_artifact_sha256": sha256_file(log),
                                "answer_file": str(
                                    log.parent / "nonexistent-answer.txt"
                                ),
                            }
                        )
        return rows


if __name__ == "__main__":
    unittest.main()
