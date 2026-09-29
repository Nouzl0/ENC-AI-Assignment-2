#!/usr/bin/env python3
"""Compute metrics, uncertainty, hypothesis tests and rater agreement.

Inputs (all CSV):
    runs/run_plan_*.csv             filled run metadata (system, condition, latency, ...)
    annotation_key/blind_key.csv, answers_meta.csv   blind_answer_id -> run_id (data steward)
    annotation/<phase>/pairs_rated.csv       final claim-citation ratings (after disagreements resolved)
    annotation/<phase>/answers_rated.csv     final answer-level ratings (correctness 0-2, key facts, minutes)
    annotation/<phase>/pairs_rated_rater1.csv, answers_rated_rater1.csv  rater 1 BEFORE reconciliation
    annotation/<phase>/pairs_rated_rater2.csv, answers_rated_rater2.csv  rater 2 (25 % subset)

Outputs (results/): metrics.csv, hypotheses.csv, agreement.csv, report.md

Definitions follow the frozen protocol:
    precision_a = #S2 pairs / #pairs in answer a (0 if the answer has no citation)
    recall_a    = #claims with >= 1 S2 citation / #claims in answer a
    correct_a   = 1 if correctness == 2 else 0
    key_fact_coverage_a = key_facts_supported / n_key_facts (key facts stated AND backed by an S2 citation)
    System value = mean over cases of the per-case mean over runs.
    95 % CI: cluster bootstrap over cases (10 000 resamples, seed 2026); Wilson for binary shares.

Usage:
    python3 scripts/score.py
    python3 scripts/score.py --runs "demo/runs/*.csv" --annotation-dir demo/annotation --out demo/results --focus sys_D
"""
import argparse
import collections
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROMPTS, RATINGS, ROOT, load_all_cases, read_csv, read_csv_glob, write_csv  # noqa: E402


# ----------------------------------------------------------------- statistics helpers
def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


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
    point = sum(vals) / len(vals)
    if len(vals) == 1:
        return point, None, None
    rng = random.Random(seed)
    n = len(vals)
    boots = []
    for _ in range(B):
        s = 0.0
        for _ in range(n):
            s += vals[rng.randrange(n)]
        boots.append(s / n)
    return point, quantile(boots, 0.025), quantile(boots, 0.975)


def wilson(k, n, z=1.959964):
    if n == 0:
        return None, None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None, None
    labels = sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
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
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def fnum(x, pct=False, digits=3):
    if x is None or x == "":
        return ""
    return f"{x * 100:.1f}" if pct else f"{x:.{digits}f}"


