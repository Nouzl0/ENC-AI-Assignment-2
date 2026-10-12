# Rozšířený skutečný pilot – export pro projekt

Samostatný před-G1 pilot na šesti dalších veřejných dev úlohách v P2.
30 předem plánovaných řádků: **23 completed, 1 failed, 6 planned**.
Všech 24 cloudových prvních pokusů z dostupných produktů bylo skutečně odesláno;
Claude nebyl znovu zatěžován během známého limitu. Spolu s kolekcí 12. října
je v projektu **33 skutečných odpovědí na 8 unikátních úloh**. Pilot není
analytická dev/val/test/repeat matice a žádná brána jím není zpětně splněna.

- `avast/`: byte-identická metadata, původní plán před odesláním, odpovědi,
  raw HTML/text, snímky, skutečné submission záznamy, nastavení a provozní audit.
- `avast/normalization-v2/`: věrný export šesti Perplexity odpovědí, který zachovává
  44 původních citačních skupin a 57 skutečných UI zdrojových vazeb. V1/raw se nevymazaly.
- `avast/AI_REFERENCE_REVIEW.csv`, `avast/AI_SOURCE_PROVENANCE.json`: doplňková
  kontrola AI a provenance skutečných primárních snapshotů. Není lidskou verifikací.
- `human-review/`: 4 nevyplněné listy pro nezávislé hodnocení všech 23 odpovědí
  oběma lidmi. Parser navrhl 148 řádků; nejde o provedené ratingy.
- `export_manifest.json`: 183 exportovaných originálů s původem, velikostí a SHA-256.

ChatGPT CIT-004 přešel po částečném výstupu do chyby načtení. První partial/raw
je uchován, terminální JSON/TXT dokládá failed/tool_error; interval 137,738 s
se odlišuje od původního partial capture 18,878 s. Neproběhla regenerace.
U Perplexity CIT-008 selhal až snímek skryté stránky po hotové odpovědi.
Pozorování dokončení po 17,625 s bylo obnoveno ze skutečných původních probe
záznamů, text i HTML zůstaly stejné a prompt nebyl znovu odeslán. Pozdější snímek
je doložený; aktivita stránky byla emulovaná jen po odpovědi při zachycení
snímku/karuselů, pak obnovená. Tyto úkony nejsou další cloudové pokusy.

Některé původní snímky zachycují pouze prompt, neúplný viewport nebo černý
výřez. Nejde o úplný obrazový doklad; autoritativní je raw obsah a terminální
JSON/TXT. U latencí se rozlišují pozorované intervaly, prodlevy a horní meze.

Originální soukromá složka zůstává mimo worktree. Do Git nejsou přenesené
browser queue/archiv, aktivní debug relace, účty/profily/přístupové údaje,
nesouvisející historie, zaslepovací klíč, automatické nápovědy, celý obsah
primárních článků ani skrytý test. Relativní odkazy pro čtení jsou v
`results/pilot/run_summary.csv`; source CSV/manifest zachovávají původní cesty.
Git u originálů nepřevádí konce řádků. README je nově napsaný průvodce,
ne součást hashovaného originálního snapshotu.
