#!/usr/bin/env python3
"""Create the run plan (= run metadata sheet) for one phase.

Each row is one planned run: case x condition x system x run index, with the fully
rendered prompt to paste, its SHA-256 and empty metadata columns the operator fills in.
The order of systems (and of conditions) is shuffled per case with a fixed seed.

Production requires verified G1 for dev/val, G2 for test/repeat, and --out outside
the Git worktree. Parameters/subsets come from the frozen config, not observed scores.
Examples (data steward only; see HANDOFF.md for prerequisites):
    python3 scripts/make_run_plan.py --phase dev --freeze "$WORK/G1.json" --out "$WORK/runs/run_plan_dev.csv"
    python3 scripts/make_run_plan.py --phase test --freeze "$WORK/G2.json" --out "$WORK/runs/run_plan_test.csv"
Calibration before G1 is separate:
    python3 scripts/make_run_plan.py --pilot --phase dev --only CIT-001,CIT-020 --out "$WORK/calibration/pilot.csv"
--synthetic is only for local DEMO-* fixtures and anonymous sys_* systems.
"""

import argparse
import hashlib
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    INTERFACE,
    META_FILL_COLUMNS,
    PHASES,
    PROMPT_FILES,
    PROMPTS,
    ROOT,
    SYSTEMS,
    TOOL_PERMISSIONS,
    load_cases,
    prompt_lang,
    write_csv,
)
from integrity import bind_plan, private_path, verify_freeze

COLUMNS = [
    "seq",
    "run_id",
    "phase",
    "split",
    "task_id",
    "language",
    "condition",
    "prompt_file",
    "prompt_sha256",
    "rendered_prompt_sha256",
    "system",
    "interface",
    "run_index",
    "system_instruction",
    "tool_permissions",
    "context_files",
    "temperature",
    "max_output",
    "answer_file",
    *META_FILL_COLUMNS,
    "prompt_text",
]


