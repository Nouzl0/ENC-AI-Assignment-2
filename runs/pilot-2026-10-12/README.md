# Skutečné pilotní runy – export pro projekt

Tento balíček obsahuje 2 původní anonymní a 8 nových skutečných odpovědí z Avastu,
metadata, raw text/HTML, snímky a SHA-256. Jde o 2 unikátní úlohy v P2, nikoli
finální analytický benchmark. Původní soukromé soubory zůstaly beze změn.

- `legacy/`: původní odpovědi ChatGPT/Perplexity a byte-identická zdrojová metadata.
- `avast/`: nový sběr, originální odpovědi, raw HTML/texty, snímky a provozní audit.
- `avast/normalization-v2/`: úplné Perplexity citační skupiny; v1 i raw zachovány.
- `human-review/`: čtyři dosud nevyplněné pilotní listy. Oba hodnotitelé pokrývají všech 8 nových odpovědí.
- `export_manifest.json`: původ, relativní exportní cesty, velikosti a SHA-256 každé kopie.

Zdrojová CSV zachovávají původní soukromé cesty a immutable plány. Relativní odkazy
na kopie pro čtení jsou v `results/pilot/run_summary.csv`; podepsané brány neexistují.
Neúspěšný Claude pokus je auditní doklad, není odpovědí ani ratingem. Neodeslaný řádek
CIT-020 zůstává planned. Žádné první pokusy nebyly nahrazeny regenerovanými výstupy.

Z balíčku jsou vynechány browser queue, osobní věkové ověření, profily, tokeny,
nesouvisející historie chatů, operátorův zaslepovací klíč a skrytý test. Původní
Gemini screenshot celé obrazovky zůstává soukromý; exportovaný snímek odpovědi
je výslovně označen jako pozdější zachycení stejné odpovědi.
Některé původní viewportové snímky zachycují prompt nebo navazující návrhy,
nikoli celou odpověď. Dodatečné snímky v širším/vyšším viewportu jsou uložené
odděleně s časem; i u nich může být část obsahu oříznuta. Autoritativní obsah
odpovědi je proto zachovaný raw text/HTML společně s doklady citací.

Git u těchto exportů neprovádí normalizaci konců řádků: původní CRLF je součástí
zahashovaných bytes. Manifest lze zkontrolovat offline proti každé relativní cestě.

Automatické HTTP podklady a klíč jsou pouze u nehodnotícího operátora mimo Git.
Lidé při hodnocení pracují v oddělených kopiích listů a zachovají nezávislé raw ratingy.
AI komentář týmu ani parser nejsou jejich náhradou. `score --final` vyžaduje G3.
