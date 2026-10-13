(references)=
# Příloha C: zdroje a použití AI

## Zadání a metodické zdroje

- CZAI Assignment 1: porovnání AI asistentů, zadání a šablona worksheetu (`assignment/CZAI_Assignment_1.pdf`, `assignment/2026-AI-Student-worksheet.md`), 2026.
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46. (shoda hodnotitelů, κ)
- Efron, B. (1979). Bootstrap methods: another look at the jackknife. *The Annals of Statistics*, 7(1), 1–26. (bootstrapové intervaly)
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212. (intervaly pro podíly)

## Zdroje použité při kontrole referencí a v analýze chyb

Primární zdroje s odkazy jsou uvedeny přímo v tabulkách: pro všech 30 veřejných úloh v příloze [](#source-audit) a pro osm pilotních úloh
v kapitole [](#error-analysis) (např. NIST, Zeměměřický úřad, Ústava ČR na PSP, Federal Register, ČSÚ, Shakespeare Birthplace Trust,
Europe PMC). U každého je uveden locator (část stránky) a datum kontroly; soukromé snapshoty mají čas a SHA-256 a jsou součástí
auditní evidence mimo veřejný repozitář. Skutečné odpovědi produktů se citují z exportů v `runs/pilot-2026-10-12/` a `runs/pilot-2026-10-13/`.

## Nástroje

Python (standardní knihovna) pro skripty a testy, MyST Markdown a Typst pro sazbu zprávy. Zdrojové kódy a verze jsou v `scripts/`, `tests/`,
`pyproject.toml` a `uv.lock`.

## Použití AI

Odpovědi hodnocených produktů (ChatGPT, Gemini, Claude, Perplexity, Grok) jsou předmětem studie. Sběr pilotních odpovědí z webových rozhraní,
pomocná kontrola referencí, návrhy komentářů a část nástrojů a textu vznikly s pomocí AI agentů pod dohledem týmu. Všechny výstupy AI jsou v
projektu označeny (např. `SUPPLEMENTARY_AI_REVIEW_NOT_HUMAN_VERIFIED`), neslouží jako nezávislé lidské hodnocení ani jako jediný důkaz závěrů
a hodnoticí LLM se pro hlavní metriku nepoužívá. Zodpovědnost za obsah nesou autoři.
