# Plán běhů a nejistota

Výchozí plán má **500 analytických + 10 pilotních odpovědí navíc**.
P2 na předem vybraných testových úlohách spouštíme třikrát. Dev se po G1
sbírá znovu; pilot se do analytického dev nepřebírá.

| Fáze | Sada | Podmínky | Běhy | Odpovědí (× 5 systémů) |
| --- | --- | --- | --- | --- |
| 1 Vývoj | vývojová (20) | P2 | 1 | 100 |
| 2 Validace | validační (10) | P2, P3-A, P3-B | 1 | 150 |
| 3 Test | testovací (10) | P1, P2, P3 | 1 | 150 |
| 4 Opakování | testovací (10) | P2 | 2 další | 100 |
| | | | **Celkem** | **500** |

Hrubý odhad podle protokolu je 99,7 h včetně 140 druhých hodnocení
(10 min na běh a první anotaci, 7 min na druhou). Není to naměřený čas;
navíc jsou pilot, reference, audit, analýza, zpráva a čekání na limity.

**Úsporná varianta zachová všech pět produktů**: jeden P3 kandidát a pět
repeat úloh, 400 + 10 běhů, 115 druhých hodnocení a odhad 80,1 h.
Čtyřproduktová varianta 320 + 8 je možná pouze při předem doložené
nedostupnosti/nevhodnosti pátého, nikoli kvůli úspoře práce; odhad 64,1 h.
Varianta a repeat ID se určí před G1, nikdy podle výsledků.

**Volitelné rozšíření před G1:** P1 na dev (+100) umožní pouze explorační srovnání. Dev/val se nepřidávají do potvrzujícího testu H2, který používá výhradně nový holdout.

## Metody nejistoty

- **Klastrový bootstrap podle případů:** 10 000 převzorkování testovacích případů s vracením (seed 2026) a percentilový 95% interval. Dvojice tvrzení–citace nejsou nezávislé, proto převzorkováváme celé případy.
- **Párový bootstrap rozdílů** pro H1 (Perplexity minus průměr ostatních) a H2 (P2 minus P1). Všechny systémy řeší stejné případy, takže párování odstraní rozptyl obtížnosti případů.
- **Wilsonův 95% interval** pro binární podíly na úrovni odpovědi, například podíl správných odpovědí nebo odpovědí s alespoň jednou FAB citací.
- **Variabilita mezi běhy:** směrodatná odchylka přesnosti přes tři běhy P2 a podíl případů, kde se správnost odpovědi mezi běhy změní.
- **Shoda hodnotitelů:** Cohenova kappa a procento shody (viz [](#human-rating)).

:::{important} Interpretace
S 10 testovacími případy budou intervaly široké a rozdíly pod zhruba 15 procentních bodů pravděpodobně nepůjde rozlišit. Proto uvádíme velikost efektu, interval a praktický význam, ne jen „signifikanci".

Výsledky P2 z vývojové a validační sady uvedeme jako doplňkové, protože P2 na nich laděný nebyl. U P3 platí jen výsledek z testovací sady.
:::

## Selhání a opakování

Neúspěšný běh je součástí dat. Opakování povolujeme jen u selhání mimo model a vždy vykazujeme úspěšnost na první pokus i po opakování.

| Typ selhání | Příklad | Opakování | Jak se počítá |
| --- | --- | --- | --- |
| Výstup modelu | Odmítnutí, odpověď bez citací, halucinace | Ne | Hodnotí se běžně (bez citací = přesnost 0) |
| Neplatný formát | P2 odpověď bez sekce ZDROJE | Ne | Hodnotí se; zapíše se do validity formátu |
| Chyba nástroje | „Vyhledávání se nezdařilo" | 1× ihned | První pokus i výsledek zvlášť |
| Limit požadavků | Vyčerpaný denní limit | 1× do 24 hodin | První pokus i výsledek zvlášť |
| Časový limit | Žádná odpověď do 180 sekund | 1× ihned | První pokus i výsledek zvlášť |
| Výpadek produktu | Chyba serveru, stránka nedostupná | 1× v rámci 24hodinového okna | První pokus i výsledek zvlášť |
| Chyba studenta | Vložen špatný prompt, zapnutý hloubkový výzkum | Svázaná náhrada | Původní excluded řádek a důkaz zůstávají |
| Chyba evaluace | Špatně zkopírovaná URL do listu | Ne, opraví se záznam | Oprava se zapíše |

Každé selhání a každý ruční zásah zapíšeme do sloupců `failure_type`, `retries` a `manual_intervention` v metadatech běhu. Neúspěšný pokus nemazáme ani po úspěšném opakování.

Úplné příkazy s manifesty a soukromými cestami jsou v `HANDOFF.md`.
Konstantní bootstrapový CI není nulová populační nejistota. Testové úlohy
napříč systémy/podmínkami mají okno 24 h, test 72 h a repeat následujících
72 h; zdrojové ratingy do 7 dní. Odchylky a jejich dopad se zaznamenávají.
