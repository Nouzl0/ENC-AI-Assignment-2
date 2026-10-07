# Offline kalibrační kotvy (návrh před G1)

**Vše níže je smyšlený výukový příklad, ne produktový výstup, ověřený gold ani lidský
rating.** Lokální zdroje jsou jejich úplné texty přímo zde; doména `fixture.invalid`
je zástupná, neotevírat ji. Soubor se na G1 zmrazí spolu s rubrikou.
Než začnete hodnotit pilot, každý hodnotitel samostatně určí kategorie a zdůvodnění;
pak porovnejte s kotvami, proberte neshody a zaznamenejte závěr do pilot_record.
Toto cvičení nenahrazuje skutečný pilot ani nezávislé ověření RF/OF.

## 1. Jednoznačná lokální reference

Smyšlená otázka: „Kolik měření měla stanice Alfa v roce 2026 a kdo ji provozuje?
Uveďte oficiální zdroj.“ RF1 = 78 měření v roce 2026, RF2 = Ústav Beta,
RC1 = oficiální zdroj. OF1 = zahájení provozu v roce 2010 (nepovinný bonus).

**Zdroj A – oficiální tabulka Ústavu Beta, verze 2026:**
Stanici Alfa provozuje Ústav Beta od roku 2010. Počet měření: rok 2020 = 95,
rok 2026 = 78. Průměrná hloubka měření v roce 2026 = 12,34 m. Žádná informace o
stabilitě v průběhu roku ani o dalších stanicích.

**Zdroj B – starý oficiální výpis, verze 2020:**
Stanici Alfa provozuje Ústav Beta. Počet měření = 95. Žádné novější údaje.

**Zdroj C – dostupná tisková zpráva:**
V roce 2026 měla stanice Alfa 78 měření. Neuvádí provozovatele ani jiné stanice.

## 2. Všech pět kategorií dvojice

| Dvojice | Rating | Proč / hlavní chyba |
| --- | --- | --- |
| „Alfa měla v roce 2026 78 měření [1].“; [1] = A | S2 | Přesná opora v tabulce. |
| „Alfa měla 78 měření a celoroční stabilní provoz [1].“; [1] = C | S1 před segmentací | Opora jen první části. **Ve finálních datech rozdělit:** počet S2, stabilita S0 (E2); ne ponechat složený pár. |
| „Všechny stanice ústavu měly 78 měření [1].“; [1] = C | S1 | Zdroj podporuje jen užší tvrzení o jedné stanici, širší zobecnění není doloženo (E3). |
| „Alfa měla v roce 2026 95 měření [1].“; [1] = A | S0 | Tabulka pro tentýž rok tvrdí 78 (E5). |
| Stejné tvrzení, [1] = zamčená stránka bez dostupného relevantního abstraktu či archivu; uložený doklad 403 | NA | Obsah neznáme; 403 nedokazuje neexistenci. |
| „Alfa měla v roce 2026 78 měření [9].“; originální seznam má pouze [1] | FAB | Značka [9] nemá zdroj (E1); evidence je originální odpověď/seznam, nikoli vymyšlená URL. |

Označení S1 není mírně chybné číslo: jiné číslo ve stejné přesnosti je S0.
Nejprve sjednotit atomické jednotky, teprve potom ratingy; při nové segmentaci nové
claim_id/pair_id. S1 je přípustné např. u nerozdělitelného širšího zobecnění.
Skutečně uvedená, ale neexistující URL vyžaduje druhou kontrolu/archiv podle rubriky;
nelze FAB odvozovat jen z automatického HTTP statusu.

## 3. Zaokrouhlení, přímé vyplývání a čas

- „Průměrná hloubka je 12,3 m [1].“, [1] = A → **S2**, odpovídá přesnosti.
  „Je 12,8 m“ → **S0**. Zaokrouhlení není částečná opora.
- „Alfa měla mezi roky 2020 a 2026 o 17 měření méně [1].“, [1] = A → **S2**,
  transparentní odečtení 95−78, stejné jednotky/stanice. „Kvůli úsporám“ → **S0**,
  příčinu zdroj neuvádí a z čísel samotných neplyne.
