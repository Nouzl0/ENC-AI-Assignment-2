# Softwarové testy: pouze chování aplikace

Test má zavolat implementaci z `scripts/` (přímo nebo přes skutečné CLI) a porovnat
výsledek, odmítnutý vstup nebo vedlejší účinky s nezávislým očekáváním. Malý vstup
není sám o sobě trivialita: například `[0]`, NaN či jediný duplicitní klíč kontrolují
reálné chyby parseru a integrity.

Fixtures slouží jako vstupy, ne jako oracle. Samotné porovnání návratového souhrnu
generátoru s jeho pevnými počty, přítomnost slov v promptu, kopírování textu dat nebo
výpočet rozpočtu přímo v testu nejsou kontrolou aplikace. Očekávané metriky se nesmějí
získávat stejnou skórovací funkcí, kterou test ověřuje.

## Audit celé sady (2026-10-12)

| Soubor | Ponechaná kontrola aplikace |
| --- | --- |
| `test_annotation.py` | Skutečný parser: původní URL/text, značky, všechny claimy, podpůrné úryvky a deduplikace; stratifikace a validace ID. |
| `test_data_contract.py` | Odmítnutí nejednoznačného JSON, RF/RC ratingů, neúplné evidence a neplatných kvót. |
| `test_http_checks.py` | HTTP na loopbacku, redirect, snapshoty, uchování pokusů, truncation a nezměněné URL. |
| `test_integrity.py` | Soukromé cesty, plány a hashové vazby, ratingy a audit, časová evidence, izolované G1→G2→G3 a přenesené CLI replaye. |
| `test_pipeline.py` | Skutečné CLI od plánování po report, determinismus, zaslepení a odmítnutí přepsání, neúplných ratingů a symlinků. |
| `test_preparation.py` | CLI pod ASCII locale, byte-identický Git checkout, formát/neověřený status evidence, ochrana výstupů a generování úsporné matice. |
| `test_replay_paths.py` | Fail-closed mapování cest včetně duplicit, překryvů a úniku přes symlink. |
| `test_scoring.py` | Výpočty metrik, jmenovatele, selhání a neúplnost, číselné hranice, hypotézy, opakování a shoda hodnotitelů. |
| `test_selection.py` | Přepočet P3 z ratingového snapshotu, plná přesnost, prahy/shody a odmítnutí neplatných metrik. |
| `test_validation.py` | Skutečné CLI odmítne sadu pod minimální velikostí. |

Odstraněné celé testy:

- `test_bonus_not_in_required_denominator`: kontroloval hlavně pevné hodnoty a slova
  ve veřejných úlohách; jmenovatel nyní kontroluje přímo `load_answers` s RF, OF i RC.
- `test_constraints_are_separate_from_content`: kontroloval konkrétní texty úloh a
  skládal stejný referenční text v testu; RF/RC rozlišení zůstává ve skutečném scoringu.
- `test_p3b_draft_allows_direct_support_and_rounding_in_both_languages`: hledal slova
  v promptu; neověřoval renderování, parser ani účinek na skórování.

Z dalších testů odstraněny pevné návratové souhrny demo generátorů, opisované demo
hodnoty/marketingové texty a ručně vypočtených 80,1 h. Kontrola ASCII locale při
detekci publikovaného kandidáta nyní vyžaduje konkrétní odmítnutí překryvu místo
pouhého `isinstance(..., list)`. Počty skutečných CLI výstupů a vzorku hodnotitele
zůstávají: chrání kompletnost matice a povinných ≥25 %, nikoli testovací aritmetiku.

Po kritickém read-only auditu dále posílena kontrola neprázdných statických i RUN_DAY
referencí, RF/OF a unikátních vazeb evidence. Plánovací CLI nyní musí do literalních
CZ/EN šablon skutečně vložit otázku; test kontroluje přesný text i SHA-256 šablony
a vykresleného promptu, nikoli pouhý počet placeholderů.

## Skutečně provedené kontroly

- Celá sada na Pythonu **3.14.7: 87/87 OK**, bez přeskočení (61,530 s), také nad
  izolovaným snapshotem změn a aktuálního `main` mimo worktree.
- Celá sada na Pythonu **3.12.12: 87/87 OK**, bez přeskočení (67,082 s).
- Cílené regrese anotace, datového kontraktu, přípravy, scoringu a ASCII locale prošly.
- Šest reprezentativních offline mutací v dočasných kopiích/výstupech bylo odhaleno
  očekávaným selháním assertů: oprava `[0]`, sloučení fází vzorku, OF ve jmenovateli
  RF, konstantní precision, prázdná evidence a nevložení otázky do promptu.
- Validace veřejných 20 dev + 10 val (`--no-test`), Ruff 0.16.1 lint/formát testů,
  gramatika Pythonu 3.9 šesti změněných modulů a `git diff --check` prošly.

Runtime Pythonu 3.9 ani vzdálené CI ověřeny nebyly. Mutace nejsou úplné pokrytí všech
možných chyb a průchod testů neověřuje pravdivost referencí.

## Spuštění

Z kořene repozitáře, bez instalace závislostí:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_cases.py --no-test
```

Jde o kontrolu softwaru na lokálních vstupech, **ne** skutečný benchmark, ověření
pravdivosti referencí nebo udělení G1/G2/G3. Tyto činnosti nadále provádí kolega.
