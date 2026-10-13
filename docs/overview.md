(overview)=
# Shrnutí

Studie sleduje podporu tvrzení jejich citovanými zdroji u rešeršních AI produktů.
Aktuální export obsahuje **40 různých úloh, 93 věcných odpovědí a 92
podkladů pro lidské hodnocení**. Původních 33 odpovědí je oddělených od doplňku.
Deset nových otázek vzniklo po byte/hash fixaci šablon; nyní už jsou zveřejněné.
Původní chybné zachycení SUP-H002/P2 je vyřazené, náhrada vybraná jednou.

Odpovídaly ChatGPT, Gemini, Grok a Perplexity; Claude neměl dokončenou odpověď.
Účty a konfigurace se liší. Gemini má 9 nových otázek ve všech třech
podmínkách P1/P2/P3A. P3A zůstal předem fixovaný, nevyhlašuje se validačním vítězem.

## Výsledky a kontrola

AI obsahové posouzení všech 33 pilotních odpovědí našlo 47 ze 48 RF správně:
makro pokrytí 0,9848, bootstrap 95% interval 0,9516–1,0000. Opravený atomizovaný
subset 11 dokončených odpovědí na CIT-004, CIT-008 a CIT-013 má 99 explicitních
párů: 78 S2, 1 S1, 20 S0. Makro precision je 0,7954 (CI 0,7265–0,8433).
Po započtení jednoho terminálního selhání jako nuly jde o 0.7291 z 12 pokusů.
Tři záměrně vybrané klastry neumožňují obecný žebříček ani potvrzení H1/H2.

Čtyři starší clipboard exporty byly obnoveny z tehdejších záznamů, bez nového
modelového běhu. Nové exporty čtou text a href přímo z příslušného DOM, bez
schránky. Reference deseti doplňkových otázek mají AI důkazy pro 18 RF;
nezávislá lidská kontrola zůstává nutná.

## Lidské hodnocení a rozsah

Zaslepené listy mají prázdné ratingy. První hodnotitel pokryje všechny
způsobilé odpovědi; druhý ≥25 % v každém stratu fáze × produkt × podmínka.
Klíč, značky produktů a automatické návrhy ratingů se nepředávají. Postup je
v [](#human-handoff). Intervaly AI auditu nezahrnují chyby hodnotitele ani lidskou shodu.

Plná vyvážená matice, nezávislé ratingy a původní G1/G2/G3 nejsou dokončené.
Pozdější ratingy exploratorních dat nemohou zpětně schválit původní brány nebo
obnovit utajený holdout. Aktuální podklady jsou připravené k přezkumu, nikoli
vydávané za úplný potvrzující experiment.
