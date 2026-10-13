(package)=
# Příloha A: odevzdávané artefakty a reprodukce

Repozitář obsahuje metodiku, skutečný pilot a dostupné doplňkové výstupy.
Ne všechny povinné části zadání jsou dokončené; tabulka rozlišuje nástroje,
návrhy a skutečně provedené měření. Omezení času samo o sobě není schválenou
výjimkou z minimálních požadavků zadání.

| # | Povinný výstup | Umístění | Stav |
| --- | --- | --- | --- |
| 1 | Výzkumný protokol | `PROTOCOL.md`, `freeze/README.md` | Hotový (nezmrazeno) |
| 2 | Benchmarková data | `data/` (dev 20, val 10) | Hotovo; soukromý test 10 je návrh bez lidského schválení |
| 3 | Prompty a historie | `prompts/`, `prompts/CHANGELOG.md` | P1, P2, kandidáti P3; P3_final se v omezeném rozsahu nevybíral |
| 4 | Metadata běhů | `runs/`, `scripts/make_run_plan.py` | Generátor + skutečný pilot (33 odpovědí) |
| 5 | Kód a rubrika | `scripts/`, `annotation/`, `tests/` | Hotovo a testováno na syntetických datech |
| 6 | Výsledky a nejistota | [](#results), `results/pilot/` | Pilot a orientační metriky; finální skóre mimo rozsah |
| 7 | Analýza ≥ 8 úloh | [](#error-analysis) | 8 skutečných úloh, úspěchy i selhání |
| 8 | Závěrečná zpráva | `docs/`, `docs/exports/project.pdf` | Tato zpráva |
| – | Zdroje a použití AI | [](#references) | Příloha C |
| – | Worksheet | `docs/deliverables/worksheet.md` | Vyplněný v rozsahu pilotu |

Mimo rozsah (omezený čas a rozpočet): finální výsledky s intervaly, nezávislé ratingy a podepsané brány G1–G3.

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


## Aktualizace 13. 10. 2026

Doplňkový sběr nyní dokládá 40 různých měřených úloh a 84 věcných odpovědí. Pět nových úloh má Gemini P1/P2/P3A. Dostupný AI audit a intervaly jsou v kapitole [](#results), metoda v [](#supplement). Původní úplná matice a skutečné lidské hodnocení nejsou dokončené; starší plánované počty v této kapitole nejsou aktuální počet uložených odpovědí.
