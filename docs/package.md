(package)=
# Příloha A: odevzdávané artefakty a reprodukce

Repozitář obsahuje metodiku, skutečný pilot a dostupné doplňkové výstupy.
Ne všechny povinné části zadání jsou dokončené; tabulka rozlišuje nástroje,
návrhy a skutečně provedené měření. Omezení času samo o sobě není schválenou
výjimkou z minimálních požadavků zadání.

| # | Povinný výstup | Umístění | Stav |
| --- | --- | --- | --- |
| 1 | Výzkumný protokol | `PROTOCOL.md`, `freeze/README.md` | Hotový (nezmrazeno) |
| 2 | Benchmarková data | `data/` (dev 20, val 10) | 30 veřejných + 10 zveřejněných doplňkových otázek; nezávislá kontrola chybí |
| 3 | Prompty a historie | `prompts/`, `prompts/CHANGELOG.md` | P1, P2, kandidáti P3; P3_final se v omezeném rozsahu nevybíral |
| 4 | Metadata běhů | `runs/`, `scripts/make_run_plan.py` | Kanonický registr 93 uložených věcných odpovědí |
| 5 | Kód a rubrika | `scripts/`, `annotation/`, `tests/` | Hotovo a testováno na syntetických datech |
| 6 | Výsledky a nejistota | [](#results), `results/pilot/` | Pilot, AI audit v2 a intervaly; G3 skóre chybí |
| 7 | Analýza ≥ 8 úloh | [](#error-analysis) | 8 skutečných úloh, úspěchy i selhání |
| 8 | Závěrečná zpráva | `docs/`, `docs/exports/project.pdf` | Tato zpráva |
| – | Zdroje a použití AI | [](#references) | Příloha C |
| – | Worksheet | `docs/deliverables/worksheet.md` | Aktuální pilot, doplněk a AI audit |

Dosud chybí nezávislé ratingy, úplná matice a schválené brány G1–G3. Dostupné intervaly AI auditu se uvádějí samostatně.

## Reprodukce bez přístupu k produktům

Stačí Python 3.9+ a standardní knihovna; žádné klíče ani účty.

```bash
python3 scripts/validate_cases.py --no-test
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 docs/figures/make_figures.py      # obrázky z results/pilot/
cd docs && uv run --locked myst build --pdf
```

Testy a demo používají syntetická data a ověřují software, ne produkty. Surové pilotní odpovědi mají otisky
SHA-256 a nemění se; skutečné plány, klíče a hodnocení patří mimo Git (viz `HANDOFF.md`).
Složky `runs/*/avast/` jsou původní názvy evidence z pilotu; sběr probíhal v Chromu.

## Etika a data

Úlohy jsou syntetické a týkají se veřejných faktů; neobsahují osobní údaje ani důvěrná data. K pilotním
odpovědím nepatří přihlašovací údaje ani profily účtů.


## Aktuální stav po kontrole 13. 10. 2026

40 různých úloh, 93 uložených věcných odpovědí / 92 způsobilých
podkladů; 9 Gemini tripletů. Zaslepené listy pro skutečné hodnotitele
jsou připravené ([](#human-handoff)). Aktuální AI metriky pocházejí z opravované
verze 2 ([](#results)); úplná produktová matice a původní G1/G2/G3 zůstávají otevřené.
