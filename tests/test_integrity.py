import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import integrity
import freeze_protocol
import check_citations
from common import load_all_cases, read_csv, sha256_file, write_csv
from integrity import (bind_plan, private_path, run_artifact_problems, timestamp,
                       verify_freeze, verify_plans, write_json_new)
from freeze_protocol import gate_matrix_problems, prepare_manifest, template


class IntegrityTests(unittest.TestCase):
    def test_private_path_rejects_worktree_and_symlink(self):
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
        self.assertFalse(any(c["development_validation_test_split"] == "test" for c in cases.values()))
        with tempfile.TemporaryDirectory() as directory:
            for split in ("dev", "val"):
                Path(directory, f"cases_{split}.jsonl").write_text('{"task_id":"duplicate"}\n')
            with self.assertRaises(ValueError):
                load_all_cases(directory)

    def test_unsigned_gate_and_plain_p3_files_do_not_unlock_test(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "G1.json"))
            write_json_new(p, template("G1"))
            with self.assertRaisesRegex(ValueError, "unsigned"):
                verify_freeze(p, "G1")
            with self.assertRaisesRegex(ValueError, "signed_by"):
                prepare_manifest(template("G2"))

    def test_plan_preserves_metadata_but_rejects_prompt_changes_and_dropped_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "plan.csv"))
            rows = [dict(run_id="r1", phase="dev", task_id="DEMO-1", prompt_text="original", answer_file="a.txt", run_status="planned")]
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
            rows = [dict(run_id="r", seq=1, run_index=1, phase="dev", run_status="planned")]
            write_csv(p, rows, list(rows[0]))
            bind_plan(p, rows, synthetic=True)
            verify_plans(p, synthetic=True)
            write_csv(p, [], list(rows[0]))
            with self.assertRaises(ValueError):
                verify_plans(p, synthetic=True)

    def test_replacement_requires_same_condition_and_recorded_operator_error(self):
        with tempfile.TemporaryDirectory() as directory:
            p = str(Path(directory, "plan.csv"))
            original = dict(run_id="r1", phase="dev", condition="P2", seq="1", answer_file="a.txt", run_status="planned",
                            replacement_run_id="", replaces_run_id="")
            fields = list(original)
            write_csv(p, [original], fields)
            bind_plan(p, read_csv(p), synthetic=True)
            original.update(run_status="excluded", replacement_run_id="r1-replacement")
            replacement = dict(original, run_id="r1-replacement", seq="2", answer_file="b.txt", run_status="completed",
                               replaces_run_id="r1", replacement_run_id="")
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
            row = dict(run_id="r", task_id="DEMO-1", system="sys_A", condition="P2", split="dev", run_index="1",
                       run_status="completed", failure_type="none", first_attempt_ok="yes", final_attempt_ok="yes", retries="0",
                       latency_s="2", first_attempt_latency_s="2", datetime_start="2026-01-01T10:00:00+00:00",
                       datetime_end="2026-01-01T10:00:02+00:00", model_visible="unknown", plan_tier="free", operator="synthetic operator",
                       manual_intervention="none", cost_note="no marginal fee", search_used="unclear", n_sources_shown="unknown",
                       turns="1", tool_calls_visible="unknown", answer_file=str(p), answer_sha256=sha256_file(p),
                       raw_answer_file=str(p), raw_answer_sha256=sha256_file(p), screenshot_file=str(p), screenshot_sha256=sha256_file(p))
            self.assertEqual(run_artifact_problems(row), [])
            row["turns"] = "-1"
            self.assertTrue(run_artifact_problems(row))
            row["turns"] = "1"
            p.write_text("changed")
            self.assertTrue(any("SHA-256 mismatch" in e for e in run_artifact_problems(row)))

    def test_exact_matrix_requires_configured_repeat_subset(self):
        config = dict(systems=["a", "b", "c", "d"], val_candidates=["P3A"], repeat_task_ids=["t1"])
        cases = {"d1": dict(development_validation_test_split="dev"), "v1": dict(development_validation_test_split="val"),
                 "t1": dict(development_validation_test_split="test"), "t2": dict(development_validation_test_split="test")}
        runs = []
        for phase, tids, conds, indices in (("dev", ["d1"], ["P2"], [1]), ("val", ["v1"], ["P2", "P3A"], [1]),
                                          ("test", ["t1", "t2"], ["P1", "P2", "P3"], [1]), ("repeat", ["t1"], ["P2"], [2, 3])):
            runs += [dict(phase=phase, task_id=t, condition=c, system=s, run_index=str(i), run_status="failed")
                     for t in tids for c in conds for s in config["systems"] for i in indices]
        self.assertEqual(gate_matrix_problems(runs, cases, config), [])
        self.assertTrue(gate_matrix_problems(runs[:-1], cases, config))
        self.assertTrue(gate_matrix_problems(runs + [runs[-1]], cases, config))

    def test_production_annotation_rejects_unfrozen_alternate_data(self):
        with tempfile.TemporaryDirectory() as directory:
            args = ["check_citations.py", "--data-dir", directory, "--out-dir", directory + "/annotation",
                    "--key-dir", directory + "/key", "--freeze", directory + "/G1.json", "--offline"]
            with patch.object(sys, "argv", args), patch.object(check_citations, "read_csv_glob", return_value=[dict(split="dev")]):
                with self.assertRaisesRegex(SystemExit, "frozen repository data"):
                    check_citations.main()

    def rating_fixture(self, directory):
        annotation, key = Path(directory, "annotation"), Path(directory, "key")
        annotation.mkdir(); key.mkdir()
        runs = [dict(run_id=f"r{i}", phase="dev", system="sys_A", condition="P2", task_id="DEMO-1", run_status="completed",
                     operator="operator", datetime_start="2026-01-01T10:00:00+00:00", datetime_end="2026-01-01T10:00:02+00:00") for i in range(1, 5)]
        keys = [dict(blind_answer_id=f"A{i}", run_id=f"r{i}") for i in range(1, 5)]
        answers = [dict(blind_answer_id=f"A{i}", correctness="0", n_claims="1", key_facts_supported="0", key_fact_evidence="{}",
                        check_minutes="1", segmentation_reviewed="yes", rater="rater1") for i in range(1, 5)]
        pairs = [dict(blind_answer_id=f"A{i}", pair_id=f"A{i}-T1-none", claim_id="T1", claim_text="synthetic claim",
                      citation_n="", rating="", source_tier="", time_ok="", rater="rater1") for i in range(1, 5)]
        write_csv(key / "blind_key.csv", keys, list(keys[0]))
        write_json_new(key / "batches/batch/annotation_batch.json", dict(rater2_ids=["A1"], sheets={}))
        for name in ("answers_rated", "answers_rated_rater1"):
            write_csv(annotation / (name + ".csv"), answers, list(answers[0]))
        for name in ("pairs_rated", "pairs_rated_rater1"):
            write_csv(annotation / (name + ".csv"), pairs, list(pairs[0]))
        write_csv(annotation / "answers_rated_rater2.csv", [dict(answers[0], rater="rater2")], list(answers[0]))
        write_csv(annotation / "pairs_rated_rater2.csv", [dict(pairs[0], rater="rater2")], list(pairs[0]))
        cases = {"DEMO-1": dict(reference_valid_as_of="2026-01-01", reference_answer_or_tests=dict(required_facts=["fact"], optional_facts=[]))}
        return annotation, key, runs, cases, answers, pairs

    def test_final_changes_require_audit_even_after_raw_agreement_or_single_rating(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, answers, _ = self.rating_fixture(directory)
            self.assertEqual(integrity.final_rating_problems(runs, annotation, key, cases), [])
            answers[0]["correctness"] = "2"  # Both independent raw ratings were 0.
            answers[1]["correctness"] = "1"  # Only one raw rater; still needs an audit.
            write_csv(annotation / "answers_rated.csv", answers, list(answers[0]))
            errors = integrity.final_rating_problems(runs, annotation, key, cases)
            self.assertTrue(any("A1/correctness" in e for e in errors))
            self.assertTrue(any("A2/correctness" in e for e in errors))
            logs = [dict(item_id=f"A{i}", item_type="answer", field="correctness", rater1_value="0", rater2_value="0" if i == 1 else "",
                         resolution=str(3-i), resolved_by="adjudicator", note="synthetic documented correction") for i in (1, 2)]
            write_csv(annotation / "disagreements.csv", logs, list(logs[0]))
            self.assertEqual(integrity.final_rating_problems(runs, annotation, key, cases), [])

    def test_run_day_requires_exact_facts_current_utc_date_and_content(self):
        with tempfile.TemporaryDirectory() as directory:
            annotation, key, runs, cases, _, _ = self.rating_fixture(directory)
            cases["DEMO-1"]["reference_valid_as_of"] = "RUN_DAY"
            cases["DEMO-1"]["reference_answer_or_tests"] = dict(required_facts=["indicator", "value and month"], optional_facts=["comparison"])
            snapshot = Path(directory, "source.txt")
            snapshot.write_text("synthetic daily reference")
            rows = [dict(task_id="DEMO-1", run_date="2026-01-01", fact_id=fid, reference_value="current synthetic fact",
                         url="https://example.org", verified_by="independent checker", checked_at="2026-01-01T10:00:03+00:00",
                         locator="fixture", excerpt_or_summary="synthetic evidence", snapshot_file=str(snapshot), snapshot_sha256=sha256_file(snapshot),
                         verification_status="verified") for fid in ("RF1", "RF2", "OF1")]
            path = annotation / "run_day_evidence.csv"
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(integrity.final_rating_problems(runs, annotation, key, cases), [])
            # Offset is converted to UTC; this is still January 1 in UTC.
            rows[0]["checked_at"] = "2026-01-02T00:01:00+02:00"
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(integrity.final_rating_problems(runs, annotation, key, cases), [])
            rows[0].update(checked_at="2020-01-01T10:00:00+00:00", excerpt_or_summary="")
            write_csv(path, rows[:1], list(rows[0]))
            errors = integrity.final_rating_problems(runs, annotation, key, cases)
            self.assertTrue(any("checked on the run date" in e for e in errors))
            self.assertTrue(any("exactly every RF/OF" in e for e in errors))
            rows[0].update(checked_at="2026-01-01T10:00:03+00:00", excerpt_or_summary="synthetic evidence")
            write_csv(path, rows + [rows[0]], list(rows[0]))
            self.assertTrue(any("duplicate RUN_DAY" in e for e in integrity.final_rating_problems(runs, annotation, key, cases)))

    def make_g1_fixture(self, directory):
        repo = Path(directory, "fixture-repo")
        private = Path(directory, "fixture-private")
        private.mkdir()
        for name in ("data", "scripts", "prompts", "annotation"):
            (repo / name).mkdir(parents=True)
        for name in ("PROTOCOL.md", "annotation/rubric.md", "scripts/dummy.py"):
            (repo / name).write_text("synthetic fixture, not actual research approval")
        for name in ("P1_baseline", "P2_structured"):
            for lang in ("cs", "en"):
                (repo / "prompts" / f"{name}_{lang}.txt").write_text("synthetic {user_prompt}")
        (repo / "data/published_test_candidates.jsonl").write_text("")
        snapshot = private / "source.txt"
        snapshot.write_text("synthetic supporting source")
        evidence = []
        for split, start, count in (("dev", 0, 20), ("val", 20, 10), ("test", 30, 10)):
            cases = []
            for i in range(start, start + count):
                c = dict(task_id=f"DEMO-{i}", schema_version=2, capability="citation_accuracy", task_type="fact", difficulty="easy",
                         language="en", domain="it", development_validation_test_split=split,
                         user_prompt=f"unique_query_{i} unique_topic_{i} unique_marker_{i}", context_or_files=[], expected_properties=["fact"],
                         reference_answer_or_tests=dict(reference_answer="fact", key_facts=["fact"], required_facts=["fact"], optional_facts=[],
                                                        gold_sources=[dict(url="https://example.org")]), edge_case_type="ambiguous",
                         evaluation_method="human", source_or_provenance="synthetic fixture", reference_valid_as_of="2026-01-01")
                cases.append(c)
                evidence.append(dict(task_id=c["task_id"], fact_id="RF1", reference_kind="required", reference_value="fact",
                                     verified_by="synthetic checker", url="https://example.org", locator="fixture", excerpt_or_summary="synthetic source",
                                     checked_at="2026-01-01T00:00:00+00:00", snapshot_file=str(snapshot), snapshot_sha256=sha256_file(snapshot),
                                     verification_status="verified"))
            path = private / "holdout.jsonl" if split == "test" else repo / f"data/cases_{split}.jsonl"
            path.write_text("".join(json.dumps(c) + "\n" for c in cases))
        evpath = str(private / "source_evidence.csv")
        write_csv(evpath, evidence, list(evidence[0]))
        pilot = private / "pilot.txt"
        pilot.write_text("synthetic fixture pilot record; no product calls")
        config = template("G1")
        config.update(signed_by="synthetic test signer", signed_at="2026-01-01T00:00:00+00:00",
                      roles=dict(prompt_author="synthetic author", data_steward="synthetic steward", reference_checker="synthetic checker"))
        config["attestations"] = {k: True for k in config["attestations"]}
        config["config"]["repeat_task_ids"] = [f"DEMO-{i}" for i in range(30, 40)]
        config["inputs"] = dict(test_cases=str(private / "holdout.jsonl"), source_evidence=evpath, pilot_record=str(pilot))
        return repo, private, config

    def test_g1_roundtrip_rejects_changed_data_and_unverified_references(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, private, config = self.make_g1_fixture(directory)
            with patch.object(integrity, "ROOT", str(repo)), patch.object(freeze_protocol, "ROOT", str(repo)):
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
                rows = read_csv(config["inputs"]["source_evidence"])
                rows[0]["verification_status"] = "pending"
                write_csv(config["inputs"]["source_evidence"], rows, list(rows[0]))
                with self.assertRaisesRegex(ValueError, "missing verified evidence"):
                    prepare_manifest(config)

    def test_g2_g3_chain_and_failed_runs_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, private, config = self.make_g1_fixture(directory)
            for name in ("P3A_candidate", "P3B_candidate", "P3_final"):
                for lang in ("cs", "en"):
                    (repo / "prompts" / f"{name}_{lang}.txt").write_text("synthetic candidate {user_prompt}")
            (repo / "prompts/CHANGELOG.md").write_text("synthetic test selection")
            with patch.object(integrity, "ROOT", str(repo)), patch.object(freeze_protocol, "ROOT", str(repo)):
                g1 = str(private / "G1.json")
                write_json_new(g1, prepare_manifest(config))
                log = private / "outage.txt"
                log.write_text("synthetic outage log (not a benchmark result)")
                plans = []
                for phase, start, count, conds, indices in (("dev", 0, 20, ["P2"], [1]),
                                                         ("val", 20, 10, ["P2", "P3A", "P3B"], [1])):
                    rows = self.failed_fixture_rows(repo, log, phase, start, count, conds, indices)
                    p = str(private / f"run_plan_{phase}.csv")
                    write_csv(p, rows, list(rows[0]))
                    bind_plan(p, read_csv(p), g1, prompts_dir=str(repo / "prompts"))
                    plans.append(p)
                metrics = [dict(split="val", system=s, condition=c, n_cases="10") for s in config["config"]["systems"] for c in ("P2", "P3A", "P3B")]
                metrics_path = str(private / "metrics.csv")
                write_csv(metrics_path, metrics, list(metrics[0]))
                g2config = template("G2")
                g2config.update(parent_path=g1, signed_by="synthetic signer", signed_at="2026-01-02T00:00:00+00:00", selected_candidate="P3A")
                g2config["attestations"] = {k: True for k in g2config["attestations"]}
                g2config["inputs"] = dict(selection_record=str(log), development_analysis=str(log), validation_metrics=metrics_path, validation_plans=[plans[1]])
                g2 = str(private / "G2.json")
                write_json_new(g2, prepare_manifest(g2config))
                self.assertEqual(verify_freeze(g2)["gate"], "G2")
                for phase, indices in (("test", [1]), ("repeat", [2, 3])):
                    rows = self.failed_fixture_rows(repo, log, phase, 30, 10, ["P1", "P2", "P3"] if phase == "test" else ["P2"], indices)
                    p = str(private / f"run_plan_{phase}.csv")
                    write_csv(p, rows, list(rows[0]))
                    bind_plan(p, read_csv(p), g2, prompts_dir=str(repo / "prompts"))
                    plans.append(p)
                annotation, key = private / "annotation", private / "key"
                annotation.mkdir(); key.mkdir()
                g3config = template("G3")
                g3config.update(parent_path=g2, signed_by="synthetic signer", signed_at="2026-01-05T00:00:00+00:00")
                g3config["attestations"] = {k: True for k in g3config["attestations"]}
                g3config["inputs"] = dict(run_plans=plans, annotation_dir=str(annotation), key_dir=str(key), deviations_record=str(log))
                g3 = str(private / "G3.json")
                write_json_new(g3, prepare_manifest(g3config))
                self.assertEqual(verify_freeze(g3)["gate"], "G3")
                log.write_text("changed outage artifact")
                with self.assertRaisesRegex(ValueError, "frozen file changed"):
                    verify_freeze(g3)

    def failed_fixture_rows(self, repo, log, phase, start, count, conditions, indices):
        rows = []
        split = "test" if phase == "repeat" else phase
        day = "03" if phase == "repeat" else "02" if phase == "test" else "01"
        for i in range(start, start + count):
            for cond in conditions:
                for system in template("G1")["config"]["systems"]:
                    for ri in indices:
                        prompt = {"P1": "P1_baseline", "P2": "P2_structured", "P3": "P3_final", "P3A": "P3A_candidate", "P3B": "P3B_candidate"}[cond] + "_en.txt"
                        rows.append(dict(run_id=f'{phase}-DEMO-{i}-{cond}-{system}-{ri}', phase=phase, split=split, task_id=f"DEMO-{i}", language="en",
                                         condition=cond, system=system, run_index=str(ri), prompt_file=prompt, prompt_sha256=sha256_file(repo / "prompts" / prompt),
                                         run_status="failed", failure_type="product_outage", first_attempt_ok="no", final_attempt_ok="no", retries="0",
                                         latency_s="2", first_attempt_latency_s="2", datetime_start=f"2026-01-{day}T10:00:00+00:00",
                                         datetime_end=f"2026-01-{day}T10:00:02+00:00", model_visible="unknown", plan_tier="free", operator="synthetic operator",
                                         manual_intervention="none", cost_note="fixture", search_used="unclear", n_sources_shown="unknown", turns="1", tool_calls_visible="unknown",
                                         screenshot_file=str(log), screenshot_sha256=sha256_file(log), failure_artifact_file=str(log), failure_artifact_sha256=sha256_file(log),
                                         answer_file=str(log.parent / "nonexistent-answer.txt")))
        return rows


if __name__ == "__main__":
    unittest.main()
