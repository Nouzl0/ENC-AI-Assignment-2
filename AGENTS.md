# Pokyny pro agenty

Platí pro celý repozitář. Nejdřív přečti relevantní dokumentaci a kód; dělej malé,
cílené změny. Cizí rozpracované změny nemaž, nevracej ani nepřidávej do svého commitu.

## Projekt a rozsah práce

CZAI Assignment 1: správnost citací AI asistentů s webovým vyhledáváním, **směr B –
porovnání produktů, ne izolovaných modelů**. Jde o přípravný balíček; aktuální stav
ověř v `README.md`. Syntetické testy nejsou výsledky experimentu ani ověření referencí.

**Reálné benchmarky, pilot a zdrojové ověřování provede kolega.** Bez změny zadání je
nespouštěj; připravuj metodiku, nástroje, testy a předání. Nevymýšlej ratingy, výsledky,
lidské podpisy ani splnění G1/G2/G3. Izolované fixture testy falešných bran jsou povolené.

## Git: pouze main

- Pracuj výhradně na `main`; jiné větve (ani `codex/*`) nezakládej ani nepoužívej.
- Před úpravami ověř `git status --short --branch`; při čistém stromu proveď `git pull --ff-only origin main`.
- Hotovou etapu po kontrolách commitni a `git push origin main`. Žádný force push ani přepis historie; konflikty řeš bezpečně nebo oznam.

## Orientace a zdroje pravdy

Všechny cesty a níže uvedené příkazy jsou relativní ke kořeni repozitáře.

| Soubor / adresář | K čemu slouží |
| --- | --- |
| `README.md` | Stav přípravy, rychlé kontroly, mapování na povinné výstupy zadání. |
| `PROTOCOL.md` | Autoritativní metodika: matice běhů, metriky, hypotézy, nejistota a role. |
| `HANDOFF.md` | Praktický postup pro kolegu včetně soukromých příkazů a návaznosti bran. |
| `annotation/rubric.md`, `annotation/calibration.md` | Hodnoticí pravidla a offline kalibrační kotvy. |
| `freeze/README.md`, `runs/README.md` | G1/G2/G3, integrita, metadata běhů a read-only replay. |
| `data/README.md`, `data/evidence_examples.md`, `data/CHANGES.md` | Schéma úloh, reference/evidence, oddělení holdoutu a historie změn dat. |
| `prompts/`, `prompts/CHANGELOG.md` | Jazykové dvojice P1/P2/P3 kandidátů a jejich verze. |
| `REPORT_TEMPLATE.md`, `analysis/README.md` | Šablona zprávy a analýza chyb; ne hotové závěry. |
| `PREPARATION.md` | Historie přípravných etap, kritických kontrol a skutečně provedených testů. |
| `tests/`, `.github/workflows/tests.yml`, `demo/` | Softwarové testy, CI a označené ukázky; ne produktový benchmark. |

Původní DOCX je historický návrh, ne aktuální protokol. Při rozporu dokumentace a kódu
nejdřív zjisti zamýšlené pravidlo; neopravuj jen dokumentaci tak, aby zakryla chybu.

## Stack a nástroje

**Python 3.9+, pouze standardní knihovna.** Není potřeba instalovat závislosti, API
klíče ani účty produktů. Samostatná CLI spouštěj jako `python3 scripts/<název>.py`;
volby ověř přes `--help`. Podpůrné moduly níže nemají CLI, importují je ostatní nástroje.
Dokumentace je česky, identifikátory a kód převážně anglicky.

| Soubor v `scripts/` | Odpovědnost |
| --- | --- |
| `common.py` | Podpůrný modul: CSV/JSONL, schéma, ID, hashování a kontrola konečných čísel. |
| `validate_cases.py` | Schéma, stratifikace a duplicity veřejných dev/val; **neověřuje pravdivost**. |
| `make_run_plan.py` | Plán běhů, vykreslené prompty a vazba na manifest; nevolá produkty. |
| `check_citations.py` | Parser odpovědí/citací, volitelné HTTP kontroly, zaslepené exporty a oddělený klíč. |
| `score.py` | Metriky, CI, shoda hodnotitelů a snapshot vstupů; skutečné `--final` vyžaduje G3. |
| `integrity.py` | Podpůrný modul: soukromé cesty, hashové vazby a validační kontroly. |
| `freeze_protocol.py` | CLI pro šablony, validaci a manifesty bran. |
| `selection.py` | Podpůrný modul: přepočet volby P3 ze zmrazeného snapshotu v plné přesnosti. |
| `replay_paths.py` | Podpůrný modul: přemapování cest při čtení, bez změny podepsaných JSON/CSV. |
| `make_demo_data.py` | Deterministický offline integrační fixture přes skutečná CLI; ne měření produktů. |
| `make_evidence_example.py` | Smyšlená vyplněná evidence `DEMO_NOT_VERIFIED`; ne schválený gold. |

## Bezpečné kontroly (bez benchmarku)

