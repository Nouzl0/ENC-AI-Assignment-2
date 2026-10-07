"""Shared helpers for the CZAI citation benchmark scripts (standard library only)."""
import csv
import hashlib
import json
import math
import os
from replay_paths import input_glob, resolve_input

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PROMPTS = os.path.join(ROOT, "prompts")

SYSTEMS = ["chatgpt", "gemini", "claude", "perplexity", "grok"]

INTERFACE = {
    "chatgpt": "chatgpt.com (web)",
    "gemini": "gemini.google.com (web)",
    "claude": "claude.ai (web)",
    "perplexity": "perplexity.ai (web)",
    "grok": "grok.com (web)",
}
TOOL_PERMISSIONS = {
    "chatgpt": "Search vynucen; Deep research vypnut; Temporary chat (Unpersonalized)",
    "gemini": "vyhledávání automatické; Deep Research vypnut; Temporary chat",
    "claude": "Web search zapnut/automatický; Research vypnut; Incognito chat",
    "perplexity": "režim Search; Research/Labs vypnuto; Incognito",
    "grok": "vyhledávání automatické (web + X); DeepSearch vypnut; Private Chat",
}

# phase -> (split, conditions, run indices)
PHASES = {
    "dev": ("dev", ["P2"], [1]),
    "val": ("val", ["P2", "P3A", "P3B"], [1]),
    "test": ("test", ["P1", "P2", "P3"], [1]),
    "repeat": ("test", ["P2"], [2, 3]),
}

PROMPT_FILES = {
    "P1": "P1_baseline_{lang}.txt",
    "P2": "P2_structured_{lang}.txt",
    "P3A": "P3A_candidate_{lang}.txt",
    "P3B": "P3B_candidate_{lang}.txt",
    "P3": "P3_final_{lang}.txt",
}

EDGE_TYPES = {"none", "false_premise", "conflicting_evidence", "missing_info", "ambiguous",
              "time_constraint", "recent_change", "cz_en_mix"}
RATINGS = {"S2", "S1", "S0", "NA", "FAB"}

META_FILL_COLUMNS = [
    "run_status", "final_attempt_ok", "attempt1_file", "first_attempt_latency_s",
    "model_visible", "plan_tier", "datetime_start", "datetime_end", "latency_s",
    "search_used", "n_sources_shown", "turns", "tool_calls_visible", "retries",
    "failure_type", "first_attempt_ok", "manual_intervention", "share_link",
    "screenshot_file", "operator", "cost_note", "notes",
    "answer_sha256", "raw_answer_file", "raw_answer_sha256", "screenshot_sha256",
    "attempt1_sha256", "failure_artifact_file", "failure_artifact_sha256",
    "replacement_run_id", "replaces_run_id",
]
FAILURE_TYPES = {"", "none", "model_output", "invalid_format", "tool_error", "rate_limit",
                 "timeout", "product_outage", "student_error", "student_error_rerun", "evaluation_error"}
RUN_STATUSES = {"planned", "completed", "failed", "excluded"}
OPERATIONAL_FAILURES = {"tool_error", "rate_limit", "timeout", "product_outage"}


def finite_number(value):
    """CSV numeric value, or None (never NaN/inf)."""
    try:
        number = float(str(value).replace(",", "."))
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def unique_index(rows, field, label):
    """Fail closed: duplicate identifiers must never silently overwrite a row."""
    out = {}
    for row in rows:
        value = row.get(field, "")
        if not value or value in out:
            raise ValueError(f"{label}: missing or duplicate {field}={value!r}")
        out[value] = row
    return out


def diagnostic_problems(answer, pairs, case):
    """Unknown is explicit missing evidence, not an empty or favorable denominator."""
    errors = []
    uncertain = case.get("edge_case_type") in {"missing_info", "ambiguous"}
    if answer.get("acknowledges_uncertainty") not in ({"yes", "no", "unknown"} if uncertain else {"na"}):
        errors.append("acknowledges_uncertainty must be yes/no/unknown on ambiguous/missing_info, otherwise na")
    timed = case.get("edge_case_type") == "time_constraint"
    for pair in pairs:
        if pair.get("citation_n") in {None, ""}:
            continue
        if pair.get("source_tier") not in {"1", "2", "3", "unknown"}:
            errors.append(f"{pair.get('pair_id')}: source_tier must be 1/2/3/unknown")
        if pair.get("time_ok") not in ({"yes", "no", "unknown"} if timed else {"na"}):
            errors.append(f"{pair.get('pair_id')}: time_ok must be yes/no/unknown on time_constraint, otherwise na")
    return errors