def to_float(s):
    try:
        return float(str(s).replace(",", "."))
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------- loading
def load_answers(runs, key, pairs, answers, cases, allow_missing, meta=None):
    meta = meta or {}
    run_by_id = {r["run_id"]: r for r in runs}
    bid_to_run = {k["blind_answer_id"]: k["run_id"] for k in key}
    pairs_by_bid = collections.defaultdict(list)
    problems = []
    for p in pairs:
        cit = (p.get("citation_n") or "").strip()
        rating = (p.get("rating") or "").strip().upper()
        if cit != "" and rating not in RATINGS:
            problems.append(f"pair {p.get('pair_id')}: rating {rating!r} not in {sorted(RATINGS)}")
            if not allow_missing:
                continue
        p["_rating"] = rating
        p["_cit"] = cit
        pairs_by_bid[p["blind_answer_id"]].append(p)

    out = []
    for a in answers:
        bid = a["blind_answer_id"]
        run = run_by_id.get(bid_to_run.get(bid, ""))
        if run is None:
            problems.append(f"answer {bid}: no run metadata (check blind_key / runs)")
            continue
        corr = (a.get("correctness") or "").strip()
        if corr not in {"0", "1", "2"}:
            problems.append(f"answer {bid}: correctness {corr!r} not in 0/1/2")
            if not allow_missing:
                continue
        rows = pairs_by_bid.get(bid, [])
        cited = [p for p in rows if p["_cit"] != "" and p["_rating"] in RATINGS]
        claims = sorted({p["claim_id"] for p in rows})
        supported = {p["claim_id"] for p in cited if p["_rating"] == "S2"}
        s2 = sum(1 for p in cited if p["_rating"] == "S2")
        non_na = [p for p in cited if p["_rating"] != "NA"]
        case = cases.get(run["task_id"], {})
        out.append({
            "bid": bid, "run_id": run["run_id"], "system": run["system"],
            "condition": run["condition"], "split": run["split"], "task_id": run["task_id"],
            "run_index": int(run.get("run_index") or 1),
            "language": "en" if case.get("language", run.get("language")) == "en" else "cs",
            "edge": case.get("edge_case_type", ""),
            "precision": s2 / len(cited) if cited else 0.0,
            "precision_noNA": (sum(1 for p in non_na if p["_rating"] == "S2") / len(non_na)) if non_na else None,
            "recall": len(supported) / len(claims) if claims else 0.0,
            "correct": 1 if corr == "2" else 0 if corr in {"0", "1"} else None,
            "ack": (a.get("acknowledges_uncertainty") or "").strip().lower(),
            "n_claims": len(claims), "n_pairs": len(cited),
            "n_fab": sum(1 for p in cited if p["_rating"] == "FAB"),
            "n_na": sum(1 for p in cited if p["_rating"] == "NA"),
            "n_unlinked": sum(1 for p in cited if p["_cit"] == "*"),
            "n_tier1": sum(1 for p in cited if (p.get("source_tier") or "").strip() == "1"),
            "n_time_checked": sum(1 for p in cited if (p.get("time_ok") or "").strip().lower() in {"yes", "no"}),
            "n_time_ok": sum(1 for p in cited if (p.get("time_ok") or "").strip().lower() == "yes"),
            "check_minutes": to_float(a.get("check_minutes")),
            "kf_cov": (min(1.0, to_float(a.get("key_facts_supported")) / to_float(a.get("n_key_facts")))
                       if to_float(a.get("key_facts_supported")) is not None and to_float(a.get("n_key_facts")) else None),
            "turns": to_float(run.get("turns")),
            "search_used": (run.get("search_used") or "").strip().lower(),
            "sources_shown": to_float(run.get("n_sources_shown")),
            "tool_calls": to_float(run.get("tool_calls_visible")),
            "format_valid": meta.get(bid, {}).get("format_valid", ""),
            "latency": to_float(run.get("latency_s")),
            "retries": to_float(run.get("retries")) or 0,
            "first_ok": (run.get("first_attempt_ok") or "").strip().lower(),
            "errors": [p.get("error_code", "").strip() for p in cited if p.get("error_code", "").strip()],
            "prompt_file": run.get("prompt_file", ""),
        })
    return out, problems


