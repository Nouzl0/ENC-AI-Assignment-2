# Automatické kontroly a lidské hodnocení

`check_citations.py` parsuje citace, uchovává původní URL a připravuje
zaslepené podklady. HTTP dostupnost, přesměrování, obecnost URL, shoda
entit, datum publikace a formát jsou diagnostiky pro správce. **Oba
nezávislí hodnotitelé dostávají stejné podklady bez automatických nápověd.**
Automatika nepředvyplňuje jejich ratingy. Samotná HTTP chyba neprokazuje
neexistenci zdroje; paywall není automaticky nepodpořené tvrzení.

(human-rating)=
## Rubrika a nezávislost

| Rating | Pravidlo |
| --- | --- |
| S2 | Zdroj plně podporuje atomické tvrzení v uvedené přesnosti |
| S1 | Podporuje jen část nebo užší tvrzení |
| S0 | Tvrzení neobsahuje nebo mu odporuje |
| NA | Obsah se nepodařilo přečíst; rozhodnutí má zdrojovou evidenci |
| FAB | Neexistence zdroje je doložená podle rubriky |

Úplná pravidla a kotvy všech ratingů i správnosti 0/1/2 jsou v
`annotation/rubric.md` a `annotation/calibration.md`. Skóre správnosti 2
vyžaduje správné RF a splněné RC; vynechání OF se netrestá. Segmentace
zahrnuje celou odpověď, bez limitu osmi tvrzení.

Uživatel 12. 10. 2026 určil **Reného Mrákavu a Jana Duba jako plánované
lidské hodnotitele**. To potvrzuje role, nikoli provedení hodnocení.
Jejich samostatné ratingy a kalibrace zatím nejsou k dispozici. Operátor
nesmí hodnotit vlastní běhy.

## Postup

1. Před G1 oba lidé samostatně projdou offline kotvy a skutečný pilot
   CIT-001/CIT-020. Kalibrace a případné změny rubriky se archivují.
2. Správce exportuje zaslepené listy v náhodném pořadí, seed 2026.
   Identita produktu/podmínka jsou skryté, formát je však může prozradit.
   Původní text, atribuce a URL se při normalizaci neopravují.
3. Hodnotitel 1 posoudí všechny dokončené odpovědi. Hodnotitel 2 posoudí
   předem náhodně vybraných **≥25 % v každém stratu fáze × produkt × podmínka**,
   se zaokrouhlením nahoru. Zadání vyžaduje nejméně 20 %.
4. Původní nezávislé listy zůstanou zachované před diskusí. Cohenova kappa
   S2/ostatní, surová shoda a n se počítají z nich, nikoli z konsenzu.
   Při konstantní kategorii je kappa nedefinovaná; segmentace se posuzuje zvlášť.
5. Každá neshoda a každá změna final oproti raw1 se zapíše do auditu.
   Nevyřešenou neshodu rozhodne nezávislý třetí člověk. Slabá shoda se
   neskrývá selektivním přehodnocením ani přepisem původních ratingů.
6. G3 vyžaduje úplnou matici, ratingy, source/RUN_DAY důkazy, audit a
   skutečný lidský podpis. Poté lze spustit `score.py --final`.

LLM návrh segmentace nebo ratingu musí být oddělený a označený jako
strojový. Svolení týmu není důkaz dvou nezávislých lidských kontrol.
Pokud se LLM skutečně použije jako hodnotitel, platí požadavky zadání na
identifikaci modelu, lidskou kalibraci, shodu a kontrolu hodnoticích zkreslení.