```bash
# Pouze veřejná dev/val data:
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_cases.py --no-test
# Cílený test – vzor změň na soubor odpovídající úpravě:
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_preparation.py' -v
# Celá softwarová sada:
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

- `bash demo/run_demo.sh` je obal stejné celé testovací sady, ne další benchmark.
- `python3 scripts/make_demo_data.py` běží offline v dočasném adresáři a uklidí výstupy.
  Pro zachování ukázky použij `--out` s **novým absolutním adresářem mimo repo**;
  stejně tak `make_evidence_example.py --out ...`. Nepřepisuj existující artefakty.
- Testy HTTP používají lokální server na `127.0.0.1`. Samostatné `check_citations.py`
  naopak standardně provádí HTTP; pro offline fixture použij `--synthetic --offline`
  a DEMO-* / sys_* data. Režimy `--synthetic` a `--final` nekombinuj.
- Pro změny Pythonu, schématu, skórování nebo metodických pravidel spusť relevantní
  regresní testy i celou sadu. U čistě dokumentační úpravy ověř odkazy, příkazy a diff.
- CI je nastaveno na Python 3.9 a 3.12. Uváděj lokální verzi a skutečné výsledky;
  lokální průchod ani kontrola syntaxe nejsou důkaz průchodu vzdáleného CI.

## Hranice, které nesmí úprava rozbít

- **Holdout:** Git obsahuje 20 dev + 10 val a historické `data/published_test_candidates.jsonl`.
  Zveřejněné kandidáty nelze vydávat za skrytý test. Nový holdout je mimo Git a autor
  promptu jej před G2 nesmí číst; ostré příkazy s holdoutem/manifesty provádí správce dat.
- **Soukromí:** skutečné plány, odpovědi, ratingy, klíče, evidence a výsledky patří na
  absolutní cesty mimo worktree, i po rozlišení symlinků. `.gitignore` není ochrana
  přístupu. Nekomituj soukromá data, přihlašovací údaje ani skutečné výsledky.
- **Reference:** RF = povinné fakty, OF = nepovinné fakty, RC = požadavky na formát/zdroje.
  Nepřidávej skryté povinnosti ani netrestej chybějící OF jako chybějící RF. `fact_text`
  není automaticky ověřená `reference_value`; pro RUN_DAY uchovej oddělenou evidenci
  podle UTC dne běhu, nepřepisuj původní zmrazenou referenci.
- **Parser a metriky:** zachovej původní text, URL včetně query parametrů a chybné odkazy
  jako `[0]`; citace neopravuj ani nedoplňuj. Hlavní precision je průměr po odpovědích,
  explicitní S2 / všechny explicitní páry včetně NA/FAB; bez citací či při konečném
  selhání je nula. `*` bez vazby je jen diagnostika. Recall zahrnuje faktická tvrzení
  celé odpovědi, nejen CLAIMS; podpůrné citované úryvky nejsou další tvrzení.
- **Lidské hodnocení:** oba hodnotitelé dostávají stejné zaslepené podklady bez auto
  nápověd. Zachovej původní nezávislé ratingy a audit neshod; druhý hodnotitel pokrývá
  ≥25 % v každém stratu fáze×systému×podmínce (ceil). Klíč/auto kontroly zůstávají u správce.
- **Zmrazení:** G1 váže metodiku, data, rubriku, P1/P2 a kód; P3 se ladí jen na dev.
  Výběr před G2 musí jít přepočítat ze snapshotu v plné přesnosti, P3_final je přesná
  kopie vítěze CZ/EN. Nepřidávej instrukce podle konkrétní úlohy či produktu.
  Podepsané JSON/CSV při replayi nepřepisuj ani znovu nepečeť jen kvůli změně cest.
- **Integrita a interpretace:** duplicity, chybějící vazby a NaN/Inf musí selhat, ne se
  tiše ignorovat. Zachovej neúspěšné běhy i první pokusy. S2 neznamená pravdivost
  odpovědi; neznámé hodnoty nenahrazuj odhadem a konstantní CI nevydávej za jistotu.

## Jak dokončovat změny

- Drž stávající CSV/JSONL schéma a stabilní ID; sdílené čtení/zápis používej z
  `common.py`. Nové chování pokryj `unittest` regresí v odpovídajícím `tests/test_*.py`.
  Nepřidávej nové závislosti bez odůvodnění a souhlasu.
- Změny dat zaznamenej do `data/CHANGES.md`, promptů do `prompts/CHANGELOG.md`;
  u promptů zachovej CZ/EN dvojici a placeholdery. Metodické změny slaď s protokolem,
  rubrikou, předáním a testy podle dopadu, ne pouhým uvolněním kontrol integrity.
- Větší přípravné úpravy dělej po etapách: implementace → kritický read-only subagent
  → opravy a kontroly → commit/push → další etapa, dle požadavku uživatele.
- Ve shrnutí napiš co a proč se změnilo, co jsi skutečně ověřil a co zbývá kolegovi.
  Nevyzkoušené kontroly a neúspěšný push výslovně přiznej; příprava není experiment.
