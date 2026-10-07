#!/usr/bin/env python3
"""Generate SYNTHETIC demo data to test the whole pipeline end to end.

Nothing here is a real result: systems are anonymous (sys_A ... sys_E), cases are dummy
questions (DEMO-001 ... DEMO-040) and all ratings are random draws from made-up
probabilities. The demo lets another student check that the scripts run and that the
numbers they print are sensible before any real data exist.

Usage:
    python3 scripts/make_demo_data.py         # writes demo/data, demo/runs, demo/annotation
    bash demo/run_demo.sh                     # runs validate -> check_citations -> score
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import META_FILL_COLUMNS, PHASES, ROOT, write_csv  # noqa: E402

DEMO = os.path.join(ROOT, "demo")
SYSTEMS = ["sys_A", "sys_B", "sys_C", "sys_D", "sys_E"]
BASE = {"sys_A": 0.66, "sys_B": 0.60, "sys_C": 0.68, "sys_D": 0.80, "sys_E": 0.55}   # made up
CITE = {"sys_A": 0.85, "sys_B": 0.75, "sys_C": 0.80, "sys_D": 0.95, "sys_E": 0.70}   # made up
COND = {"P1": -0.08, "P2": 0.0, "P3A": 0.03, "P3B": 0.04, "P3": 0.04}
LAT = {"sys_A": 14, "sys_B": 10, "sys_C": 18, "sys_D": 8, "sys_E": 12}
DOMAINS = ["veda_zdravi", "pravo", "it", "ekonomika", "historie_kultura"]
WORDS = ("alfa beta gama delta epsilon zeta theta iota kappa lambda sigma omega "
         "jablko hruška švestka meruňka broskev třešeň višeň malina ostružina borůvka "
         "řeka hora údolí jezero moře ostrov poušť les louka pole "
         "motor kolo vlak loď letadlo raketa balón tramvaj autobus metro "
         "zákon soud úřad obec kraj stát parlament senát vláda ministr "
         "atom molekula buňka gen protein virus bakterie planeta hvězda galaxie").split()
EDGES = ["false_premise", "conflicting_evidence", "missing_info", "ambiguous",
         "time_constraint", "recent_change", "cz_en_mix"]


def make_cases(rng):
    os.makedirs(os.path.join(DEMO, "data"), exist_ok=True)
    splits = [("dev", 20), ("val", 10), ("test", 10)]
    n = 0
    for split, size in splits:
        rows = []
        for i in range(size):
            n += 1
            edge = EDGES[n % len(EDGES)] if i % 5 in (0, 3) else "none"
            lang = "cs+en" if edge == "cz_en_mix" else ("cs" if n % 2 else "en")
            rows.append({
                "task_id": f"DEMO-{n:03d}", "capability": "citation_accuracy",
                "task_type": ["fact", "primary_source", "synthesis"][n % 3],
                "difficulty": ["easy", "medium", "hard"][n % 3], "language": lang,
                "domain": DOMAINS[i % 5], "development_validation_test_split": split,
                "user_prompt": "DEMO " + " ".join(rng.sample(WORDS, 6)) + f" {n}?",
                "context_or_files": [], "expected_properties": ["demo"],
                "reference_answer_or_tests": {"reference_answer": "demo", "key_facts": ["demo1", "demo2", "demo3"],
                                              "gold_sources": [{"title": "demo", "publisher": "demo",
                                                                "url": "http://127.0.0.1:8765/demo.html", "supports": "demo"}]},
                "edge_case_type": edge, "evaluation_method": "demo",
                "source_or_provenance": "SYNTHETIC DEMO", "reference_valid_as_of": "2026-09-29",
                "rater_notes": "",
            })
        with open(os.path.join(DEMO, "data", f"cases_{split}.jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {s: [f"DEMO-{i:03d}" for i in rng_range] for s, rng_range in
            [("dev", range(1, 21)), ("val", range(21, 31)), ("test", range(31, 41))]}


def main():
    rng = random.Random(2026)
    case_ids = make_cases(rng)
    difficulty = {cid: rng.uniform(-0.12, 0.12) for ids in case_ids.values() for cid in ids}
    run_rows = {p: [] for p in PHASES}
    key, pairs, answers = [], [], []
    for phase, (split, conds, run_idx) in PHASES.items():
        seq = 0
        for ri in run_idx:
            for cid in case_ids[split]:
                for cond in conds:
                    for s in SYSTEMS:
                        seq += 1
                        run_id = f"{phase}-{cid}-{cond}-{s}-r{ri}"
                        lat = round(rng.lognormvariate(0, 0.35) * LAT[s], 1)
                        retry = 1 if rng.random() < 0.04 else 0
                        row = {"seq": seq, "run_id": run_id, "phase": phase, "split": split,
                               "task_id": cid, "language": "cs", "condition": cond,
                               "prompt_file": "", "prompt_sha256": "", "system": s, "run_index": ri,
                               "answer_file": f"demo/answers/{run_id}.txt"}
                        for c in META_FILL_COLUMNS:
                            row[c] = ""
                        row.update({"model_visible": "demo-model", "plan_tier": "free",
                                    "run_status": "completed", "final_attempt_ok": "yes",
                                    "attempt1_file": f"demo/answers/{run_id}__attempt1.txt" if retry else "",
                                    "first_attempt_latency_s": lat / 2 if retry else lat,
                                    "latency_s": lat, "search_used": "yes" if rng.random() < 0.95 else "no",
                                    "turns": 1, "n_sources_shown": rng.randint(2, 8), "tool_calls_visible": rng.randint(1, 4),
                                    "retries": retry, "failure_type": "tool_error" if retry else "none",
                                    "first_attempt_ok": "no" if retry else "yes", "operator": "demo"})
                        run_rows[phase].append(row)
                        # --- synthetic annotation
                        bid = f"A{len(key):05d}"
                        key.append({"blind_answer_id": bid, "run_id": run_id})
                        p_s2 = min(0.97, max(0.05, BASE[s] + COND[cond] + difficulty[cid] + rng.gauss(0, 0.05)))
                        n_claims = rng.randint(2, 6)
                        s2_total = n_cited = 0
                        for ci in range(1, n_claims + 1):
                            if rng.random() > CITE[s]:
                                pairs.append({"pair_id": f"{bid}-T{ci}-none", "blind_answer_id": bid,
                                              "claim_id": f"T{ci}", "citation_n": "", "rating": ""})
                                continue
                            u = rng.random()
                            if u < p_s2:
                                rating = "S2"
                            else:
                                rating = rng.choices(["S1", "S0", "NA", "FAB"], [0.4, 0.35, 0.15, 0.10])[0]
                            n_cited += 1
                            s2_total += rating == "S2"
                            auto = rng.uniform(0.8, 1.0) if (rating == "S2" and rng.random() < 0.8) else rng.uniform(0, 0.79)
                            pairs.append({"pair_id": f"{bid}-T{ci}-1", "blind_answer_id": bid,
                                          "claim_id": f"T{ci}", "citation_n": "1", "rating": rating,
                                          "auto_match_ratio": f"{auto:.2f}",
                                          "source_tier": rng.choice(["1", "1", "2", "3"]),
                                          "time_ok": "", "error_code": "" if rating == "S2" else
                                          {"S1": "E3", "S0": "E2", "FAB": "E1"}.get(rating, "")})
                        prec = s2_total / n_cited if n_cited else 0
                        corr = "2" if rng.random() < 0.3 + 0.6 * prec else rng.choice(["0", "1"])
                        supported_ids = [p["pair_id"] for p in pairs if p["blind_answer_id"] == bid and p["rating"] == "S2"]
                        nk = min(3, round(3 * prec * rng.uniform(0.7, 1.1))) if supported_ids else 0
                        answers.append({"blind_answer_id": bid, "correctness": corr, "n_key_facts": 3, "n_claims": n_claims,
                                        "segmentation_reviewed": "yes",
                                        "key_facts_supported": nk,
                                        "key_fact_evidence": json.dumps({f"RF{i}": [supported_ids[0]] for i in range(1, nk + 1)}),
                                        "acknowledges_uncertainty": rng.choice(["yes", "no"]),
                                        "check_minutes": round(rng.uniform(3, 11), 1), "rater": "demo1"})

    for phase, rows in run_rows.items():
        write_csv(os.path.join(DEMO, "runs", f"run_plan_{phase}.csv"), rows, list(rows[0].keys()))
    ad = os.path.join(DEMO, "annotation", "all")
    write_csv(os.path.join(DEMO, "annotation_key", "blind_key.csv"), key, ["blind_answer_id", "run_id"])
    pf = ["pair_id", "blind_answer_id", "claim_id", "citation_n", "rating", "source_tier", "time_ok",
          "error_code", "auto_match_ratio"]
    write_csv(os.path.join(ad, "pairs_rated.csv"), pairs, pf)
    af = ["blind_answer_id", "correctness", "n_key_facts", "n_claims", "segmentation_reviewed", "key_facts_supported", "key_fact_evidence", "acknowledges_uncertainty",
          "check_minutes", "rater"]
    write_csv(os.path.join(ad, "answers_rated.csv"), answers, af)
    # rater 1 before reconciliation = final values here (demo); a real project keeps the raw file
    write_csv(os.path.join(ad, "pairs_rated_rater1.csv"), pairs, pf)
    write_csv(os.path.join(ad, "answers_rated_rater1.csv"), answers, af)

    # second rater on 25 % of answers: agrees with probability 0.85
    chosen = set(rng.sample([a["blind_answer_id"] for a in answers], len(answers) // 4))
    p2 = []
    for p in pairs:
        if p["blind_answer_id"] in chosen:
            q = dict(p)
            if q["citation_n"] and rng.random() > 0.85:
                q["rating"] = rng.choice([r for r in ["S2", "S1", "S0", "NA", "FAB"] if r != q["rating"]])
            p2.append(q)
    a2 = []
    for a in answers:
        if a["blind_answer_id"] in chosen:
            q = dict(a)
            if rng.random() > 0.85:
                q["correctness"] = rng.choice([c for c in "012" if c != q["correctness"]])
            a2.append(q)
    write_csv(os.path.join(ad, "pairs_rated_rater2.csv"), p2, pf)
    write_csv(os.path.join(ad, "answers_rated_rater2.csv"), a2, af)
    print(f"SYNTHETIC demo: {len(key)} answers, {len(pairs)} claim rows -> {DEMO}")


if __name__ == "__main__":
    main()
