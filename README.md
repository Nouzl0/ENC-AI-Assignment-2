# CZAI Assignment 1 – Správnost citací AI asistentů s webovým vyhledáváním

Reprodukovatelný balíček k projektu (Směr B: výzkum podložený zdroji). Porovnává, jak často citace pěti asistentů
(ChatGPT, Gemini, Claude, Perplexity, Grok) skutečně podporují tvrzení, ke kterým jsou připojeny, ve třech podmínkách promptu.

- **Návrh projektu** (odůvodnění všech rozhodnutí): https://claude.ai/code/artifact/7d19bd66-2c7e-48ad-9c81-fd4939f1ab72
- **Zmrazené parametry a hashe:** [`PROTOCOL.md`](PROTOCOL.md)
- Požadavky: Python 3.9+ (jen standardní knihovna), prohlížeč, účty u pěti produktů.

## Struktura

```text
czai-citace/
├── README.md                  tento soubor
├── PROTOCOL.md                výzkumná otázka, hypotézy, metriky, brány, hashe, odchylky
├── data/                      40 případů (dev 20 / val 10 / test 10) + popis polí
├── prompts/                   P1, P2, kandidáti P3-A/P3-B (CZ + EN), CHANGELOG.md
├── runs/                      plány běhů = metadata (CSV), answers/, screenshots/, návod README.md
├── annotation/                rubric.md, šablona neshod; anotační listy po fázích (annotation/dev, val, test)
├── annotation_key/            JEN správce dat: blind_key.csv, answers_meta.csv, salt.txt (vytvoří skript)
├── analysis/                  šablona analýzy chyb + návod
├── scripts/
│   ├── validate_cases.py      schéma, stratifikace, ≥ 20 % okrajových případů, duplicity, SHA-256
│   ├── make_run_plan.py       plán běhů s náhodným pořadím, vyrenderovaným promptem a hashem
│   ├── check_citations.py     parsování odpovědí, kontrola URL, shoda čísel, zaslepené listy
│   ├── score.py               metriky, bootstrap, Wilson, H1/H2, přenositelnost, kappa, report
│   └── make_demo_data.py      SYNTETICKÁ data pro test celé pipeline
├── results/                   výstupy score.py
└── demo/                      run_demo.sh + ukázkové odpovědi a lokální demo web
```

## Rychlý test (2 minuty, bez internetu)

```bash
bash demo/run_demo.sh            # vše na syntetických datech
ONLINE=1 bash demo/run_demo.sh   # navíc otestuje HTTP kontroly proti lokálnímu demo webu
```

Výsledek: `demo/results/report.md`. **Demo data jsou náhodně vygenerovaná a anonymní (sys_A … sys_E) – nejde o výsledky.**

## Postup projektu

| Krok | Příkaz / činnost | Brána |
| --- | --- | --- |
| 0 | Správce dat přesune `data/cases_test.jsonl` mimo sdílenou složku (hash zůstává v `PROTOCOL.md`) | |
| 1 | `python3 scripts/make_run_plan.py --phase dev` → pilot: první 2 případy × 5 systémů (10 odpovědí) → kalibrace rubriky; `python3 scripts/validate_cases.py --write-hashes` → hashe do `PROTOCOL.md` | **G1** protokol zmrazen |
| 2 | zbytek běhů fáze dev podle `runs/README.md` | |
| 3 | `python3 scripts/check_citations.py --runs runs/run_plan_dev.csv` → hodnocení → `pairs_rated.csv`, `answers_rated.csv` | |
| 4 | Analýza chyb dev → úprava kandidátů P3-A/P3-B (jen typy chyb s ≥ 3 výskyty) → `CHANGELOG.md` | |
| 5 | `make_run_plan.py --phase val` → běhy → hodnocení → `score.py` → vítěz P3 | |
| 6 | Zkopírovat vítěze do `prompts/P3_final_cs.txt` a `_en.txt`, zapsat hash | **G2** P3 zmrazen |
| 7 | `make_run_plan.py --phase test` a `--phase repeat` → běhy do 72 h | |
| 8 | `check_citations.py --runs "runs/run_plan_*.csv"` → hodnocení (+ 25 % druhý hodnotitel) → neshody | **G3** hodnocení uzavřeno |
| 9 | `python3 scripts/score.py` → `results/report.md`; analýza 12 případů → závěrečná zpráva | |

Poznámky ke krokům:

- Pro každou fázi spusťte `check_citations.py` do vlastní složky: `--runs runs/run_plan_dev.csv --out-dir annotation/dev`, obdobně `val`, `test` (s `"runs/run_plan_test.csv"` i `repeat`). Zaslepená ID jsou deterministická (hash `run_id` se solí `--salt`), takže opakované spuštění dá stejná ID.
- Složku `annotation_key/` (klíč, sůl, metadata formátu) drží jen správce dat; hodnotitelé dostanou jen `*_to_rate*.csv`.
- Hodnotitel 1 uloží svůj list **před diskusí** jako `pairs_rated_rater1.csv` / `answers_rated_rater1.csv`, hodnotitel 2 jako `*_rated_rater2.csv`; po vyřešení neshod vznikne finální `pairs_rated.csv` / `answers_rated.csv`. Vše ve složce fáze; `score.py` načte všechny podsložky `annotation/` a kappu počítá z hodnocení před smířením.

## Mapování na povinný balíček zadání

| Požadavek zadání | Kde |
| --- | --- |
| 1 Výzkumný protokol | návrh projektu  + `PROTOCOL.md` |
| 2 Benchmarková data | `data/` (případy, rozdělení, zdroje, původ) |
| 3 Sada promptů + historie verzí | `prompts/` + `prompts/CHANGELOG.md` |
| 4 Metadata běhů | `runs/run_plan_*.csv` (vyplněné), `runs/answers/`, `runs/screenshots/` |
| 5 Kód a postupy hodnocení | `scripts/`, `annotation/rubric.md` |
| 6 Výsledky | `results/` (metriky, intervaly, opakované běhy, užitek, Pareto) |
| 7 Analýza chyb | `analysis/error_analysis.csv` + text ve zprávě |
| 8 Závěrečná zpráva | samostatný dokument týmu (šablona sekcí: návrh projektu, kap. Limity) |
