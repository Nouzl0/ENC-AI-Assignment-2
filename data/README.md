# Benchmarková data

30 aktuálních týmových dev/val návrhů a 10 veřejných historických kandidátů testu.
To ještě není 40 úloh se skutečně soukromým holdoutem. Datované původní reference jsou **návrh**, nikoli protokol
dokončené nezávislé kontroly. Před G1 správce dat ověří každý povinný fakt a vyplní
`source_evidence.csv` podle šablony. Aktuální změny dev/val: `CHANGES.md`.

| Soubor | Případy | Použití |
| --- | --- | --- |
| `cases_dev.jsonl` | CIT-001 – CIT-020 | ladění promptů, validátorů a rubriky |
| `cases_val.jsonl` | CIT-021 – CIT-030 | výběr kandidáta P3 |
| `published_test_candidates.jsonl` | CIT-031 – CIT-040 | původní **publikovaní kandidáti**, nepoužívat jako nový holdout |

Soubor byl commitnut do Git; pouhé přesunutí neodstraní historii ani neobnoví utajení. To není důkaz,
že už je každý produkt kontaminovaný, ale původní soubor nelze prezentovat jako zaručeně skrytý.
Nový skutečný holdout připraví nezávislý správce mimo repozitář; autor promptu jej před G2 neuvidí.
Část otázek s protichůdnými zdroji rozpor záměrně nenaznačuje (kontrola, že P2 nezvýhodňuje jen navádění).

Default validátor i `--no-test` čtou **pouze dev/val**, nikoli test:

```bash
python3 scripts/validate_cases.py --no-test
# Jen správce, nikoli autor promptu: vyžaduje přístup k celému soukromému souboru.
python3 scripts/validate_cases.py --test-file "$WORK/holdout.jsonl"
```

Skript nevypisuje otázky, ale čte jejich obsah a vypisuje ID/agregáty. To nenahrazuje
izolaci přístupu. Před G1 lze opravit návrhové reference se záznamem důvodu; od G1
jsou soubory/hashy neměnné. Průchod validátorem není nezávislé ověření faktů.

## Pole případu

| Pole | Význam |
| --- | --- |
| `task_id` | unikátní ID; nové testy nesdílejí ID ani otázky s dev/val a publikovanými kandidáty; DEMO-* jen softwarové fixtures |
| `capability` | vždy `citation_accuracy` |
| `task_type` | `fact` (dohledání faktu), `primary_source` (vyžaduje primární dokument), `synthesis` (více zdrojů) |
| `difficulty` | `easy` / `medium` / `hard` |
| `language` | `cs`, `en`, `cs+en` (smíšené; používá český prompt) |
| `domain` | `veda_zdravi`, `pravo`, `it`, `ekonomika`, `historie_kultura` |
| `development_validation_test_split` | `dev` / `val` / `test` |
| `user_prompt` | otázka, která se vloží do šablony promptu |
| `context_or_files` | vždy prázdné (bez příloh) |
| `expected_properties` | co musí dobrá odpověď splnit (pro hodnotitele) |
| `schema_version` | 2 pro revidované dev/val; nové soukromé testy musí použít stejné schéma |
| `reference_answer_or_tests` | `reference_answer` (i kontext), `required_facts` (povinné; RF1…), `optional_facts` (bonus), `key_facts` (alias povinných), `gold_sources` (doklady k lidskému ověření) |
| `edge_case_type` | `none`, `false_premise`, `conflicting_evidence`, `missing_info`, `ambiguous`, `time_constraint`, `recent_change`, `cz_en_mix` |
| `evaluation_method` | lidská rubrika + automatická kontrola URL + shoda s referencí (u dynamických: ověření v den běhu) |
| `source_or_provenance` | původ dotazu a datum ověření |
| `reference_valid_as_of` | datum platnosti reference; `RUN_DAY` = ověřit v den běhu (CIT-015, CIT-027) |
| `rater_notes` | časté chyby a tolerance pro hodnotitele |

## Doklady a etika

- `source_evidence_TEMPLATE.csv` → soukromé `source_evidence.csv`: před G1 každý RF/OF
  všech skutečných úloh, přesná hodnota, nezávislý ověřovatel, primární zdroj a snapshot/hash.
- `annotation/run_day_evidence_TEMPLATE.csv` → soukromé `run_day_evidence.csv`: každý
  RF/OF dokončené RUN_DAY úlohy v každém skutečném UTC dni, včetně dev/val/repeat.
  Tento denní záznam doplňuje aktuální hodnotu, **nepřepisuje** zmrazenou referenci.
- Žádné osobní údaje, důvěrná data, soukromé konverzace ani přístupové tokeny.
  Otázky jsou vlastní texty o veřejných faktech, ne neautorizované převzaté materiály.
  Veřejná dostupnost stránky není automaticky právem šířit celý text/snapshot.
- Evidence a audity musí být oprávněně kontrolovatelné učitelem; nepoužívat materiál,
  který nelze takto sdílet. Veřejně sdílet vlastní popis/krátký oprávněný výňatek,
  ne úplný chráněný či paywallový obsah. Soukromé zdrojové snapshoty nejsou automaticky
  součástí veřejného balíčku. Publikace nového testu až po G3 a kontrole týmem.
