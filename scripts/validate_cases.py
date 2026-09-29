#!/usr/bin/env python3
"""Validate the benchmark cases: schema, split sizes, stratification, edge-case share,
test/dev near-duplicates and SHA-256 hashes.

It never prints the content of test cases, only IDs and aggregate counts, so the
prompt author can run it without seeing the held-out set.

Usage:
    python3 scripts/validate_cases.py            # validate all splits
    python3 scripts/validate_cases.py --no-test  # skip the held-out file entirely
    python3 scripts/validate_cases.py --write-hashes
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


def tokens(text):
    return {t for t in re.findall(r"\w+", text.lower()) if len(t) >= 3}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=DATA)
    ap.add_argument("--no-test", action="store_true", help="do not open cases_test.jsonl")
    ap.add_argument("--write-hashes", action="store_true", help="write data/HASHES.txt")
    args = ap.parse_args()

    splits = ["dev", "val"] + ([] if args.no_test else ["test"])
    errors, warnings = [], []
    cases = {}
    for s in splits:
        path = os.path.join(args.data_dir, f"cases_{s}.jsonl")
        if not os.path.exists(path):
            errors.append(f"missing file {path}")
            continue
        cases[s] = load_cases(s, args.data_dir)

    seen = set()
    for s, rows in cases.items():
        if len(rows) != EXPECTED_SIZES[s]:
            warnings.append(f"{s}: {len(rows)} cases (plan: {EXPECTED_SIZES[s]})")
        for c in rows:
            tid = c.get("task_id", "?")
            if tid in seen:
                errors.append(f"duplicate task_id {tid}")
            seen.add(tid)
            for field in REQUIRED:
                if field not in c or c[field] in (None, ""):
                    if field != "context_or_files":
                        errors.append(f"{tid}: missing field {field}")
            if c.get("development_validation_test_split") != s:
                errors.append(f"{tid}: split field does not match file {s}")
            for field, allowed in ALLOWED.items():
                if c.get(field) not in allowed:
                    errors.append(f"{tid}: invalid {field}={c.get(field)!r}")
            ref = c.get("reference_answer_or_tests", {})
            if not ref.get("reference_answer"):
                errors.append(f"{tid}: empty reference_answer")
            if not ref.get("key_facts"):
                errors.append(f"{tid}: empty key_facts")
            gold = ref.get("gold_sources", [])
            if not gold or not all(str(g.get("url", "")).startswith("http") for g in gold):
                errors.append(f"{tid}: gold_sources missing or without http URL")
            if not c.get("expected_properties"):
                errors.append(f"{tid}: empty expected_properties")

    # Stratification table (aggregates only)
    print("\n== Stratification ==")
    for field in ["domain", "language", "task_type", "difficulty", "edge_case_type"]:
        print(f"\n{field}:")
        values = sorted({c.get(field) for rows in cases.values() for c in rows})
        header = "  " + "value".ljust(22) + "".join(s.rjust(7) for s in cases)
        print(header)
        for v in values:
            counts = [sum(1 for c in cases[s] if c.get(field) == v) for s in cases]
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

    if "test" in cases:
        n_test = len(cases["test"])
        if n_test < 10:
            errors.append(f"test split has {n_test} cases (< 10 required)")
        print(f"\n== Near-duplicates test vs dev/val (Jaccard >= {DUP_THRESHOLD}) ==")
        found = False
        for t in cases["test"]:
            tt = tokens(t["user_prompt"])
            for s in ("dev", "val"):
                for d in cases.get(s, []):
                    j = jaccard(tt, tokens(d["user_prompt"]))
                    if j >= DUP_THRESHOLD:
                        found = True
                        errors.append(f"near-duplicate {t['task_id']} ~ {d['task_id']} (J={j:.2f})")
                        print(f"  {t['task_id']} ~ {d['task_id']}: {j:.2f}")
        if not found:
            print("  none")

    print("\n== SHA-256 ==")
    lines = []
    for s in splits:
        path = os.path.join(args.data_dir, f"cases_{s}.jsonl")
        if os.path.exists(path):
            h = sha256_file(path)
            lines.append(f"{h}  cases_{s}.jsonl")
            print(f"  {h}  cases_{s}.jsonl")
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
