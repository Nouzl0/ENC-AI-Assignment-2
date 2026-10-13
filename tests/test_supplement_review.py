"""Offline regression tests for independent exploratory human-review inputs."""

import csv
import hashlib
import json
import math
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import supplement_review


class SupplementReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="czai-human-review-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.repo = self.work / "repo"
        self.repo.mkdir()
        self.registry = self.repo / "registry.jsonl"
        self.cases = self.repo / "cases.jsonl"
        self.out = self.work / "raters"
        self.key = self.work / "steward"
        self.case_rows = [
            {
                "task_id": "CASE-001",
                "language": "en",
                "user_prompt": "What is the recorded value?",
                "reference_valid_as_of": "2026-10-13",
                "reference_answer_or_tests": {
                    "reference_answer": "The required value is 31.",
                    "required_facts": ["The value is 31."],
                    "optional_facts": ["An optional detail."],
                    "required_constraints": ["Cite the original source."],
                },
                "source_or_provenance": "PRIVATE-REFERENCE-PROVENANCE",
                "rater_notes": "PRIVATE-AI-DIAGNOSTIC",
            }
        ]
        self.rows = []
        self.add_record("first")
        self.save_inputs()

    def add_record(self, name, text=None, **changes):
        if text is None:
            text = "ANSWER: The value is 31 [1].\nSOURCES:\n[1] https://example.org/record_\n"
        answer = self.repo / (name + ".txt")
        answer.write_bytes(text.encode("utf-8"))
        digest = hashlib.sha256(answer.read_bytes()).hexdigest()
        row = {
            "record_id": "PRIVATE-IDENTITY:" + name,
            "task_id": "CASE-001",
            "phase": "PRIVATE-PHASE",
            "system": "PRIVATE-PRODUCT",
            "condition": "PRIVATE-CONDITION",
            "run_status": "completed",
            "include_in_analysis": True,
            "answer_file": answer.name,
            "answer_sha256": digest,
            "raw_answer_file": answer.name,
            "raw_answer_sha256": digest,
            "ai_rating": "PRIVATE-AI-RATING",
            "diagnostics": "PRIVATE-PARSER-DIAGNOSTIC",
            "screenshot_file": "PRIVATE-SCREENSHOT-PATH",
        }
        row.update(changes)
        self.rows.append(row)
        return row

    def save_inputs(self):
        self.registry.write_text(
            "".join(json.dumps(row) + "\n" for row in self.rows), encoding="utf-8"
        )
        self.cases.write_text(
            "".join(json.dumps(row) + "\n" for row in self.case_rows), encoding="utf-8"
        )

    def export(self, out=None, key=None, **changes):
        return supplement_review.export_review(
            self.registry,
            [self.cases],
            out or self.out,
            key or self.key,
            root=self.repo,
            **changes,
        )

    @staticmethod
    def read_rows(path):
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def assert_no_output(self):
        self.assertFalse(self.out.exists())
        self.assertFalse(self.key.exists())

    def test_rater_files_have_no_identity_diagnostics_or_hash_hints(self):
        self.add_record("failed", run_status="failed")
        self.add_record("excluded", run_status="excluded", include_in_analysis=False)
        self.add_record("not-selected", include_in_analysis=False)
        self.save_inputs()
        result = self.export()
        self.assertEqual(result["rater1_answers"], 1)
        self.assertEqual(result["human_ratings_completed"], 0)
        forbidden = [
            "PRIVATE-IDENTITY",
            "PRIVATE-PHASE",
            "PRIVATE-PRODUCT",
            "PRIVATE-CONDITION",
            "PRIVATE-AI-RATING",
            "PRIVATE-PARSER-DIAGNOSTIC",
            "PRIVATE-SCREENSHOT",
            "PRIVATE-REFERENCE-PROVENANCE",
            "PRIVATE-AI-DIAGNOSTIC",
            "CASE-001",
            self.rows[0]["answer_sha256"],
        ]
        for path in self.out.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for value in forbidden:
                with self.subTest(file=path.name, forbidden=value):
                    self.assertNotIn(value, text)
        for name in ("rater1", "rater2"):
            answers = self.read_rows(self.out / name / "answers_to_rate.csv")
            pairs = self.read_rows(self.out / name / "pairs_to_rate.csv")
            self.assertEqual(set(answers[0]), set(supplement_review.ANSWER_FIELDS))
            self.assertEqual(set(pairs[0]), set(supplement_review.PAIR_FIELDS))
            for row in answers:
                for field in supplement_review.ANSWER_FIELDS[11:]:
                    self.assertEqual(row[field], "")
                self.assertIn("RF1: The value is 31.", row["required_facts"])
                self.assertIn("OF1: An optional detail.", row["optional_facts"])
                self.assertIn(
                    "RC1: Cite the original source.", row["required_constraints"]
                )
            for row in pairs:
                for field in supplement_review.PAIR_FIELDS[7:]:
                    self.assertEqual(row[field], "")
            self.assertIn("POUZE NÁVRHY", (self.out / name / "README.md").read_text())
        excluded = (self.key / "excluded_records.jsonl").read_text()
        self.assertIn("PRIVATE-IDENTITY:failed", excluded)
        self.assertIn("PRIVATE-IDENTITY:excluded", excluded)
        self.assertNotIn("PRIVATE-IDENTITY:first", excluded)

    def test_second_rater_ceil_quarter_in_every_stratum_and_identical_shared_rows(self):
        self.rows = []
        sizes = [1, 2, 3, 4, 5, 9, 11, 13]
        for index, size in enumerate(sizes):
            for item in range(size):
                self.add_record(
                    f"stratum-{index}-{item}",
                    phase=f"phase-{index // 4}",
                    system=f"system-{index % 2}",
                    condition=f"condition-{(index // 2) % 2}",
                )
        self.save_inputs()
        result = self.export()
        self.assertEqual(result["rater1_answers"], sum(sizes))
        self.assertEqual(
            result["rater2_answers"], sum(math.ceil(size / 4) for size in sizes)
        )
        selection = self.read_rows(self.key / "canonical_selection.csv")
        counts = Counter(
            (row["phase"], row["system"], row["condition"])
            for row in selection
            if row["rater2_selected"] == "True"
        )
        for index, size in enumerate(sizes):
            key = (
                f"phase-{index // 4}",
                f"system-{index % 2}",
                f"condition-{(index // 2) % 2}",
            )
            self.assertEqual(counts[key], math.ceil(size / 4))
        first = {
            row["blind_answer_id"]: row
            for row in self.read_rows(self.out / "rater1/answers_to_rate.csv")
        }
        second = self.read_rows(self.out / "rater2/answers_to_rate.csv")
        self.assertEqual([first[row["blind_answer_id"]] for row in second], second)
        ids = {row["blind_answer_id"] for row in second}
        first_pairs = self.read_rows(self.out / "rater1/pairs_to_rate.csv")
        self.assertEqual(
            [row for row in first_pairs if row["blind_answer_id"] in ids],
            self.read_rows(self.out / "rater2/pairs_to_rate.csv"),
        )
        again = self.work / "raters-again"
        self.export(out=again, key=self.work / "steward-again")
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertEqual(
                    path.read_bytes(), (again / path.relative_to(self.out)).read_bytes()
                )

    def test_native_labels_zero_markers_and_exact_captured_urls_are_preserved(self):
        url = "https://example.org/a_(b)?z=%2f&z=second&utm_id=x_"
        extra = "https://example.org/native?b=2&a=%2F&b=3"
        text = (
            "  ANSWER: The value is 31 [1.1.2].\r\nNative Journal + 1\r\n"
            "CLAIMS:\r\nC1: Another value is 0 [0].\r\n"
            "C2: Unresolved native citation [1.2.3, 1.2.4].\r\n"
            f"SOURCES:\r\n[1.1.2] [Recorded document]({url})\r\n"
        )
        self.rows = []
        row = self.add_record("native", text=text)
        dom = self.repo / "native-dom.json"
        dom.write_text(
            json.dumps(
                {
                    "links": [{"label": "Native Journal", "href": extra}],
                    "chip_labels": [{"label": "Native Journal + 1"}],
                }
            ),
            encoding="utf-8",
        )
        row.update(
            citation_artifact_file=dom.name,
            citation_artifact_sha256=hashlib.sha256(dom.read_bytes()).hexdigest(),
        )
        self.save_inputs()
        self.export()
        answer = self.read_rows(self.out / "rater1/answers_to_rate.csv")[0]
        self.assertEqual(answer["answer_text"], text)
        sources = json.loads(answer["recorded_sources"])
        self.assertIn(url, {source["url"] for source in sources})
        self.assertIn(extra, {source["url"] for source in sources})
        self.assertIn(
            "Native Journal + 1", {source["citation_label"] for source in sources}
        )
        pairs = self.read_rows(self.out / "rater1/pairs_to_rate.csv")
        self.assertIn("[1.1.2]", {row["citation_label"] for row in pairs})
        self.assertIn("[0]", {row["citation_label"] for row in pairs})
        grouped = [row for row in pairs if row["citation_label"] == "[1.2.3, 1.2.4]"]
        self.assertTrue(grouped)
        self.assertEqual({row["url"] for row in grouped}, {""})
        self.assertTrue(all(row["rating"] == "" for row in pairs))
        self.assertFalse(any(row["url"] == extra for row in pairs))

    def test_all_body_parts_remain_proposals_and_confidence_is_not_discarded(self):
        text = (
            "ANSWER: Intro fact [1].\nCLAIMS:\nC1: Listed fact [1].\n"
            "SOURCES:\n[1] https://example.org/source\n"
            "CONFIDENCE: high because an additional fact exists.\n"
        )
        pairs, _ = supplement_review.build_proposals(text)
        self.assertTrue(any("Intro fact" in row["claim_text"] for row in pairs))
        self.assertTrue(any("Listed fact" in row["claim_text"] for row in pairs))
        self.assertTrue(any("additional fact" in row["claim_text"] for row in pairs))

    def test_declared_hash_mismatch_prevents_any_output(self):
        (self.repo / self.rows[0]["answer_file"]).write_text(
            "Changed answer.", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.export()
        self.assert_no_output()

    def test_input_mutation_during_preparation_prevents_any_output(self):
        original = supplement_review.build_proposals

        def change_input(*args, **kwargs):
            self.cases.write_text(self.cases.read_text() + "\n", encoding="utf-8")
            return original(*args, **kwargs)

        with (
            patch.object(
                supplement_review, "build_proposals", side_effect=change_input
            ),
            self.assertRaisesRegex(ValueError, "input changed before export"),
        ):
            self.export()
        self.assert_no_output()

    def test_artifact_hash_required_for_every_used_eligible_source(self):
        self.rows[0].pop("raw_answer_sha256")
        self.save_inputs()
        with self.assertRaisesRegex(ValueError, "missing raw_answer_sha256"):
            self.export()
        self.assert_no_output()

    def test_duplicate_record_and_case_ids_unknown_case_and_nonboolean_selection_rejected(
        self,
    ):
        baseline = dict(self.rows[0])
        for change, message in (
            ("record", "duplicate"),
            ("case", "duplicate"),
            ("unknown", "unknown case"),
            ("boolean", "JSON boolean"),
        ):
            with self.subTest(change=change):
                self.rows = [dict(baseline)]
                self.case_rows = self.case_rows[:1]
                if change == "record":
                    self.rows.append(dict(baseline))
                elif change == "case":
                    self.case_rows.append(dict(self.case_rows[0]))
                elif change == "unknown":
                    self.rows[0]["task_id"] = "UNKNOWN"
                else:
                    self.rows[0]["include_in_analysis"] = "false"
                self.save_inputs()
                with self.assertRaisesRegex(ValueError, message):
                    self.export()
                self.assert_no_output()

    def test_non_finite_json_and_numeric_metadata_are_rejected(self):
        for value in (float("nan"), float("inf"), "NaN", "Infinity"):
            with self.subTest(value=value):
                self.rows[0]["latency_s"] = value
                self.save_inputs()
                with self.assertRaisesRegex(ValueError, "non-finite"):
                    self.export()
                self.assert_no_output()
        self.rows[0].pop("latency_s")
        self.save_inputs()
        self.registry.write_text(
            self.registry.read_text().replace('"completed"', "1e999"), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "non-finite"):
            self.export()
        self.assert_no_output()

    def test_artifact_path_escape_absolute_paths_and_symlinks_rejected(self):
        baseline = dict(self.rows[0])
        for value in (
            "../escape.txt",
            str(self.repo / "first.txt"),
            "C:\\private\\answer.txt",
        ):
            with self.subTest(path=value):
                self.rows[0] = dict(baseline, answer_file=value)
                self.save_inputs()
                with self.assertRaisesRegex(
                    ValueError, "repository-relative|escapes repository"
                ):
                    self.export()
                self.assert_no_output()
        self.rows[0] = dict(baseline, answer_file="linked.txt")
        (self.repo / "linked.txt").symlink_to(self.repo / "first.txt")
        self.save_inputs()
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.export()
        self.assert_no_output()

    def test_private_output_paths_and_separate_key_are_required(self):
        for out, key in (
            (Path("relative-review"), self.key),
            (self.repo / "review", self.key),
            (self.out, self.out / "key"),
            (self.key / "raters", self.key),
            (self.out, self.out),
        ):
            with (
                self.subTest(out=out, key=key),
                self.assertRaisesRegex(ValueError, "absolute|outside|separate"),
            ):
                self.export(out=out, key=key)
        linked = self.work / "linked"
        linked.symlink_to(self.work, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.export(out=linked / "raters")
        self.assert_no_output()

    def test_no_overwrite_even_when_existing_directory_is_empty(self):
        self.out.mkdir()
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            self.export()
        self.assertFalse(self.key.exists())
        self.out.rmdir()
        self.export()
        original = {
            str(path): path.read_bytes()
            for path in self.out.rglob("*")
            if path.is_file()
        }
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            self.export()
        self.assertEqual(
            original,
            {
                str(path): path.read_bytes()
                for path in self.out.rglob("*")
                if path.is_file()
            },
        )

    def test_second_case_file_and_legacy_key_facts_are_supported(self):
        second = self.repo / "cases-other.jsonl"
        other = dict(self.case_rows[0], task_id="CASE-002")
        other["reference_answer_or_tests"] = {
            "reference_answer": "32",
            "key_facts": ["The value is 32."],
        }
        second.write_text(json.dumps(other) + "\n", encoding="utf-8")
        self.add_record("other", task_id="CASE-002")
        self.save_inputs()
        result = supplement_review.export_review(
            self.registry, [self.cases, second], self.out, self.key, root=self.repo
        )
        self.assertEqual(result["rater1_answers"], 2)
        answers = self.read_rows(self.out / "rater1/answers_to_rate.csv")
        self.assertTrue(
            any("RF1: The value is 32." in row["required_facts"] for row in answers)
        )

    def test_run_day_uses_utc_submission_date_across_midnight_and_preserves_case_hash(
        self,
    ):
        self.case_rows[0]["reference_valid_as_of"] = "RUN_DAY"
        for index, (start, expected) in enumerate(
            [
                ("2026-10-13T00:30:00+02:00", "2026-10-12"),
                ("2026-10-12T23:30:00-02:00", "2026-10-13"),
                ("2026-10-13T10:03:25.683Z", "2026-10-13"),
            ]
        ):
            with self.subTest(start=start):
                self.rows[0]["datetime_start"] = start
                self.save_inputs()
                original_case_bytes = self.cases.read_bytes()
                out = self.work / f"utc-raters-{index}"
                result = self.export(out=out, key=self.work / f"utc-key-{index}")
                for rater in ("rater1", "rater2"):
                    answer = self.read_rows(out / rater / "answers_to_rate.csv")[0]
                    self.assertEqual(answer["reference_valid_as_of"], expected)
                self.assertEqual(self.cases.read_bytes(), original_case_bytes)
                snapshot = next(
                    entry
                    for entry in result["inputs"]
                    if entry["path"] == str(self.cases)
                )
                self.assertEqual(
                    snapshot["sha256"], hashlib.sha256(original_case_bytes).hexdigest()
                )

    def test_run_day_missing_naive_or_invalid_start_fails_without_using_end(self):
        self.case_rows[0]["reference_valid_as_of"] = "RUN_DAY"
        for start in (None, "", "unknown", "2026-10-13T10:03:25", "not-a-date"):
            with self.subTest(start=start):
                self.rows[0]["datetime_start"] = start
                self.rows[0]["datetime_end"] = "2026-10-13T10:03:48Z"
                self.save_inputs()
                with self.assertRaisesRegex(
                    ValueError, "timezone-aware datetime_start"
                ):
                    self.export()
                self.assert_no_output()

    def test_fixed_reference_date_is_unchanged_without_a_submission_time(self):
        self.case_rows[0]["reference_valid_as_of"] = "2026-09-29"
        self.rows[0]["datetime_start"] = None
        self.save_inputs()
        self.export()
        answer = self.read_rows(self.out / "rater1/answers_to_rate.csv")[0]
        self.assertEqual(answer["reference_valid_as_of"], "2026-09-29")


if __name__ == "__main__":
    unittest.main()
