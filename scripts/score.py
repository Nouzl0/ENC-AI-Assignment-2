#!/usr/bin/env python3
"""Compute metrics, uncertainty, hypothesis tests and rater agreement.

Inputs (all CSV):
    runs/run_plan_*.csv             filled run metadata (system, condition, latency, ...)
    annotation_key/blind_key.csv, answers_meta.csv   blind_answer_id -> run_id (data steward)
    annotation/<phase>/pairs_rated.csv       final claim-citation ratings (after disagreements resolved)
    annotation/<phase>/answers_rated.csv     final answer-level ratings (correctness 0-2, key facts, minutes)
    annotation/<phase>/pairs_rated_rater1.csv, answers_rated_rater1.csv  rater 1 BEFORE reconciliation
    annotation/<phase>/pairs_rated_rater2.csv, answers_rated_rater2.csv  rater 2 (25 % subset)

Outputs (private --out): metrics.csv, answer_metrics.csv, hypotheses.csv,
agreement.csv, report.md. Production --final requires the G3-bound inputs.
Complete preliminary analyses also save scoring_inputs.json for reproducible G2 selection.

Definitions follow the frozen protocol:
    precision_a = #S2 explicit pairs / #explicit pairs (0 without explicit citations)
    recall_a    = #unique claims with >= 1 explicit S2 / #all unique factual claims
    correct_a   = 1 if correctness == 2 else 0
    key_fact_coverage_a = key_facts_supported / n_key_facts (key facts stated AND backed by an S2 citation)
    Primary system value = mean over cases of first runs; repeats are a separate matched sensitivity analysis.
    95 % CI: cluster bootstrap over cases (10 000 resamples, seed 2026); Wilson for binary shares.

Usage:
    See HANDOFF.md for private G1/G2 exploratory and G3 final commands.
    python3 scripts/make_demo_data.py  # disposable, synthetic integration test
"""

import argparse
import collections
import copy
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    PROMPTS,
    RATINGS,
    ROOT,
    SYSTEMS,
    constraint_problems,
    diagnostic_problems,
    finite_number,
    key_fact_problems,
    load_all_cases,
    read_csv,
    read_csv_glob,
    run_problems,
    sha256_file,
    unique_index,
    validate_pair_rows,
    write_csv,
)
from integrity import (
    private_path,
    run_artifact_problems,
    verify_freeze,
    verify_plans,
    write_json_new,
)
from replay_paths import configure_path_map, resolve_input


# ----------------------------------------------------------------- statistics helpers
def mean(xs):
    xs = [x for x in xs if x is not None]
    # Built-in sum's float algorithm changed in Python 3.12. Keep threshold
    # decisions and replay aggregates independent of that runtime difference.
    return math.fsum(xs) / len(xs) if xs else None


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def bootstrap_ci(case_values, B, seed):
    """case_values: dict case -> value. Returns (point, lo, hi)."""
    vals = [v for v in case_values.values() if v is not None]
    if not vals:
        return None, None, None
    point = mean(vals)
    if len(vals) == 1:
        return point, None, None
    rng = random.Random(seed)
    n = len(vals)
    boots = []
    for _ in range(B):
        boots.append(math.fsum(vals[rng.randrange(n)] for _ in range(n)) / n)
    return point, quantile(boots, 0.025), quantile(boots, 0.975)


def wilson(k, n, z=1.959964):
    if n == 0:
        return None, None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_diagnostic(values):
    values = [v for v in values.values() if v is not None]
    if len(values) < 2:
        return "insufficient_cases"
    return "constant_empirical_sample" if max(values) == min(values) else "ok"


def attribution_summary(items):
    explicit = [a for a in items if a["n_pairs"] > 0]
    return {
        "explicit_answer_share": len(explicit) / len(items) if items else None,
        "explicit_answer_n": len(explicit),
        "precision_given_explicit": mean([a["precision"] for a in explicit]),
        "precision_given_explicit_n": len(explicit),
    }


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None, None
    labels = sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[label] * cb[label] for label in labels) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else None
    return kappa, po


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r

    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = mean(rx), mean(ry)
    num = math.fsum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(
        math.fsum((a - mx) ** 2 for a in rx) * math.fsum((b - my) ** 2 for b in ry)
    )
    return num / den if den else None


def fnum(x, pct=False, digits=3):
    if x is None or x == "":
        return ""
    return f"{x * 100:.1f}" if pct else f"{x:.{digits}f}"


def to_float(s):
    return finite_number(s)