def load_prompt(condition, lang, prompts_dir):
    name = PROMPT_FILES[condition].format(lang=lang)
    path = os.path.join(prompts_dir, name)
    if not os.path.exists(path):
        raise SystemExit(
            f"Missing prompt file {path}. "
            + (
                "Freeze P3 first (copy the winning candidate to P3_final_*.txt)."
                if condition == "P3"
                else ""
            )
        )
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
    ap.add_argument("--freeze", help="G1 for dev/val; G2 for test/repeat")
    ap.add_argument(
        "--test-file", help="explicit private holdout; must match the freeze"
    )
    ap.add_argument(
        "--val-candidates",
        default="P3A,P3B",
        help="synthetic/pilot only; real plans use G1 config",
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument(
        "--pilot",
        action="store_true",
        help="pre-G1 dev calibration only, not confirmatory data",
    )
    mode.add_argument(
        "--synthetic",
        action="store_true",
        help="local DEMO-* fixtures only, not product results",
    )
    args = ap.parse_args()

    split, conditions, run_indices = PHASES[args.phase]
    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    if (
        not systems
        or len(set(systems)) != len(systems)
        or (not args.synthetic and set(systems) - set(SYSTEMS))
    ):
        raise SystemExit("--systems must contain unique known product identifiers")
    if args.synthetic and any(not re.fullmatch(r"sys_[A-Z]", s) for s in systems):
        raise SystemExit("synthetic systems must be anonymous sys_A, sys_B, ...")
    if args.pilot and (args.phase != "dev" or not args.only or args.freeze):
        raise SystemExit(
            "pilot requires --phase dev --only <calibration IDs>, without a freeze"
        )
    if not (args.synthetic or args.pilot):
        try:
            gate = verify_freeze(args.freeze, "G2" if split == "test" else "G1")
            cfg = gate["config"]
            if args.systems != ",".join(SYSTEMS) and systems != cfg["systems"]:
                raise ValueError("--systems differs from frozen config")
            systems, args.seed = cfg["systems"], cfg["seed"]
            if (
                os.path.realpath(args.data_dir) != os.path.join(ROOT, "data")
                or os.path.realpath(args.prompts_dir) != PROMPTS
            ):
                raise ValueError(
                    "real plans must use the frozen repository data/prompts"
                )
            if (
                args.test_file
                and os.path.realpath(args.test_file) != gate["inputs"]["test_cases"]
            ):
                raise ValueError("--test-file differs from frozen holdout")
            args.test_file = gate["inputs"]["test_cases"]
            if args.phase == "val":
                conditions = ["P2"] + cfg["val_candidates"]
            if args.phase == "repeat":
                if args.only and set(args.only.split(",")) != set(
                    cfg["repeat_task_ids"]
                ):
                    raise ValueError("repeat subset differs from G1")
                args.only = ",".join(cfg["repeat_task_ids"])
            elif args.only:
                raise ValueError(
                    "real analytical phases require the full prespecified split"
                )
        except (ValueError, OSError, KeyError) as e:
            raise SystemExit(str(e)) from e
    elif args.phase == "val":
        conditions = ["P2", *args.val_candidates.split(",")]
        if set(conditions) - {"P2", "P3A", "P3B"} or len(set(conditions)) != len(
            conditions
        ):
            raise SystemExit("invalid --val-candidates")
    cases = load_cases(split, args.data_dir, args.test_file)
    if args.synthetic and any(
        not c["task_id"].startswith("DEMO-")
        or "synthetic" not in c["source_or_provenance"].lower()
        for c in cases
    ):
        raise SystemExit("synthetic mode accepts only declared synthetic DEMO-* cases")
    if args.only:
        keep = {t.strip() for t in args.only.split(",")}
        unknown = keep - {c["task_id"] for c in cases}
        if unknown:
            raise SystemExit(f"unknown task IDs: {sorted(unknown)}")
        cases = [c for c in cases if c["task_id"] in keep]
    out = args.out or os.path.join(ROOT, "runs", f"run_plan_{args.phase}.csv")
    if not args.synthetic:
        out = private_path(out)
    if os.path.exists(out) or os.path.exists(out + ".manifest.json"):
        raise SystemExit(
            f"Refusing to overwrite {out}; preserve the existing plan/metadata"
        )
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
                    run_id = (
                        f"{args.phase}-{case['task_id']}-{cond}-{system}-r{run_index}"
                    )
                    row = {
                        "seq": seq,
                        "run_id": run_id,
                        "phase": args.phase,
                        "split": split,
                        "task_id": case["task_id"],
                        "language": case["language"],
                        "condition": cond,
                        "prompt_file": pname,
                        "prompt_sha256": psha,
                        "rendered_prompt_sha256": hashlib.sha256(
                            rendered.encode("utf-8")
                        ).hexdigest(),
                        "system": system,
                        "interface": INTERFACE.get(system, ""),
                        "run_index": run_index,
                        "system_instruction": "výchozí, neviditelná",
                        "tool_permissions": TOOL_PERMISSIONS.get(system, ""),
                        "context_files": "žádné",
                        "temperature": "výchozí, nenastavitelné",
                        "max_output": "výchozí",
                        "answer_file": os.path.join(
                            os.path.dirname(os.path.abspath(out)),
                            "answers",
                            f"{run_id}.txt",
                        ),
                        "prompt_text": rendered,
                        "run_status": "planned",
                    }
                    for col in META_FILL_COLUMNS:
                        row.setdefault(col, "")
                    rows.append(row)

    write_csv(out, rows, COLUMNS)
    bind_plan(out, rows, args.freeze, args.synthetic, args.pilot, args.prompts_dir)
    print(f"{len(rows)} planned runs -> {out}")
    shas = sorted({(r["prompt_file"], r["prompt_sha256"]) for r in rows})
    for name, h in shas:
        print(f"  {h}  {name}")


if __name__ == "__main__":
    main()