def validate_pair_rows(rows, label):
    unique_index(rows, "pair_id", label)
    identities = set()
    for row in rows:
        cit = (row.get("citation_n") or "").strip()
        if cit not in {"", "*"}:
            # Preserve malformed model output [0] for human rating; metadata
            # records invalid numbering. This is not automatically FAB.
            if not cit.isdigit() or int(cit) < 0:
                raise ValueError(f"{label}: invalid citation_n={cit!r}")
            cit = str(int(cit))
        identity = (row.get("blind_answer_id"), row.get("claim_id"), cit)
        if not all(identity[:2]) or identity in identities:
            raise ValueError(f"{label}: duplicate or missing claim-citation identity: {identity}")
        identities.add(identity)
        expected_id = f"{identity[0]}-{identity[1]}-{cit or 'none'}"
        if row["pair_id"] != expected_id:
            raise ValueError(f"{label}: pair_id must be {expected_id!r}; regenerate after splitting claims")


def required_facts(case):
    ref = case.get("reference_answer_or_tests", {})
    return ref.get("required_facts", ref.get("key_facts", []))


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def constraint_problems(row, case):
    """Question-level source/format constraints are not claim–citation facts."""
    constraints = case.get("reference_answer_or_tests", {}).get("required_constraints", [])
    try:
        results = json.loads(row.get("constraint_results") or "{}", object_pairs_hook=unique_json_object)
    except (ValueError, TypeError):
        return ["constraint_results must be a JSON object"]
    expected = {f"RC{i}" for i in range(1, len(constraints) + 1)}
    if (not isinstance(results, dict) or set(results) != expected
            or any(not isinstance(value, str) or value not in {"yes", "no", "unknown"} for value in results.values())):
        return ["constraint_results must cover exactly RC1…RCn with yes/no/unknown"]
    if str(row.get("correctness")).strip() == "2" and any(v != "yes" for v in results.values()):
        return ["correctness=2 requires every question-level constraint to be met"]
    return []


def run_problems(row, require_terminal=True):
    """Validate outcome and numeric fields without consulting model answers."""
    errors = []
    status = row.get("run_status", "")
    failure = row.get("failure_type", "")
    for field in ("run_id", "task_id", "system", "condition", "split"):
        if not row.get(field):
            errors.append(f"missing {field}")
    if status not in RUN_STATUSES or (require_terminal and status == "planned"):
        errors.append(f"run_status={status!r}; expected a terminal outcome")
    if failure not in FAILURE_TYPES:
        errors.append(f"unknown failure_type={failure!r}")
    if status == "excluded" and failure != "student_error":
        errors.append("only documented student_error can be excluded; replacement is required")
    if status == "failed" and failure not in OPERATIONAL_FAILURES:
        errors.append("failed requires a terminal operational failure")
    if status == "completed" and (not row.get("answer_file") or failure in {"student_error", "evaluation_error"}):
        errors.append("completed requires an answer_file and a valid final attempt")
    ri = finite_number(row.get("run_index"))
    if ri is None or ri < 1 or not ri.is_integer():
        errors.append("run_index must be a positive integer")
    if status in {"completed", "failed"}:
        for field in ("latency_s", "first_attempt_latency_s", "retries"):
            number = finite_number(row.get(field))
            if number is None or number < 0 or (field == "retries" and number not in {0, 1}):
                errors.append(f"invalid {field} (finite, nonnegative; retries <= 1)")
        if row.get("first_attempt_ok") not in {"yes", "no"}:
            errors.append("first_attempt_ok must be yes/no")
        if row.get("final_attempt_ok") != ("yes" if status == "completed" else "no"):
            errors.append("final_attempt_ok contradicts run_status")
        retry = finite_number(row.get("retries"))
        if retry == 0 and row.get("first_attempt_ok") != row.get("final_attempt_ok"):
            errors.append("without a retry, first and final outcomes must match")
        if retry == 1:
            if not row.get("attempt1_file"):
                errors.append("retry requires an attempt1_file (including an outage log)")
            if row.get("first_attempt_ok") != "no" or failure not in OPERATIONAL_FAILURES:
                errors.append("retry only follows a failed first attempt with an operational failure")
        first, total = finite_number(row.get("first_attempt_latency_s")), finite_number(row.get("latency_s"))
        if first is not None and total is not None and first > total:
            errors.append("first-attempt latency exceeds end-to-end latency")
    return errors


def prompt_lang(case_language):
    """Czech prompt for 'cs' and mixed 'cs+en' cases, English prompt for 'en'."""
    return "en" if case_language == "en" else "cs"


def sha256_file(path):
    h = hashlib.sha256()
    with open(resolve_input(path), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cases(split, data_dir=DATA, test_file=None):
    if split == "test" and not test_file:
        raise ValueError("test requires an explicit --test-file; published candidates are not a private holdout")
    path = test_file if split == "test" else os.path.join(data_dir, f"cases_{split}.jsonl")
    with open(resolve_input(path), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_all_cases(data_dir=DATA, test_file=None):
    rows = []
    for split in ("dev", "val") + (("test",) if test_file else ()):
        rows.extend(load_cases(split, data_dir, test_file))
    return unique_index(rows, "task_id", "cases")


def read_csv(path):
    with open(resolve_input(path), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_glob(pattern):
    rows = []
    for p in input_glob(pattern):
        rows.extend(read_csv(p))
    return rows


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
