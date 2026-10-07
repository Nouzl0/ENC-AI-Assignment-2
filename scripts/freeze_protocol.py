#!/usr/bin/env python3
"""Prepare unsigned templates, seal human-approved gates, or verify their hashes.

No command runs a benchmark or invents approvals. Manifests are private audit records,
not cryptographic signatures; archive them independently before the next phase.
"""
import argparse
import datetime as dt
import os
from pathlib import Path
from replay_paths import configure_path_map
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, SYSTEMS, load_all_cases, read_csv, required_facts, sha256_file
from integrity import (ATTESTATIONS, artifact, collect_csv, config_problems, final_rating_problems,
                       frozen_files, holdout_problems, private_path, read_json,
                       run_artifact_problems, source_evidence_problems, timestamp,
                       verify_freeze, verify_plans, write_json_new)

def template(gate):
    m = dict(schema_version=1, gate=gate, signed_by="", signed_at="",
             attestations={key: False for key in ATTESTATIONS[gate]})
    if gate == "G1":
        m.update(config=dict(systems=SYSTEMS, exclusion_reasons={}, val_candidates=["P3A", "P3B"],
                             repeat_task_ids=[], bootstrap=10000, seed=2026, focus="perplexity",
                             h1_margin=.10, h2_margin=.05),
                 roles=dict(prompt_author="", data_steward="", reference_checker=""),
                 inputs=dict(test_cases="", source_evidence="", pilot_record=""))
    else:
        m["parent_path"] = ""
        if gate == "G2":
            m.update(selected_candidate="", inputs=dict(selection_record="", development_analysis="", validation_metrics="", validation_plans=[]))
        else:
            m["inputs"] = dict(run_plans=[], annotation_dir="", key_dir="", deviations_record="")
    return m


def gate_matrix_problems(runs, cases, config):
    from common import PHASES, finite_number
    errors = []
    expected = set()
    for phase, (split, conditions, indices) in PHASES.items():
        if phase == "val":
            conditions = ["P2"] + config["val_candidates"]
        tasks = [tid for tid, c in cases.items() if c["development_validation_test_split"] == split]
        if phase == "repeat":
            tasks = config["repeat_task_ids"]
        expected.update((phase, t, c, s, i) for t in tasks for c in conditions for s in config["systems"] for i in indices)
    actual = []
    for r in runs:
        if r.get("run_status") == "excluded":
            continue
        i = finite_number(r.get("run_index"))
        actual.append((r.get("phase"), r.get("task_id"), r.get("condition"), r.get("system"), i))
    if len(actual) != len(set(actual)) or set(actual) != expected:
        errors.append("G3 requires the exact prespecified dev/val/test/repeat matrix, including failures")
    return errors


def timing_problems(runs):
    errors = []
    active = [r for r in runs if r["run_status"] != "excluded" and r["phase"] in {"test", "repeat"}]
    for phase in ("test", "repeat"):
        rows = [r for r in active if r["phase"] == phase]
        if not rows:
            continue
        if max(timestamp(r["datetime_end"]) for r in rows) - min(timestamp(r["datetime_start"]) for r in rows) > dt.timedelta(hours=72):
            errors.append(f"{phase}: exceeds 72h window")
        for tid in {r["task_id"] for r in rows}:
            group = [r for r in rows if r["task_id"] == tid]
            if max(timestamp(r["datetime_end"]) for r in group) - min(timestamp(r["datetime_start"]) for r in group) > dt.timedelta(hours=24):
                errors.append(f"{phase}/{tid}: exceeds 24h case window")
    test = [r for r in active if r["phase"] == "test"]
    repeat = [r for r in active if r["phase"] == "repeat"]
    if test and repeat:
        test_end = max(timestamp(r["datetime_end"]) for r in test)
        if min(timestamp(r["datetime_start"]) for r in repeat) < test_end or max(timestamp(r["datetime_end"]) for r in repeat) - test_end > dt.timedelta(hours=72):
            errors.append("repeat is not in the subsequent 72h window")
    return errors


