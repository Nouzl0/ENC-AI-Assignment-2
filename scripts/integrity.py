"""Private paths, reproducible freezes and immutable plans. No product calls."""
import datetime as dt
import json
import math
import os
from pathlib import Path
from replay_paths import input_glob, resolve_input

from common import (ROOT, SYSTEMS, META_FILL_COLUMNS, constraint_problems, diagnostic_problems, finite_number, key_fact_problems, load_all_cases,
                    read_csv, required_facts, run_problems, sha256_file, unique_index, unique_json_object)

ATTESTATIONS = {
    "G1": ["pilot_calibrated", "independent_references_checked", "fresh_holdout_private",
           "prompt_author_has_not_seen_holdout", "roles_allow_no_own_run_rating",
           "systems_availability_checked", "protocol_approved"],
    "G2": ["dev_only_optimization", "validation_selection_recorded",
           "no_test_access_before_freeze", "p3_changelog_complete"],
    "G3": ["independent_raw_ratings_preserved", "disagreements_resolved",
           "no_selective_exclusions", "deviations_recorded"],
}


def private_path(path):
    if not path:
        raise ValueError("missing private path (use a directory outside the Git worktree)")
    if not os.path.isabs(os.fspath(path)):
        raise ValueError("private artifact path must be absolute")
    p = Path(resolve_input(path)).resolve()
    if p == Path(ROOT) or Path(ROOT) in p.parents:
        raise ValueError(f"private artifact must be outside the worktree, also after resolving symlinks: {p}")
    return str(p)


def timestamp(value):
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}")
    if result.utcoffset() is None:
        raise ValueError("timestamp requires a UTC offset, e.g. 2026-10-12T14:03:00+02:00")
    return result


def read_json(path):
    with open(resolve_input(path), encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=unique_json_object)