# ----------------------------------------------------------------- loading
def load_answers(runs, key, pairs, answers, cases, allow_missing, meta=None):
    meta = meta or {}
    run_by_id = unique_index(runs, "run_id", "runs")
    key_by_bid = unique_index(key, "blind_answer_id", "blind key")
    unique_index(key, "run_id", "blind key")
    validate_pair_rows(pairs, "final pairs")
    answer_by_bid = unique_index(answers, "blind_answer_id", "final answers")
    bid_to_run = {b: k["run_id"] for b, k in key_by_bid.items()}
    run_to_bid = {k["run_id"]: b for b, k in key_by_bid.items()}
    pairs_by_bid = collections.defaultdict(list)
    problems = []
    invalid_bids = set()
    for p in pairs:
        bid = p.get("blind_answer_id", "")
        cit = (p.get("citation_n") or "").strip()
        rating = (p.get("rating") or "").strip().upper()
        if cit != "" and rating not in RATINGS:
            problems.append(
                f"pair {p.get('pair_id')}: rating {rating!r} not in {sorted(RATINGS)}"
            )
            invalid_bids.add(bid)
        if bid not in answer_by_bid:
            problems.append(f"pair {p.get('pair_id')}: no answer-level row")
        p["_rating"] = rating
        p["_cit"] = cit
        pairs_by_bid[bid].append(p)
    for bid in answer_by_bid:
        if bid_to_run.get(bid) not in run_by_id:
            problems.append(f"answer {bid}: no run metadata (check blind_key / runs)")
    for bid, rid in bid_to_run.items():
        if rid not in run_by_id:
            problems.append(f"blind key {bid}: unknown run_id {rid}")

    out = []
    cells = set()
    for run in runs:
        errors = run_problems(run)
        problems.extend(f"run {run['run_id']}: {e}" for e in errors)
        if errors or run.get("run_status") == "excluded":
            continue
        cell = (
            run["split"],
            run["task_id"],
            run["condition"],
            run["system"],
            int(to_float(run["run_index"])),
        )
        if cell in cells:
            raise ValueError(f"duplicate run matrix cell: {cell}")
        cells.add(cell)
        bid = run_to_bid.get(run["run_id"], "")
        failed = run["run_status"] == "failed"
        a = answer_by_bid.get(bid, {})
        if not a and not failed:
            problems.append(f"run {run['run_id']}: missing key or answer-level rating")
            continue
        if bid in invalid_bids and not failed:
            continue  # Never improve precision by discarding just an unrated citation.
        corr = (a.get("correctness") or "").strip()
        if failed:
            corr = "0"  # Predefined operational failure, not an invented model answer.
        elif corr not in {"0", "1", "2"}:
            problems.append(f"answer {bid}: correctness {corr!r} not in 0/1/2")
            continue
        rows = [] if failed else pairs_by_bid.get(bid, [])
        unlinked = [p for p in rows if p["_cit"] == "*" and p["_rating"] in RATINGS]
        cited = [
            p for p in rows if p["_cit"] not in {"", "*"} and p["_rating"] in RATINGS
        ]
        claims = sorted({p["claim_id"] for p in rows})
        supported = {p["claim_id"] for p in cited if p["_rating"] == "S2"}
        s2 = sum(1 for p in cited if p["_rating"] == "S2")
        non_na = [p for p in cited if p["_rating"] != "NA"]
        case = cases.get(run["task_id"], {})
        if not case:
            problems.append(f"run {run['run_id']}: unknown task_id")
            continue
        constraint_errors = (
            []
            if failed
            else constraint_problems(a, case) + diagnostic_problems(a, rows, case)
        )
        if constraint_errors:
            problems.extend(f"answer {bid}: {e}" for e in constraint_errors)
            continue
        kf, nkf = to_float(a.get("key_facts_supported")), to_float(a.get("n_key_facts"))
        minutes = to_float(a.get("check_minutes"))
        if not failed and (
            kf is None
            or nkf is None
            or nkf < 1
            or not nkf.is_integer()
            or not kf.is_integer()
            or not 0 <= kf <= nkf
            or minutes is None
            or minutes < 0
        ):
            problems.append(f"answer {bid}: invalid key-fact counts or check_minutes")
            continue
        if not failed:
            fact_errors = key_fact_problems(a, case, rows)
            if fact_errors:
                problems.extend(f"answer {bid}: {e}" for e in fact_errors)
                continue
        declared_claims = to_float(a.get("n_claims"))
        if not failed and (
            declared_claims is None
            or declared_claims != len(claims)
            or a.get("segmentation_reviewed") != "yes"
        ):
            problems.append(
                f"answer {bid}: n_claims does not match final segmentation or human review is missing"
            )
            continue
        out.append(
            {
                "bid": bid,
                "run_id": run["run_id"],
                "system": run["system"],
                "run_status": run["run_status"],
                "failure_type": run.get("failure_type", ""),
                "condition": run["condition"],
                "split": run["split"],
                "task_id": run["task_id"],
                "run_index": int(to_float(run["run_index"])),
                "language": "en"
                if case.get("language", run.get("language")) == "en"
                else "cs",
                "edge": case.get("edge_case_type", ""),
                "precision": s2 / len(cited) if cited else 0.0,
                "precision_noNA": (
                    sum(1 for p in non_na if p["_rating"] == "S2") / len(non_na)
                )
                if non_na
                else None,
                "recall": len(supported) / len(claims) if claims else 0.0,
                "correct": 1 if corr == "2" else 0 if corr in {"0", "1"} else None,
                "ack": (a.get("acknowledges_uncertainty") or "").strip().lower(),
                "n_claims": len(claims),
                "n_pairs": len(cited),
                "n_fab": sum(1 for p in cited if p["_rating"] == "FAB"),
                "n_na": sum(1 for p in cited if p["_rating"] == "NA"),
                "n_unlinked": len(unlinked),
                "unlinked_support": sum(p["_rating"] == "S2" for p in unlinked)
                / len(unlinked)
                if unlinked
                else None,
                "n_tier1": sum(
                    1 for p in cited if (p.get("source_tier") or "").strip() == "1"
                ),
                "n_tier_checked": sum(
                    1 for p in cited if p.get("source_tier") in {"1", "2", "3"}
                ),
                "n_time_expected": len(cited)
                if case.get("edge_case_type") == "time_constraint"
                else 0,
                "n_time_checked": sum(
                    1
                    for p in cited
                    if (p.get("time_ok") or "").strip().lower() in {"yes", "no"}
                ),
                "n_time_ok": sum(
                    1
                    for p in cited
                    if (p.get("time_ok") or "").strip().lower() == "yes"
                ),
                "check_minutes": minutes,
                "kf_cov": 0.0 if failed else kf / nkf,
                "turns": to_float(run.get("turns")),
                "search_used": (run.get("search_used") or "").strip().lower(),
                "sources_shown": to_float(run.get("n_sources_shown")),
                "tool_calls": to_float(run.get("tool_calls_visible")),
                "format_valid": meta.get(bid, {}).get("format_valid", ""),
                "latency": to_float(run.get("latency_s")),
                "retries": to_float(run.get("retries")) or 0,
                "first_ok": (run.get("first_attempt_ok") or "").strip().lower(),
                "final_ok": run.get("final_attempt_ok", ""),
                "first_latency": to_float(run.get("first_attempt_latency_s")),
                "cost_note": run.get("cost_note", ""),
                "errors": [
                    code
                    for _, code in sorted(
                        {
                            (p["claim_id"], p.get("error_code", "").strip())
                            for p in rows
                            if p.get("error_code", "").strip()
                        }
                    )
                ],
                "prompt_file": run.get("prompt_file", ""),
            }
        )
    return out, problems


def test_matrix_problems(answers, cases, systems):
    """Confirmatory claims require the full prespecified, paired first-run matrix."""
    errors = []
    task_ids = {
        tid
        for tid, c in cases.items()
        if c.get("development_validation_test_split") == "test"
    }
    if len(cases) < 40 or len(task_ids) < 10:
        errors.append("requires >= 40 cases including >= 10 held-out test cases")
    if len(systems) < 4 or len(set(systems)) != len(systems):
        errors.append("requires >= 4 distinct prespecified systems")
    expected = {
        (t, s, c) for t in task_ids for s in systems for c in ("P1", "P2", "P3")
    }
    observed = {
        (a["task_id"], a["system"], a["condition"])
        for a in answers
        if a["split"] == "test" and a["run_index"] == 1
    }
    if expected != observed:
        errors.append(
            f"incomplete first-run matrix: {len(expected - observed)} missing, {len(observed - expected)} unexpected cells"
        )
    return errors


def repeat_summary(items):
    """Compare like with like, including in a prespecified repeat subset."""
    indices = sorted({a["run_index"] for a in items})
    tasks = [{a["task_id"] for a in items if a["run_index"] == i} for i in indices]
    common = set.intersection(*tasks) if len(tasks) >= 2 else set()
    matched = [a for a in items if a["task_id"] in common]
    per_run = [
        mean(
            list(
                case_values(
                    [a for a in matched if a["run_index"] == i], "precision"
                ).values()
            )
        )
        for i in indices
    ]
    values = [v for v in per_run if v is not None]
    by_case = collections.defaultdict(set)
    for a in matched:
        by_case[a["task_id"]].add(a["correct"])
    flips = sum(len(v) > 1 for v in by_case.values())
    return (
        values,
        statistics.stdev(values) if len(values) > 1 else None,
        flips / len(common) if common else None,
        len(common),
    )


