# Reprodukovatelný balíček

Balíček `czai-citace.zip` obsahuje vše, co jiný student potřebuje ke kontrole a zopakování analýzy. Skripty potřebují jen Python 3.9+ se standardní knihovnou a celý tok je otestovaný na syntetických datech (`bash demo/run_demo.sh`).

Zdrojový kód je dostupný na <https://github.com/Nouzl0/ENC-AI-Project>.

| Požadavek zadání | Soubor v balíčku |
| --- | --- |
| 1 Výzkumný protokol | tento dokument a `PROTOCOL.md` (zmrazené parametry, brány, hashe, odchylky) |
| 2 Benchmarková data | `data/cases_dev.jsonl`, `cases_val.jsonl`, `cases_test.jsonl` a popis polí v `data/README.md` |
| 3 Sada promptů | `prompts/` (P1, P2, kandidáti P3-A a P3-B, česky i anglicky) a `prompts/CHANGELOG.md` |
| 4 Metadata běhů | `runs/run_plan_*.csv` z `make_run_plan.py`, návod `runs/README.md` |
| 5 Kód a postupy hodnocení | `scripts/validate_cases.py`, `check_citations.py`, `score.py`, rubrika `annotation/rubric.md` |
| 6 Výsledky | `results/` z `score.py`: metriky, intervaly, hypotézy, opakované běhy, užitek, Pareto, shoda |
| 7 Analýza chyb | `analysis/error_analysis_TEMPLATE.csv` a návod |
| 8 Závěrečná zpráva | Sepíše tým po bězích; osnovu dávají sekce tohoto dokumentu |

## Postup v příkazech

1. `python3 scripts/validate_cases.py --write-hashes`, pak zapsat hashe do `PROTOCOL.md` (**G1**).
2. `python3 scripts/make_run_plan.py --phase dev`, spustit běhy podle `runs/README.md`.
3. `python3 scripts/check_citations.py --runs runs/run_plan_dev.csv --out-dir annotation/dev`, ohodnotit listy.
4. Stejně fáze `val`, poté vytvořit `prompts/P3_final_*.txt` (**G2**). Skript bez něj fázi `test` nespustí.
5. Fáze `test` a `repeat`, hodnocení s druhým hodnotitelem, vyřešení neshod (**G3**).
6. `python3 scripts/score.py`, pak analýza chyb a závěrečná zpráva.

## Zdroje

- Zadání: CZAI Assignment 1 (PDF od vyučujícího).
- Nastavení produktů (stav k 29. 9. 2026): ChatGPT search, ChatGPT Temporary Chat, Gemini Apps Help, Gemini temporary chats, Claude web search, Claude incognito, Perplexity Pro Search, Perplexity Memory, About Grok.
- API s webovým vyhledáváním: OpenAI web search, Gemini grounding, Anthropic web search tool, xAI web search.
- Referenční zdroje ke každému testovacímu případu jsou v poli `gold_sources` v `data/`, všechny otevřené a ověřené 29. 9. 2026.
