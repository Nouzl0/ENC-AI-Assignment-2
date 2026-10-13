# Odevzdávané artefakty (CZAI Assignment 1)

Přehled povinného balíčku ze zadání (kapitola „Povinný balíček k odevzdání") a
worksheetu. Soubory mimo tuto složku se **nekopírují**, protože by se rozcházely se
zdrojem pravdy. Tabulka na ně odkazuje.

**Stav:** kompletní metodika, data, nástroje a skutečný pilot (33 odpovědí, 8 úloh). Analytické běhy, nezávislé lidské ratingy a finální
výsledky s intervaly jsou **mimo rozsah kvůli omezenému času a rozpočtu na využití produktů a AI agentů** a nejsou odhadovány
(viz [PROTOCOL.md](../../PROTOCOL.md)).

## Shrnutí pro hodnotitele

**Dodáno:** kompletní metodika (protokol, hypotézy, metriky, rubrika), 40 případů s původem, tři podmínky promptů s historií,
reprodukovatelné nástroje a testy a **skutečný pilot** (33 odpovědí, 8 úloh, 5 produktů, 95,8 % dokončených prvních pokusů,
183 zpracovaných dvojic tvrzení–zdroj, analýza 8 úloh). **Mimo rozsah (omezený čas a rozpočet):** finální citační přesnost s intervaly
a testy H1/H2, které vyžadují nezávislé lidské ratingy; místo nich jsou vykázány předběžné orientační metriky označené jako takové.

| # | Požadavek zadání | Artefakt | Stav |
| --- | --- | --- | --- |
| 0 | Worksheet (počáteční verze k návrhu, vyplněná k závěrečné zprávě) | [worksheet.md](worksheet.md) | Závěrečná verze v rozsahu pilotu: modely, role, pilot a analýza chyb vyplněné; části mimo rozsah označeny „Nevyhodnoceno“. |
| 1 | Výzkumný protokol | [PROTOCOL.md](../../PROTOCOL.md), [docs/](../) | Hotový, formálně nezmrazeno (G1 mimo rozsah) |
| 2 | Benchmarková data (případy, sady, zdroje, původ) | [data/](../../data/), [data/README.md](../../data/README.md) | Dev 20 a val 10. Soukromý návrh 10 testů je bez nezávislého lidského ověření. |
| 3 | Sada promptů, historie verzí a zdůvodnění změn | [prompts/](../../prompts/), [prompts/CHANGELOG.md](../../prompts/CHANGELOG.md) | P1, P2 a kandidáti P3; P3_final se v omezeném rozsahu nevybíral. |
| 4 | Metadata běhů | [runs/README.md](../../runs/README.md), `scripts/make_run_plan.py` | Generátor a skutečný oddělený pilot; analytická matice je mimo rozsah |
| 5 | Kód a postupy hodnocení, rubrika | [scripts/](../../scripts/), [annotation/rubric.md](../../annotation/rubric.md), [annotation/calibration.md](../../annotation/calibration.md) | Hotovo, testováno na syntetických datech |
| 6 | Výsledky (skóre, nejistota, opakování, kvalita vs. úsilí) | Vznikne z `scripts/score.py` | Mimo rozsah: vyžaduje lidské ratingy a G3; místo toho orientační metriky pilotu |
| 7 | Analýza chyb (≥8 případů, úspěšné i neúspěšné) | [docs/error-analysis.md](../error-analysis.md), [analysis/README.md](../../analysis/README.md) | Rozbor osmi unikátních skutečných pilotních úloh s úspěchy, citačními problémy i selháním; pomocná analýza AI; finální test mimo rozsah |
| 8 | Závěrečná zpráva | [docs/](../), [PDF](../exports/project.pdf) | Zpráva se skutečnými pilotními výsledky a analýzou; neobsahuje dokončený analytický benchmark (omezený rozsah) |

## Podmíněné povinnosti ze zadání

| Požadavek | Řešení |
| --- | --- |
| Písemné zdůvodnění vynechaného systému | Nevynecháváme žádný z pěti. Claude Code je mimo rozsah (směr B). Viz [design.md](../design.md). |
| Zvolený přístup k nástrojům | Návrh podle schopností produktu. Výsledky jsou porovnáním produktů. |
| Souhlas vyučujícího | Nevyžadován (tým, dvě hlavní metriky nejvýše, bez LLM hodnotitele jako jediného důkazu). |

## Co by plný experiment přidal nad rozsah pilotu

Úplná analytická metadata, položky 6 a 7 a finální sekce K–N worksheetu, plus `P3_final`
a soukromý holdout. V této verzi jsou výslovně označeny jako nezměřené kvůli omezenému rozsahu a nevyplňují se odhadem.


## Soulad s minimálním řešením zadání

| Požadavek | Splněno | Kde |
| --- | --- | --- |
| Jedna schopnost, jeden směr (B) | Ano | [introduction.md](../introduction.md) |
| ≥ 4 systémy (máme 5), vynechání jen s odůvodněním | Ano | [design.md](../design.md) |
| ≥ 40 případů, ≥ 10 držených stranou | Návrh ano (20 + 10 + 10); soukromý test 10 je návrh bez lidského schválení | [design.md](../design.md), `data/` |
| Tři podmínky promptů, historie změn | Ano; P3_final se v omezeném rozsahu nevybíral | `prompts/`, [design.md](../design.md) |
| 1 hlavní + 2 vedlejší metriky, definované předem | Ano | [evaluation.md](../evaluation.md) |
| ≥ 1 automatická kontrola, ≥ 1 lidská složka (≥ 20 %, 2 hodnotitelé, kotvy, neshody) | Nástroje a postup ano; ratingy mimo rozsah (omezené prostředky) | [evaluation.md](../evaluation.md), `annotation/` |
| Okrajové případy ≥ 20 % | Ano: 43 % dev + val | [design.md](../design.md) |
| Analýza chyb ≥ 8 případů vč. úspěšných | Ano (8 pilotních úloh) | [error-analysis.md](../error-analysis.md) |
| Metadata běhů, selhání, opakování | Ano pro pilot | `runs/`, [results.md](../results.md) |
| Výsledky: orientační agregace bez ratingů | **Částečně:** provozní metriky a lexikální proxy podpory (`results/pilot/pilot_metrics.csv`, `analysis/pilot_proxy.py`), označené jako předběžné | [results.md](../results.md) |
| Výsledky s nejistotou, kvalita vs. úsilí | **Ne:** skripty a postup hotové, výsledky vyžadují lidské ratingy | [results.md](../results.md), [limits.md](../limits.md) |

## Obsah odevzdávaného ZIP

PDF `docs/exports/project.pdf` (zpráva) a následující adresáře a soubory repozitáře. Doporučený postup je po
commitu spustit `git archive`, který zahrne jen sledované soubory a vynechá `.venv`, `_build`, cache i soukromá data.

| Cesta | Položka zadání |
| --- | --- |
| `docs/exports/project.pdf`, `docs/*.md`, `docs/figures/`, `docs/deliverables/worksheet.md` | Závěrečná zpráva a worksheet |
| `PROTOCOL.md`, `freeze/`, `README.md`, `HANDOFF.md` | Výzkumný protokol, orientace a předání |
| `data/` | Benchmarková data, původ, historie změn |
| `prompts/` | Sada promptů a historie verzí |
| `runs/` (včetně `pilot-2026-10-12/`, `pilot-2026-10-13/`) | Metadata běhů a původní pilotní výstupy |
| `scripts/`, `tests/`, `annotation/`, `pyproject.toml`, `uv.lock` | Kód, testy a rubrika |
| `results/`, `analysis/` | Pilotní souhrny, `pilot_metrics.csv`, skript `pilot_proxy.py`, šablona analýzy chyb |
| `assignment/` (volitelně) | Zadání a prázdná šablona worksheetu |

Do ZIP **nepatří**: `.git`, `.venv`, `.ruff_cache`, `docs/_build`, `AGENTS.md`/`CLAUDE.md` (interní pokyny agentům),
původní `*.docx` návrh (historický), soukromý test, klíče a hodnocení.

```bash
git archive --format=zip -o ../czai-assignment-1.zip HEAD   docs PROTOCOL.md README.md HANDOFF.md REPORT_TEMPLATE.md freeze data prompts runs scripts tests   annotation results analysis assignment pyproject.toml uv.lock LICENSE
```

**Před odevzdáním zkontrolovat:** (1) PDF je přestavěné z aktuálních `docs/*.md`; (2) snímky v `runs/*/screens/` neukazují
e-mail, jméno účtu ani jiné osobní údaje (textové soubory byly automaticky prohledány bez nálezu, snímky nutno zkontrolovat očima); (3) formát ZIP/PDF
potvrdil vyučující; (4) Worksheet obsahuje jen skutečně změřené hodnoty, zbylé `Nevyhodnoceno` označují části mimo rozsah pilotu.