def case_values(answers, metric):
    by_case = collections.defaultdict(list)
    for a in answers:
        v = a[metric]
        if v is not None:
            by_case[a["task_id"]].append(v)
    return {c: mean(v) for c, v in by_case.items() if v}


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "runs", "run_plan_*.csv"))
    ap.add_argument("--annotation-dir", default=os.path.join(ROOT, "annotation"))
    ap.add_argument("--key-dir", default=os.path.join(ROOT, "annotation_key"))
    ap.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    ap.add_argument("--test-file", help="private holdout matching G2/G3")
    ap.add_argument("--freeze", help="G1/G2 for exploratory analysis, G3 for --final")
    ap.add_argument(
        "--final",
        action="store_true",
        help="requires verified G3; enables confirmatory decisions",
    )
    ap.add_argument(
        "--path-map",
        help="read-only G3 replay: relocate original repo/private prefixes without rewriting artifacts",
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument(
        "--synthetic",
        action="store_true",
        help="local DEMO-* fixtures; never confirms real hypotheses",
    )
    ap.add_argument("--prompts-dir", default=PROMPTS)
    ap.add_argument("--out", default=os.path.join(ROOT, "results"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--focus", default="perplexity", help="system tested in H1")
    ap.add_argument(
        "--systems",
        default=",".join(SYSTEMS),
        help="prespecified systems (never inferred from successful answers)",
    )
    ap.add_argument("--h1-margin", type=float, default=0.10)
    ap.add_argument("--h2-margin", type=float, default=0.05)
    ap.add_argument(
        "--allow-missing",
        action="store_true",
        help="exploratory only: exclude WHOLE incomplete answers; never confirm hypotheses",
    )
    args = ap.parse_args()
    if args.boot < 1:
        ap.error("--boot must be positive")
    if args.final and (args.synthetic or args.pilot or args.allow_missing):
        ap.error("--final cannot be combined with synthetic/pilot/allow-missing modes")
    if args.path_map and not args.final:
        ap.error(
            "--path-map is only allowed for --final replay, never collecting or sealing new runs"
        )
    try:
        configure_path_map(args.path_map, ROOT)
    except (ValueError, OSError, TypeError) as e:
        ap.error(str(e))
    expected_systems = [s.strip() for s in args.systems.split(",") if s.strip()]

    ad = args.annotation_dir

    def collect(name, root=None):
        """Read every file with this name under a dir tree (e.g. annotation/dev, annotation/test)."""
        rows = []
        for base, _, files in sorted(os.walk(resolve_input(root or ad))):
            if name in files:
                rows.extend(read_csv(os.path.join(base, name)))
        return rows

    runs = read_csv_glob(args.runs)
    key = collect("blind_key.csv", args.key_dir) or collect("blind_key.csv")
    meta = unique_index(
        collect("answers_meta.csv", args.key_dir) or collect("answers_meta.csv"),
        "blind_answer_id",
        "answers meta",
    )
    pairs = collect("pairs_rated.csv")
    answers_raw = collect("answers_rated.csv")
    input_tables = copy.deepcopy(
        {
            "runs": runs,
            "key": key,
            "pairs": pairs,
            "answers": answers_raw,
            "meta": list(meta.values()),
        }
    )
    if not runs:
        raise SystemExit("no run metadata found")
    try:
        if not args.synthetic:
            for path in (args.out, args.annotation_dir, args.key_dir):
                private_path(path)
            if not args.pilot:
                gate = verify_freeze(args.freeze, "G3" if args.final else None)
                if any(r.get("split") == "test" for r in runs) and gate["gate"] == "G1":
                    raise ValueError("test analysis requires G2 or G3")
                cfg = gate["config"]
                if (
                    args.systems != ",".join(SYSTEMS)
                    and expected_systems != cfg["systems"]
                ):
                    raise ValueError("systems differ from frozen config")
                if (
                    args.boot,
                    args.seed,
                    args.focus,
                    args.h1_margin,
                    args.h2_margin,
                ) != (
                    cfg["bootstrap"],
                    cfg["seed"],
                    cfg["focus"],
                    cfg["h1_margin"],
                    cfg["h2_margin"],
                ):
                    raise ValueError("analysis parameters differ from frozen config")
                expected_systems = cfg["systems"]
                if (
                    os.path.realpath(args.data_dir) != os.path.join(ROOT, "data")
                    or os.path.realpath(args.prompts_dir) != PROMPTS
                ):
                    raise ValueError(
                        "real analysis must use frozen repository data/prompts"
                    )
                if args.test_file and os.path.realpath(
                    resolve_input(args.test_file)
                ) != os.path.realpath(resolve_input(gate["inputs"]["test_cases"])):
                    raise ValueError("holdout differs from freeze")
                args.test_file = (
                    gate["inputs"]["test_cases"]
                    if any(r.get("split") == "test" for r in runs)
                    else None
                )
            paths = verify_plans(args.runs, args.freeze, args.synthetic, args.pilot)
            for r in runs:
                errors = run_artifact_problems(r)
                if errors:
                    raise ValueError(f"{r['run_id']}: " + "; ".join(errors))
            if args.final and (
                set(map(os.path.realpath, paths))
                != {
                    os.path.realpath(resolve_input(p))
                    for p in gate["inputs"]["run_plans"]
                }
                or any(
                    os.path.realpath(resolve_input(p))
                    != os.path.realpath(resolve_input(gate["inputs"][k]))
                    for p, k in (
                        (args.annotation_dir, "annotation_dir"),
                        (args.key_dir, "key_dir"),
                    )
                )
            ):
                raise ValueError(
                    "final analysis must use exactly the G3-bound plans and ratings"
                )
        else:
            verify_plans(args.runs, synthetic=True)
            if any(
                not r["task_id"].startswith("DEMO-")
                or not r["system"].startswith("sys_")
                for r in runs
            ):
                raise ValueError("synthetic mode accepts only anonymous DEMO-* runs")
        cases = load_all_cases(args.data_dir, args.test_file)
        if args.synthetic and any(
            "synthetic" not in c.get("source_or_provenance", "").lower()
            for c in cases.values()
        ):
            raise ValueError("synthetic cases must declare their provenance")
        A, problems = load_answers(
            runs, key, pairs, answers_raw, cases, args.allow_missing, meta
        )
        for name, field in (
            ("pairs_rated_rater1.csv", "pair_id"),
            ("pairs_rated_rater2.csv", "pair_id"),
            ("answers_rated_rater1.csv", "blind_answer_id"),
            ("answers_rated_rater2.csv", "blind_answer_id"),
        ):
            unique_index(collect(name), field, name)
            if field == "pair_id":
                validate_pair_rows(collect(name), name)
    except (ValueError, OSError, KeyError) as e:
        raise SystemExit(str(e)) from e
    for p in problems[:30]:
        print("PROBLEM:", p)
    if problems and not args.allow_missing:
        raise SystemExit(
            f"{len(problems)} problem(s): unrated or unmatched rows. Fix the sheets, "
            "or rerun with --allow-missing to exclude them (the report will say so)."
        )
    if args.path_map and os.path.abspath(args.out) != os.path.abspath(
        resolve_input(args.out)
    ):
        ap.error(
            "--out must name the new physical output directory, not an original mapped path"
        )
    out_path = os.path.realpath(args.out)
    for directory in (args.annotation_dir, args.key_dir):
        source_path = os.path.realpath(resolve_input(directory))
        if out_path == source_path or out_path.startswith(source_path + os.path.sep):
            raise SystemExit(
                "analysis output must not modify bound annotation/key directories"
            )
    if any(
        os.path.lexists(os.path.join(args.out, n))
        for n in (
            "metrics.csv",
            "answer_metrics.csv",
            "hypotheses.csv",
            "agreement.csv",
            "report.md",
            "scoring_inputs.json",
            "replay_provenance.json",
        )
    ):
        raise SystemExit(
            "Refusing to overwrite analysis outputs; use a new versioned --out directory"
        )
    os.makedirs(args.out, exist_ok=True)
    if not args.final and not args.allow_missing:
        write_json_new(
            os.path.join(args.out, "scoring_inputs.json"),
            {
                "schema_version": 1,
                "kind": "scoring_input_snapshot",
                "tables": input_tables,
                "freeze": {
                    "path": private_path(args.freeze),
                    "sha256": sha256_file(args.freeze),
                }
                if not args.synthetic and not args.pilot
                else None,
                "mode": "synthetic"
                if args.synthetic
                else "pilot"
                if args.pilot
                else "preliminary",
            },
        )
    report = [
        "# Výsledky – citační benchmark",
        "",
        f"Plánovaných záznamů: {len(runs)}; v analýze: {len(A)}; provozních selhání zahrnutých s nulovým skóre: "
        f"{sum(a['run_status'] == 'failed' for a in A)}; vyloučených chyb obsluhy: "
        f"{sum(r.get('run_status') == 'excluded' for r in runs)}. Intervaly: klastrový bootstrap podle případů "
        f"({args.boot} převzorkování, seed {args.seed}); podíly odpovědí: Wilson (jen běh 1).",
        "",
    ]
    if not args.final:
        report += [
            "**SYNTETICKÉ LOKÁLNÍ TESTY – nikoli výsledky produktů.**"
            if args.synthetic
            else "**Předběžná / kalibrační analýza: G3 není použit, hypotézy nelze potvrzovat.**",
            "",
        ]
    elif gate.get("timing_deviations"):
        report += [
            "**Časové odchylky od protokolu:** "
            + "; ".join(gate["timing_deviations"])
            + ". Viz podepsaný záznam odchylek; výsledky nejsou plně protokolově konformní.",
            "",
        ]
    if problems:
        report += [
            f"**Upozornění:** {len(problems)} problémů ve vstupu; {len(runs) - len(A)} běhů mimo analýzu "
            "(--allow-missing). Výsledky nejsou finální.",
            "",
        ]
    if args.allow_missing:
        report += [
            "**Explorační režim --allow-missing: hypotézy nelze potvrzovat ani při úplné matici.**",
            "",
        ]
    report += [
        "Porovnání jednotlivých systémů mimo hypotézy H1 a H2 jsou **explorační**.",
        "",
    ]

    groups = collections.defaultdict(list)
    for a in A:
        groups[(a["split"], a["condition"], a["system"])].append(a)
    # Primary comparisons use first runs. Repeats are reported separately, not mixed into P2 only.
    groups = {k: [a for a in v if a["run_index"] == 1] for k, v in groups.items()}
    groups = {k: v for k, v in groups.items() if v}

    # ---------------- metrics table
    metrics = []
    for (split, cond, system), items in sorted(groups.items()):
        row = {
            "split": split,
            "condition": cond,
            "system": system,
            "n_cases": len({a["task_id"] for a in items}),
            "n_answers": len(items),
        }
        for m in (
            "precision",
            "recall",
            "precision_noNA",
            "kf_cov",
            "unlinked_support",
        ):
            p, lo, hi = bootstrap_ci(case_values(items, m), args.boot, args.seed)
            row[m], row[m + "_lo"], row[m + "_hi"] = p, lo, hi
            row[m + "_ci_diagnostic"] = bootstrap_diagnostic(case_values(items, m))
        row.update(attribution_summary(items))
        first = [a for a in items if a["run_index"] == 1 and a["correct"] is not None]
        p, lo, hi = wilson(sum(a["correct"] for a in first), len(first))
        row["correct_share"], row["correct_lo"], row["correct_hi"] = p, lo, hi
        p, lo, hi = wilson(sum(1 for a in first if a["n_fab"] > 0), len(first))
        (
            row["answers_with_fab"],
            row["answers_with_fab_lo"],
            row["answers_with_fab_hi"],
        ) = p, lo, hi
        npairs = sum(a["n_pairs"] for a in items)
        row["fab_rate"] = sum(a["n_fab"] for a in items) / npairs if npairs else None
        row["na_rate"] = sum(a["n_na"] for a in items) / npairs if npairs else None
        row["tier1_share"] = (
            sum(a["n_tier1"] for a in items) / npairs if npairs else None
        )
        row["source_tier_expected"] = npairs
        row["source_tier_checked"] = sum(a["n_tier_checked"] for a in items)
        all_pairs = npairs + sum(a["n_unlinked"] for a in items)
        row["unlinked_rate"] = (
            sum(a["n_unlinked"] for a in items) / all_pairs if all_pairs else None
        )
        tchk = sum(a["n_time_checked"] for a in items)
        row["time_expected"] = sum(a["n_time_expected"] for a in items)
        row["time_checked"] = tchk
        row["time_ok_share"] = (
            sum(a["n_time_ok"] for a in items) / tchk if tchk else None
        )
        unc = [
            a
            for a in items
            if a["edge"] in {"missing_info", "ambiguous"} and a["ack"] in {"yes", "no"}
        ]
        row["ack_uncertainty_share"] = (
            sum(1 for a in unc if a["ack"] == "yes") / len(unc) if unc else None
        )
        row["ack_expected"] = sum(
            a["run_status"] == "completed"
            and a["edge"] in {"missing_info", "ambiguous"}
            for a in items
        )
        row["ack_checked"] = len(unc)
        row["claims_per_answer"] = mean([a["n_claims"] for a in items])
        row["citations_per_answer"] = mean([a["n_pairs"] for a in items])
        lat = [a["latency"] for a in items if a["latency"] is not None]
        row["latency_median"] = statistics.median(lat) if lat else None
        row["latency_p90"] = quantile(lat, 0.9) if lat else None
        row["latency_n"] = len(lat)
        row["retry_rate"] = mean([1 if a["retries"] > 0 else 0 for a in items])
        fo = [a for a in items if a["first_ok"] in {"yes", "no"}]
        row["first_attempt_success"] = (
            sum(1 for a in fo if a["first_ok"] == "yes") / len(fo) if fo else None
        )
        row["final_attempt_success"] = mean(
            [1 if a["final_ok"] == "yes" else 0 for a in items]
        )
        row["first_latency_median"] = statistics.median(
            [a["first_latency"] for a in items]
        )
        row["n_failed"] = sum(a["run_status"] == "failed" for a in items)
        row["turns_mean"] = mean([a["turns"] for a in items])
        su = [a for a in items if a["search_used"] in {"yes", "no"}]
        row["search_used_share"] = (
            sum(1 for a in su if a["search_used"] == "yes") / len(su) if su else None
        )
        row["search_used_n"] = len(su)
        row["sources_shown_mean"] = mean([a["sources_shown"] for a in items])
        row["tool_calls_mean"] = mean([a["tool_calls"] for a in items])
        fv = [a for a in items if a["format_valid"] in {"yes", "no"}]
        row["format_valid_share"] = (
            sum(1 for a in fv if a["format_valid"] == "yes") / len(fv) if fv else None
        )
        cm = [a["check_minutes"] for a in items if a["check_minutes"] is not None]
        row["check_minutes_median"] = statistics.median(cm) if cm else None
        row["check_minutes_n"] = len(cm)
        metrics.append(row)

    # Exploratory annotation-effort index; preserve the historic utility CSV alias.
    # Fixed weights: precision - 0.1*L_norm - 0.1*T_norm, within split x condition.
    by_sc = collections.defaultdict(list)
    for r in metrics:
        by_sc[(r["split"], r["condition"])].append(r)
    for rows in by_sc.values():
        lat_vals = [r["latency_median"] for r in rows if r["latency_median"]]
        chk_vals = [
            r["check_minutes_median"] for r in rows if r["check_minutes_median"]
        ]
        lmax = max(lat_vals) if lat_vals else None
        tmax = max(chk_vals) if chk_vals else None
        for r in rows:
            if (
                r["precision"] is None
                or r["latency_median"] is None
                or r["check_minutes_median"] is None
                or not lmax
                or not tmax
            ):
                r["utility"] = (
                    None  # missing latency or check time -> no utility (never a free pass)
                )
            else:
                r["utility"] = (
                    r["precision"]
                    - 0.1 * r["latency_median"] / lmax
                    - 0.1 * r["check_minutes_median"] / tmax
                )
            r["annotation_effort_index"] = r[
                "utility"
            ]  # Keep the historic CSV alias for compatibility.
            dominated = any(
                o is not r
                and o["precision"] is not None
                and r["precision"] is not None
                and o["latency_median"] is not None
                and r["latency_median"] is not None
                and o["precision"] >= r["precision"]
                and o["latency_median"] <= r["latency_median"]
                and (
                    o["precision"] > r["precision"]
                    or o["latency_median"] < r["latency_median"]
                )
                for o in rows
            )
            r["pareto"] = (
                ""
                if r["precision"] is None or r["latency_median"] is None
                else "no"
                if dominated
                else "yes"
            )

    mfields = list(metrics[0].keys()) if metrics else []
    write_csv(
        os.path.join(args.out, "metrics.csv"),
        [
            {
                k: (fnum(v, digits=4) if isinstance(v, float) else v)
                for k, v in r.items()
            }
            for r in metrics
        ],
        mfields,
    )
    answer_fields = (
        [k for k in A[0] if k not in {"bid", "errors"}] + ["errors"]
        if A
        else ["run_id"]
    )
    write_csv(
        os.path.join(args.out, "answer_metrics.csv"),
        [dict(a, errors=";".join(a["errors"])) for a in A],
        answer_fields,
    )

    def ci(r, m, pct=True):
        p, lo, hi = r.get(m), r.get(m + "_lo"), r.get(m + "_hi")
        if p is None:
            return ""
        s = fnum(p, pct)
        if lo is not None and hi is not None:
            s += f" [{fnum(lo, pct)}–{fnum(hi, pct)}]"
        return s

    for split in ("test", "val", "dev"):
        rows = [r for r in metrics if r["split"] == split]
        if not rows:
            continue
        report += [
            f"## Sada: {split}",
            "",
            "| Podmínka | Systém | Případů | Odpovědí | Citační přesnost % [95% CI] | Úplnost citací % | Pokrytí kl. faktů % | Správnost odpovědi % (Wilson) | FAB % | NA % | Tvrzení/odp. | Vyhledávání % | 1. pokus OK % | Medián latence s | Explorační index | Pareto |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in rows:
            report.append(
                f"| {r['condition']} | {r['system']} | {r['n_cases']} | {r['n_answers']} | {ci(r, 'precision')} | "
                f"{ci(r, 'recall')} | {ci(r, 'kf_cov')} | {fnum(r['correct_share'], True)} [{fnum(r['correct_lo'], True)}–{fnum(r['correct_hi'], True)}] | "
                f"{fnum(r['fab_rate'], True)} | {fnum(r['na_rate'], True)} | {fnum(r['claims_per_answer'], digits=1)} | "
                f"{fnum(r['search_used_share'], True)} | {fnum(r['first_attempt_success'], True)} | "
                f"{fnum(r['latency_median'], digits=1)} | {fnum(r['utility'])} | {r['pareto']} |"
            )
        report.append("")

    report += [
        "## Diagnostiky atribuce a pokrytí kontrol",
        "",
        "H2 měří celý efekt P2 včetně explicitního přiřazení zdrojů: P1 seznam URL nevyžaduje atribuci ke tvrzení. "
        "Nejde o čistý efekt kvality retrieval/generation. Přesnost při alespoň jedné explicitní citaci je "
        "deskriptivní výsledek na vybrané podmnožině, ne náhradní hlavní metrika či další potvrzovací test.",
        "",
        "| Sada/podmínka | Systém | Odpovědi s explicitní citací (n/N) | Přesnost jen těchto odpovědí % | Tier kontrola n/expected | Čas n/expected | Nejistota n/expected |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in metrics:
        report.append(
            f"| {r['split']}/{r['condition']} | {r['system']} | {r['explicit_answer_n']}/{r['n_answers']} | "
            f"{fnum(r['precision_given_explicit'], True)} | {r['source_tier_checked']}/{r['source_tier_expected']} | "
            f"{r['time_checked']}/{r['time_expected']} | {r['ack_checked']}/{r['ack_expected']} |"
        )
    report += [
        "",
        "unknown se nepočítá mezi dokončené kontroly; jejich podíly proto číst vždy s n/expected. "
        "tier1_share používá všechny explicitní páry, včetně unknown (konzervativní podíl doložených tier1).",
        "",
        "**Nejistota:** konstantní empirický vzorek může dát bootstrap CI [p,p]; nejde o jistotu "
        "v populaci ani důkaz nulové variability. CSV *_ci_diagnostic / ci_diagnostic označují tuto degeneraci "
        "a nedostatek případů. Účelový malý vzorek a bootstrap nepostihují změny produktu, zdrojů ani nové domény.",
        "",
    ]

    report += [
        "## Provoz a lidská práce (první běhy)",
        "",
        "| Sada/podmínka | Systém | Selhání | 1. pokus OK % | Konečný pokus OK % | Opakování % | Latence medián/p90 s | Anotace medián min (n) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in metrics:
        report.append(
            f"| {r['split']}/{r['condition']} | {r['system']} | {r['n_failed']} | {fnum(r['first_attempt_success'], True)} | "
            f"{fnum(r['final_attempt_success'], True)} | {fnum(r['retry_rate'], True)} | "
            f"{fnum(r['latency_median'], digits=1)}/{fnum(r['latency_p90'], digits=1)} | {fnum(r['check_minutes_median'], digits=1)} ({r['check_minutes_n']}) |"
        )
    report += [
        "",
        "Latence zahrnuje čekání na retry; check_minutes je čas anotace dokončených odpovědí, ne uživatelský čas oprav. "
        "Explorační index = přesnost − 0,1×normovaná latence − 0,1×normovaný čas anotace; normalizace je vůči "
        "maximu mediánů v sadě/podmínce, závisí na zvolených systémech a vahách. CSV utility je pouze historický alias. "
        "Nejde o obecný užitek. Neznámá cena není nula; cost_note každého běhu je v answer_metrics.csv, "
        "předplatné, mezní náklad a čas týmu je nutné ve zprávě odlišit. Vyhledávání % má ve jmenovateli jen yes/no "
        "(počet search_used_n v metrics.csv), nikoli unknown/unclear.",
        "",
    ]

    # ---------------- hypotheses (held-out test split only)
    hyp = []
    test = [a for a in A if a["split"] == "test"]
    first_test = [a for a in test if a["run_index"] == 1]
    matrix_errors = test_matrix_problems(first_test, cases, expected_systems)
    confirmatory = args.final and not matrix_errors and not args.allow_missing

    def sys_case(cond, system, metric="precision"):
        return case_values(
            [a for a in first_test if a["condition"] == cond and a["system"] == system],
            metric,
        )

    systems = expected_systems
    report += ["## Hypotézy (testovací sada)", ""]
    if matrix_errors:
        report += [
            "**Hypotézy nelze vyhodnotit:** " + "; ".join(matrix_errors) + ".",
            "",
        ]
    if confirmatory and args.focus in systems:
        focus = sys_case("P2", args.focus)
        others = {s: sys_case("P2", s) for s in systems if s != args.focus}
        diffs = {}
        for c, v in focus.items():
            ov = [others[s][c] for s in others if c in others[s]]
            if ov:
                diffs[c] = v - mean(ov)
        p, lo, hi = bootstrap_ci(diffs, args.boot, args.seed)
        supported = p is not None and lo is not None and p >= args.h1_margin and lo > 0
        hyp.append(
            {
                "hypothesis": "H1",
                "comparison": f"{args.focus} − průměr ostatních, P2, přesnost",
                "estimate": fnum(p, digits=4),
                "ci_lo": fnum(lo, digits=4),
                "ci_hi": fnum(hi, digits=4),
                "n_cases": len(diffs),
                "criterion": f">= {args.h1_margin} a CI nad 0",
                "ci_diagnostic": bootstrap_diagnostic(diffs),
                "ci_above_margin": "yes"
                if lo is not None and lo >= args.h1_margin
                else "no",
                "supported": "yes" if supported else "no",
            }
        )
    else:
        report.append(
            "H1 není potvrzována: nutný G3 finální režim, úplná testová matice a předem určený focus."
        )

    if confirmatory:
        per_sys, case_diffs = {}, collections.defaultdict(list)
        for s in systems:
            p1, p2 = sys_case("P1", s), sys_case("P2", s)
            d = {c: p2[c] - p1[c] for c in p2 if c in p1}
            if d:
                per_sys[s] = bootstrap_ci(d, args.boot, args.seed)
                for c, v in d.items():
                    case_diffs[c].append(v)
        avg = {c: mean(v) for c, v in case_diffs.items()}
        p, lo, hi = bootstrap_ci(avg, args.boot, args.seed)
        improved = sum(
            1 for s, (pt, _, _) in per_sys.items() if pt is not None and pt > 0
        )
        need = len(systems) - 1  # 4 of 5 systems; 3 of 4 in the lean variant
        supported = (
            p is not None
            and lo is not None
            and p >= args.h2_margin
            and lo > 0
            and improved >= need
        )
        hyp.append(
            {
                "hypothesis": "H2",
                "comparison": "P2 − P1, průměr přes systémy, přesnost",
                "estimate": fnum(p, digits=4),
                "ci_lo": fnum(lo, digits=4),
                "ci_hi": fnum(hi, digits=4),
                "n_cases": len(avg),
                "criterion": f">= {args.h2_margin}, CI nad 0 a zlepšení u >= {need} systémů (zlepšeno: {improved}/{len(per_sys)})",
                "ci_diagnostic": bootstrap_diagnostic(avg),
                "ci_above_margin": "yes"
                if lo is not None and lo >= args.h2_margin
                else "no",
                "supported": "yes" if supported else "no",
            }
        )
    for name in ("H1", "H2"):
        if not any(h["hypothesis"] == name for h in hyp):
            hyp.append(
                {
                    "hypothesis": name,
                    "comparison": "",
                    "estimate": "",
                    "ci_lo": "",
                    "ci_hi": "",
                    "n_cases": 0,
                    "criterion": "; ".join(matrix_errors)
                    or "G3 final mode required or missing focus system",
                    "ci_above_margin": "not_evaluable",
                    "supported": "not_evaluable",
                }
            )

    write_csv(
        os.path.join(args.out, "hypotheses.csv"),
        hyp,
        [
            "hypothesis",
            "comparison",
            "estimate",
            "ci_lo",
            "ci_hi",
            "n_cases",
            "criterion",
            "ci_diagnostic",
            "ci_above_margin",
            "supported",
        ],
    )
    if hyp:
        report += [
            "| Hypotéza | Porovnání | Odhad | 95% CI | Případů | Kritérium | Podpořena |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for h in hyp:
            report.append(
                f"| {h['hypothesis']} | {h['comparison']} | {h['estimate']} | {h['ci_lo']}–{h['ci_hi']} | "
                f"{h['n_cases']} | {h['criterion']} | {h['supported']} |"
            )
        report.append("")
    report += [
        "Podpora podle předem daného pravidla (bodový odhad ≥ margin a CI nad 0) **nedokazuje**, že skutečný rozdíl "
        "dosahuje alespoň margin. Silnější otázku odděleně zachycuje ci_above_margin (dolní mez CI ≥ margin); "
        "tato diagnostika nenahrazuje původní kritérium H1/H2.",
        "",
    ]

    # ---------------- prompt portability
    if test:
        report += [
            "## Přenositelnost promptů (testovací sada, rozdíl citační přesnosti v p. b.)",
            "",
            "| Systém | P2 − P1 [95% CI] | P3 − P1 [95% CI] | P3 − P2 [95% CI] |",
            "| --- | --- | --- | --- |",
        ]
        agg = {
            "P2-P1": collections.defaultdict(list),
            "P3-P1": collections.defaultdict(list),
            "P3-P2": collections.defaultdict(list),
        }
        for s in systems:
            cells = []
            for a_, b_ in (("P2", "P1"), ("P3", "P1"), ("P3", "P2")):
                x, y = sys_case(a_, s), sys_case(b_, s)
                d = {c: x[c] - y[c] for c in x if c in y}
                for c, v in d.items():
                    agg[f"{a_}-{b_}"][c].append(v)
                pt, lo, hi = bootstrap_ci(d, args.boot, args.seed)
                cells.append(
                    ""
                    if pt is None
                    else f"{fnum(pt, True)} [{fnum(lo, True)}–{fnum(hi, True)}]"
                )
            report.append(f"| {s} | " + " | ".join(cells) + " |")
        avg_cells = []
        for k in ("P2-P1", "P3-P1", "P3-P2"):
            pt, lo, hi = bootstrap_ci(
                {c: mean(v) for c, v in agg[k].items()}, args.boot, args.seed
            )
            avg_cells.append(
                ""
                if pt is None
                else f"{fnum(pt, True)} [{fnum(lo, True)}–{fnum(hi, True)}]"
            )
        report.append("| **průměr** | " + " | ".join(avg_cells) + " |")
        lengths = []
        for pf in sorted({a["prompt_file"] for a in test if a["prompt_file"]}):
            path = os.path.join(args.prompts_dir, pf)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    lengths.append(f"{pf}: {len(f.read())} znaků")
        report += [
            "",
            "Délka promptů (bez otázky): " + "; ".join(lengths) if lengths else "",
            "",
        ]

    # ---------------- alternative explanations
    if test:
        report += ["## Kontrola alternativních vysvětlení", ""]
        xs = [a["n_claims"] for a in first_test]
        ys = [a["precision"] for a in first_test]
        rho = spearman(xs, ys)
        report.append(
            f"A1 – Spearmanova korelace počtu tvrzení a přesnosti (test, první běhy): {fnum(rho)} "
            f"(n = {len(xs)}). Pouze deskriptivní: systémy, podmínky i případy jsou smíšené; nejde o důkaz příčiny."
        )
        report += [
            "",
            "A2 – citační přesnost podle jazyka dotazu (test, P2, %):",
            "",
            "| Systém | CZ | EN |",
            "| --- | --- | --- |",
        ]
        for s in systems:
            cz = mean(
                list(
                    case_values(
                        [
                            a
                            for a in first_test
                            if a["system"] == s
                            and a["condition"] == "P2"
                            and a["language"] == "cs"
                        ],
                        "precision",
                    ).values()
                )
            )
            en = mean(
                list(
                    case_values(
                        [
                            a
                            for a in first_test
                            if a["system"] == s
                            and a["condition"] == "P2"
                            and a["language"] == "en"
                        ],
                        "precision",
                    ).values()
                )
            )
            report.append(f"| {s} | {fnum(cz, True)} | {fnum(en, True)} |")
        report += [
            "",
            "CZ a EN nejsou párované překlady týchž otázek a mohou se lišit doménou/obtížností; "
            "tabulka je deskriptivní, nikoli důkaz jazykové příčiny. cs+en je zahrnuto do CZ.",
            "",
        ]

    # ---------------- run-to-run variability (test, P2, run_index 1..3)
    rep = [a for a in test if a["condition"] == "P2"]
    if rep and len({a["run_index"] for a in rep}) > 1:
        report += [
            "## Variabilita mezi běhy (test, P2)",
            "",
            "| Systém | Společných případů | Přesnost po bězích % | SD (p. b.) | Podíl případů se změnou správnosti |",
            "| --- | --- | --- | --- | --- |",
        ]
        for s in systems:
            items = [a for a in rep if a["system"] == s]
            per_run, sd, flips, total = repeat_summary(items)
            report.append(
                f"| {s} | {total} | {' / '.join(fnum(x, True) for x in per_run)} | {fnum(sd, True)} | "
                f"{fnum(flips, True)} |"
            )
        report += [
            "",
            "Opakování probíhají v pozdějším okně: variabilita směšuje náhodnost, změnu zdrojů i produktu; "
            "není čistým odhadem vnitřní stochastičnosti modelu.",
            "",
        ]

    # ---------------- error codes
    codes = collections.defaultdict(collections.Counter)
    for a in A:
        for e in a["errors"]:
            codes[a["system"]][e] += 1
    if codes:
        all_codes = sorted(
            {c for cnt in codes.values() for c in cnt}, key=lambda x: (len(x), x)
        )
        report += [
            "## Kódy chyb (všechny sady)",
            "",
            "| Systém | " + " | ".join(all_codes) + " |",
            "| --- | " + " | ".join("---" for _ in all_codes) + " |",
        ]
        for s in sorted(codes):
            report.append(
                f"| {s} | "
                + " | ".join(str(codes[s].get(c, 0)) for c in all_codes)
                + " |"
            )
        report.append("")

    # ---------------- inter-rater agreement (rater 1 BEFORE reconciliation vs rater 2)
    agr = []
    pairs1_raw = collect("pairs_rated_rater1.csv")
    answers1_raw = collect("answers_rated_rater1.csv")
    pairs2 = collect("pairs_rated_rater2.csv")
    answers2 = collect("answers_rated_rater2.csv")
    if pairs2 and not pairs1_raw:
        report += [
            "**Shoda dvojic nedostupná:** chybí nezávislé hodnocení rater1 před smířením.",
            "",
        ]
    if answers2 and not answers1_raw:
        report += [
            "**Shoda odpovědí nedostupná:** chybí nezávislé hodnocení rater1 před smířením.",
            "",
        ]
    if pairs2 and pairs1_raw:
        signatures = []
        for rows in (pairs1_raw, pairs2):
            sig = collections.defaultdict(set)
            for p in rows:
                sig[p["blind_answer_id"]].add(
                    (
                        p["pair_id"],
                        p["claim_id"],
                        p.get("claim_text", ""),
                        p.get("citation_n", ""),
                    )
                )
            signatures.append(sig)
        incompatible = {
            b for b in signatures[1] if signatures[0].get(b) != signatures[1][b]
        }
        if incompatible:
            report += [
                f"**Nesrovnatelná segmentace:** {len(incompatible)} dvojitě hodnocených odpovědí mimo kappu dvojic; "
                "nejprve sjednotit jednotky bez znalosti ratingů a provést nové nezávislé hodnocení.",
                "",
            ]
        r1 = {
            p["pair_id"]: (p.get("rating") or "").strip().upper()
            for p in pairs1_raw
            if (p.get("citation_n") or "").strip() not in {"", "*"}
        }
        r2 = {
            p["pair_id"]: (p.get("rating") or "").strip().upper()
            for p in pairs2
            if (p.get("citation_n") or "").strip() not in {"", "*"}
            and p["blind_answer_id"] not in incompatible
        }
        common = [k for k in r2 if k in r1 and r1[k] in RATINGS and r2[k] in RATINGS]
        a_, b_ = [r1[k] for k in common], [r2[k] for k in common]
        k5, po5 = cohen_kappa(a_, b_)
        kb, pob = cohen_kappa(
            ["S2" if x == "S2" else "other" for x in a_],
            ["S2" if x == "S2" else "other" for x in b_],
        )
        agr.append(
            {
                "measure": "explicit pairs S2 vs other",
                "n": len(common),
                "kappa": fnum(kb),
                "agreement": fnum(pob),
            }
        )
        agr.append(
            {
                "measure": "explicit pairs 5 categories",
                "n": len(common),
                "kappa": fnum(k5),
                "agreement": fnum(po5),
            }
        )

        # segmentation agreement: number of claims per answer
        def n_claims(rows):
            out = collections.defaultdict(set)
            for p in rows:
                out[p["blind_answer_id"]].add(p["claim_id"])
            return {b: len(c) for b, c in out.items()}

        c1n, c2n = n_claims(pairs1_raw), n_claims(pairs2)
        both = [b for b in c2n if b in c1n]
        if both:
            mad = sum(abs(c1n[b] - c2n[b]) for b in both) / len(both)
            same = sum(1 for b in both if c1n[b] == c2n[b]) / len(both)
            agr.append(
                {
                    "measure": "segmentation: mean abs. difference in claims (r1 vs r2)",
                    "n": len(both),
                    "kappa": "",
                    "agreement": fnum(mad),
                }
            )
            agr.append(
                {
                    "measure": "segmentation: same number of claims",
                    "n": len(both),
                    "kappa": "",
                    "agreement": fnum(same),
                }
            )
    if answers2 and answers1_raw:
        c1 = {
            a["blind_answer_id"]: (a.get("correctness") or "").strip()
            for a in answers1_raw
        }
        c2 = {
            a["blind_answer_id"]: (a.get("correctness") or "").strip() for a in answers2
        }
        common = [
            k
            for k in c2
            if k in c1 and c1[k] in {"0", "1", "2"} and c2[k] in {"0", "1", "2"}
        ]
        k3, po3 = cohen_kappa([c1[k] for k in common], [c2[k] for k in common])
        agr.append(
            {
                "measure": "answer correctness 0-2",
                "n": len(common),
                "kappa": fnum(k3),
                "agreement": fnum(po3),
            }
        )

    # ---------------- validation of the automated number/name match against human S2 (dev split)
    split_of = {a["bid"]: a["split"] for a in A}
    auto_checks = unique_index(
        collect("pairs_auto_checks.csv", args.key_dir), "pair_id", "automated checks"
    )
    auto = [
        (
            to_float(auto_checks.get(p["pair_id"], {}).get("auto_match_ratio")),
            p["_rating"],
        )
        for p in pairs
        if p.get("_cit") not in (None, "", "*")
        and p.get("_rating") in RATINGS
        and to_float(auto_checks.get(p["pair_id"], {}).get("auto_match_ratio"))
        is not None
        and split_of.get(p["blind_answer_id"]) == "dev"
    ]
    if auto:
        flag = ["S2" if r >= 0.8 else "other" for r, _ in auto]
        human = ["S2" if h == "S2" else "other" for _, h in auto]
        ka, pa = cohen_kappa(flag, human)
        tp = sum(1 for f, h in zip(flag, human) if f == h == "S2")
        prec = tp / flag.count("S2") if flag.count("S2") else None
        rec = tp / human.count("S2") if human.count("S2") else None
        agr.append(
            {
                "measure": "auto match>=0.8 vs human S2 (dev)",
                "n": len(auto),
                "kappa": fnum(ka),
                "agreement": f"{fnum(pa)} (precision {fnum(prec)}, recall {fnum(rec)})",
            }
        )

    write_csv(
        os.path.join(args.out, "agreement.csv"),
        agr,
        ["measure", "n", "kappa", "agreement"],
    )
    if agr:
        report += [
            "## Shoda hodnotitelů a validace automatiky",
            "",
            "| Míra | n | Cohenova kappa | Shoda / hodnota |",
            "| --- | --- | --- | --- |",
        ]
        for g in agr:
            report.append(
                f"| {g['measure']} | {g['n']} | {g['kappa']} | {g['agreement']} |"
            )
        report += [
            "",
            "Cíl protokolu: kappa (S2 vs ostatní) alespoň 0,6. Automatická shoda je pouze "
            "deskriptivní post-rating diagnostika u správce dat; nikdy podklad nezávislého ratingu ani důkaz S2.",
            "",
        ]

    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    if args.path_map:
        write_json_new(
            os.path.join(args.out, "replay_provenance.json"),
            {
                "schema_version": 1,
                "kind": "derived_G3_replay_not_new_approval",
                "parent_g3_sha256": sha256_file(args.freeze),
                "path_map_sha256": sha256_file(args.path_map),
                "outputs": {
                    name: sha256_file(os.path.join(args.out, name))
                    for name in (
                        "metrics.csv",
                        "answer_metrics.csv",
                        "hypotheses.csv",
                        "agreement.csv",
                        "report.md",
                    )
                },
            },
        )
    print(
        f"{len(A)} answers scored -> {args.out}/metrics.csv, hypotheses.csv, agreement.csv, report.md"
    )


if __name__ == "__main__":
    main()
