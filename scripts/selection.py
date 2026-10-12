"""Recompute the prespecified P3 choice from immutable, self-contained ratings."""

import copy
import math
from pathlib import Path

from common import finite_number, unique_index, validate_pair_rows
from replay_paths import resolve_input


def choose_candidate(means, lengths):
    if set(means) != set(lengths) or not set(means) <= {"P3A", "P3B"} or not means:
        raise ValueError("invalid candidate scores/lengths")
    if any(
        not isinstance(v, (float, int))
        or isinstance(v, bool)
        or finite_number(v) is None
        or not 0 <= v <= 1
        for v in means.values()
    ):
        raise ValueError("candidate precision must be finite in [0,1]")
    if any(
        not isinstance(v, (float, int))
        or isinstance(v, bool)
        or finite_number(v) is None
        or v < 0
        for v in lengths.values()
    ):
        raise ValueError("candidate lengths must be finite and nonnegative")
    if len(means) == 1:
        return next(iter(means))
    # No decimal rounding: only the input floats' representation error at .02.
    tolerance = math.ulp(means["P3A"]) + math.ulp(means["P3B"])
    if abs(means["P3A"] - means["P3B"]) < 0.02 - tolerance:
        return min(means, key=lambda c: (lengths[c], c))
    return max(means, key=means.get)


def validation_selection(snapshot, runs, cases, config, prompts_dir):
    from score import load_answers

    if (
        not isinstance(snapshot, dict)
        or snapshot.get("schema_version") != 1
        or snapshot.get("kind") != "scoring_input_snapshot"
    ):
        raise ValueError("invalid validation scoring snapshot")
    tables = snapshot.get("tables", {})
    if not isinstance(tables, dict):
        raise ValueError("invalid validation snapshot tables")
    for name in ("runs", "key", "pairs", "answers", "meta"):
        if not isinstance(tables.get(name), list) or any(
            not isinstance(r, dict) for r in tables[name]
        ):
            raise ValueError("missing/invalid validation snapshot table: " + name)
    for name, field in (
        ("runs", "run_id"),
        ("key", "blind_answer_id"),
        ("answers", "blind_answer_id"),
        ("meta", "blind_answer_id"),
    ):
        unique_index(tables[name], field, "snapshot " + name)
    unique_index(tables["key"], "run_id", "snapshot key")
    validate_pair_rows(tables["pairs"], "snapshot pairs")
    recorded = {r["run_id"]: r for r in tables["runs"] if r.get("phase") == "val"}
    if recorded != unique_index(runs, "run_id", "validation plans"):
        raise ValueError(
            "validation scoring snapshot differs from completed validation plans"
        )
    ids = set(recorded)
    keys = [k for k in tables["key"] if k.get("run_id") in ids]
    if {k["run_id"] for k in keys} != {
        r["run_id"] for r in runs if r["run_status"] == "completed"
    }:
        raise ValueError(
            "validation snapshot key must cover exactly completed validation runs"
        )
    bids = {k["blind_answer_id"] for k in keys}
    pairs = copy.deepcopy(
        [p for p in tables["pairs"] if p.get("blind_answer_id") in bids]
    )
    answers = [a for a in tables["answers"] if a.get("blind_answer_id") in bids]
    if {a["blind_answer_id"] for a in answers} != bids:
        raise ValueError("validation snapshot lacks final answer ratings")
    scored, errors = load_answers(
        runs,
        keys,
        pairs,
        answers,
        cases,
        False,
        {a["blind_answer_id"]: a for a in tables["meta"]},
    )
    if errors:
        raise ValueError("invalid validation ratings: " + "; ".join(errors))
    cells = {}
    for system in config["systems"]:
        for cond in ["P2"] + config["val_candidates"]:
            items = [
                a for a in scored if a["system"] == system and a["condition"] == cond
            ]
            if not items:
                raise ValueError(
                    "validation snapshot has no scored cell: " + system + "/" + cond
                )
            cells[(system, cond)] = {
                "precision": math.fsum(a["precision"] for a in items) / len(items),
                "n_cases": len({a["task_id"] for a in items}),
                "n_answers": len(items),
            }
    means = {
        c: math.fsum(cells[(s, c)]["precision"] for s in config["systems"])
        / len(config["systems"])
        for c in config["val_candidates"]
    }
    lengths = {
        c: sum(
            len(
                Path(
                    resolve_input(Path(prompts_dir, f"{c}_candidate_{lang}.txt"))
                ).read_text(encoding="utf-8")
            )
            for lang in ("cs", "en")
        )
        / 2
        for c in config["val_candidates"]
    }
    baseline = math.fsum(
        cells[(s, "P2")]["precision"] for s in config["systems"]
    ) / len(config["systems"])
    return {
        "selected_candidate": choose_candidate(means, lengths),
        "precision_means": means,
        "mean_prompt_characters": lengths,
        "p2_precision": baseline,
    }, cells


def check_validation_metrics(rows, cells):
    val = [r for r in rows if r.get("split") == "val"]
    if len(val) != len(cells) or {
        (r.get("system"), r.get("condition")) for r in val
    } != set(cells):
        raise ValueError(
            "validation_metrics has missing, duplicate or unexpected validation cells"
        )
    for r in val:
        expected = cells[(r["system"], r["condition"])]
        p = finite_number(r.get("precision"))
        if p is None or not 0 <= p <= 1 or abs(p - expected["precision"]) > 0.000051:
            raise ValueError(
                "validation_metrics precision differs from recomputed ratings (or is missing/nonfinite)"
            )
        for field in ("n_cases", "n_answers"):
            if finite_number(r.get(field)) != expected[field]:
                raise ValueError(
                    "validation_metrics " + field + " differs from recomputed ratings"
                )
