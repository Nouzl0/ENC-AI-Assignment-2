"""Draft-data contracts, not source verification or product benchmarks."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import test_integrity
from common import constraint_problems, load_all_cases, load_cases, read_csv, write_csv
from integrity import source_evidence_problems
from score import load_answers
from test_scoring import fixture
from validate_cases import holdout_stratification_problems, validate_case

ROOT = Path(__file__).resolve().parents[1]


class DataContractTests(unittest.TestCase):
    def test_duplicate_case_json_fields_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "cases_dev.jsonl")
            for value in (
                '{"task_id":"first","task_id":"second"}',
                '{"task_id":"DEMO-1","reference_answer_or_tests":{"required_facts":[],"required_facts":["fact"]}}',
            ):
                with self.subTest(value=value):
                    path.write_text(value + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        load_cases("dev", directory)

    def test_constraints_are_separate_from_content(self):
        cases = load_all_cases()
        who = cases["CIT-002"]["reference_answer_or_tests"]
        self.assertNotIn("2015", " ".join(who["required_facts"]))
        self.assertIn("nejsou povinné", " ".join(who["required_constraints"]))
        self.assertEqual(
            len(cases["CIT-004"]["reference_answer_or_tests"]["required_facts"]), 2
        )
        rag = cases["CIT-025"]["reference_answer_or_tests"]
        self.assertIn(
            "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            rag["required_facts"],
        )
        self.assertTrue(rag["required_constraints"])
        for case in cases.values():
            ref = case["reference_answer_or_tests"]
            text = "; ".join(ref["required_facts"]) + "."
            if ref["optional_facts"]:
                text += (
                    " Nepovinný kontext (vynechání se nepenalizuje): "
                    + "; ".join(ref["optional_facts"])
                    + "."
                )
            self.assertEqual(ref["reference_answer"], text)
            self.assertEqual(
                case["expected_properties"],
                ref["required_facts"] + ref["required_constraints"],
            )

    def test_constraint_results_fail_closed(self):
        case = {
            "reference_answer_or_tests": {
                "required_constraints": ["official source", "Czech"]
            }
        }
        for value in (
            "",
            "[]",
            "not json",
            '{"RC1":"yes"}',
            '{"RC1":[],"RC2":"yes"}',
            '{"RC1":"yes","RC2":"na"}',
            '{"RC1":"no","RC1":"yes","RC2":"yes"}',
            '{"RC1":"yes","RC2":"yes","RC3":"yes"}',
        ):
            self.assertTrue(
                constraint_problems(
                    {"correctness": "2", "constraint_results": value}, case
                )
            )
        for result in ("no", "unknown"):
            row = {
                "correctness": "2",
                "constraint_results": json.dumps({"RC1": "yes", "RC2": result}),
            }
            self.assertTrue(constraint_problems(row, case))
            row["correctness"] = " 2 "
            self.assertTrue(constraint_problems(row, case))
            row["correctness"] = "1"
            self.assertEqual(constraint_problems(row, case), [])
        self.assertEqual(
            constraint_problems(
                {"correctness": "2", "constraint_results": '{"RC1":"yes","RC2":"yes"}'},
                case,
            ),
            [],
        )
        self.assertEqual(constraint_problems({}, {"reference_answer_or_tests": {}}), [])

    def test_actual_reference_value_need_not_equal_fact_text(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, _, config = test_integrity.IntegrityTests().make_g1_fixture(directory)
            cases = load_all_cases(str(repo / "data"), config["inputs"]["test_cases"])
            path = config["inputs"]["source_evidence"]
            rows = read_csv(path)
            rows[0]["reference_value"] = (
                "actual independently checked value, not a placeholder"
            )
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(source_evidence_problems(cases, path), [])
            for field, value in (
                ("reference_value", " "),
                ("reference_value", None),
                ("fact_text", "different requirement"),
                ("valid_as_of", "2025-12-31"),
            ):
                changed = copy.deepcopy(rows)
                changed[0][field] = value
                write_csv(path, changed, list(changed[0]))
                self.assertTrue(source_evidence_problems(cases, path))
            cases[rows[0]["task_id"]]["reference_valid_as_of"] = "RUN_DAY"
            rows[0].update(
                checked_at="2026-01-02T00:30:00+02:00", valid_as_of="2026-01-01"
            )
            write_csv(path, rows, list(rows[0]))
            self.assertEqual(source_evidence_problems(cases, path), [])
            rows[0]["valid_as_of"] = "2026-01-02"
            write_csv(path, rows, list(rows[0]))
            self.assertTrue(source_evidence_problems(cases, path))
            cases[rows[0]["task_id"]].pop("reference_valid_as_of")
            rows[0].pop("valid_as_of")
            write_csv(path, rows, list(rows[0]))
            self.assertTrue(source_evidence_problems(cases, path))
            self.assertTrue(
                any(
                    "reference_valid_as_of" in e
                    for e in validate_case(cases[rows[0]["task_id"]], "dev")
                )
            )

    def test_holdout_quotas_reject_single_domain_and_malformed_blueprint(self):
        blueprint = ROOT / "data/holdout_blueprint.json"
        with tempfile.TemporaryDirectory() as directory:
            repo, _, config = test_integrity.IntegrityTests().make_g1_fixture(directory)
            rows = list(
                load_all_cases(
                    str(repo / "data"), config["inputs"]["test_cases"]
                ).values()
            )[-10:]
            self.assertEqual(holdout_stratification_problems(rows, blueprint), [])
            self.assertEqual(holdout_stratification_problems(rows * 2, blueprint), [])
            bad = [
                dict(row, domain="it", language="en", difficulty="easy") for row in rows
            ]
            self.assertTrue(holdout_stratification_problems(bad, blueprint))
            # A list with the right category names must not crash at .items().
            data = json.loads(blueprint.read_text())
            data["counts_per_10"]["language"] = ["cs", "en", "cs+en"]
            path = Path(directory, "bad.json")
            path.write_text(json.dumps(data))
            self.assertTrue(holdout_stratification_problems(rows, path))

    def test_scoring_rejects_correctness_two_with_unmet_constraint(self):
        run, key, pair, answer, cases = fixture()
        cases["TEST"]["reference_answer_or_tests"]["required_constraints"] = [
            "official source"
        ]
        answer["constraint_results"] = '{"RC1":"unknown"}'
        scored, errors = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(scored, [])
        self.assertTrue(any("constraint" in e for e in errors))
        answer.update(correctness="1", constraint_results='{"RC1":"yes"}')
        scored, errors = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(errors, [])
        self.assertEqual(scored[0]["kf_cov"], 1)  # RC is not an extra required fact.


if __name__ == "__main__":
    unittest.main()
