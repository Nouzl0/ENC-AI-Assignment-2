"""Read-only canonical integrity checks, including Git newline normalization."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from verify_exploratory import verify_registry


class ExploratoryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="czai-exploratory-check-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        self.registry = self.repo / "registry.jsonl"
        self.cases = self.repo / "cases.jsonl"
        self.case = {
            "task_id": "CASE-001",
            "language": "cs+en",
            "user_prompt": "Which value is recorded?",
            "reference_answer_or_tests": {"required_facts": ["The value is 31."]},
        }
        self.cases.write_text(json.dumps(self.case) + "\n", encoding="utf-8")
        self.row = {
            "collection": "legacy",
            "run_id": "same-run-r1",
            "record_id": "legacy/same-run-r1",
            "task_id": "CASE-001",
            "system": "chatgpt",
            "condition": "P2",
            "phase": "exploratory",
            "run_status": "completed",
            "include_in_analysis": True,
        }
        self.file(
            "template_file",
            "prompts/P2_structured_cs.txt",
            "Question:\n{user_prompt}\n",
        )
        self.file(
            "rendered_prompt_file",
            "rendered.txt",
            "Question:\nWhich value is recorded?\n",
        )
        self.file(
            "answer_file",
            "answer.txt",
            "ANSWER: The value is 31 [1].\nSOURCES:\n[1] https://example.org/value\n",
        )
        self.file("raw_answer_file", "raw.txt", "The value is 31.\n")
        self.file("screenshot_file", "screen.png", b"\x89PNG\r\n\x00fixture")
        self.rows = [self.row]
        self.save()

    def file(self, field, path, contents):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        data = contents.encode() if isinstance(contents, str) else contents
        target.write_bytes(data)
        self.row[field] = path
        self.row[field.removesuffix("_file") + "_sha256"] = hashlib.sha256(
            data
        ).hexdigest()

    def save(self):
        self.registry.write_text(
            "".join(json.dumps(row) + "\n" for row in self.rows), encoding="utf-8"
        )

    def verify(self, **kwargs):
        return verify_registry(self.registry, [self.cases], root=self.repo, **kwargs)

    def assert_problem(self, substring):
        report = self.verify()
        self.assertFalse(report["valid"], report)
        self.assertTrue(
            any(substring in error for error in report["errors"]), report["errors"]
        )
        return report

    def test_valid_mixed_language_record_and_read_only_behavior(self):
        before = {
            str(path): path.read_bytes()
            for path in self.repo.rglob("*")
            if path.is_file()
        }
        report = self.verify()
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["eligible_completed"], 1)
        self.assertEqual(report["unique_artifact_files"], 5)
        self.assertEqual(report["scope"], "EXPLORATORY_INTEGRITY_CHECK_NOT_G3")
        self.assertEqual(
            before,
            {
                str(path): path.read_bytes()
                for path in self.repo.rglob("*")
                if path.is_file()
            },
        )

    def test_source_qualified_legacy_run_ids_are_distinct(self):
        self.rows.append(
            dict(self.row, collection="avast", record_id="avast/same-run-r1")
        )
        self.save()
        report = self.verify()
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["record_count"], 2)
        self.rows.append(dict(self.row, record_id="different-id"))
        self.save()
        self.assert_problem("duplicate collection + run_id")

    def test_record_id_qualification_and_duplicates_rejected(self):
        self.row["record_id"] = "unqualified"
        self.save()
        self.assert_problem("record_id must equal")
        self.row["record_id"] = "legacy/same-run-r1"
        self.rows.append(dict(self.row))
        self.save()
        self.assert_problem("duplicate record_id")

    def test_every_status_remains_in_report_without_fabricating_artifacts(self):
        for status in ("planned", "failed", "excluded"):
            row = {
                key: value
                for key, value in self.row.items()
                if key
                not in {
                    "answer_file",
                    "answer_sha256",
                    "raw_answer_file",
                    "raw_answer_sha256",
                    "screenshot_file",
                    "screenshot_sha256",
                }
            }
            row.update(
                run_id=status,
                record_id="legacy/" + status,
                run_status=status,
                include_in_analysis=False,
                disposition="Original outcome retained",
            )
            self.rows.append(row)
        self.save()
        report = self.verify()
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["record_count"], 4)
        self.assertEqual(
            report["status_counts"],
            {"completed": 1, "planned": 1, "failed": 1, "excluded": 1},
        )
        self.assertEqual(report["eligible_completed"], 1)
        self.rows[-1].pop("disposition")
        self.save()
        self.assert_problem("explicit disposition")

    def test_unknown_case_and_nonboolean_inclusion_fail_closed(self):
        self.row["task_id"] = "UNKNOWN"
        self.save()
        self.assert_problem("unknown task_id")
        self.row["task_id"] = "CASE-001"
        self.row["include_in_analysis"] = "false"
        self.save()
        self.assert_problem("JSON boolean")

    def test_matching_hashes_do_not_hide_wrong_rendered_prompt(self):
        self.file(
            "rendered_prompt_file", "rendered.txt", "Question:\nA different question\n"
        )
        self.save()
        self.assert_problem("rendered prompt differs")

    def test_wrong_condition_template_and_prompt_as_answer_are_rejected(self):
        self.row["condition"] = "P1"
        self.save()
        self.assert_problem("template filename does not match")
        self.row["condition"] = "P2"
        self.file(
            "answer_file", "answer.txt", (self.repo / "rendered.txt").read_bytes()
        )
        self.save()
        self.assert_problem("answer bytes equal a prompt")

    def test_required_completion_evidence_and_all_additional_artifacts_checked(self):
        self.row.pop("screenshot_file")
        self.row.pop("screenshot_sha256")
        self.save()
        self.assert_problem("missing screenshot_file")
        self.file("screenshot_file", "screen.png", b"\x00PNG")
        self.file("citation_artifact_file", "citation.json", '{"links": []}\n')
        (self.repo / "citation.json").write_text(
            '{"changed": true}\n', encoding="utf-8"
        )
        self.save()
        self.assert_problem("SHA-256 mismatch for citation_artifact_file")

    def test_path_escape_absolute_path_and_symlink_are_rejected(self):
        original = self.row["answer_file"]
        for value in (
            "../answer.txt",
            str(self.repo / original),
            "C:\\private\\answer.txt",
        ):
            with self.subTest(value=value):
                self.row["answer_file"] = value
                self.save()
                self.assert_problem("artifact path")
        (self.repo / "linked.txt").symlink_to(self.repo / original)
        self.row["answer_file"] = "linked.txt"
        self.save()
        self.assert_problem("symlink")

    def test_nonfinite_metadata_and_malformed_identity_types_do_not_crash(self):
        for value in (float("nan"), float("inf"), "NaN", "Infinity"):
            with self.subTest(value=value):
                self.row["latency_s"] = value
                self.save()
                self.assert_problem("non-finite")
        self.row.pop("latency_s")
        self.row["run_status"] = []
        self.row["condition"] = []
        self.row["record_id"] = {}
        self.save()
        report = self.verify()
        self.assertFalse(report["valid"])
        self.assertTrue(report["errors"])

    @unittest.skipUnless(shutil.which("git"), "Git is needed for staged byte checks")
    def test_staged_git_normalization_mismatch_cannot_pass_disk_hash_checks(self):
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        env.update(
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1"
        )

        def git(*args):
            subprocess.run(
                ["git", *args],
                cwd=self.repo,
                env=env,
                capture_output=True,
                check=True,
                timeout=30,
            )

        git("-c", "init.defaultBranch=main", "init", "--quiet")
        (self.repo / ".gitattributes").write_text(
            "* text=auto eol=lf\n", encoding="utf-8"
        )
        self.file("answer_file", "answer.txt", b"ANSWER: The value is 31.\r\n")
        self.save()
        git("add", "--all")
        self.assertTrue(self.verify()["valid"])
        staged = self.verify(staged=True)
        self.assertFalse(staged["valid"])
        self.assertTrue(
            any(
                "Git bytes differ" in error and "answer.txt" in error
                for error in staged["errors"]
            ),
            staged["errors"],
        )
        self.file("answer_file", "answer.txt", b"ANSWER: The value is 31.\n")
        self.save()
        git("add", "--all")
        staged = self.verify(staged=True)
        self.assertTrue(staged["valid"], staged["errors"])


if __name__ == "__main__":
    unittest.main()
