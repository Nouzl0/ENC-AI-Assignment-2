# Doplňková skutečná UI měření 13. 10. 2026

**Před G1, explorace; žádné lidské hodnocení ani finální analytická matice.**

20 záznamů: 19 completed odpovědí (18 věcných a 1 autentizační odmítnutí) a 1 failed bez odpovědi. Autoritativní je run_index.json. Věcné odpovědi pokrývají 16 nových unikátních veřejných dev/val úloh.

ChatGPT: P1 1, P2 12 věcných + 1 failed. Perplexity: P1 1, P2 1 věcná + 1 odmítnutí přihlášení. Gemini: P2 3 věcné odpovědi.

ChatGPT a Perplexity byly anonymní bez nákupu; dostupný model nebyl prokazatelně pojmenován. ChatGPT později zobrazil basic model a limit zpráv. Gemini používal existující přihlášený účet, viditelný Flash-Lite a dočasný chat. Tarif Gemini se nemá vydávat za stejný free režim. Vyhledávání bylo viditelné v Perplexity/Gemini; u ChatGPT zůstává unclear.

Raw HTML obsahuje pouze DOM odpovědi, nikoli cookies, tokeny nebo stav účtu. PNG zachovávají skutečné UI. Úplné AX/account snapshoty zůstávají mimo Git. Normalizace zachovává skutečné URL včetně query; odpovědi ani špatné/nepárovatelné značky se neopravují. Perplexity čipy jsou převedené na [n] se samostatnou mapou.

Časy jsou skutečné UTC offset ISO řetězce. Začátek CIT-022 ChatGPT a CIT-002 Perplexity nebyl zaznamenán, je null. Konec je okamžik převzetí výsledku; batch scheduling jej prodlužuje a **není platným měřením generovací latence**. Latency je proto null.

Autentizační odpověď Perplexity CIT-009 zní „Sign up and repeat your request.“ a je completed odmítnutí bez citací, nikoli věcná odpověď. ChatGPT CIT-006 má limit bez odpovědi a je failed; prázdný text se nepočítá jako výsledek.

AI review je samostatné kvalitativní posouzení skutečných citovaných stránek; nenahrazuje nezávislé ratingy René/Jan, G1–G3, úplnou segmentaci ani finální precision/CI. Testy a lint nebyly spuštěny.
