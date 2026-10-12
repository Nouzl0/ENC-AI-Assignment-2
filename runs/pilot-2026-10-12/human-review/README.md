# Nezávislé pilotní hodnocení pro Reného a Jana

Tyto čtyři listy obsahují zaslepené podklady pro 8 skutečných nových odpovědí.
Hodnoticí pole jsou prázdná. René a Jan každý hodnotí všech 8 odpovědí samostatně
podle [rubriky](../../../annotation/rubric.md) a
[kalibračních kotev](../../../annotation/calibration.md).
Pojmenované zdrojové pilotní odpovědi jsou současně zveřejněné v tomto projektu.
U lidí, kteří je již četli, nelze zaručit zaslepení. Tento pilot slouží kalibraci;
analytické odpovědi se do projektu exportují až po dokončení nezávislých ratingů.

1. René vytvoří vlastní kopie `pairs_to_rate.csv` a `answers_to_rate.csv`;
   Jan vytvoří vlastní kopie `pairs_to_rate_rater2.csv` a `answers_to_rate_rater2.csv`.
   Originály zůstanou beze změny. Vyplněné soubory patří mimo Git do oddělených
   adresářů; při práci si lidé nesdílejí ratingy ani operátorův produktový klíč.
2. Každý zkontroluje segmentaci celé odpovědi a otevře citované zdroje. HTTP stav
   ani počet citací neurčuje S2. Doplní skutečné zdrojové rozhodnutí a evidenci,
   correctness, RF/RC a svou identitu ve všech příslušných řádcích.
3. Každý uloží původní nezávislé ratingy před společnou diskusí. Až potom se
   sepíší neshody, kalibrační závěr a případné změny rubriky. Hodnocení po úpravě
   rubriky se znovu provede na stejných podkladech.

První osobní komentář v `results/pilot/team_commentary.md` je návrh podle
uživatelem popsaných názorů. Není vyplněnou rubrikou, nezávislým ratingem
ani podpisem G1/G3. Operátor nesmí do těchto listů doplnit vlastní úsudek
pod identitou Reného nebo Jana.

`PROVENANCE.json` popisuje původ částečné pilotní anotační dávky. Produktové
originály a exportní manifest zůstávají uložené; tento návod není jejich součástí
a nemění žádnou zahashovanou kopii.