def prepare_manifest(config):
    gate = config.get("gate")
    if gate not in ATTESTATIONS or config.get("schema_version") != 1:
        raise ValueError("wrong template schema/gate")
    if not isinstance(config.get("signed_by"), str) or not config["signed_by"].strip():
        raise ValueError("human signed_by required; never seal an unsigned template")
    signed = timestamp(config.get("signed_at"))
    if signed > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise ValueError("signed_at is in the future")
    if set(config.get("attestations", {})) != set(ATTESTATIONS[gate]) or not all(v is True for v in config["attestations"].values()):
        raise ValueError("all named human attestations must be explicitly true")
    m = dict(config)
    paths = []
    if gate != "G1":
        p, digest = artifact(config.get("parent_path"))
        parent = verify_freeze(p, "G1" if gate == "G2" else "G2")
        if signed < timestamp(parent["signed_at"]):
            raise ValueError("gate timestamp precedes its parent")
        m["parent"] = dict(path=p, sha256=digest)
        m["config"] = parent["config"]
        m["roles"] = parent["roles"]
        m["inputs"] = dict(parent["inputs"], **config["inputs"])
        m.pop("parent_path", None)
    problems = config_problems(m.get("config", {}))
    inputs = m["inputs"]
    for k in ("test_cases", "source_evidence", "pilot_record"):
        inputs[k] = artifact(inputs[k])[0]
    cases = load_all_cases(os.path.join(ROOT, "data"), inputs["test_cases"])
    if gate == "G1":
        roles = m.get("roles", {})
        if not all(roles.get(k) for k in ("prompt_author", "data_steward", "reference_checker")) or roles.get("prompt_author") in {roles.get("data_steward"), roles.get("reference_checker")}:
            problems.append("prompt author must be distinct from private data steward and independent reference checker")
        problems += holdout_problems(cases)
        problems += source_evidence_problems(cases, inputs["source_evidence"])
        for row in read_csv(inputs["source_evidence"]):
            if row.get("verified_by") != roles.get("reference_checker"):
                problems.append("source evidence must name the declared independent reference checker")
            try:
                if timestamp(row.get("checked_at")) > signed:
                    problems.append("G1 signed_at precedes reference verification checked_at")
            except ValueError as e:
                problems.append(f"source evidence checked_at: {e}")
        test_ids = {t for t, c in cases.items() if c["development_validation_test_split"] == "test"}
        if set(m["config"]["repeat_task_ids"]) - test_ids:
            problems.append("repeat_task_ids must belong to the new private holdout")
        paths += [inputs[k] for k in ("test_cases", "source_evidence", "pilot_record")]
        paths += [r["snapshot_file"] for r in read_csv(inputs["source_evidence"])]
    elif gate == "G2":
        chosen = m.get("selected_candidate")
        if chosen not in m["config"]["val_candidates"]:
            problems.append("selected P3 must be a prespecified validation candidate")
        for k in ("selection_record", "development_analysis", "validation_metrics"):
            inputs[k] = artifact(inputs[k])[0]
            paths.append(inputs[k])
        plans = inputs.get("validation_plans", [])
        if not isinstance(plans, list) or not plans:
            raise ValueError("G2 requires the actual completed validation plans")
        plans = inputs["validation_plans"] = [private_path(p) for p in plans]
        val_runs = []
        for p in plans:
            verify_plans(p, m["parent"]["path"])
            val_runs += read_csv(p)
            paths += [p, p + ".manifest.json"]
        expected_val = {(tid, c, s) for tid, case in cases.items() if case["development_validation_test_split"] == "val"
                        for c in ["P2"] + m["config"]["val_candidates"] for s in m["config"]["systems"]}
        cells = [(r["task_id"], r["condition"], r["system"]) for r in val_runs if r["run_status"] != "excluded"]
        if set(cells) != expected_val or len(cells) != len(set(cells)) or any(r["phase"] != "val" or r["run_status"] not in {"completed", "failed", "excluded"} for r in val_runs):
            problems.append("G2 requires the complete prespecified validation run matrix")
        for r in val_runs:
            problems += [f"{r['run_id']}: {e}" for e in run_artifact_problems(r)]
            if timestamp(r["datetime_end"]) > signed:
                problems.append("G2 signed_at precedes a validation run outcome")
        metrics = read_csv(inputs["validation_metrics"])
        required = {(s, c) for s in m["config"]["systems"] for c in ["P2"] + m["config"]["val_candidates"]}
        val = [r for r in metrics if r.get("split") == "val"]
        if {(r.get("system"), r.get("condition")) for r in val} != required or any(int(r.get("n_cases", 0)) != 10 for r in val):
            problems.append("validation_metrics must cover 10 validation tasks for every prespecified candidate/system")
        for lang in ("cs", "en"):
            final = str(Path(ROOT, "prompts", f"P3_final_{lang}.txt"))
            candidate = str(Path(ROOT, "prompts", f"{chosen}_candidate_{lang}.txt"))
            if not os.path.isfile(final) or not os.path.isfile(candidate) or sha256_file(final) != sha256_file(candidate):
                problems.append(f"P3_final_{lang} must be an exact copy of the selected candidate")
            else:
                paths.extend([final, candidate])
                if any(r.get("prompt_sha256") != sha256_file(candidate) for r in val_runs if r["condition"] == chosen and r["language"] == lang):
                    problems.append("selected P3 differs from the prompt actually used during validation")
        paths.append(str(Path(ROOT, "prompts/CHANGELOG.md")))
    else:
        plans = inputs.get("run_plans", [])
        if not isinstance(plans, list) or not plans:
            raise ValueError("G3 requires explicit run_plans")
        plans = inputs["run_plans"] = [private_path(p) for p in plans]
        runs = []
        for p in plans:
            private_path(p)
            verify_plans(p, m["parent"]["path"])
            runs += read_csv(p)
            paths += [p, p + ".manifest.json"]
        for k in ("annotation_dir", "key_dir"):
            inputs[k] = private_path(inputs[k])
            if not os.path.isdir(inputs[k]):
                raise ValueError(f"missing {k}")
            paths += [str(p) for p in Path(inputs[k]).rglob("*") if p.is_file()]
            for p in paths:
                private_path(p)
        inputs["deviations_record"] = artifact(inputs["deviations_record"])[0]
        paths.append(inputs["deviations_record"])
        for row in runs:
            problems += [f"{row['run_id']}: {e}" for e in run_artifact_problems(row)]
            if timestamp(row["datetime_end"]) > signed:
                problems.append("G3 signed_at precedes a run outcome")
            for k in ("answer_file", "raw_answer_file", "screenshot_file", "attempt1_file", "failure_artifact_file"):
                if row.get(k) and os.path.isfile(row[k]):
                    paths.append(row[k])
        problems += gate_matrix_problems(runs, cases, m["config"])
        problems += final_rating_problems(runs, inputs["annotation_dir"], inputs["key_dir"], cases)
        from score import load_answers
        _, errors = load_answers(runs, collect_csv(inputs["key_dir"], "blind_key.csv"),
                                 collect_csv(inputs["annotation_dir"], "pairs_rated.csv"),
                                 collect_csv(inputs["annotation_dir"], "answers_rated.csv"), cases, False)
        problems += errors
        windows = timing_problems(runs) if not problems else []
        # Timing departures remain visible; a nonempty written deviation record is mandatory.
        m["timing_deviations"] = windows
        for row in collect_csv(inputs["annotation_dir"], "pairs_rated.csv"):
            if row.get("evidence_snapshot"):
                paths.append(row["evidence_snapshot"])
                if timestamp(row.get("evidence_checked_at")) > signed:
                    problems.append("G3 signed_at precedes a source decision")
        for row in collect_csv(inputs["annotation_dir"], "run_day_evidence.csv"):
            if row.get("snapshot_file"):
                paths.append(row["snapshot_file"])
                if timestamp(row.get("checked_at")) > signed:
                    problems.append("G3 signed_at precedes RUN_DAY reference verification")
    if problems:
        raise ValueError("Cannot seal gate:\n" + "\n".join(problems))
    m["files"] = frozen_files(gate, paths)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--template", choices=sorted(ATTESTATIONS))
    action.add_argument("--seal", help="filled, human-approved private config JSON")
    action.add_argument("--verify", help="private sealed manifest JSON")
    ap.add_argument("--path-map", help="read-time relocation for --verify only; never rewrite/reseal an original gate")
    ap.add_argument("--out", help="new private output file; never overwrites")
    args = ap.parse_args()
    if args.path_map and not args.verify:
        ap.error("--path-map is only allowed with --verify")
    try:
        configure_path_map(args.path_map, ROOT)
        if args.verify:
            m = verify_freeze(args.verify)
            print(f"{m['gate']}: hashes and declared approvals verified (not a digital signature)")
        else:
            out = private_path(args.out)
            m = template(args.template) if args.template else prepare_manifest(read_json(private_path(args.seal)))
            write_json_new(out, m)
            print(f"{m['gate']}: {'UNSIGNED template' if args.template else 'sealed audit manifest'} -> {out}")
    except (ValueError, OSError, KeyError, TypeError) as e:
        ap.exit(1, f"{e}\n")


if __name__ == "__main__":
    main()