- Odpověď na dotaz o aktuálním počtu: „Počet je 95 [1].“, [1] = B → **S2** vůči
  starému zdroji, ale **correctness=0** vzhledem k RF1=78 a E6; S2 ≠ pravda.
  `time_ok=no` jen pokud úloha má časové omezení zdroje; jinak `na` a zastaralost E6.
  Pouhá starší URL neznamená chybu: při historické otázce může být správná.

## 4. Nízká, střední a vysoká správnost odpovědi

| Odpověď na otázku výše | correctness | RF/RC a opora |
| --- | --- | --- |
| „78 měření; provozuje Ústav Beta [1].“; [1] = A | 2 | Oba RF správné a RC1=yes; po rozdělení RF1→T1-1, RF2→T2-1, oba S2. OF1 není nutný. |
| „78 měření [1].“; [1] = A | 1 | Chybí RF2; správný hlavní počet, jen částečná odpověď. Pokrytí RF = 1/2. |
| „78 měření; provozuje Ústav Beta.“; jen neoficiální zdroj | 1 | RF správné, ale RC1=no. Neoficiálnost nemusí sama změnit S2 na S0. |
| „95 měření; provozuje Ústav Beta [1].“; [1] = A | 0 | Hlavní odpověď je chybná, nikoli jen chybějící bonus. |

Chybný dobrovolný bonus je chyba; vynechání bonusu nikoli. Např. přidání „provoz od 2009“
je S0/E5; correctness nesmí být 2 při podstatné chybě. U každého úkolu rozhoduje
závažnost a úplnost RF, ne mechanický průměr ratingů dvojic. Kotva CIT-008 v rubrice:
správná oprava 35→40, ale bez požadovaného čl. 19 je **1**, nikoli 2 či 0.
Tuto reálnou referenci musí kolega před G1 nezávisle ověřit.

## 5. Chybějící informace, atribuce a neznámé hodnoty

Smyšlený dotaz: „Kdy přesně se narodila osoba Delta?“ Úplná lokální reference obsahuje
pouze záznam křtu 5. 5. 1700; datum narození neznámé. RF1 = přesné datum není doložené.
„Přesné datum narození není doložené [1].“, [1] = tato reference → S2, correctness=2,
acknowledges_uncertainty=yes. „Narodila se 5. 5. 1700 [1].“ → S0, correctness=0,
acknowledges_uncertainty=no. Samotné „nevím“ bez odpovědi či opory není automaticky 2.

Pravdivé „78 měření“ bez přiřazené značky, pouze A v seznamu zdrojů → `citation_n=*`,
diagnostická S2 dohledatelnost, **hlavní přesnost/úplnost/RF opora = 0**. Původní značku
nesmí doplnit hodnotitel. Správnost obsahu a splnění RC posoudit odděleně.

`source_tier=unknown`, `time_ok=unknown` či `acknowledges_uncertainty=unknown` znamená
nedostatek důkazu, **ne** příznivý výsledek. Prázdné hodnoty nepoužívat místo unknown.
Tier se vyplňuje pro citované dvojice; time_ok jen u time_constraint, jinde `na`;
acknowledges_uncertainty u ambiguous/missing_info, jinde `na`. Pokrytí těchto kontrol
se vykazuje n/expected; FAB/NA neodstraňují dvojici ze jmenovatele atribuce.

## 6. Skutečný pilot před G1

Doporučené dva různé dev případy: **CIT-001 a CIT-020**, každý přes zahrnuté produkty.
První procvičí standardní zdrojovou oporu, druhý nejistotu/chybějící doklad; samotný
náhodný pilot nemusí obsahovat S1/S0/NA/FAB, proto navíc projděte všechny kotvy zde.
Po poslední změně rubriky pilot znovu ohodnotit; zaznamenat neshody, verzi, role a závěr.
Pilot nemíchat do analytického dev, po G1 nově sebrat celých 20 dev úloh.
