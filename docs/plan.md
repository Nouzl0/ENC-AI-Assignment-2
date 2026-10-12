# Plán běhů a nejistota

Výchozí plán má 500 odpovědí. Hlavní podmínku P2 na testovací sadě spouštíme třikrát, abychom změřili rozptyl mezi běhy.

| Fáze | Sada | Podmínky | Běhy | Odpovědí (× 5 systémů) |
| --- | --- | --- | --- | --- |
| 1 Vývoj | vývojová (20) | P2 | 1 | 100 |
| 2 Validace | validační (10) | P2, P3-A, P3-B | 1 | 150 |
| 3 Test | testovací (10) | P1, P2, P3 | 1 | 150 |
| 4 Opakování | testovací (10) | P2 | 2 další | 100 |
| | | | **Celkem** | **500** |

Odhad práce je asi 3 minuty na běh a 7 minut na hodnocení, celkem asi 85 hodin, tedy 21 hodin na člena čtyřčlenného týmu.

**Úsporná varianta** pro 2–3 členy: čtyři systémy (Grok vynecháme s písemným odůvodněním), jeden kandidát P3 a opakování jen na 5 testovacích případech, celkem 320 odpovědí.

**Rozšíření:** P1 i na vývojové sadě (+100) zvýší sílu testu H2, protože P1 ani P2 na ní laděné nejsou.

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
| Chyba studenta | Vložen špatný prompt, zapnutý hloubkový výzkum | Ano, běh se zahodí | Nepočítá se systému, eviduje se |
| Chyba evaluace | Špatně zkopírovaná URL do listu | Ne, opraví se záznam | Oprava se zapíše |

Každé selhání a každý ruční zásah zapíšeme do sloupců `failure_type`, `retries` a `manual_intervention` v metadatech běhu. Neúspěšný pokus nemazáme ani po úspěšném opakování.
