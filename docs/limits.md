(limits)=
# Limity a co výsledky neprokážou

Výsledek je porovnáním pěti produktů na konkrétních dotazech v jednom časovém okně, ne měřením schopnosti jazykových modelů ani obecným žebříčkem.

:::{important} Omezené prostředky
Studie vznikla s omezeným časem a rozpočtem na využití produktů a AI agentů. Plný rozsah (≈ 500 analytických odpovědí, dva lidští hodnotitelé) proto zatím běžel jen v podobě **skutečného pilotu na 8 úlohách**. Metodika, nástroje a data jsou připravené tak, aby šel plný experiment spustit bez změn návrhu. Místo odhadování chybějících čísel je výslovně uvádíme jako nezměřená.
:::

- **Malý vzorek (10 testovacích případů).** Široké intervaly, malé rozdíly nerozlišíme. *Řešení:* Velikost efektu a intervaly, doplňkové výsledky z vývoje
- **Produkty se mění.** Model, rozhraní i vyhledávání se mohou změnit během dnů. *Řešení:* 72hodinové okno, záznam viditelného modelu a data
- **Web se mění.** Zdroj může zmizet nebo se změnit mezi během a hodnocením. *Řešení:* Hodnocení do 7 dní od běhu, snímky obrazovky, archivace stránky
- **Bez parity nástrojů.** Rozdíly nelze připsat modelu. *Řešení:* Závěry formulujeme jen o produktech
- **Úroveň účtu a personalizace.** Pilot používá existující účty, Gemini Plus; rozdíl úrovní může výsledek ovlivnit. *Řešení:* Před zmrazením sladíme konfiguraci nebo deklarujeme rozdíly; úroveň/model zapisujeme u každého běhu
- **Jedno kolo a povolené standardní doptání.** Neměříme volnou vícekolovou konverzaci; případné druhé kolo zaznamenáme. *Řešení:* Uvedeme jako hranici platnosti
- **Dotazy sám zvolil tým.** Známá fakta může model znát i bez vyhledávání. *Řešení:* Hodnotíme citaci, ne jen odpověď; dev/val mají 13/30 edge (43,3 %), soukromý test čeká na lidskou kontrolu
- **Pilot bez lidských ratingů.** Pozorování v pilotu jsou kvalitativní a kontroly AI nenahrazují lidské hodnocení. *Řešení:* Listy pro dva hodnotitele jsou připravené; výsledky se publikují až po ratingu
- **Hodnotitelé jsou studenti.** U odborných zdrojů (právo, zdraví) mohou chybovat. *Řešení:* Kalibrace, dvojité hodnocení, zlaté zdroje v případu
- **Dělení na tvrzení je subjektivní.** Počet dvojic se může mezi hodnotiteli lišit. *Řešení:* Pravidla v rubrice, člověk kontroluje celou odpověď ve všech podmínkách, bez limitu osmi tvrzení
- **Jen čeština a angličtina, česká IP.** Jiné jazyky a regiony mohou dopadnout jinak. *Řešení:* Uvedeme jako hranici platnosti

:::{tip} Co výsledky prokázat mohou
Zda se na této sadě a v tomto období liší citační přesnost produktů a zda strukturovaný prompt u jednotlivých produktů pomáhá. Také jaké typy chyb citací se opakují.
:::

:::{warning} Co prokázat nemohou
Který jazykový model je lepší, jak se produkty chovají na jiných typech dotazů a zda rozdíly vydrží po další aktualizaci produktu.
:::
