#!/usr/bin/env python3
"""Write filled, explicitly unverified DEMO reference evidence, entirely offline.

Never fetches a source, runs a product, or seals a gate. DEMO_NOT_VERIFIED is
deliberately rejected by production gates. Real evidence requires a human check.
"""
import argparse
import csv
import json
from pathlib import Path

from common import ROOT, sha256_file, write_csv
from integrity import private_path


def create_example(out):
    if not Path(out).is_absolute():
        raise ValueError("--out must be a new absolute directory outside Git")
    out = Path(private_path(out))
    out.mkdir(parents=True, exist_ok=False)
    static = dict(task_id="DEMO-EVIDENCE-STATIC", reference_valid_as_of="2026-01-01",
                  reference_answer_or_tests=dict(
                      required_facts=["Počet měření stanice Alfa dne 2026-01-01 UTC.", "Provozovatel stanice Alfa."],
                      optional_facts=["Rok zahájení provozu stanice Alfa."]))
    dynamic = dict(task_id="DEMO-EVIDENCE-DYNAMIC", reference_valid_as_of="RUN_DAY",
                   reference_answer_or_tests=dict(
                       required_facts=["Aktuální počet měření stanice Alfa v UTC den běhu."],
                       optional_facts=["Průměrná hloubka měření v UTC den běhu."]))
    (out / "reference_units_DEMO.json").write_text(json.dumps([static, dynamic], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    snapshots = {}
    for date, count, depth in (("2026-01-01", 78, "12,34"), ("2026-01-04", 82, "12,36")):
        path = out / f"DEMO-source-{date}.txt"
        path.write_text(f"DEMO: smyšlený zdroj, žádné webové/lidské ověření.\n"
                        f"Ústav Beta, výpis stanice Alfa pro UTC den {date}.\n"
                        f"Počet měření: {count}. Průměrná hloubka: {depth} m.\n"
                        "Provozovatel: Ústav Beta. Zahájení provozu: 2010.\n", encoding="utf-8")
        snapshots[date] = path

    def evidence(date, value, locator):
        path = snapshots[date]
        return dict(reference_value=value, url=f"https://fixture.invalid/alfa/{date}",
                    verified_by="DEMO generator, nikoli člověk", checked_at=f"{date}T10:00:00+00:00",
                    locator=locator, excerpt_or_summary=f"Smyšlený výpis: {value}",
                    snapshot_file=str(path), snapshot_sha256=sha256_file(path),
                    verification_status="DEMO_NOT_VERIFIED", note="Pouze offline ukázka; není ověřený gold ani podpis.")

    source_rows = []
    for case, values in ((static, {"RF1": "78 měření dne 2026-01-01 UTC", "RF2": "Ústav Beta", "OF1": "2010"}),
                         (dynamic, {"RF1": "78 měření dne 2026-01-01 UTC", "OF1": "12,34 m dne 2026-01-01 UTC"})):
        for prefix, kind, facts in (("RF", "required", case["reference_answer_or_tests"]["required_facts"]),
                                    ("OF", "optional", case["reference_answer_or_tests"]["optional_facts"])):
            for i, fact in enumerate(facts, 1):
                fid = f"{prefix}{i}"
                source_rows.append(dict(evidence("2026-01-01", values[fid], f"řádky 2–4, {fid}"),
                                        task_id=case["task_id"], fact_id=fid, reference_kind=kind, fact_text=fact,
                                        valid_as_of="2026-01-01", archive_url=""))
    daily_rows = [dict(evidence(date, value, f"řádek 3, {fid}"), task_id=dynamic["task_id"], run_date=date, fact_id=fid)
                  for date, values in (("2026-01-01", ("78 měření", "12,34 m")), ("2026-01-04", ("82 měření", "12,36 m")))
                  for fid, value in zip(("RF1", "OF1"), values)]
    for name, template, rows in (("source_evidence.csv", "data/source_evidence_TEMPLATE.csv", source_rows),
                                 ("run_day_evidence.csv", "annotation/run_day_evidence_TEMPLATE.csv", daily_rows)):
        with open(Path(ROOT, template), encoding="utf-8", newline="") as f:
            fields = next(csv.reader(f))
        write_csv(out / name, rows, fields)
    (out / "README_DEMO.md").write_text(
        "# DEMO – pouze smyšlená offline ukázka evidence\n\n"
        "Žádný web, produkt, lidské ověření ani G1/G2/G3. Neodevzdávat jako výsledky.\n"
        "DEMO_NOT_VERIFIED záměrně neprojde ostrou bránou. Neměnit jen status/identitu\n"
        "na verified: skutečné doklady musí získat a ověřit nezávislý člověk.\n"
        "reference_units_DEMO.json ukazuje jen RF/OF, není úplná benchmarková sada.\n"
        "Statický snapshot zůstává; RUN_DAY má oddělené RF i OF pro dva UTC dny.\n"
        "Postup a význam polí: data/evidence_examples.md ve veřejném repozitáři.\n", encoding="utf-8")
    return dict(source_rows=len(source_rows), run_day_rows=len(daily_rows), verification_status="DEMO_NOT_VERIFIED")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="new absolute DEMO directory outside the worktree")
    args = ap.parse_args()
    try:
        summary = create_example(args.out)
    except (ValueError, OSError) as e:
        ap.error(str(e))
    print("DEMO only; no human verification or benchmark:", json.dumps(summary))


if __name__ == "__main__":
    main()
