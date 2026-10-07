#!/usr/bin/env python3
"""Offline, deterministic integration fixture; never runs an AI product.

Real CLIs generate plans, parse fixture answers, export blinded sheets, then score
ratings derived from those exact sheets. No independent random score CSVs are used.
Default: disposable temporary directory. --out: new absolute directory outside Git.
"""
import argparse
import collections
import datetime as dt
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from common import ROOT, read_csv, sha256_file, write_csv
from integrity import private_path

SYSTEMS = [f"sys_{c}" for c in "ABCDE"]
CONDITIONS = {"P1": 0, "P2": 1, "P3A": 2, "P3B": 3, "P3": 3}
DOMAINS = ["veda_zdravi", "pravo", "it", "ekonomika", "historie_kultura"]


def run_cli(script, *args):
    result = subprocess.run([sys.executable, str(Path(ROOT, "scripts", script)), *map(str, args)],
                            capture_output=True, text=True, timeout=60,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    if result.returncode:
        raise RuntimeError(f"{script} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout


def make_cases(work):
    (work / "data").mkdir()
    for split, start, size in (("dev", 1, 20), ("val", 21, 10), ("test", 31, 10)):
        rows = []
        for i in range(start, start + size):
            j = (i - 1) % 10
            fact = f"The fixture value is {i}"
            rows.append(dict(task_id=f"DEMO-{i:03d}", schema_version=2, capability="citation_accuracy",
                             task_type="fact" if j < 5 else "primary_source" if j < 8 else "synthesis",
                             difficulty="easy" if j < 2 else "medium" if j < 7 else "hard", language="cs" if i % 2 else "en",
                             domain=DOMAINS[(i - 1) % 5], development_validation_test_split=split,
                             user_prompt=f"fixture_query_{i} fixture_topic_{i} fixture_marker_{i}?", context_or_files=[],
                             expected_properties=["give the synthetic fixture value"],
                             reference_answer_or_tests=dict(reference_answer=fact, key_facts=[fact], required_facts=[fact], optional_facts=[],
                                                            gold_sources=[dict(title="Synthetic source", publisher="fixture",
                                                                               url="https://fixture.invalid/source", supports=fact)]),
                             edge_case_type="ambiguous" if j < 4 else "none", evaluation_method="synthetic human-rating fixture",
                             source_or_provenance="SYNTHETIC LOCAL TEST, not product results", reference_valid_as_of="2026-01-01",
                             rater_notes="Synthetic software-test input, not a factual benchmark reference."))
        (work / "data" / f"cases_{split}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def fill_runs(work, phase):
    path = work / "runs" / f"run_plan_{phase}.csv"
    rows = read_csv(path)
    expected = {}
    for row in rows:
        i = int(row["task_id"].split("-")[-1])
        mode = (i + SYSTEMS.index(row["system"]) + CONDITIONS[row["condition"]] + int(row["run_index"]) - 1) % 9
        failed = mode == 8
        retry = mode in (0, 8) and i % 2 == 0
        latency = 4 if retry else 2
        day = {"dev": 1, "val": 2, "test": 3, "repeat": 4}[phase]
        start = dt.datetime(2026, 1, day, 10, tzinfo=dt.timezone.utc)
        row.update(run_status="failed" if failed else "completed", failure_type="product_outage" if failed or retry else "none",
                   final_attempt_ok="no" if failed else "yes", first_attempt_ok="no" if failed or retry else "yes",
                   retries=str(int(retry)), latency_s=str(latency), first_attempt_latency_s="1" if retry else "2",
                   datetime_start=start.isoformat(), datetime_end=(start + dt.timedelta(seconds=latency)).isoformat(),
                   model_visible="synthetic fixture", plan_tier="fixture", operator="synthetic operator", manual_intervention="none",
                   cost_note="synthetic: no product accessed", search_used="unclear" if failed else "yes",
                   n_sources_shown="0" if mode == 5 or failed else "1", turns="1", tool_calls_visible="unknown")
        artifacts = work / "artifacts"
        artifacts.mkdir(exist_ok=True)
        screenshot = artifacts / (row["run_id"] + ".txt")
        screenshot.write_text("SYNTHETIC screenshot substitute for software tests only", encoding="utf-8")
        row.update(screenshot_file=str(screenshot), screenshot_sha256=sha256_file(screenshot))
        if retry:
            attempt = artifacts / (row["run_id"] + "__attempt1.txt")
            attempt.write_text("Synthetic first-attempt outage", encoding="utf-8")
            row.update(attempt1_file=str(attempt), attempt1_sha256=sha256_file(attempt))
        if failed:
            log = artifacts / (row["run_id"] + "__failure.txt")
            log.write_text("Synthetic terminal outage, not an actual product incident", encoding="utf-8")
            row.update(failure_artifact_file=str(log), failure_artifact_sha256=sha256_file(log))
        else:
            fact = f"The fixture value is {i}"
            mark = "[9]" if mode == 4 else "[1]" if mode not in (5, 6) else ""
            claim = f"{fact} {mark}".strip()
            if row["condition"].startswith("P3") and mode == 0:
                claim += ' "Synthetic support sentence. Another synthetic support sentence."'
            source = "\n[1] Synthetic source – fixture – 2026-01-01 – https://fixture.invalid/source" if mode != 5 else ""
            extra = " The unsupported fixture bonus is 9999." if mode == 7 else ""
            if row["condition"] == "P1":
                answer = claim + "." + extra + ("\nSOURCES:" + source if source else "")
            else:
                answer = f"ANSWER: {claim}." + extra + f"\nCLAIMS:\nC1: {claim}\nSOURCES:{source}\nCONFIDENCE: high – synthetic fixture."
            dest = Path(row["answer_file"])
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(answer + "\n", encoding="utf-8")
            row.update(answer_sha256=sha256_file(dest), raw_answer_file=str(dest), raw_answer_sha256=sha256_file(dest))
        expected[row["run_id"]] = dict(mode=mode, precision=1 if mode in (0, 7) else 0,
                                        recall=1 if mode == 0 else .5 if mode == 7 else 0,
                                        correct=1 if mode in (0, 5, 6) else 0, kf_cov=1 if mode in (0, 7) else 0,
                                        n_claims=0 if failed else 2 if mode == 7 else 1, n_unlinked=int(mode == 6),
                                        run_status=row["run_status"], first_ok=row["first_attempt_ok"], final_ok=row["final_attempt_ok"])
    write_csv(path, rows, list(rows[0]))
    return expected


def rate_export(work, phase, expected):
    """Fixture ratings attach to exported units; these are not human measurements."""
    ad = work / "annotation" / phase
    key = {r["blind_answer_id"]: r["run_id"] for r in read_csv(work / "key/blind_key.csv")}
    snapshot = work / "source.txt"
    for suffix, rater in (("", "synthetic rater1"), ("_rater2", "synthetic rater2")):
        answers = read_csv(ad / f"answers_to_rate{suffix}.csv")
        pairs = read_csv(ad / f"pairs_to_rate{suffix}.csv")
        grouped = collections.defaultdict(list)
        for pair in pairs:
            e = expected[key[pair["blind_answer_id"]]]
            cit = pair["citation_n"]
            rating = {0: "S2", 1: "S1", 2: "S0", 3: "NA", 4: "FAB", 6: "S2", 7: "S2"}.get(e["mode"], "") if cit else ""
            pair.update(rating=rating, source_tier="1" if rating else "", time_ok="", rater=rater,
                        rater_source_n="1" if cit == "*" else "", error_code={"S1": "E3", "S0": "E2", "FAB": "E1"}.get(rating, "") if cit else "E9")
            if cit:
                pair.update(evidence_url="https://fixture.invalid/source", evidence_checked_at="2026-01-05T10:00:00+00:00",
                            evidence_locator="synthetic fixture", evidence_excerpt="Synthetic rating evidence, not an actual web page",
                            evidence_snapshot=str(snapshot), evidence_sha256=sha256_file(snapshot))
            grouped[pair["blind_answer_id"]].append(pair)
        for answer in answers:
            e = expected[key[answer["blind_answer_id"]]]
            units = grouped[answer["blind_answer_id"]]
            support = [p["pair_id"] for p in units if p["rating"] == "S2" and p["citation_n"] not in ("", "*")]
            answer.update(correctness="2" if e["correct"] else "1" if e["mode"] in (1, 7) else "0",
                          n_claims=str(len({p["claim_id"] for p in units})), segmentation_reviewed="yes",
                          key_facts_supported=str(e["kf_cov"]), key_fact_evidence=json.dumps({"RF1": [support[0]]} if e["kf_cov"] else {}),
                          acknowledges_uncertainty="yes" if e["mode"] == 3 else "no", check_minutes="3" if not suffix else "4",
                          rater=rater, comment="Synthetic rating fixture; no human experiment.")
        rated = "_rater2" if suffix else "_rater1"
        write_csv(ad / f"answers_rated{rated}.csv", answers, list(answers[0]))
        write_csv(ad / f"pairs_rated{rated}.csv", pairs, list(pairs[0]))
        if not suffix:
            write_csv(ad / "answers_rated.csv", answers, list(answers[0]))
            write_csv(ad / "pairs_rated.csv", pairs, list(pairs[0]))


def assert_fixture(work, expected):
    actual = {r["run_id"]: r for r in read_csv(work / "results/answer_metrics.csv")}
    if len(actual) != 500 or set(actual) != set(expected):
        raise AssertionError("integration fixture lost/added run identities")
    for rid, values in expected.items():
        for field in ("precision", "recall", "correct", "kf_cov", "n_claims", "n_unlinked"):
            if not math.isclose(float(actual[rid][field]), values[field], abs_tol=1e-12):
                raise AssertionError(f"{rid}/{field}: {actual[rid][field]} != {values[field]}")
        for field in ("run_status", "first_ok", "final_ok"):
            if actual[rid][field] != values[field]:
                raise AssertionError(f"{rid}: inconsistent {field}")
    metrics = read_csv(work / "results/metrics.csv")
    if len(metrics) != 35:
        raise AssertionError("expected 5 dev + 15 val + 15 first-test aggregate rows")
    for row in metrics:
        items = [a for a in actual.values() if (a["split"], a["condition"], a["system"]) == (row["split"], row["condition"], row["system"]) and a["run_index"] == "1"]
        if int(row["n_answers"]) != len(items):
            raise AssertionError("repeats leaked into primary aggregates")
        for field in ("precision", "recall", "kf_cov"):
            value = sum(float(a[field]) for a in items) / len(items)
            if not math.isclose(float(row[field]), value, abs_tol=.000051):
                raise AssertionError(f"aggregate {field} mismatch")
    if any(r["supported"] != "not_evaluable" for r in read_csv(work / "results/hypotheses.csv")):
        raise AssertionError("synthetic data must not confirm real hypotheses")
    if "SYNTETICKÉ LOKÁLNÍ TESTY" not in (work / "results/report.md").read_text(encoding="utf-8"):
        raise AssertionError("missing synthetic-result warning")
    return dict(runs=len(actual), terminal_failures=sum(v["mode"] == 8 for v in expected.values()), aggregate_rows=len(metrics))


def create_fixture(out):
    work = Path(private_path(out))
    work.mkdir(parents=True, exist_ok=False)
    make_cases(work)
    shutil.copyfile(Path(ROOT, "data/holdout_blueprint.json"), work / "data/holdout_blueprint.json")
    (work / "prompts").mkdir()
    for name in ("P1_baseline", "P2_structured", "P3A_candidate", "P3B_candidate"):
        for lang in ("cs", "en"):
            filename = f"{name}_{lang}.txt"
            shutil.copyfile(Path(ROOT, "prompts", filename), work / "prompts" / filename)
    # Only in this synthetic workspace, never in the actual prompts directory.
    for lang in ("cs", "en"):
        shutil.copyfile(work / "prompts" / f"P3B_candidate_{lang}.txt", work / "prompts" / f"P3_final_{lang}.txt")
    (work / "source.txt").write_text("SYNTHETIC evidence snapshot, not a downloaded source", encoding="utf-8")
    run_cli("validate_cases.py", "--data-dir", work / "data", "--test-file", work / "data/cases_test.jsonl")
    expected = {}
    for phase in ("dev", "val", "test", "repeat"):
        plan = work / "runs" / f"run_plan_{phase}.csv"
        run_cli("make_run_plan.py", "--synthetic", "--phase", phase, "--systems", ",".join(SYSTEMS),
                "--data-dir", work / "data", "--test-file", work / "data/cases_test.jsonl", "--prompts-dir", work / "prompts", "--out", plan)
        expected.update(fill_runs(work, phase))
        run_cli("check_citations.py", "--synthetic", "--runs", plan, "--data-dir", work / "data", "--test-file", work / "data/cases_test.jsonl",
                "--out-dir", work / "annotation" / phase, "--key-dir", work / "key", "--offline", "--salt", "synthetic-test-salt")
        rate_export(work, phase, expected)
    run_cli("score.py", "--synthetic", "--runs", work / "runs/run_plan_*.csv", "--annotation-dir", work / "annotation", "--key-dir", work / "key",
            "--data-dir", work / "data", "--test-file", work / "data/cases_test.jsonl", "--prompts-dir", work / "prompts",
            "--out", work / "results", "--systems", ",".join(SYSTEMS), "--focus", "sys_D", "--boot", "200")
    summary = assert_fixture(work, expected)
    (work / "fixture_expected.json").write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="new absolute output directory outside Git; default is disposable")
    args = ap.parse_args()
    if args.out:
        if not Path(args.out).is_absolute():
            ap.error("--out must be absolute")
        summary = create_fixture(args.out)
        print(f"SYNTHETIC software-test fixture: {summary}; saved to {args.out}. Not product results.")
    else:
        with tempfile.TemporaryDirectory(prefix="czai-offline-") as tmp:
            summary = create_fixture(Path(tmp, "fixture"))
        print(f"SYNTHETIC software-test fixture passed: {summary}; temporary data removed. No product calls.")


if __name__ == "__main__":
    main()
