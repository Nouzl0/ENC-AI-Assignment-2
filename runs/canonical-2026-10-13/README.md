# Kanonický registr skutečných zachycení

Jeden record_id = collection/run_id; historicky opakované run_id mezi kolekcemi nejsou sloučeny. registry.jsonl je zdroj pro nový zaslepený export. coverage.json rozlišuje uložené věcné odpovědi a způsobilé podklady pro hodnocení; obsahuje i plánované řádky, odmítnutí, chyby a náhrady. Původní exporty zůstávají beze změny.

Čtyři nesprávné clipboard texty nahradila věrná rekonstrukce odpovědi z tehdejšího AX a snímku. Viz capture-corrections.json a recovery-v2. Nešlo o nové modelové pokusy ani opravu odpovědi. Nezachycené cíle nativních citací zůstávají neznámé. Původní SUP-H002/P2 s operátorskou chybou je vyřazený a náhrada započítaná jednou.

Template SHA a rendered-prompt SHA jsou samostatná pole. Vykreslené soubory jsou byte shodné s původními známými hashi/texty. Přesné časy zůstávají původní; capture interval je horní mez se zpožděním operátora. Prázdné časy a neviditelné náklady/modely se nedopočítávají.

Případy: data/cases_dev.jsonl, data/cases_val.jsonl a runs/reference-correction-2026-10-13/cases_supplement_v2.jsonl. Post-collection AI opravy referencí jsou datované, nikoli nezávisle lidsky schválené. Sběr stále neplní G1/G2/G3 ani úplnou produktovou matici.

V podkladu SUP-H004/P2 byl odstraněn pouze UI nadpis „Odpověď Gemini“; původní raw je zachovaný. Jde o zaslepení, ne změnu odpovědi. Pro dynamické otázky zaslepený export převádí RUN_DAY na doložený UTC den odeslání, bez změny původního případu.
