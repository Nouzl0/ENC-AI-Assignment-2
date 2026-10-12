# Odevzdávané artefakty (CZAI Assignment 1)

Přehled povinného balíčku ze zadání (kapitola „Povinný balíček k odevzdání") a
worksheetu. Soubory mimo tuto složku se **nekopírují**, protože by se rozcházely se
zdrojem pravdy. Tabulka na ně odkazuje.

**Stav:** přípravný balíček před G1. Nic není zmrazeno a existují skutečné pilotní odpovědi; analytické běhy, nezávislé ratingy a
finální výsledky zatím neexistují (viz [PROTOCOL.md](../../PROTOCOL.md)).

| # | Požadavek zadání | Artefakt | Stav |
| --- | --- | --- | --- |
| 0 | Worksheet (počáteční verze k návrhu, vyplněná k závěrečné zprávě) | [worksheet.md](worksheet.md) | Počáteční verze částečně vyplněná; potvrzeni jsou René/Jan jako plánovaní hodnotitelé. K obsahuje skutečný pilot; modely, role a dílčí pozorování jsou vyplněné. Finální části výslovně přiznávají chybějící měření. |
| 1 | Výzkumný protokol | [PROTOCOL.md](../../PROTOCOL.md), [docs/](../) | Návrh, nezmrazeno |
| 2 | Benchmarková data (případy, sady, zdroje, původ) | [data/](../../data/), [data/README.md](../../data/README.md) | Dev 20 a val 10. Nový soukromý návrh 10 testů čeká na nezávislé lidské ověření. |
| 3 | Sada promptů, historie verzí a zdůvodnění změn | [prompts/](../../prompts/), [prompts/CHANGELOG.md](../../prompts/CHANGELOG.md) | P1, P2 a kandidáti P3. P3_final chybí. |
| 4 | Metadata běhů | [runs/README.md](../../runs/README.md), `scripts/make_run_plan.py` | Generátor a skutečný oddělený pilot; analytická matice ještě chybí |
| 5 | Kód a postupy hodnocení, rubrika | [scripts/](../../scripts/), [annotation/rubric.md](../../annotation/rubric.md), [annotation/calibration.md](../../annotation/calibration.md) | Hotovo, testováno na syntetických datech |
| 6 | Výsledky (skóre, nejistota, opakování, kvalita vs. úsilí) | Vznikne z `scripts/score.py` | Chybí, vyžaduje reálné běhy a G3 |
| 7 | Analýza chyb (≥8 případů, úspěšné i neúspěšné) | [analysis/README.md](../../analysis/README.md), `analysis/error_analysis_TEMPLATE.csv` | Pouze šablona |
| 8 | Závěrečná zpráva | [REPORT_TEMPLATE.md](../../REPORT_TEMPLATE.md), [docs/](../) | Kostra bez výsledků |

## Podmíněné povinnosti ze zadání

| Požadavek | Řešení |
| --- | --- |
| Písemné zdůvodnění vynechaného systému | Nevynecháváme žádný z pěti. Claude Code je mimo rozsah (směr B). Viz [systems.md](../systems.md). |
| Zvolený přístup k nástrojům | Návrh podle schopností produktu. Výsledky jsou porovnáním produktů. |
| Souhlas vyučujícího | Nevyžadován (tým, dvě hlavní metriky nejvýše, bez LLM hodnotitele jako jediného důkazu). |

## Co ještě vyžaduje dokončení experimentu

Úplná analytická metadata, položky 6 a 7 a finální sekce K–N worksheetu, plus `P3_final`
a soukromý holdout. Do té doby zůstávají výslovně označeny jako dosud nezměřené/nedokončené a nevyplňují se odhadem.