def write_json_new(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def artifact(path, digest=None):
    p = private_path(path)
    if not os.path.isfile(p) or os.path.getsize(p) == 0:
        raise ValueError(f"missing/empty artifact: {p}")
    actual = sha256_file(p)
    if digest is not None and digest != actual:
        raise ValueError(f"artifact SHA-256 mismatch: {p}")
    return p, actual


def config_problems(config):
    errors = []
    systems = config.get("systems", [])
    if (not isinstance(systems, list) or not 4 <= len(systems) <= 5
            or len(set(systems)) != len(systems) or set(systems) - set(SYSTEMS)):
        errors.append("prespecify 4 or 5 distinct known systems")
    if config.get("focus") not in systems:
        errors.append("H1 focus must be included in systems")
    for excluded in set(SYSTEMS) - set(systems):
        if not config.get("exclusion_reasons", {}).get(excluded, "").strip():
            errors.append(f"missing written access/availability/suitability reason for {excluded}")
    if config.get("val_candidates") not in (["P3A"], ["P3B"], ["P3A", "P3B"]):
        errors.append("val_candidates must be P3A, P3B, or both (fixed before validation)")
    if config.get("bootstrap") != 10000 or config.get("seed") != 2026:
        errors.append("protocol fixes bootstrap=10000 and seed=2026")
    if config.get("h1_margin") != .10 or config.get("h2_margin") != .05:
        errors.append("protocol fixes h1_margin=.10 and h2_margin=.05")
    repeat = config.get("repeat_task_ids")
    if not isinstance(repeat, list) or len(set(repeat)) != len(repeat) or len(repeat) < 5:
        errors.append("prespecify at least 5 distinct repeat_task_ids before G1")
    return errors


def source_evidence_problems(cases, path):
    """All reference facts require an independently verified, hashed snapshot."""
    rows = read_csv(private_path(path))
    index = {}
    errors = []
    for row in rows:
        key = (row.get("task_id"), row.get("fact_id"))
        if key in index:
            errors.append(f"duplicate reference evidence: {key}")
        index[key] = row
    for case in cases.values():
        ref = case["reference_answer_or_tests"]
        facts = [(f"RF{i}", f, "required") for i, f in enumerate(required_facts(case), 1)]
        facts += [(f"OF{i}", f, "optional") for i, f in enumerate(ref.get("optional_facts", []), 1)]
        for fid, fact, kind in facts:
            row = index.get((case["task_id"], fid), {})
            prefix = f"{case['task_id']}/{fid}"
            if (row.get("verification_status") != "verified" or row.get("fact_text") != fact
                    or not isinstance(row.get("reference_value"), str) or not row["reference_value"].strip()
                    or row.get("reference_kind") != kind or not row.get("verified_by")):
                errors.append(f"{prefix}: missing verified evidence matching the current fact")
                continue
            if not row.get("url", "").startswith(("https://", "http://")) or not row.get("locator") or not row.get("excerpt_or_summary"):
                errors.append(f"{prefix}: missing URL/locator/excerpt or summary")
            try:
                checked = timestamp(row.get("checked_at"))
                valid_as_of = case.get("reference_valid_as_of")
                if valid_as_of == "RUN_DAY":
                    valid_as_of = checked.astimezone(dt.timezone.utc).date().isoformat()
                if (not isinstance(valid_as_of, str)
                        or dt.date.fromisoformat(valid_as_of).isoformat() != valid_as_of):
                    raise ValueError("reference_valid_as_of must be YYYY-MM-DD or RUN_DAY")
                if row.get("valid_as_of") != valid_as_of:
                    raise ValueError("valid_as_of must match the static reference or UTC check date for RUN_DAY")
                if not row.get("snapshot_sha256"):
                    raise ValueError("missing snapshot_sha256")
                artifact(row.get("snapshot_file"), row["snapshot_sha256"])
            except ValueError as e:
                errors.append(f"{prefix}: {e}")
    expected = {(c["task_id"], f"{kind}{i}") for c in cases.values()
                for kind, facts in (("RF", required_facts(c)), ("OF", c["reference_answer_or_tests"].get("optional_facts", [])))
                for i, _ in enumerate(facts, 1)}
    if set(index) != expected:
        errors.append("reference evidence must contain exactly the current RF/OF units")
    return errors


def holdout_problems(cases):
    from validate_cases import validate_case, tokens, jaccard, holdout_stratification_problems
    errors = []
    test = [c for c in cases.values() if c.get("development_validation_test_split") == "test"]
    if len(cases) < 40 or len(test) < 10:
        errors.append("assignment requires >=40 cases including >=10 private test cases")
    errors += holdout_stratification_problems(test, str(Path(ROOT, "data/holdout_blueprint.json")))
    for split in ("dev", "val", "test"):
        rows = [c for c in cases.values() if c.get("development_validation_test_split") == split]
        for c in rows:
            errors.extend(validate_case(c, split))
            if c.get("schema_version") != 2:
                errors.append(f"{c['task_id']}: G1 requires schema_version=2")
        if not rows or sum(c.get("edge_case_type") != "none" for c in rows) / len(rows) < .2:
            errors.append(f"{split}: requires >=20% edge cases")
    published = [json.loads(l, object_pairs_hook=unique_json_object) for l in
                 Path(ROOT, "data/published_test_candidates.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    exposed = published + [c for c in cases.values() if c not in test]
    for c in test:
        for old in exposed:
            if c["task_id"] == old["task_id"] or jaccard(tokens(c["user_prompt"]), tokens(old["user_prompt"])) >= .5:
                errors.append(f"{c['task_id']}: overlaps an exposed dev/val/published candidate {old['task_id']}")
    return errors


def frozen_files(gate, inputs):
    """Research-critical repository files; candidate P3 stays editable until G2."""
    fixed = ["PROTOCOL.md", "annotation/rubric.md", "annotation/calibration.md", "data/cases_dev.jsonl", "data/cases_val.jsonl", "data/holdout_blueprint.json"]
    fixed += [str(p.relative_to(ROOT)) for p in Path(ROOT, "scripts").glob("*.py")]
    fixed += [f"prompts/{name}_{lang}.txt" for name in ("P1_baseline", "P2_structured") for lang in ("cs", "en")]
    paths = [str(Path(ROOT, p)) for p in fixed] if gate == "G1" else []
    paths += list(inputs)
    return {str(Path(resolve_input(p)).resolve()): sha256_file(p) for p in sorted(set(paths))}


def verify_freeze(path, gate=None):
    path = private_path(path)
    m = read_json(path)
    if m.get("schema_version") != 1 or m.get("gate") not in {"G1", "G2", "G3"} or (gate and m["gate"] != gate):
        raise ValueError("wrong freeze schema/gate")
    if not m.get("signed_by") or set(m.get("attestations", {})) != set(ATTESTATIONS[m["gate"]]) or not all(v is True for v in m["attestations"].values()):
        raise ValueError("unsigned/incomplete gate; a template is not a freeze")
    timestamp(m.get("signed_at"))
    if not m.get("files"):
        raise ValueError("freeze has no bound files")
    for p, digest in m["files"].items():
        if not os.path.isfile(resolve_input(p)) or sha256_file(p) != digest:
            raise ValueError(f"frozen file changed/missing: {p}")
    if m["gate"] != "G1":
        parent = m.get("parent", {})
        artifact(parent.get("path"), parent.get("sha256", ""))
        prev = verify_freeze(parent["path"], "G1" if m["gate"] == "G2" else "G2")
        if timestamp(m["signed_at"]) < timestamp(prev["signed_at"]):
            raise ValueError("gate timestamp precedes its parent")
        if m.get("config") != prev["config"] or m.get("inputs", {}).get("test_cases") != prev["inputs"]["test_cases"]:
            raise ValueError("gate changed prespecified config or test data")
    errors = config_problems(m.get("config", {}))
    if errors:
        raise ValueError("; ".join(errors))
    # Required file bindings cannot be omitted by manually trimming a manifest.
    expected = set(frozen_files("G1", [m["inputs"]["test_cases"], m["inputs"]["source_evidence"], m["inputs"]["pilot_record"]])) if m["gate"] == "G1" else set()
    if m["gate"] == "G1":
        expected |= {private_path(r["snapshot_file"]) for r in read_csv(m["inputs"]["source_evidence"])}
    if m["gate"] == "G2":
        expected = {str(Path(ROOT, "prompts", f"P3_final_{lang}.txt")) for lang in ("cs", "en")}
        expected |= {m["inputs"][k] for k in ("selection_record", "development_analysis", "validation_metrics", "validation_scoring_inputs")}
        expected |= {str(Path(ROOT, "prompts", f"{c}_candidate_{lang}.txt")) for c in m["config"]["val_candidates"] for lang in ("cs", "en")}
        expected.add(str(Path(ROOT, "prompts/CHANGELOG.md")))
        expected |= set(m["inputs"]["validation_plans"])
        expected |= {p + ".manifest.json" for p in m["inputs"]["validation_plans"]}
        from selection import check_validation_metrics, validation_selection
        runs = [r for p in m["inputs"]["validation_plans"] for r in read_csv(p)]
        snapshot = read_json(m["inputs"]["validation_scoring_inputs"])
        summary, cells = validation_selection(snapshot, runs, load_all_cases(os.path.join(ROOT, "data"), m["inputs"]["test_cases"]), m["config"], Path(ROOT, "prompts"))
        if snapshot.get("mode") != "preliminary" or snapshot.get("freeze") != m["parent"]:
            raise ValueError("validation snapshot parent/mode differs")
        problems = validation_source_problems(snapshot, runs, timestamp(m["signed_at"]))
        if problems:
            raise ValueError("; ".join(problems))
        check_validation_metrics(read_csv(m["inputs"]["validation_metrics"]), cells)
        if summary != m.get("selection_summary") or summary["selected_candidate"] != m.get("selected_candidate"):
            raise ValueError("selection_summary/selected_candidate differs from recomputed validation")
        for r in runs:
            expected |= {r[k] for k in ("answer_file", "raw_answer_file", "screenshot_file", "attempt1_file", "failure_artifact_file") if r.get(k) and os.path.isfile(resolve_input(r[k]))}
        bids = {k["blind_answer_id"] for k in snapshot["tables"]["key"] if k["run_id"] in {r["run_id"] for r in runs}}
        expected |= {p["evidence_snapshot"] for p in snapshot["tables"]["pairs"] if p.get("evidence_snapshot") and p["blind_answer_id"] in bids}
    if m["gate"] == "G3":
        expected = set(m["inputs"]["run_plans"])
        expected |= {p + ".manifest.json" for p in m["inputs"]["run_plans"]}
        expected |= {str(p.resolve()) for k in ("annotation_dir", "key_dir") for p in Path(resolve_input(m["inputs"][k])).rglob("*") if p.is_file()}
        expected.add(m["inputs"]["deviations_record"])
        for p in m["inputs"]["run_plans"]:
            for r in read_csv(p):
                expected |= {str(Path(resolve_input(r[k])).resolve()) for k in ("answer_file", "raw_answer_file", "screenshot_file", "attempt1_file", "failure_artifact_file") if r.get(k) and os.path.isfile(resolve_input(r[k]))}
        for row in collect_csv(m["inputs"]["annotation_dir"], "pairs_rated.csv"):
            if row.get("evidence_snapshot"):
                expected.add(private_path(row["evidence_snapshot"]))
        for row in collect_csv(m["inputs"]["annotation_dir"], "run_day_evidence.csv"):
            expected.add(private_path(row["snapshot_file"]))
    bound_paths = [str(Path(resolve_input(p)).resolve()) for p in m["files"]]
    if len(bound_paths) != len(set(bound_paths)) or not {str(Path(resolve_input(p)).resolve()) for p in expected} <= set(bound_paths):
        raise ValueError("freeze omits required bindings")
    return m


def immutable_rows(rows):
    # CSV is the interchange format: DictReader returns strings even when the
    # generator used ints. Normalize before serializing the immutable sidecar.
    return [{k: "" if v is None else str(v) for k, v in r.items() if k not in META_FILL_COLUMNS} for r in rows]


def bind_plan(path, rows, freeze=None, synthetic=False, pilot=False, prompts_dir=None):
    write_json_new(path + ".manifest.json", {
        "schema_version": 1, "synthetic": synthetic, "pilot": pilot,
        "freeze": {"path": str(Path(freeze).resolve()), "sha256": sha256_file(freeze)} if freeze else None,
        "rows": immutable_rows(rows),
        "prompts": {str(Path(prompts_dir, r["prompt_file"]).resolve()): sha256_file(Path(prompts_dir, r["prompt_file"])) for r in rows} if prompts_dir else {},
    })


def verify_plans(pattern, freeze=None, synthetic=False, pilot=False):
    paths = input_glob(pattern)
    if not paths:
        raise ValueError("no run plans matched")
    for path in paths:
        if not synthetic:
            private_path(path)
        m = read_json(path + ".manifest.json")
        if m.get("schema_version") != 1 or m.get("synthetic") != synthetic or m.get("pilot", False) != pilot:
            raise ValueError("wrong/missing immutable plan manifest or synthetic mode")
        if not synthetic and not pilot:
            bound = m.get("freeze") or {}
            artifact(bound.get("path"), bound.get("sha256", ""))
            gate = verify_freeze(bound["path"])
            if any(r.get("phase") in {"test", "repeat"} for r in m["rows"]) and gate["gate"] != "G2":
                raise ValueError("test/repeat plan must be bound to G2")
            if any(r.get("phase") in {"dev", "val"} for r in m["rows"]) and gate["gate"] != "G1":
                raise ValueError("dev/val plan must be bound to G1")
            if freeze:
                target = verify_freeze(freeze)
                target_path = str(Path(resolve_input(freeze)).resolve())
                while target["gate"] != gate["gate"] and target.get("parent"):
                    target_path = str(Path(resolve_input(target["parent"]["path"])).resolve())
                    target = verify_freeze(target_path)
                if str(Path(resolve_input(bound["path"])).resolve()) != target_path or sha256_file(target_path) != bound["sha256"]:
                    raise ValueError("run plan belongs to a different protocol")
        for p, digest in m.get("prompts", {}).items():
            if not os.path.isfile(resolve_input(p)) or sha256_file(p) != digest:
                raise ValueError(f"prompt used by plan changed: {p}")
        planned = unique_index(m.get("rows", []), "run_id", "immutable plan")
        rows = read_csv(path)
        if not (synthetic or pilot):
            for r in rows:
                if r.get("run_status") in {"completed", "failed", "excluded"} and timestamp(r.get("datetime_start")) < timestamp(gate["signed_at"]):
                    raise ValueError("run precedes its required freeze")
        if pilot and (m.get("freeze") or any(r.get("phase") != "dev" for r in rows)):
            raise ValueError("pilot permits only unfrozen dev calibration plans")
        actual = unique_index(rows, "run_id", "runs")
        for rid, original in planned.items():
            if rid not in actual or immutable_rows([actual[rid]])[0] != original:
                raise ValueError(f"planned row removed/changed: {rid}")
        extras = set(actual) - set(planned)
        authorized = set()
        for rid in planned:
            r = actual[rid]
            replacement = r.get("replacement_run_id", "")
            if r.get("run_status") == "excluded":
                if not replacement or replacement not in extras:
                    raise ValueError(f"{rid}: excluded operator error requires a recorded replacement")
                new = actual[replacement]
                if new.get("replaces_run_id") != rid or new.get("run_status") not in {"completed", "failed"}:
                    raise ValueError(f"{rid}: invalid replacement")
                a, b = immutable_rows([r, new])
                for k in ("seq", "run_id", "answer_file"):
                    a.pop(k, None); b.pop(k, None)
                if a != b:
                    raise ValueError(f"{rid}: replacement changed the experimental condition")
                authorized.add(replacement)
            elif replacement:
                raise ValueError(f"{rid}: only excluded rows may authorize a replacement")
        if extras != authorized:
            raise ValueError("unplanned/unauthorized extra run rows")
    return paths


def run_artifact_problems(row):
    errors = run_problems(row)
    if row.get("run_status") == "planned":
        return errors
    for f in ("model_visible", "plan_tier", "operator", "manual_intervention", "cost_note"):
        if not row.get(f):
            errors.append(f"missing {f} (use explicit unknown/none where appropriate)")
    try:
        start, end = timestamp(row.get("datetime_start")), timestamp(row.get("datetime_end"))
        if end < start:
            raise ValueError("datetime_end precedes start")
        latency = finite_number(row.get("latency_s"))
        if latency is not None and abs((end - start).total_seconds() - latency) > 5:
            raise ValueError("latency_s differs from timestamp duration by >5s")
    except ValueError as e:
        errors.append(str(e))
    for f in ("n_sources_shown", "tool_calls_visible"):
        n = finite_number(row.get(f))
        if row.get(f) != "unknown" and (n is None or n < 0 or not n.is_integer()):
            errors.append(f"invalid {f}: nonnegative integer or unknown")
    if row.get("search_used") not in {"yes", "no", "unclear"}:
        errors.append("search_used must be yes/no/unclear")
    if row.get("turns") not in {"1", "2"}:
        errors.append("turns must be 1 or 2 (only the prespecified clarification)")
    fields = [("screenshot_file", "screenshot_sha256")]
    if row.get("run_status") == "completed":
        fields += [("answer_file", "answer_sha256"), ("raw_answer_file", "raw_answer_sha256")]
    if row.get("run_status") in {"failed", "excluded"}:
        fields += [("failure_artifact_file", "failure_artifact_sha256")]
    if finite_number(row.get("retries")) == 1:
        fields += [("attempt1_file", "attempt1_sha256")]
    for f, h in fields:
        try:
            if not row.get(h):
                raise ValueError(f"missing {h}")
            artifact(row.get(f), row[h])
        except ValueError as e:
            errors.append(str(e))
    if row.get("run_status") == "completed" and row.get("answer_sha256") != row.get("raw_answer_sha256") and row.get("manual_intervention") == "none":
        errors.append("normalized answer differs from raw export; document the normalization intervention")
    if row.get("run_status") == "excluded" and (not row.get("notes") or not row.get("replacement_run_id")):
        errors.append("excluded operator error requires explanation and replacement_run_id")
    return errors


def collect_csv(directory, name):
    return [r for p in sorted(Path(resolve_input(directory)).rglob(name)) for r in read_csv(p)]


def source_decision_problems(row, run, signed_at=None):
    """Final citation decisions require timely local evidence, including NA/FAB logs."""
    if row.get("citation_n") in {"", None}:
        return []
    try:
        checked = timestamp(row.get("evidence_checked_at"))
        end = timestamp(run["datetime_end"])
        if not end <= checked <= end + dt.timedelta(days=7):
            raise ValueError("source decision must be checked within 7 days after the run")
        if signed_at is not None and checked > signed_at:
            raise ValueError("gate signed_at precedes a source decision")
        # A missing source marker still needs an original-answer/check-log snapshot.
        missing_source = (row.get("rating") == "FAB" and row.get("citation_n") not in {"", "*", None}
                          and not row.get("url") and not row.get("source_line"))
        if (not all(row.get(k) for k in ("evidence_locator", "evidence_excerpt", "evidence_sha256"))
                or (not missing_source and not row.get("evidence_url"))):
            raise ValueError("missing source-decision evidence")
        artifact(row.get("evidence_snapshot"), row["evidence_sha256"])
    except ValueError as e:
        return [f"{row['pair_id']}: {e}"]
    return []


def validation_source_problems(snapshot, runs, signed_at):
    """Validated snapshot source decisions must already exist when G2 is signed."""
    outcomes = {r["run_id"]: r for r in runs if r.get("phase") == "val"}
    key = {k["blind_answer_id"]: outcomes[k["run_id"]] for k in snapshot["tables"]["key"] if k["run_id"] in outcomes}
    return [e for p in snapshot["tables"]["pairs"] if p["blind_answer_id"] in key
            for e in source_decision_problems(p, key[p["blind_answer_id"]], signed_at)]


def validation_rating_binding_problems(snapshot, runs, annotation_dir, key_dir):
    """Post-G2 validation ratings cannot silently change before final scoring."""
    ids = {r["run_id"] for r in runs if r.get("phase") == "val"}
    tables = snapshot["tables"]
    keys = [k for k in tables["key"] if k["run_id"] in ids]
    bids = {k["blind_answer_id"] for k in keys}
    errors = []
    for name, filename, directory, field in (("key", "blind_key.csv", key_dir, "blind_answer_id"),
                                             ("answers", "answers_rated.csv", annotation_dir, "blind_answer_id"),
                                             ("pairs", "pairs_rated.csv", annotation_dir, "pair_id")):
        expected = keys if name == "key" else [r for r in tables[name] if r["blind_answer_id"] in bids]
        current = [r for r in collect_csv(directory, filename) if r["blind_answer_id"] in bids]
        if unique_index(expected, field, "G2 validation " + name) != unique_index(current, field, "G3 validation " + name):
            errors.append("validation " + name + " changed since G2 scoring snapshot")
    return errors


def final_rating_problems(runs, annotation_dir, key_dir, cases):
    errors = []
    key = unique_index(collect_csv(key_dir, "blind_key.csv"), "blind_answer_id", "blind key")
    outcomes = unique_index(runs, "run_id", "runs")
    completed = {r["run_id"] for r in runs if r["run_status"] == "completed"}
    if {r["run_id"] for r in key.values()} != completed:
        errors.append("blind key must cover exactly all completed runs")
    final = collect_csv(annotation_dir, "answers_rated.csv")
    first = collect_csv(annotation_dir, "answers_rated_rater1.csv")
    second = collect_csv(annotation_dir, "answers_rated_rater2.csv")
    indexes = [unique_index(rows, "blind_answer_id", label) for rows, label in ((final, "final"), (first, "rater1"), (second, "rater2"))]
    if set(indexes[0]) != set(key) or set(indexes[1]) != set(key):
        errors.append("final and pre-consensus rater1 must cover every completed answer")
    sample = set()
    for p in Path(resolve_input(key_dir)).rglob("annotation_batch.json"):
        m = read_json(str(p))
        for path, digest in m.get("sheets", {}).items():
            try:
                artifact(path, digest)
            except ValueError as e:
                errors.append(f"original annotation sheet changed: {e}")
        sample.update(m["rater2_ids"])
    if sample != set(indexes[2]) or not sample <= set(key):
        errors.append("rater2 must cover exactly the presampled answers (no selective substitution)")
    strata = {}
    for bid, k in key.items():
        r = outcomes.get(k["run_id"], {})
        strata.setdefault((r.get("phase"), r.get("system"), r.get("condition")), []).append(bid)
    for ids in strata.values():
        if len(set(ids) & sample) < math.ceil(len(ids) * .25):
            errors.append("a phase/system/condition stratum has less than 25% double rating")
    pair_sets = []
    for name, index in zip(("pairs_rated.csv", "pairs_rated_rater1.csv", "pairs_rated_rater2.csv"), indexes):
        rows = collect_csv(annotation_dir, name)
        from common import validate_pair_rows, RATINGS
        validate_pair_rows(rows, name)
        pair_sets.append(rows)
        for row in rows:
            bid = row["blind_answer_id"]
            if bid not in index:
                errors.append(f"{name}: orphan pair {row['pair_id']}")
            if row.get("citation_n") and row.get("rating") not in RATINGS:
                errors.append(f"{name}: missing/invalid rating {row['pair_id']}")
        for bid, answer in index.items():
            if bid not in key:
                errors.append(f"{name}: unknown blind ID {bid}")
                continue
            operator = outcomes[key[bid]["run_id"]].get("operator")
            if not answer.get("rater") or answer["rater"] == operator:
                errors.append(f"{bid}: missing rater or rater evaluates their own run")
            if answer.get("correctness") not in {"0", "1", "2"} or answer.get("segmentation_reviewed") != "yes":
                errors.append(f"{bid}: incomplete raw/final answer-level rating")
            case = cases.get(outcomes[key[bid]["run_id"]]["task_id"], {})
            own_pairs = [p for p in rows if p["blind_answer_id"] == bid]
            errors += [f"{bid}: {e}" for e in key_fact_problems(answer, case, own_pairs)]
            minutes = finite_number(answer.get("check_minutes"))
            if minutes is None or minutes < 0:
                errors.append(f"{bid}: invalid check_minutes (finite and nonnegative required)")
            errors += [f"{bid}: {e}" for e in constraint_problems(answer, case)]
            errors += [f"{bid}: {e}" for e in diagnostic_problems(answer, own_pairs, case)]
            claims = {p["claim_id"] for p in rows if p["blind_answer_id"] == bid}
            if finite_number(answer.get("n_claims")) != len(claims):
                errors.append(f"{bid}: raw/final claim count differs from rating units")
            if any(p.get("rater") != answer.get("rater") for p in rows if p["blind_answer_id"] == bid):
                errors.append(f"{bid}: pair rater differs from answer-level rater")
            if bid in indexes[1] and bid in indexes[2] and indexes[1][bid].get("rater") == indexes[2][bid].get("rater"):
                errors.append(f"{bid}: two raters must be distinct")
    # Snapshots for final source decisions; inaccessible/fabricated also need a check log.
    for row in pair_sets[0]:
        if row.get("citation_n") not in {"", None}:
            errors += source_decision_problems(row, outcomes[key[row["blind_answer_id"]]["run_id"]])
    # Dynamic references are separate dated evidence, not edits to frozen gold data.
    dynamic = collect_csv(annotation_dir, "run_day_evidence.csv")
    expected_dynamic = {}
    for r in runs:
        if r["run_status"] != "completed" or cases[r["task_id"]].get("reference_valid_as_of") != "RUN_DAY":
            continue
        # One date convention regardless of the operator's displayed timezone.
        date = timestamp(r["datetime_start"]).astimezone(dt.timezone.utc).date().isoformat()
        case = cases[r["task_id"]]
        for kind, facts in (("RF", required_facts(case)), ("OF", case["reference_answer_or_tests"].get("optional_facts", []))):
            for i, _ in enumerate(facts, 1):
                expected_dynamic[(r["task_id"], date, f"{kind}{i}")] = r["run_id"]
    dynamic_index = {}
    for d in dynamic:
        unit = (d.get("task_id"), d.get("run_date"), d.get("fact_id"))
        if unit in dynamic_index:
            errors.append(f"{unit}: duplicate RUN_DAY evidence")
        dynamic_index[unit] = d
        try:
            checked = timestamp(d.get("checked_at"))
            if checked.astimezone(dt.timezone.utc).date().isoformat() != d.get("run_date"):
                raise ValueError("RUN_DAY evidence must be checked on the run date (UTC)")
            if (d.get("verification_status") != "verified"
                    or not all(d.get(k) for k in ("reference_value", "verified_by", "locator", "excerpt_or_summary", "snapshot_sha256"))
                    or not d.get("url", "").startswith(("https://", "http://"))):
                raise ValueError("incomplete RUN_DAY evidence")
            artifact(d.get("snapshot_file"), d["snapshot_sha256"])
        except ValueError as e:
            errors.append(f"{unit}: {e}")
    if set(dynamic_index) != set(expected_dynamic):
        errors.append("RUN_DAY evidence must cover exactly every RF/OF unit for each completed task/UTC date")
    # Every changed categorical rating needs a resolved adjudication record.
    disagreements = collect_csv(annotation_dir, "disagreements.csv")
    for kind, left, right, final_rows, id_field, fields in (
            ("answer", first, second, final, "blind_answer_id", ("correctness", "n_claims", "key_facts_supported", "key_fact_evidence", "constraint_results", "acknowledges_uncertainty", "check_minutes")),
            ("pair", pair_sets[1], pair_sets[2], pair_sets[0], "pair_id", ("claim_text", "citation_n", "url", "rating", "source_tier", "time_ok", "error_code", "rater_source_n"))):
        a, b, final_index = (unique_index(rows, id_field, kind) for rows in (left, right, final_rows))
        for iid in set(a) | set(b) | set(final_index):
            bid = iid if kind == "answer" else (a.get(iid) or b.get(iid) or final_index[iid])["blind_answer_id"]
            double_rated = bid in indexes[2]
            values = {"present": ("yes" if iid in a else "no", "yes" if iid in b else "no", "yes" if iid in final_index else "no")}
            if iid in a and iid in final_index:
                values.update({field: (a[iid].get(field, ""), b.get(iid, {}).get(field, ""), final_index[iid].get(field, "")) for field in fields})
            for field, (v1, v2, decision) in values.items():
                # Raters measure their own annotation time; unequal times are not a rating disagreement.
                raw_disagreement = double_rated and field != "check_minutes" and (field == "present" or iid in b) and v1 != v2
                if not raw_disagreement and decision == v1:
                    continue
                logs = [r for r in disagreements if r.get("item_id") == iid and r.get("item_type") == kind and r.get("field") == field]
                if (len(logs) != 1 or not logs[0].get("resolved_by") or not logs[0].get("note")
                        or logs[0].get("resolution") != decision or logs[0].get("rater1_value", "") != v1
                        or logs[0].get("rater2_value", "") != (v2 if double_rated else "")):
                    errors.append(f"{iid}/{field}: missing resolved disagreement matching the final decision")
    return errors
