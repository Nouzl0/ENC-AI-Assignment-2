#!/usr/bin/env python3
"""Validate the benchmark cases: schema, split sizes, stratification, edge-case share,
test/dev near-duplicates and SHA-256 hashes.

By default it opens only dev/val. A steward can opt in to a private holdout;
output contains IDs/aggregates, not questions, but the process must read the file.
This is a schema/overlap check, not access control or independent fact verification.

Usage:
    python3 scripts/validate_cases.py --no-test  # public dev/val only (also default)
    python3 scripts/validate_cases.py --test-file "$WORK/holdout.jsonl"  # steward only
--write-hashes writes a checksum listing; it does not create or approve G1.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, EDGE_TYPES, load_cases, sha256_file  # noqa: E402

REQUIRED = ["task_id", "capability", "task_type", "difficulty", "language",
            "development_validation_test_split", "user_prompt", "context_or_files",
            "expected_properties", "reference_answer_or_tests", "edge_case_type",
            "evaluation_method", "source_or_provenance"]
ALLOWED = {
    "task_type": {"fact", "primary_source", "synthesis"},
    "difficulty": {"easy", "medium", "hard"},
    "language": {"cs", "en", "cs+en"},
    "domain": {"veda_zdravi", "pravo", "it", "ekonomika", "historie_kultura"},
    "edge_case_type": EDGE_TYPES,
}
EXPECTED_SIZES = {"dev": 20, "val": 10, "test": 10}
DUP_THRESHOLD = 0.5


def validate_case(case, split):
    """Validate types before consumers can crash or use a bonus as a denominator."""
    errors = []
    if not isinstance(case, dict):
        return [f"{split}: case must be an object"]
    tid = case.get("task_id", "?")
    for field in REQUIRED:
        if field not in case or case[field] in (None, ""):
            errors.append(f"{tid}: missing field {field}")
    for field in ("task_id", "capability", "user_prompt", "evaluation_method", "source_or_provenance"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            errors.append(f"{tid}: {field} must be a nonempty string")
    if case.get("development_validation_test_split") != split:
        errors.append(f"{tid}: split field does not match file {split}")
    for field, allowed in ALLOWED.items():
        if not isinstance(case.get(field), str) or case[field] not in allowed:
            errors.append(f"{tid}: invalid {field}={case.get(field)!r}")
    if not isinstance(case.get("context_or_files"), list):
        errors.append(f"{tid}: context_or_files must be a list (empty is allowed)")
    properties = case.get("expected_properties")
    if not isinstance(properties, list) or not properties or not all(isinstance(p, str) and p.strip() for p in properties):
        errors.append(f"{tid}: expected_properties must be a nonempty string list")
    ref = case.get("reference_answer_or_tests")
    if not isinstance(ref, dict):
        return errors + [f"{tid}: reference_answer_or_tests must be an object"]
    if not isinstance(ref.get("reference_answer"), str) or not ref["reference_answer"].strip():
        errors.append(f"{tid}: empty reference_answer")
    for field in ("key_facts", "required_facts", "optional_facts"):
        if field not in ref and field != "key_facts":
            if case.get("schema_version") == 2:
                errors.append(f"{tid}: schema v2 requires {field}")
            continue
        facts = ref.get(field)
        if not isinstance(facts, list) or (field != "optional_facts" and not facts) or not all(isinstance(f, str) and f.strip() for f in facts):
            errors.append(f"{tid}: invalid {field} string list")
        elif len(set(facts)) != len(facts):
            errors.append(f"{tid}: duplicate {field}")
    if "required_facts" in ref and ref.get("key_facts") != ref["required_facts"]:
        errors.append(f"{tid}: key_facts must be the required_facts compatibility alias")
    gold = ref.get("gold_sources")
    if not isinstance(gold, list) or not gold or not all(isinstance(g, dict) and isinstance(g.get("url"), str)
                                                       and g["url"].startswith(("http://", "https://")) for g in gold):
        errors.append(f"{tid}: gold_sources missing or without http URL")
    return errors


def tokens(text):
    return {t for t in re.findall(r"\w+", text.lower()) if len(t) >= 3}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=DATA)
    ap.add_argument("--no-test", action="store_true", help="validate public dev/val only (default without --test-file)")
    ap.add_argument("--test-file", help="explicit path to new holdout, never the published candidates")
    ap.add_argument("--write-hashes", action="store_true", help="write data/HASHES.txt")
    args = ap.parse_args()

    if args.no_test and args.test_file:
        ap.error("--no-test and --test-file are mutually exclusive")
    splits = ["dev", "val"] + (["test"] if args.test_file else [])
    errors, warnings = [], []
    cases = {}
    for s in splits:
        path = args.test_file if s == "test" else os.path.join(args.data_dir, f"cases_{s}.jsonl")
        if not os.path.exists(path):
            errors.append(f"missing file {path}")
            continue
        try:
            cases[s] = load_cases(s, args.data_dir, args.test_file)
        except ValueError as e:
            errors.append(f"{path}: {e}")
            continue
        for c in cases[s]:
            errors.extend(validate_case(c, s))
        cases[s] = [c for c in cases[s] if isinstance(c, dict)]

    seen = set()
    for s, rows in cases.items():
        if len(rows) != EXPECTED_SIZES[s]:
            warnings.append(f"{s}: {len(rows)} cases (plan: {EXPECTED_SIZES[s]})")
        for c in rows:
            tid = str(c.get("task_id", "?"))
            if tid in seen:
                errors.append(f"duplicate task_id {tid}")
            seen.add(tid)

    # Stratification table (aggregates only)
    print("\n== Stratification ==")
    for field in ["domain", "language", "task_type", "difficulty", "edge_case_type"]:
        print(f"\n{field}:")
        values = sorted({str(c.get(field)) for rows in cases.values() for c in rows})
        header = "  " + "value".ljust(22) + "".join(s.rjust(7) for s in cases)
        print(header)
        for v in values:
            counts = [sum(1 for c in cases[s] if str(c.get(field)) == v) for s in cases]
            print("  " + str(v).ljust(22) + "".join(str(n).rjust(7) for n in counts))

    print("\n== Edge-case share (requirement: >= 20 %) ==")
    total = edge = 0
    for s, rows in cases.items():
        e = sum(1 for c in rows if c.get("edge_case_type") != "none")
        total += len(rows)
        edge += e
        share = e / len(rows) if rows else 0
        print(f"  {s}: {e}/{len(rows)} = {share:.0%}")
        if share < 0.2:
            errors.append(f"{s}: edge-case share {share:.0%} < 20 %")
    if total:
        print(f"  all: {edge}/{total} = {edge / total:.0%}")
    if args.test_file and total < 40:
        errors.append(f"benchmark has {total} cases (< 40 required)")

    if "test" in cases:
        n_test = len(cases["test"])
        if n_test < 10:
            errors.append(f"test split has {n_test} cases (< 10 required)")
        print(f"\n== Near-duplicates test vs dev/val (Jaccard >= {DUP_THRESHOLD}) ==")
        found = False
        for t in cases["test"]:
            tt = tokens(str(t.get("user_prompt", "")))
            for s in ("dev", "val"):
                for d in cases.get(s, []):
                    j = jaccard(tt, tokens(str(d.get("user_prompt", ""))))
                    if j >= DUP_THRESHOLD:
                        found = True
                        errors.append(f"near-duplicate {t.get('task_id', '?')} ~ {d.get('task_id', '?')} (J={j:.2f})")
                        print(f"  {t.get('task_id', '?')} ~ {d.get('task_id', '?')}: {j:.2f}")
        if not found:
            print("  none")

    print("\n== SHA-256 ==")
    lines = []
    for s in splits:
        path = args.test_file if s == "test" else os.path.join(args.data_dir, f"cases_{s}.jsonl")
        if os.path.exists(path):
            h = sha256_file(path)
            lines.append(f"{h}  {'private_holdout' if s == 'test' else 'cases_' + s + '.jsonl'}")
            print("  " + lines[-1])
    prompt_dir = os.path.join(os.path.dirname(os.path.abspath(args.data_dir)), "prompts")
    if os.path.isdir(prompt_dir):
        for name in sorted(os.listdir(prompt_dir)):
            if name.endswith(".txt"):
                h = sha256_file(os.path.join(prompt_dir, name))
                lines.append(f"{h}  prompts/{name}")
                print(f"  {h}  prompts/{name}")
    if args.write_hashes:
        with open(os.path.join(args.data_dir, "HASHES.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("  written to data/HASHES.txt")

    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    print("\nRESULT:", "OK" if not errors else f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
