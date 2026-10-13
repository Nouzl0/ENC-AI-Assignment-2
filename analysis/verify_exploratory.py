#!/usr/bin/env python3
"""Read-only integrity check of canonical exploratory records and Git bytes.

All records, including plans, failures and excluded captures, remain in the
report. This checks identities, paths, recorded hashes and prompt rendering;
it neither assesses answer correctness nor verifies protocol gates.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from supplement_review import (
    DIGEST_RE,
    _artifact_path,
    _case_index,
    _jsonl,
    _no_symlinks,
    _snapshot,
)

from common import PROMPT_FILES, ROOT, finite_number, prompt_lang, sha256_file

REQUIRED_COMPLETED = (
    "answer_file",
    "raw_answer_file",
    "screenshot_file",
)
REQUIRED_PROMPT = ("template_file", "rendered_prompt_file")
NUMERIC_FIELDS = (
    "latency_s",
    "observed_interval_s",
    "first_attempt_latency_s",
    "retries",
    "turns",
    "run_index",
    "n_sources_shown",
    "tool_calls_visible",
)


def _git_blob(root, relative, ref, staged):
    object_name = f":{relative}" if staged else f"{ref}:{relative}"
    result = subprocess.run(
        ["git", "-C", str(root), "show", object_name],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"input not present in requested Git tree: {relative}")
    return result.stdout


def verify_registry(registry, case_paths, root=ROOT, git_ref=None, staged=False):
    """Return every integrity error; inspect sources without writing any files."""
    report = {
        "scope": "EXPLORATORY_INTEGRITY_CHECK_NOT_G3",
        "valid": False,
        "git_tree": "index" if staged else git_ref,
        "records": [],
        "artifacts": [],
        "errors": [],
        "warnings": [],
    }
    errors, warnings = report["errors"], report["warnings"]
    snapshots, contents = {}, {}
    if staged and git_ref:
        errors.append("choose --staged or --git-ref, not both")
        return report
    try:
        root = _no_symlinks(root)
        records = _jsonl(registry, snapshots)
        cases = _case_index(case_paths, snapshots)
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(str(error))
        return report
    identities, record_ids = set(), set()
    answer_digests = defaultdict(list)
    for row in records:
        rid = row.get("record_id", "<missing record_id>")

        def problem(message, record_id=rid):
            errors.append(f"{record_id}: {message}")

        for field in (
            "record_id",
            "collection",
            "run_id",
            "task_id",
            "phase",
            "system",
            "condition",
            "run_status",
        ):
            if not isinstance(row.get(field), str) or not row[field].strip():
                problem(f"missing/nontext {field}")
        if not isinstance(rid, str):
            rid = repr(rid)
        if rid in record_ids:
            problem("duplicate record_id")
        record_ids.add(rid)
        collection, run_id = row.get("collection"), row.get("run_id")
        if isinstance(collection, str) and isinstance(run_id, str):
            identity = (collection, run_id)
            if identity in identities:
                problem("duplicate collection + run_id identity")
            identities.add(identity)
            if rid != collection + "/" + run_id:
                problem("record_id must equal collection + '/' + run_id")
        else:
            problem("invalid collection + run_id identity")
        status = row.get("run_status")
        if not isinstance(status, str) or status not in {
            "completed",
            "failed",
            "excluded",
            "planned",
        }:
            problem("unknown run_status")
        if type(row.get("include_in_analysis")) is not bool:
            problem("include_in_analysis must be a JSON boolean")
        eligible = row.get("include_in_analysis") is True and status == "completed"
        if not eligible and not row.get("disposition"):
            problem("noneligible record needs an explicit disposition")
        for field in NUMERIC_FIELDS:
            value = row.get(field)
            if value not in (None, "", "unknown") and finite_number(value) is None:
                problem(f"non-finite/invalid {field}")
        task_id = row.get("task_id")
        case = cases.get(task_id) if isinstance(task_id, str) else None
        if case is None:
            problem("unknown task_id")
        report["records"].append(
            {
                "record_id": rid,
                "run_status": status,
                "include_in_analysis": row.get("include_in_analysis"),
                "eligible_completed": eligible,
                "disposition": row.get("disposition", ""),
            }
        )
        for field in (*REQUIRED_PROMPT, *(REQUIRED_COMPLETED if eligible else ())):
            if not row.get(field):
                problem(f"missing {field}")
        files = {}
        # Every declared artifact uses a matching digest; do not ignore additional
        # file fields just because they are not needed for the rater packet.
        for field, value in row.items():
            if not field.endswith("_file"):
                continue
            hash_field = field.removesuffix("_file") + "_sha256"
            digest = row.get(hash_field)
            if not value:
                if digest:
                    problem(f"{hash_field} without {field}")
                continue
            try:
                path = _artifact_path(root, value)
                if not digest:
                    raise ValueError(f"missing {hash_field}")
                if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
                    raise ValueError(f"invalid {hash_field}")
                data = _snapshot(path, snapshots)
                actual = hashlib.sha256(data).hexdigest()
                if actual != digest:
                    raise ValueError(f"SHA-256 mismatch for {field}")
                files[field] = data
                contents[str(path)] = data
                report["artifacts"].append(
                    {
                        "record_id": rid,
                        "field": field,
                        "path": value,
                        "bytes": len(data),
                        "sha256": actual,
                    }
                )
            except (OSError, UnicodeError, ValueError) as error:
                problem(str(error))
        for field, digest in row.items():
            if field.endswith("_sha256") and not field.startswith("original_"):
                file_field = field.removesuffix("_sha256") + "_file"
                if digest and file_field not in row:
                    problem(f"{field} without {file_field}")
        if case and "template_file" in files and "rendered_prompt_file" in files:
            condition = row.get("condition")
            if not isinstance(condition, str) or condition not in PROMPT_FILES:
                problem("unknown prompt condition")
            else:
                expected_name = PROMPT_FILES[condition].format(
                    lang=prompt_lang(case.get("language"))
                )
                if Path(row["template_file"]).name != expected_name:
                    problem("template filename does not match condition/language")
            try:
                template = files["template_file"].decode("utf-8")
                if "{user_prompt}" not in template:
                    problem("template has no {user_prompt} placeholder")
                expected = template.replace(
                    "{user_prompt}", case["user_prompt"]
                ).encode("utf-8")
                if files["rendered_prompt_file"] != expected:
                    problem(
                        "rendered prompt differs from exact template + case question"
                    )
            except UnicodeError as error:
                problem(str(error))
        if eligible and "answer_file" in files:
            try:
                if not files["answer_file"].decode("utf-8").strip():
                    problem("completed answer is empty")
            except UnicodeError as error:
                problem(str(error))
            if files["answer_file"] in (
                files.get("template_file"),
                files.get("rendered_prompt_file"),
            ):
                problem("answer bytes equal a prompt artifact")
            answer_digests[hashlib.sha256(files["answer_file"]).hexdigest()].append(
                (rid, task_id)
            )
    for digest, matches in answer_digests.items():
        if len({task for _, task in matches}) > 1:
            warnings.append(
                {
                    "warning": "identical answer bytes across different tasks; inspect capture correspondence",
                    "answer_sha256": digest,
                    "record_ids": [rid for rid, _ in matches],
                }
            )
    if git_ref or staged:
        for path, snapshot in sorted(snapshots.items()):
            try:
                relative = str(Path(path).relative_to(root))
                blob = _git_blob(root, relative, git_ref, staged)
                if (
                    hashlib.sha256(blob).hexdigest() != snapshot["sha256"]
                    or len(blob) != snapshot["bytes"]
                ):
                    errors.append(
                        f"Git bytes differ from recorded disk snapshot: {relative}"
                    )
            except (OSError, ValueError) as error:
                errors.append(str(error))
    for path, snapshot in sorted(snapshots.items()):
        try:
            _no_symlinks(path)
            if not Path(path).is_file() or sha256_file(path) != snapshot["sha256"]:
                errors.append(f"input changed during integrity check: {path}")
        except (OSError, ValueError) as error:
            errors.append(str(error))
    report.update(
        valid=not errors,
        record_count=len(records),
        eligible_completed=sum(row["eligible_completed"] for row in report["records"]),
        status_counts=dict(Counter(str(row.get("run_status")) for row in records)),
        unique_task_ids=len(
            {
                row.get("task_id")
                for row in records
                if isinstance(row.get("task_id"), str)
            }
        ),
        unique_artifact_files=len(contents),
        input_snapshots=[
            {"path": path, **snapshot} for path, snapshot in sorted(snapshots.items())
        ],
    )
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--cases", type=Path, action="append", required=True)
    git = parser.add_mutually_exclusive_group()
    git.add_argument(
        "--staged",
        action="store_true",
        help="also compare every input with the Git index",
    )
    git.add_argument("--git-ref", help="also compare every input with a Git commit/ref")
    args = parser.parse_args(argv)
    report = verify_registry(
        args.registry, args.cases, root=ROOT, git_ref=args.git_ref, staged=args.staged
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
