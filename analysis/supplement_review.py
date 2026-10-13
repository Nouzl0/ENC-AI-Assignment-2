#!/usr/bin/env python3
"""Export independent, blinded human-review inputs for exploratory collections.

This is an offline preparation tool. It does not rate answers, fetch sources,
validate protocol gates, or turn the exploratory collection into a final run.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import random
import re
import shutil
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path, PureWindowsPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_citations import HEAD_RE, markdown_links, stratified_sample, strip_md
from common import (
    ROOT,
    finite_number,
    required_facts,
    sha256_file,
    unique_index,
    unique_json_object,
)
from integrity import timestamp

ANSWER_FIELDS = [
    "blind_answer_id",
    "blind_question_id",
    "language",
    "question",
    "reference_answer",
    "reference_valid_as_of",
    "required_facts",
    "optional_facts",
    "required_constraints",
    "answer_text",
    "recorded_sources",
    "segmentation_reviewed",
    "correctness",
    "key_facts_supported",
    "key_fact_evidence",
    "constraint_results",
    "acknowledges_uncertainty",
    "check_minutes",
    "rater",
    "comment",
]
PAIR_FIELDS = [
    "pair_id",
    "blind_answer_id",
    "claim_id",
    "claim_text",
    "citation_label",
    "url",
    "source_text",
    "segmentation_reviewed",
    "rater_source_label",
    "rating",
    "source_tier",
    "time_ok",
    "evidence_url",
    "evidence_checked_at",
    "evidence_locator",
    "evidence_excerpt",
    "evidence_snapshot",
    "evidence_sha256",
    "evidence_archive_url",
    "error_code",
    "rater",
    "comment",
]
SELECTION_FIELDS = [
    "record_id",
    "task_id",
    "phase",
    "system",
    "condition",
    "run_status",
    "include_in_analysis",
    "blind_answer_id",
    "blind_question_id",
    "rater2_selected",
    "disposition",
]
ARTIFACT_FIELDS = (
    ("answer_file", "answer_sha256"),
    ("raw_answer_file", "raw_answer_sha256"),
    ("rendered_prompt_file", "rendered_prompt_sha256"),
    ("template_file", "template_sha256"),
    ("citation_artifact_file", "citation_artifact_sha256"),
)
MARKER_RE = re.compile(r"\[\d+(?:\.\d+)*(?:\s*[,;–-]\s*\d+(?:\.\d+)*)*\]")
BARE_URL_RE = re.compile(r"https?://[^\s<>\"']+")
SOURCE_LABEL_RE = re.compile(r"^\[(\d+(?:\.\d+)*)\]")
DIGEST_RE = re.compile(r"[0-9a-f]{64}\Z")
README = """# Nezávislé lidské hodnocení

Rozsah tohoto balíčku je exploratorní. Listy obsahují podklady k samostatnému
lidskému posouzení, nikoli již provedené hodnocení. Pracujte nezávisle a do
odevzdání původních listů nesdílejte rozhodnutí s druhým hodnotitelem.

V answers_to_rate.csv je úplný zaznamenaný text odpovědi, otázka a referenční
RF (povinné fakty), OF (nepovinné fakty) a RC (povinné požadavky). Chybějící OF
nepenalizujte jako chybějící RF. Reference a jejich platnost samostatně ověřte;
správnost odpovědi není totéž jako podpora její konkrétní citace.

U referencí označených RUN_DAY uvádí reference_valid_as_of skutečný UTC den
prvního odeslání podle dochovaného časového záznamu. Je to základ relativních
časových požadavků, například publikací nejvýše 30 dní starých. Datum samo
nepotvrzuje referenční hodnoty ani neznamená již provedené lidské hodnocení.

pairs_to_rate.csv obsahuje POUZE NÁVRHY řádků z původního textu. Nejde o schválenou
atomickou segmentaci ani o rozhodnutí, který zdroj tvrzení podporuje. Zkontrolujte
celou odpověď včetně úvodu, doplňků a závěru; rozdělte složená tvrzení, spojte
významové duplicity a doplňte chybějící řádky. Podpůrný citovaný úryvek není další
generované tvrzení. Zachovejte původní citace, jejich neobvyklé značky a URL.

recorded_sources je katalog pouze zaznamenaných URL a zdrojových popisků. Samotná
přítomnost URL neprokazuje přiřazení k tvrzení ani podporu. Prázdný url u návrhu
ponechává přiřazení na vaší kontrole; nativní značky vyhodnoťte podle celého textu
a katalogu. Žádný chybějící zdroj nedoplňujte domněnkou.

