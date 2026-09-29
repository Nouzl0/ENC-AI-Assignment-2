#!/usr/bin/env python3
"""Create the run plan (= run metadata sheet) for one phase.

Each row is one planned run: case x condition x system x run index, with the fully
rendered prompt to paste, its SHA-256 and empty metadata columns the operator fills in.
The order of systems (and of conditions) is shuffled per case with a fixed seed.

Usage:
    python3 scripts/make_run_plan.py --phase dev
    python3 scripts/make_run_plan.py --phase val
    python3 scripts/make_run_plan.py --phase test     # requires prompts/P3_final_*.txt
    python3 scripts/make_run_plan.py --phase repeat
Options:
    --systems chatgpt,gemini,claude,perplexity   (lean variant without grok)
    --only CIT-031,CIT-032                       (subset, e.g. repeats on 5 cases)
"""
import argparse
import hashlib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (INTERFACE, META_FILL_COLUMNS, PHASES, PROMPT_FILES, PROMPTS, ROOT,  # noqa: E402
                    SYSTEMS, TOOL_PERMISSIONS, load_cases, prompt_lang, write_csv)

COLUMNS = ["seq", "run_id", "phase", "split", "task_id", "language", "condition",
           "prompt_file", "prompt_sha256", "system", "interface", "run_index",
           "system_instruction", "tool_permissions", "context_files", "temperature",
           "max_output", "answer_file"] + META_FILL_COLUMNS + ["prompt_text"]


def load_prompt(condition, lang, prompts_dir):
    name = PROMPT_FILES[condition].format(lang=lang)
    path = os.path.join(prompts_dir, name)
    if not os.path.exists(path):
        raise SystemExit(f"Missing prompt file {path}. "
                         + ("Freeze P3 first (copy the winning candidate to P3_final_*.txt)."
                            if condition == "P3" else ""))
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return name, text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=sorted(PHASES))
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--systems", default=",".join(SYSTEMS))
    ap.add_argument("--only", default="", help="comma-separated task_ids to include")
    ap.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    ap.add_argument("--prompts-dir", default=PROMPTS)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    split, conditions, run_indices = PHASES[args.phase]
    if split == "test":
        # Held-out set: only after P3 is frozen (protocol gate G2).
        for lang in ("cs", "en"):
            load_prompt("P3", lang, args.prompts_dir)
    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    cases = load_cases(split, args.data_dir)
    if args.only:
        keep = {t.strip() for t in args.only.split(",")}
        cases = [c for c in cases if c["task_id"] in keep]
    rng = random.Random(f"{args.seed}-{args.phase}")

    rows, seq = [], 0
    for run_index in run_indices:
        for case in cases:
            lang = prompt_lang(case["language"])
            conds = conditions[:]
            rng.shuffle(conds)
            for cond in conds:
                pname, ptext, psha = load_prompt(cond, lang, args.prompts_dir)
                rendered = ptext.replace("{user_prompt}", case["user_prompt"])
                order = systems[:]
                rng.shuffle(order)
                for system in order:
                    seq += 1
                    run_id = f"{args.phase}-{case['task_id']}-{cond}-{system}-r{run_index}"
                    row = {
                        "seq": seq, "run_id": run_id, "phase": args.phase, "split": split,
                        "task_id": case["task_id"], "language": case["language"],
                        "condition": cond, "prompt_file": pname, "prompt_sha256": psha,
                        "system": system, "interface": INTERFACE.get(system, ""),
                        "run_index": run_index,
                        "system_instruction": "výchozí, neviditelná",
                        "tool_permissions": TOOL_PERMISSIONS.get(system, ""),
                        "context_files": "žádné", "temperature": "výchozí, nenastavitelné",
                        "max_output": "výchozí", "answer_file": f"runs/answers/{run_id}.txt",
                        "prompt_text": rendered,
                    }
                    for col in META_FILL_COLUMNS:
                        row.setdefault(col, "")
                    rows.append(row)

    out = args.out or os.path.join(ROOT, "runs", f"run_plan_{args.phase}.csv")
    write_csv(out, rows, COLUMNS)
    print(f"{len(rows)} planned runs -> {out}")
    shas = sorted({(r['prompt_file'], r['prompt_sha256']) for r in rows})
    for name, h in shas:
        print(f"  {h}  {name}")


if __name__ == "__main__":
    main()
