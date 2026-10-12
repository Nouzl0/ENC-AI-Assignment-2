# Reprodukovatelný balíček

Centrem projektu je `ENC-AI-Project`. Originální sběr a hashově svázané
auditní artefakty jsou mimo worktree, aktuálně v sousední `czai-private-v1`.
Podepsané soubory se při přenosu nepřepisují. Po G3 se do projektu přidá
schválený export dat, běhů a výsledků pro odevzdání. Reprodukce využije
původní auditní balíček a read-only mapu cest podle `freeze/README.md`.

| # | Povinný výstup | Umístění a skutečný stav |
| --- | --- | --- |
| 1 | Výzkumný protokol | `PROTOCOL.md`, rubrika, `freeze/README.md`; G1/G2/G3 zatím nepodepsané |
| 2 | Benchmarková data | Dev 20, val 10 v `data/`; soukromý návrh 10 nových testů čeká na lidské schválení; RF/OF evidence připravena k ověření |
| 3 | Prompty a historie | `prompts/`; P1/P2 a kandidáti existují, P3_final se vybere z validace |
| 4 | Metadata a původní výstupy | `runs/README.md`, generátor a pilot; analytické běhy zatím neexistují |
| 5 | Kód a rubrika | `scripts/`, `annotation/`, `tests/`; softwarové testy jsou oddělené od experimentu |
| 6 | Výsledky a nejistota | [](#results), `results/README.md`; finální CSV vyžadují skutečné ratingy a G3 |
| 7 | Analýza ≥8 unikátních úloh | `analysis/`, [](#error-analysis); zatím plán |
| 8 | Závěrečná zpráva | MyST zdroje v `docs/` a PDF `docs/exports/project.pdf`; pracovní verze |

Worksheet je v `docs/deliverables/worksheet.md`. Stav povinností je v
`docs/deliverables/README.md`. Připravujeme **PDF i zdroje** a kompletní
oprávněný auditní balíček; formát vyžadovaný vyučujícím zatím nebyl potvrzen.
Žádný ZIP zatím není vydáván za dokončené odevzdání.

## Kontrola a sestavení

```bash
python3 scripts/validate_cases.py --no-test
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
uv run --locked ruff check .
uv run --locked ruff format --check .
cd docs
uv run --locked myst build --pdf
```

Skripty podporují Python 3.9+ a standardní knihovnu. Dokumentační nástroje
mají oddělené uv prostředí podle `pyproject.toml` a `uv.lock`.
PDF ani zelené testy neověřují reference a nenahrazují benchmark.

Úplné příkazy s povinnými G1/G2/G3 manifesty, soukromými cestami, exporty
pro hodnotitele a finálním scoringem jsou v `HANDOFF.md`. Citlivé snapshoty
a přihlašovací údaje nepatří do Git exportu.