Hodnoticí a evidenční buňky jsou prázdné. U každého explicitního vztahu zapište
S2 (plná podpora), S1 (částečná), S0 (bez podpory), NA (nelze ověřit) nebo FAB
(doložené vymyšlení). Nedostupnost zdroje sama o sobě není FAB. Nehodnoticí návrh
označte NONE a vysvětlete proč. Obsahovou správnost zapište na škále 0–2 podle
ověřených povinných faktů a požadavků. Zaznamenejte přesný důkaz, datum kontroly,
locator, vlastní identitu a komentář; nepředvyplňujte neprovedené úkony.
"""


def _reject_constant(value):
    raise ValueError(f"non-finite JSON value: {value}")


def _finite_values(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite numeric value")
    if isinstance(value, dict):
        for item in value.values():
            _finite_values(item)
    elif isinstance(value, list):
        for item in value:
            _finite_values(item)


def _no_symlinks(path):
    path = Path(os.path.abspath(path))
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError(f"symlink paths are not permitted: {path}")
    return path


def _snapshot(path, snapshots):
    path = _no_symlinks(path)
    if not path.is_file():
        raise ValueError(f"missing input file: {path}")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    old = snapshots.get(str(path))
    if old and old["sha256"] != digest:
        raise ValueError(f"input changed while preparing review: {path}")
    snapshots[str(path)] = {"sha256": digest, "bytes": len(data)}
    return data


def _jsonl(path, snapshots):
    rows = []
    for number, line in enumerate(
        _snapshot(path, snapshots).decode("utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(
                line,
                object_pairs_hook=unique_json_object,
                parse_constant=_reject_constant,
            )
            if not isinstance(row, dict):
                raise ValueError("each JSONL row must be an object")
            _finite_values(row)
        except ValueError as error:
            raise ValueError(f"{path}:{number}: {error}") from error
        rows.append(row)
    return rows


def _artifact_path(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError("artifact path must be a nonempty repository-relative string")
    path = Path(value)
    if path.is_absolute() or PureWindowsPath(value).is_absolute() or "\\" in value:
        raise ValueError(f"artifact path must be repository-relative: {value}")
    if ".." in path.parts:
        raise ValueError(f"artifact path escapes repository: {value}")
    target = _no_symlinks(root / path)
    if root not in target.parents:
        raise ValueError(f"artifact path escapes repository: {value}")
    return target


def _output_path(value, root):
    if not Path(value).is_absolute():
        raise ValueError("output directories must be absolute and outside the worktree")
    path = _no_symlinks(value)
    if path == root or root in path.parents:
        raise ValueError("output directories must be outside the worktree")
    if os.path.lexists(path):
        raise ValueError(f"refusing to overwrite existing output: {path}")
    return path


def _case_index(paths, snapshots):
    rows = [row for path in paths for row in _jsonl(path, snapshots)]
    for row in rows:
        if not isinstance(row.get("task_id"), str) or not row["task_id"]:
            raise ValueError("case requires a nonempty task_id")
        if (
            not isinstance(row.get("user_prompt"), str)
            or not row["user_prompt"].strip()
        ):
            raise ValueError(f"{row['task_id']}: missing question")
        ref = row.get("reference_answer_or_tests")
        if not isinstance(ref, dict):
            raise ValueError(f"{row['task_id']}: missing reference units")
        for field in (
            "required_facts",
            "key_facts",
            "optional_facts",
            "required_constraints",
        ):
            units = ref.get(field, [])
            if not isinstance(units, list) or any(
                not isinstance(u, str) for u in units
            ):
                raise ValueError(
                    f"{row['task_id']}: {field} must be a list of text units"
                )
        if not required_facts(row):
            raise ValueError(f"{row['task_id']}: missing required facts")
        for field, value in (
            ("reference_answer", ref.get("reference_answer", "")),
            ("language", row.get("language", "")),
            ("reference_valid_as_of", row.get("reference_valid_as_of", "")),
        ):
            if not isinstance(value, str):
                raise ValueError(f"{row['task_id']}: {field} must be text")
    return unique_index(rows, "task_id", "review cases")


def reference_day(case, record):
    """Resolve RUN_DAY from the recorded, timezone-aware submission only."""
    value = case.get("reference_valid_as_of", "")
    if value != "RUN_DAY":
        return value
    try:
        start = timestamp(record.get("datetime_start"))
    except ValueError as error:
        raise ValueError(
            f"{record['record_id']}: RUN_DAY requires a timezone-aware datetime_start"
        ) from error
    return start.astimezone(dt.timezone.utc).date().isoformat()


def urls_in_text(text):
    """Keep recorded targets, without canonicalization or punctuation repair."""
    links = list(markdown_links(text))
    urls = [url for _, _, _, url, _ in links]
    for match in BARE_URL_RE.finditer(text):
        if not any(start <= match.start() < end for start, end, _, _, _ in links):
            urls.append(match.group(0))
    return list(dict.fromkeys(urls))


class _RecordedLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith(("https://", "http://")):
                self.current = {"citation_label": "", "url": href, "source_text": ""}

    def handle_data(self, data):
        if self.current is not None:
            self.current["source_text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None


def _artifact_sources(data):
    text = data.decode("utf-8")
    sources = []
    if text.lstrip().startswith(("{", "[")):
        value = json.loads(
            text, object_pairs_hook=unique_json_object, parse_constant=_reject_constant
        )
        _finite_values(value)

        def visit(item):
            if isinstance(item, list):
                for entry in item:
                    visit(entry)
            elif isinstance(item, dict):
                url = item.get("href", item.get("url", ""))
                label = item.get("citation_label", item.get("marker", ""))
                description = item.get("label", item.get("text", ""))
                if isinstance(url, str) and url.startswith(("https://", "http://")):
                    sources.append(
                        {
                            "citation_label": label if isinstance(label, str) else "",
                            "url": url,
                            "source_text": description
                            if isinstance(description, str)
                            else "",
                        }
                    )
                for key, child in item.items():
                    if key == "html" and isinstance(child, str):
                        parser = _RecordedLinks()
                        parser.feed(child)
                        sources.extend(parser.links)
                    elif key == "chip_labels" and isinstance(child, list):
                        for chip in child:
                            if isinstance(chip, dict) and isinstance(
                                chip.get("label"), str
                            ):
                                sources.append(
                                    {
                                        "citation_label": chip["label"],
                                        "url": "",
                                        "source_text": chip["label"],
                                    }
                                )
                    elif isinstance(child, (dict, list)):
                        # The steward supplies a response-only artifact, including
                        # native popovers when captured. Nested links stay unassigned
                        # unless the artifact explicitly records their citation label.
                        visit(child)

        visit(value)
    elif "<" in text:
        parser = _RecordedLinks()
        parser.feed(text)
        sources.extend(parser.links)
    return sources


def _section(line):
    for name, expression in HEAD_RE.items():
        match = expression.match(strip_md(line))
        if match:
            return name, bool(match.group(1))
    return None, False


def build_proposals(text, artifacts=()):
    """Conservative, verbatim line proposals; never renumber native labels."""
    sources, lines, section = [], [], "body"
    for line in text.splitlines():
        name, has_content = _section(line)
        if name:
            section = name
            if not has_content:
                continue
        if not line.strip():
            continue
        if section == "sources":
            match = SOURCE_LABEL_RE.match(strip_md(line))
            label = match.group(0) if match else ""
            for url in urls_in_text(line):
                sources.append(
                    {"citation_label": label, "url": url, "source_text": line}
                )
        else:
            lines.append(line)
    for data in artifacts:
        sources.extend(_artifact_sources(data))
    # Unassigned URLs remain visible even when no source-list heading exists.
    known_urls = {source["url"] for source in sources}
    for url in urls_in_text(text):
        if url not in known_urls:
            sources.append({"citation_label": "", "url": url, "source_text": ""})
            known_urls.add(url)
    sources = list({tuple(source.items()): source for source in sources}.values())
    pairs = []
    for number, line in enumerate(lines, 1):
        labels = list(
            dict.fromkeys(match.group(0) for match in MARKER_RE.finditer(line))
        )
        if labels:
            for label in labels:
                members = {
                    f"[{part.strip()}]" for part in re.split(r"[,;]", label[1:-1])
                }
                matched = [
                    source for source in sources if source["citation_label"] in members
                ]
                for source in matched or [{"url": "", "source_text": ""}]:
                    pairs.append(
                        {
                            "claim_id": f"T{number}",
                            "claim_text": line,
                            "citation_label": label,
                            "url": source["url"],
                            "source_text": source["source_text"],
                        }
                    )
        else:
            for url in urls_in_text(line) or [""]:
                pairs.append(
                    {
                        "claim_id": f"T{number}",
                        "claim_text": line,
                        "citation_label": "",
                        "url": url,
                        "source_text": "",
                    }
                )
    return pairs, sources


def _write_csv_new(path, rows, fields):
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fields, lineterminator="\n", extrasaction="raise"
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_jsonl_new(path, rows):
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def export_review(
    registry_path, cases_paths, out_dir, key_dir, seed=20261013, root=ROOT
):
    root = _no_symlinks(root)
    out_dir, key_dir = _output_path(out_dir, root), _output_path(key_dir, root)
    if out_dir == key_dir or out_dir in key_dir.parents or key_dir in out_dir.parents:
        raise ValueError(
            "key and rater output directories must be separate, not nested"
        )
    snapshots = {}
    cases = _case_index(cases_paths, snapshots)
    records = _jsonl(registry_path, snapshots)
    for record in records:
        for field in (
            "record_id",
            "task_id",
            "phase",
            "system",
            "condition",
            "run_status",
        ):
            if not isinstance(record.get(field), str) or not record[field]:
                raise ValueError(f"registry requires a nonempty {field}")
        if record["task_id"] not in cases:
            raise ValueError(f"unknown case: {record['task_id']}")
        if type(record.get("include_in_analysis")) is not bool:
            raise ValueError("include_in_analysis must be a JSON boolean")
        if record["run_status"] not in {"completed", "failed", "excluded", "planned"}:
            raise ValueError(f"unknown run status: {record['run_status']}")
        for field in ("latency_s", "observed_interval_s", "first_attempt_latency_s"):
            value = record.get(field)
            if value not in (None, "", "unknown") and finite_number(value) is None:
                raise ValueError(f"non-finite or invalid {field}")
    unique_index(records, "record_id", "canonical registry")
    eligible = sorted(
        (
            row
            for row in records
            if row["include_in_analysis"] and row["run_status"] == "completed"
        ),
        key=lambda row: row["record_id"],
    )
    contents = {}
    for record in records:
        files = {}
        for field, hash_field in ARTIFACT_FIELDS:
            value, declared = record.get(field), record.get(hash_field)
            if not value:
                if declared:
                    raise ValueError(
                        f"{record['record_id']}: {hash_field} without {field}"
                    )
                continue
            path = _artifact_path(root, value)
            data = _snapshot(path, snapshots)
            if declared:
                if not isinstance(declared, str) or not DIGEST_RE.fullmatch(declared):
                    raise ValueError(f"{record['record_id']}: invalid {hash_field}")
                if hashlib.sha256(data).hexdigest() != declared:
                    raise ValueError(
                        f"{record['record_id']}: SHA-256 mismatch for {field}"
                    )
            elif record in eligible:
                raise ValueError(f"{record['record_id']}: missing {hash_field}")
            files[field] = data
        if record in eligible:
            if (
                "answer_file" not in files
                or not files["answer_file"].decode("utf-8").strip()
            ):
                raise ValueError(
                    f"{record['record_id']}: completed record requires a nonempty answer"
                )
            contents[record["record_id"]] = files
    rng = random.Random(seed)
    rng.shuffle(eligible)
    task_ids = sorted({row["task_id"] for row in eligible})
    rng.shuffle(task_ids)
    question_ids = {task_id: f"Q{i:04d}" for i, task_id in enumerate(task_ids, 1)}
    answers, pairs, key_rows, sample_rows = [], [], [], []
    blind_ids = {}
    for number, record in enumerate(eligible, 1):
        blind_id = f"A{number:04d}"
        blind_ids[record["record_id"]] = blind_id
        case = cases[record["task_id"]]
        reference = case["reference_answer_or_tests"]
        files = contents[record["record_id"]]
        text = files["answer_file"].decode("utf-8")
        proposal_rows, sources = build_proposals(
            text,
            [
                data
                for field, data in files.items()
                if field in {"raw_answer_file", "citation_artifact_file"}
            ],
        )
        answer = dict.fromkeys(ANSWER_FIELDS, "")
        answer.update(
            blind_answer_id=blind_id,
            blind_question_id=question_ids[record["task_id"]],
            language=case.get("language", ""),
            question=case["user_prompt"],
            reference_answer=reference.get("reference_answer", ""),
            reference_valid_as_of=reference_day(case, record),
            required_facts="\n".join(
                f"RF{i}: {unit}" for i, unit in enumerate(required_facts(case), 1)
            ),
            optional_facts="\n".join(
                f"OF{i}: {unit}"
                for i, unit in enumerate(reference.get("optional_facts", []), 1)
            ),
            required_constraints="\n".join(
                f"RC{i}: {unit}"
                for i, unit in enumerate(reference.get("required_constraints", []), 1)
            ),
            answer_text=text,
            recorded_sources=json.dumps(sources, ensure_ascii=False),
        )
        answers.append(answer)
        for index, proposal in enumerate(proposal_rows, 1):
            pair = dict.fromkeys(PAIR_FIELDS, "")
            pair.update(
                proposal, pair_id=f"{blind_id}-P{index:04d}", blind_answer_id=blind_id
            )
            pairs.append(pair)
        sample_rows.append(
            {
                "blind_answer_id": blind_id,
                "_phase": record["phase"],
                "_system": record["system"],
                "_condition": record["condition"],
            }
        )
    selected = stratified_sample(sample_rows, 0.25, rng)
    for record in records:
        blind_id = blind_ids.get(record["record_id"], "")
        key_row = {
            field: record[field] for field in SELECTION_FIELDS if field in record
        }
        key_row.update(
            blind_answer_id=blind_id,
            blind_question_id=question_ids.get(record["task_id"], "")
            if blind_id
            else "",
            rater2_selected=blind_id in selected,
            disposition="human_input" if blind_id else "not_eligible_completed",
        )
        key_rows.append(key_row)
    # Recheck all inputs immediately before creating either package. No stale export.
    for path, snapshot in snapshots.items():
        _no_symlinks(path)
        if not Path(path).is_file() or sha256_file(path) != snapshot["sha256"]:
            raise ValueError(f"input changed before export: {path}")
    created = []
    try:
        for directory in (out_dir, key_dir):
            directory.mkdir(parents=True, exist_ok=False)
            created.append(directory)
        for name, ids in (("rater1", set(blind_ids.values())), ("rater2", selected)):
            directory = out_dir / name
            directory.mkdir()
            _write_csv_new(
                directory / "answers_to_rate.csv",
                [row for row in answers if row["blind_answer_id"] in ids],
                ANSWER_FIELDS,
            )
            _write_csv_new(
                directory / "pairs_to_rate.csv",
                [row for row in pairs if row["blind_answer_id"] in ids],
                PAIR_FIELDS,
            )
            with (directory / "README.md").open("x", encoding="utf-8") as handle:
                handle.write(README)
        _write_csv_new(key_dir / "canonical_selection.csv", key_rows, SELECTION_FIELDS)
        _write_jsonl_new(key_dir / "eligible_records.jsonl", eligible)
        _write_jsonl_new(
            key_dir / "excluded_records.jsonl",
            [row for row in records if row["record_id"] not in blind_ids],
        )
        totals = Counter(
            (row["phase"], row["system"], row["condition"]) for row in eligible
        )
        chosen = Counter(
            (row["_phase"], row["_system"], row["_condition"])
            for row in sample_rows
            if row["blind_answer_id"] in selected
        )
        manifest = {
            "scope": "EXPLORATORY_HUMAN_REVIEW_INPUTS_NOT_G3",
            "human_ratings_completed": 0,
            "seed": seed,
            "rater1_answers": len(answers),
            "rater2_answers": len(selected),
            "double_review_share": 0.25,
            "strata": [
                {
                    "phase": phase,
                    "system": system,
                    "condition": condition,
                    "eligible": count,
                    "rater2_selected": chosen[(phase, system, condition)],
                }
                for (phase, system, condition), count in sorted(totals.items())
            ],
            "inputs": [
                {"path": path, **snapshot}
                for path, snapshot in sorted(snapshots.items())
            ],
            "outputs": [
                {
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                }
                for directory in (out_dir, key_dir)
                for path in sorted(directory.rglob("*"))
                if path.is_file()
            ],
        }
        with (key_dir / "export_manifest.json").open("x", encoding="utf-8") as handle:
            handle.write(
                json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False)
                + "\n"
            )
    except Exception:
        for directory in reversed(created):
            shutil.rmtree(directory)
        raise
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--cases", required=True, action="append", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--key-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20261013)
    args = parser.parse_args(argv)
    try:
        result = export_review(
            args.registry, args.cases, args.out_dir, args.key_dir, args.seed
        )
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(
        f"Exploratory review inputs: {result['rater1_answers']} answers; {result['rater2_answers']} independently double-reviewed inputs. Ratings are blank."
    )


if __name__ == "__main__":
    main()
