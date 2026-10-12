# Limity a co výsledky neprokážou

Výsledek bude porovnáním pěti produktů na 40 konkrétních dotazech v jednom časovém okně. Nebude to měření schopnosti jazykových modelů ani obecný žebříček.

| Limit | Důsledek | Co s tím děláme |
| --- | --- | --- |
| Malý vzorek (10 testovacích případů) | Široké intervaly, malé rozdíly nerozlišíme | Velikost efektu a intervaly, doplňkové výsledky z vývoje |
| Produkty se mění | Model, rozhraní i vyhledávání se mohou změnit během dnů | 72hodinové okno, záznam viditelného modelu a data |
| Web se mění | Zdroj může zmizet nebo se změnit mezi během a hodnocením | Hodnocení do 7 dní od běhu, snímky obrazovky, archivace stránky |
| Bez parity nástrojů | Rozdíly nelze připsat modelu | Závěry formulujeme jen o produktech |
| Úroveň účtu a personalizace | Nový pilot používá existující účty, Gemini Plus; rozdíl úrovní může výsledek ovlivnit | Před G1 sladíme konfiguraci nebo deklarujeme rozdíly; úroveň/model u každého běhu |
| Jedno kolo a povolené standardní doptání | Neměříme volnou vícekolovou konverzaci; případné druhé kolo zaznamenáme | Uvedeme jako hranici platnosti |
| Dotazy sám zvolil tým | Známá fakta může model znát i bez vyhledávání | Hodnotíme citaci, ne jen odpověď; dev/val mají 13/30 edge (43,3 %), nový test ještě není hotový |
| Hodnotitelé jsou studenti | U odborných zdrojů (právo, zdraví) mohou chybovat | Kalibrace, dvojité hodnocení, zlaté zdroje v případu |
| Dělení na tvrzení je subjektivní | Počet dvojic se může mezi hodnotiteli lišit | Pravidla v rubrice, člověk kontroluje celou odpověď ve všech podmínkách, bez limitu osmi tvrzení |
| Jen čeština a angličtina, česká IP | Jiné jazyky a regiony mohou dopadnout jinak | Uvedeme jako hranici platnosti |

:::{tip} Co výsledky prokázat mohou
Zda se na této sadě a v tomto období liší citační přesnost produktů a zda strukturovaný prompt u jednotlivých produktů pomáhá. Také jaké typy chyb citací se opakují.
:::

:::{warning} Co prokázat nemohou
Který jazykový model je lepší, jak se produkty chovají na jiných typech dotazů a zda rozdíly vydrží po další aktualizaci produktu.
:::
