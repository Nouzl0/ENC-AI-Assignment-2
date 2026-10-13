# Doplňkový sběr 13. 10. 2026

Dokumentované pokrytí: **40 různých úloh** (20 dev, 10 val, 10 nových oddělených otázek).
Původní pilot má 33 odpovědí; tento doplněk přidává **51 věcných odpovědí**.
Celkem je tedy 84 věcných odpovědí, včetně oddělené náhrady operatorovy chyby.
Náhrada nezvyšuje počet úloh. Jeden autentizační text a dvě chyby bez odpovědi
jsou uchovány zvlášť. `run_registry.jsonl`, `coverage.csv` a `task_coverage.csv`
popisují skutečné pokrytí; nikoli pouhý plán.

Pět nových otázek má Gemini P1/P2/P3A. Další otázky mají neúplnou promptovou
nebo produktovou matici. P3A byl byte/hash zmrazen před konstrukcí nových otázek,
ale nebyl validačně vybrán jako původní P3_final. Původní G1/G2/G3 se netvrdí.
Nové otázky jsou vytvořeny a ověřovány AI, nikoli nezávisle schváleny člověkem.

Původní lidské listy nejsou vyplněné. AI review je výslovně označeno v jednotlivých
kolekcích a v `results/ai-review-2026-10-13/`. Latence jsou pozorované horní meze
nebo unknown; neznámé časy, tarify a náklady nejsou odhadnuté. Account gates,
původní chybné zachycení a náhrady jsou zachovány v auditu. Původní snapshoty
mimo git nejsou upraveny; export obsahuje jen schválené odpovědi a snímky.

Testy ani lint nebyly na žádost uživatele spuštěny.
