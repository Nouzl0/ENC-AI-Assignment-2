# Výzkumný protokol – shrnutí k zmrazení

Plné znění návrhu (s odůvodněním) je v dokumentu **„Návrh projektu: Správnost citací AI asistentů s webovým vyhledáváním"**
(Claude Docs): https://claude.ai/code/artifact/7d19bd66-2c7e-48ad-9c81-fd4939f1ab72
Tento soubor drží parametry, které se po zmrazení nesmí měnit. Změna po zmrazení = nový záznam v tabulce „Odchylky" dole.

## Výzkumná otázka

Jak často citovaný zdroj skutečně podporuje tvrzení, ke kterému ho asistent připojil (citační přesnost), u pěti AI asistentů
s webovým vyhledáváním (ChatGPT, Gemini, Claude, Perplexity, Grok) na 40 faktických rešeršních dotazech v češtině a angličtině
z pěti oblastí a o kolik ji mění strukturovaný a optimalizovaný prompt?

Směr B (výzkum podložený zdroji). Návrh podle schopností produktu → výsledky jsou **porovnáním produktů**, ne modelů.

## Hypotézy (vyhodnocení jen na testovací sadě)

- **H1:** Perplexity má v podmínce P2 citační přesnost alespoň o 10 p. b. vyšší než průměr ChatGPT, Gemini, Claude a Grok.
  Podpořena, pokud odhad ≥ 0,10 a 95% párový bootstrapový interval rozdílu leží nad 0.
- **H2:** P2 zvýší citační přesnost oproti P1 v průměru přes systémy alespoň o 5 p. b., 95% párový bootstrapový interval
  průměrného zlepšení leží nad 0 a zlepšení se projeví alespoň u 4 z 5 systémů (3 ze 4 v úsporné variantě).
- Ostatní porovnání jednotlivých systémů jsou explorační.
- **A1 (alternativa):** vyšší přesnost jen díky menšímu počtu tvrzení → vždy vykázat úplnost citací, počet tvrzení a pokrytí
  klíčových faktů (podíl `key_facts`, které odpověď uvádí a dokládá citací S2); Spearman(počet tvrzení, přesnost).
- **A2 (alternativa):** rozdíly způsobí dostupnost zdrojů / čeština → NA zvlášť, výsledky CZ vs. EN.

## Metriky (definice zmrazeny)

| Role | Metrika | Definice |
| --- | --- | --- |
| Hlavní | Citační přesnost | #S2 dvojic / #všech dvojic v odpovědi (0 bez citací); NA a FAB = selhání; systém = průměr přes případy |
| Vedlejší 1 | Úplnost citací | #tvrzení s ≥ 1 citací S2 / #hodnocených tvrzení (max. 8 na odpověď) |
| Vedlejší 2 | Správnost odpovědi | podíl odpovědí se skóre 2 (škála 0–2 proti referenci a key_facts) |
| Diagnostika | pokrytí klíčových faktů, FAB %, NA %, zdroje úrovně 1 %, dodržení časového limitu, přiznání nejistoty, tvrzení a citace na odpověď, nepřiřazené citace, podíl běhů s vyhledáváním, validita formátu P2/P3 | viz návrh |
| Provoz | medián a p90 latence, kola, zobrazená vyhledávání, náklady, míra opakování, čas lidské kontroly | viz návrh |
| Užitek | Přesnost − 0,1 · L_norm − 0,1 · T_norm | L, T = medián / maximum mezi systémy v dané podmínce; plus Pareto-fronta přesnost × latence |

Nejistota: klastrový bootstrap podle případů (10 000, seed 2026), párový bootstrap rozdílů, Wilson (běh 1),
SD mezi 3 běhy P2, Cohenova kappa mezi hodnoceními **před smířením** (cíl ≥ 0,6 pro S2 vs. ostatní), shoda v dělení na tvrzení.
Dělení na tvrzení: stejná pravidla pro všechny podmínky (rubrika §1).

## Plán běhů

| Fáze | Sada | Podmínky | Běhy | Odpovědí (5 systémů) |
| --- | --- | --- | --- | --- |
| dev | vývojová (20) | P2 | 1 | 100 |
| val | validační (10) | P2, P3A, P3B | 1 | 150 |
| test | testovací (10) | P1, P2, P3 | 1 | 150 |
| repeat | testovací (10) | P2 | +2 | 100 |

Úsporná varianta (2–3 členové): 4 systémy (bez Grok, písemně zdůvodnit), jeden kandidát P3, opakování jen na 5 testovacích případech (`--only`), celkem 320 odpovědí.
Doporučené rozšíření: P1 i na vývojové sadě (+100) jako předem ohlášená replikace H2 – rozhodnout a zapsat před G1.
Pilot (T3): 2 vývojové případy × 5 systémů = 10 odpovědí pro kalibraci rubriky (součást fáze dev).

## Brány (nevracíme se za ně)

| Brána | Podmínka | Datum | Podpis |
| --- | --- | --- | --- |
| G1 Protokol zmrazen | pilot a kalibrace hotové; rubrika v1.x a tento soubor zmrazeny; hashe dat zapsány níže; test sada přesunuta správcem dat mimo sdílenou složku | | |
| G2 P3 zmrazen | P3_final_*.txt vytvořen, hash zapsán, CHANGELOG vyplněn | | |
| G3 Hodnocení uzavřeno | pairs_rated.csv a answers_rated.csv finální, neshody vyřešeny | | |

## Hashe (SHA-256)

Stav balíčku k 2026-09-29. Při G1 přepočítat `python3 scripts/validate_cases.py --write-hashes` a doplnit, pokud se data změnila.

| Soubor | SHA-256 (2026-09-29) | SHA-256 při G1 / G2 |
| --- | --- | --- |
| data/cases_dev.jsonl | c96033cfa8df02e640a4252d3df43376a850bd0450ff3f9ed581e31e7338c01f | |
| data/cases_val.jsonl | eb07e6f63440ba400e8f81fa9723219367853880819a2729911c3b4c7c7b189f | |
| data/cases_test.jsonl | 4611bdf6c8ad26db5109861ea71a5c49eafecc6042fffb20e413abd58b5fcc7f | |
| prompts/P1_baseline_cs.txt | d0326d3204d161e8cf67a556ddd5691ffb585c466de351e8aefef034cf3e3316 | |
| prompts/P1_baseline_en.txt | 4c307ffc626b24bb62f89ccea6e36e9f65477aba426c4400a76d23d114494ac3 | |
| prompts/P2_structured_cs.txt | 481c3fa95fa65d7c3478e2974c6c6d81653082108a466c467d96111a788211b1 | |
| prompts/P2_structured_en.txt | 96e3772d7a11776b3ff0e949dfb000bdf214b480f7a571e5cab19d61da59b554 | |
| prompts/P3_final_cs.txt | (vznikne při G2) | |
| prompts/P3_final_en.txt | (vznikne při G2) | |

## Odchylky od protokolu

| Datum | Odchylka | Důvod | Dopad na interpretaci |
| --- | --- | --- | --- |
| | | | |