def case_values(answers, metric):
    by_case = collections.defaultdict(list)
    for a in answers:
        v = a[metric]
        if v is not None:
            by_case[a["task_id"]].append(v)
    return {c: sum(v) / len(v) for c, v in by_case.items() if v}


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "runs", "run_plan_*.csv"))
    ap.add_argument("--annotation-dir", default=os.path.join(ROOT, "annotation"))
    ap.add_argument("--key-dir", default=os.path.join(ROOT, "annotation_key"))
    ap.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    ap.add_argument("--prompts-dir", default=PROMPTS)
    ap.add_argument("--out", default=os.path.join(ROOT, "results"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--focus", default="perplexity", help="system tested in H1")
    ap.add_argument("--h1-margin", type=float, default=0.10)
    ap.add_argument("--h2-margin", type=float, default=0.05)
    ap.add_argument("--allow-missing", action="store_true",
                    help="exclude unrated rows instead of stopping (the report states how many)")
    args = ap.parse_args()

    ad = args.annotation_dir

    def collect(name, root=None):
        """Read every file with this name under a dir tree (e.g. annotation/dev, annotation/test)."""
        rows = []
        for base, _, files in sorted(os.walk(root or ad)):
            if name in files:
                rows.extend(read_csv(os.path.join(base, name)))
        return rows

    runs = read_csv_glob(args.runs)
    key = collect("blind_key.csv", args.key_dir) or collect("blind_key.csv")
    meta = {m["blind_answer_id"]: m for m in (collect("answers_meta.csv", args.key_dir) or collect("answers_meta.csv"))}
    pairs = collect("pairs_rated.csv")
    answers_raw = collect("answers_rated.csv")
    if not (key and pairs and answers_raw):
        raise SystemExit(f"missing blind_key.csv / pairs_rated.csv / answers_rated.csv under {ad}")
    cases = load_all_cases(args.data_dir)
    A, problems = load_answers(runs, key, pairs, answers_raw, cases, args.allow_missing, meta)
    for p in problems[:30]:
        print("PROBLEM:", p)
    if problems and not args.allow_missing:
        raise SystemExit(f"{len(problems)} problem(s): unrated or unmatched rows. Fix the sheets, "
                         "or rerun with --allow-missing to exclude them (the report will say so).")
    os.makedirs(args.out, exist_ok=True)
    report = ["# Výsledky – citační benchmark", "",
              f"Odpovědí v analýze: {len(A)}. Intervaly: klastrový bootstrap podle případů "
              f"({args.boot} převzorkování, seed {args.seed}); podíly odpovědí: Wilson (jen běh 1).", ""]
    if problems:
        report += [f"**Upozornění:** {len(problems)} nehodnocených nebo nespárovaných řádků bylo vyloučeno "
                   "(--allow-missing). Výsledky nejsou finální.", ""]
    report += ["Porovnání jednotlivých systémů mimo hypotézy H1 a H2 jsou **explorační**.", ""]

    groups = collections.defaultdict(list)
    for a in A:
        groups[(a["split"], a["condition"], a["system"])].append(a)

    # ---------------- metrics table
    metrics = []
    for (split, cond, system), items in sorted(groups.items()):
        row = {"split": split, "condition": cond, "system": system,
               "n_cases": len({a["task_id"] for a in items}), "n_answers": len(items)}
        for m in ("precision", "recall", "precision_noNA", "kf_cov"):
            p, lo, hi = bootstrap_ci(case_values(items, m), args.boot, args.seed)
            row[m], row[m + "_lo"], row[m + "_hi"] = p, lo, hi
        first = [a for a in items if a["run_index"] == 1 and a["correct"] is not None]
        p, lo, hi = wilson(sum(a["correct"] for a in first), len(first))
        row["correct_share"], row["correct_lo"], row["correct_hi"] = p, lo, hi
        p, lo, hi = wilson(sum(1 for a in first if a["n_fab"] > 0), len(first))
        row["answers_with_fab"], row["answers_with_fab_lo"], row["answers_with_fab_hi"] = p, lo, hi
        npairs = sum(a["n_pairs"] for a in items)
        row["fab_rate"] = sum(a["n_fab"] for a in items) / npairs if npairs else None
        row["na_rate"] = sum(a["n_na"] for a in items) / npairs if npairs else None
        row["tier1_share"] = sum(a["n_tier1"] for a in items) / npairs if npairs else None
        row["unlinked_rate"] = sum(a["n_unlinked"] for a in items) / npairs if npairs else None
        tchk = sum(a["n_time_checked"] for a in items)
        row["time_ok_share"] = sum(a["n_time_ok"] for a in items) / tchk if tchk else None
        unc = [a for a in items if a["edge"] in {"missing_info", "ambiguous"} and a["ack"] in {"yes", "no"}]
        row["ack_uncertainty_share"] = sum(1 for a in unc if a["ack"] == "yes") / len(unc) if unc else None
        row["claims_per_answer"] = mean([a["n_claims"] for a in items])
        row["citations_per_answer"] = mean([a["n_pairs"] for a in items])
        lat = [a["latency"] for a in items if a["latency"] is not None]
        row["latency_median"] = statistics.median(lat) if lat else None
        row["latency_p90"] = quantile(lat, 0.9) if lat else None
        row["retry_rate"] = mean([1 if a["retries"] > 0 else 0 for a in items])
        fo = [a for a in items if a["first_ok"] in {"yes", "no"}]
        row["first_attempt_success"] = sum(1 for a in fo if a["first_ok"] == "yes") / len(fo) if fo else None
        row["turns_mean"] = mean([a["turns"] for a in items])
        su = [a for a in items if a["search_used"] in {"yes", "no"}]
        row["search_used_share"] = sum(1 for a in su if a["search_used"] == "yes") / len(su) if su else None
        row["sources_shown_mean"] = mean([a["sources_shown"] for a in items])
        row["tool_calls_mean"] = mean([a["tool_calls"] for a in items])
        fv = [a for a in items if a["format_valid"] in {"yes", "no"}]
        row["format_valid_share"] = sum(1 for a in fv if a["format_valid"] == "yes") / len(fv) if fv else None
        cm = [a["check_minutes"] for a in items if a["check_minutes"] is not None]
        row["check_minutes_median"] = statistics.median(cm) if cm else None
        metrics.append(row)

    # utility (weights fixed in protocol): precision - 0.1*L_norm - 0.1*T_norm, within split x condition
    by_sc = collections.defaultdict(list)
    for r in metrics:
        by_sc[(r["split"], r["condition"])].append(r)
    for rows in by_sc.values():
        lat_vals = [r["latency_median"] for r in rows if r["latency_median"]]
        chk_vals = [r["check_minutes_median"] for r in rows if r["check_minutes_median"]]
        lmax = max(lat_vals) if lat_vals else None
        tmax = max(chk_vals) if chk_vals else None
        for r in rows:
            if r["precision"] is None or r["latency_median"] is None or r["check_minutes_median"] is None or not lmax or not tmax:
                r["utility"] = None          # missing latency or check time -> no utility (never a free pass)
            else:
                r["utility"] = r["precision"] - 0.1 * r["latency_median"] / lmax - 0.1 * r["check_minutes_median"] / tmax
            dominated = any(o is not r and o["precision"] is not None and r["precision"] is not None
                            and o["latency_median"] is not None and r["latency_median"] is not None
                            and o["precision"] >= r["precision"] and o["latency_median"] <= r["latency_median"]
                            and (o["precision"] > r["precision"] or o["latency_median"] < r["latency_median"])
                            for o in rows)
            r["pareto"] = "no" if dominated else "yes"

    mfields = list(metrics[0].keys()) if metrics else []
    write_csv(os.path.join(args.out, "metrics.csv"),
              [{k: (fnum(v, digits=4) if isinstance(v, float) else v) for k, v in r.items()} for r in metrics], mfields)

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
        report += [f"## Sada: {split}", "",
                   "| Podmínka | Systém | Případů | Odpovědí | Citační přesnost % [95% CI] | Úplnost citací % | Pokrytí kl. faktů % | Správnost odpovědi % (Wilson) | FAB % | NA % | Tvrzení/odp. | Vyhledávání % | 1. pokus OK % | Medián latence s | Užitek | Pareto |",
                   "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in rows:
            report.append(f"| {r['condition']} | {r['system']} | {r['n_cases']} | {r['n_answers']} | {ci(r, 'precision')} | "
                          f"{ci(r, 'recall')} | {ci(r, 'kf_cov')} | {fnum(r['correct_share'], True)} [{fnum(r['correct_lo'], True)}–{fnum(r['correct_hi'], True)}] | "
                          f"{fnum(r['fab_rate'], True)} | {fnum(r['na_rate'], True)} | {fnum(r['claims_per_answer'], digits=1)} | "
                          f"{fnum(r['search_used_share'], True)} | {fnum(r['first_attempt_success'], True)} | "
                          f"{fnum(r['latency_median'], digits=1)} | {fnum(r['utility'])} | {r['pareto']} |")
        report.append("")

    # ---------------- hypotheses (held-out test split only)
    hyp = []
    test = [a for a in A if a["split"] == "test"]

    def sys_case(cond, system, metric="precision"):
        return case_values([a for a in test if a["condition"] == cond and a["system"] == system], metric)

    systems = sorted({a["system"] for a in test})
    report += ["## Hypotézy (testovací sada)", ""]
    if test and args.focus in systems:
        focus = sys_case("P2", args.focus)
        others = {s: sys_case("P2", s) for s in systems if s != args.focus}
        diffs = {}
        for c, v in focus.items():
            ov = [others[s][c] for s in others if c in others[s]]
            if ov:
                diffs[c] = v - sum(ov) / len(ov)
        p, lo, hi = bootstrap_ci(diffs, args.boot, args.seed)
        supported = p is not None and lo is not None and p >= args.h1_margin and lo > 0
        hyp.append({"hypothesis": "H1", "comparison": f"{args.focus} − průměr ostatních, P2, přesnost",
                    "estimate": fnum(p, digits=4), "ci_lo": fnum(lo, digits=4), "ci_hi": fnum(hi, digits=4),
                    "n_cases": len(diffs), "criterion": f">= {args.h1_margin} a CI nad 0",
                    "supported": "yes" if supported else "no"})
    else:
        report.append(f"H1 nelze vyhodnotit: systém {args.focus!r} nebo testovací data chybí.")

    if test:
        per_sys, case_diffs = {}, collections.defaultdict(list)
        for s in systems:
            p1, p2 = sys_case("P1", s), sys_case("P2", s)
            d = {c: p2[c] - p1[c] for c in p2 if c in p1}
            if d:
                per_sys[s] = bootstrap_ci(d, args.boot, args.seed)
                for c, v in d.items():
                    case_diffs[c].append(v)
        avg = {c: sum(v) / len(v) for c, v in case_diffs.items()}
        p, lo, hi = bootstrap_ci(avg, args.boot, args.seed)
        improved = sum(1 for s, (pt, _, _) in per_sys.items() if pt is not None and pt > 0)
        need = max(1, len(per_sys) - 1)          # 4 of 5 systems; 3 of 4 in the lean variant
        supported = p is not None and lo is not None and p >= args.h2_margin and lo > 0 and improved >= need
        hyp.append({"hypothesis": "H2", "comparison": "P2 − P1, průměr přes systémy, přesnost",
                    "estimate": fnum(p, digits=4), "ci_lo": fnum(lo, digits=4), "ci_hi": fnum(hi, digits=4),
                    "n_cases": len(avg), "criterion": f">= {args.h2_margin}, CI nad 0 a zlepšení u >= {need} systémů (zlepšeno: {improved}/{len(per_sys)})",
                    "supported": "yes" if supported else "no"})

    write_csv(os.path.join(args.out, "hypotheses.csv"), hyp,
              ["hypothesis", "comparison", "estimate", "ci_lo", "ci_hi", "n_cases", "criterion", "supported"])
    if hyp:
        report += ["| Hypotéza | Porovnání | Odhad | 95% CI | Případů | Kritérium | Podpořena |",
                   "| --- | --- | --- | --- | --- | --- | --- |"]
        for h in hyp:
            report.append(f"| {h['hypothesis']} | {h['comparison']} | {h['estimate']} | {h['ci_lo']}–{h['ci_hi']} | "
                          f"{h['n_cases']} | {h['criterion']} | {h['supported']} |")
        report.append("")

    # ---------------- prompt portability
    if test:
        report += ["## Přenositelnost promptů (testovací sada, rozdíl citační přesnosti v p. b.)", "",
                   "| Systém | P2 − P1 [95% CI] | P3 − P1 [95% CI] | P3 − P2 [95% CI] |", "| --- | --- | --- | --- |"]
        agg = {"P2-P1": collections.defaultdict(list), "P3-P1": collections.defaultdict(list), "P3-P2": collections.defaultdict(list)}
        for s in systems:
            cells = []
            for a_, b_ in (("P2", "P1"), ("P3", "P1"), ("P3", "P2")):
                x, y = sys_case(a_, s), sys_case(b_, s)
                d = {c: x[c] - y[c] for c in x if c in y}
                for c, v in d.items():
                    agg[f"{a_}-{b_}"][c].append(v)
                pt, lo, hi = bootstrap_ci(d, args.boot, args.seed)
                cells.append("" if pt is None else f"{fnum(pt, True)} [{fnum(lo, True)}–{fnum(hi, True)}]")
            report.append(f"| {s} | " + " | ".join(cells) + " |")
        avg_cells = []
        for k in ("P2-P1", "P3-P1", "P3-P2"):
            pt, lo, hi = bootstrap_ci({c: sum(v) / len(v) for c, v in agg[k].items()}, args.boot, args.seed)
            avg_cells.append("" if pt is None else f"{fnum(pt, True)} [{fnum(lo, True)}–{fnum(hi, True)}]")
        report.append("| **průměr** | " + " | ".join(avg_cells) + " |")
        lengths = []
        for pf in sorted({a["prompt_file"] for a in test if a["prompt_file"]}):
            path = os.path.join(args.prompts_dir, pf)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    lengths.append(f"{pf}: {len(f.read())} znaků")
        report += ["", "Délka promptů (bez otázky): " + "; ".join(lengths) if lengths else "", ""]

    # ---------------- alternative explanations
    if test:
        report += ["## Kontrola alternativních vysvětlení", ""]
        xs = [a["n_claims"] for a in test]
        ys = [a["precision"] for a in test]
        rho = spearman(xs, ys)
        report.append(f"A1 – Spearmanova korelace počtu tvrzení a přesnosti odpovědi (test, všechny podmínky): {fnum(rho)} "
                      f"(n = {len(xs)}). Záporná hodnota = systémy s méně tvrzeními mají vyšší přesnost.")
        report += ["", "A2 – citační přesnost podle jazyka dotazu (test, P2, %):", "",
                    "| Systém | CZ | EN |", "| --- | --- | --- |"]
        for s in systems:
            cz = mean(list(case_values([a for a in test if a["system"] == s and a["condition"] == "P2" and a["language"] == "cs"], "precision").values()))
            en = mean(list(case_values([a for a in test if a["system"] == s and a["condition"] == "P2" and a["language"] == "en"], "precision").values()))
            report.append(f"| {s} | {fnum(cz, True)} | {fnum(en, True)} |")
        report.append("")

    # ---------------- run-to-run variability (test, P2, run_index 1..3)
    rep = [a for a in test if a["condition"] == "P2"]
    if rep and len({a["run_index"] for a in rep}) > 1:
        report += ["## Variabilita mezi běhy (test, P2)", "",
                   "| Systém | Přesnost po bězích % | SD (p. b.) | Podíl případů se změnou správnosti |", "| --- | --- | --- | --- |"]
        for s in systems:
            items = [a for a in rep if a["system"] == s]
            per_run = []
            for ri in sorted({a["run_index"] for a in items}):
                v = case_values([a for a in items if a["run_index"] == ri], "precision")
                if v:
                    per_run.append(sum(v.values()) / len(v))
            sd = statistics.stdev(per_run) if len(per_run) > 1 else None
            flips, total = 0, 0
            by_case = collections.defaultdict(set)
            for a in items:
                if a["correct"] is not None:
                    by_case[a["task_id"]].add(a["correct"])
            for c, vals in by_case.items():
                total += 1
                flips += 1 if len(vals) > 1 else 0
            report.append(f"| {s} | {' / '.join(fnum(x, True) for x in per_run)} | {fnum(sd, True)} | "
                          f"{fnum(flips / total, True) if total else ''} |")
        report.append("")

    # ---------------- error codes
    codes = collections.defaultdict(collections.Counter)
    for a in A:
        for e in a["errors"]:
            codes[a["system"]][e] += 1
    if codes:
        all_codes = sorted({c for cnt in codes.values() for c in cnt}, key=lambda x: (len(x), x))
        report += ["## Kódy chyb (všechny sady)", "", "| Systém | " + " | ".join(all_codes) + " |",
                   "| --- | " + " | ".join("---" for _ in all_codes) + " |"]
        for s in sorted(codes):
            report.append(f"| {s} | " + " | ".join(str(codes[s].get(c, 0)) for c in all_codes) + " |")
        report.append("")

    # ---------------- inter-rater agreement (rater 1 BEFORE reconciliation vs rater 2)
    agr = []
    pairs1_raw = collect("pairs_rated_rater1.csv")
    answers1_raw = collect("answers_rated_rater1.csv")
    pairs2 = collect("pairs_rated_rater2.csv")
    answers2 = collect("answers_rated_rater2.csv")
    inflated = False
    if pairs2 and not pairs1_raw:
        pairs1_raw, inflated = pairs, True
    if answers2 and not answers1_raw:
        answers1_raw, inflated = answers_raw, True
    if pairs2:
        r1 = {p["pair_id"]: (p.get("rating") or "").strip().upper() for p in pairs1_raw if (p.get("citation_n") or "").strip() != ""}
        r2 = {p["pair_id"]: (p.get("rating") or "").strip().upper() for p in pairs2 if (p.get("citation_n") or "").strip() != ""}
        common = [k for k in r2 if k in r1 and r1[k] in RATINGS and r2[k] in RATINGS]
        a_, b_ = [r1[k] for k in common], [r2[k] for k in common]
        k5, po5 = cohen_kappa(a_, b_)
        kb, pob = cohen_kappa(["S2" if x == "S2" else "other" for x in a_], ["S2" if x == "S2" else "other" for x in b_])
        agr.append({"measure": "pairs S2 vs other", "n": len(common), "kappa": fnum(kb), "agreement": fnum(pob)})
        agr.append({"measure": "pairs 5 categories", "n": len(common), "kappa": fnum(k5), "agreement": fnum(po5)})
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
            agr.append({"measure": "segmentation: mean abs. difference in claims (r1 vs r2)", "n": len(both), "kappa": "", "agreement": fnum(mad)})
            agr.append({"measure": "segmentation: same number of claims", "n": len(both), "kappa": "", "agreement": fnum(same)})
    if answers2:
        c1 = {a["blind_answer_id"]: (a.get("correctness") or "").strip() for a in answers1_raw}
        c2 = {a["blind_answer_id"]: (a.get("correctness") or "").strip() for a in answers2}
        common = [k for k in c2 if k in c1 and c1[k] in {"0", "1", "2"} and c2[k] in {"0", "1", "2"}]
        k3, po3 = cohen_kappa([c1[k] for k in common], [c2[k] for k in common])
        agr.append({"measure": "answer correctness 0-2", "n": len(common), "kappa": fnum(k3), "agreement": fnum(po3)})

    # ---------------- validation of the automated number/name match against human S2 (dev split)
    split_of = {a["bid"]: a["split"] for a in A}
    auto = [(to_float(p.get("auto_match_ratio")), p["_rating"]) for p in pairs
            if p.get("_cit") not in (None, "") and p.get("_rating") in RATINGS
            and to_float(p.get("auto_match_ratio")) is not None and split_of.get(p["blind_answer_id"]) == "dev"]
    if auto:
        flag = ["S2" if r >= 0.8 else "other" for r, _ in auto]
        human = ["S2" if h == "S2" else "other" for _, h in auto]
        ka, pa = cohen_kappa(flag, human)
        tp = sum(1 for f, h in zip(flag, human) if f == h == "S2")
        prec = tp / flag.count("S2") if flag.count("S2") else None
        rec = tp / human.count("S2") if human.count("S2") else None
        agr.append({"measure": "auto match>=0.8 vs human S2 (dev)", "n": len(auto), "kappa": fnum(ka),
                    "agreement": f"{fnum(pa)} (precision {fnum(prec)}, recall {fnum(rec)})"})

    write_csv(os.path.join(args.out, "agreement.csv"), agr, ["measure", "n", "kappa", "agreement"])
    if agr:
        report += ["## Shoda hodnotitelů a validace automatiky", "", "| Míra | n | Cohenova kappa | Shoda / hodnota |", "| --- | --- | --- | --- |"]
        for g in agr:
            report.append(f"| {g['measure']} | {g['n']} | {g['kappa']} | {g['agreement']} |")
        report += ["", "Cíl protokolu: kappa (S2 vs ostatní) alespoň 0,6. Automatický příznak shody se použije jen jako "
                   "nápověda, pokud je jeho kappa s lidským hodnocením pod 0,4.", ""]
        if inflated:
            report += ["**Upozornění:** chybí `*_rated_rater1.csv` (hodnocení 1. hodnotitele před smířením); shoda je "
                       "počítána z finálních hodnot a je proto nadhodnocená.", ""]

    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print(f"{len(A)} answers scored -> {args.out}/metrics.csv, hypotheses.csv, agreement.csv, report.md")


if __name__ == "__main__":
    main()
