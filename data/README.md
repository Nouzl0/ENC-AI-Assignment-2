# Benchmarková data

40 syntetických faktických dotazů vytvořených týmem; referenční odpovědi a `gold_sources` ověřeny na otevřených zdrojích 29. 9. 2026.

| Soubor | Případy | Použití |
| --- | --- | --- |
| `cases_dev.jsonl` | CIT-001 – CIT-020 | ladění promptů, validátorů a rubriky |
| `cases_val.jsonl` | CIT-021 – CIT-030 | výběr kandidáta P3 |
| `cases_test.jsonl` | CIT-031 – CIT-040 | **držená stranou** – otevřít až po zmrazení P3 (brána G2) |

**Autor promptu tento soubor neotevírá.** Správce dat ho po stažení balíčku přesune mimo sdílenou složku (hash zůstává
v `PROTOCOL.md`) a vrátí ho až na bráně G2.
Část otázek s protichůdnými zdroji rozpor záměrně nenaznačuje (kontrola, že P2 nezvýhodňuje jen navádění).

Pro kontrolu bez otevření použijte `python3 scripts/validate_cases.py --no-test`
(skript nikdy nevypisuje obsah testovacích případů, jen agregáty a ID).

## Pole případu

| Pole | Význam |
| --- | --- |
| `task_id` | CIT-001 … CIT-040 |
| `capability` | vždy `citation_accuracy` |
| `task_type` | `fact` (dohledání faktu), `primary_source` (vyžaduje primární dokument), `synthesis` (více zdrojů) |
| `difficulty` | `easy` / `medium` / `hard` |
| `language` | `cs`, `en`, `cs+en` (smíšené; používá český prompt) |
| `domain` | `veda_zdravi`, `pravo`, `it`, `ekonomika`, `historie_kultura` |
| `development_validation_test_split` | `dev` / `val` / `test` |
| `user_prompt` | otázka, která se vloží do šablony promptu |
| `context_or_files` | vždy prázdné (bez příloh) |
| `expected_properties` | co musí dobrá odpověď splnit (pro hodnotitele) |
| `reference_answer_or_tests` | `reference_answer`, `key_facts` (pro správnost 0–2), `gold_sources` (ověřené URL) |
| `edge_case_type` | `none`, `false_premise`, `conflicting_evidence`, `missing_info`, `ambiguous`, `time_constraint`, `recent_change`, `cz_en_mix` |
| `evaluation_method` | lidská rubrika + automatická kontrola URL + shoda s referencí (u dynamických: ověření v den běhu) |
| `source_or_provenance` | původ dotazu a datum ověření |
| `reference_valid_as_of` | datum platnosti reference; `RUN_DAY` = ověřit v den běhu (CIT-015, CIT-027) |
| `rater_notes` | časté chyby a tolerance pro hodnotitele |

Etika: žádné osobní údaje, důvěrná data, soukromé konverzace ani autorsky chráněné texty; jen veřejně dostupná fakta.
