(plan)=
# Plán, role a další kroky

Plný experiment má **500 analytických odpovědí** (5 produktů × 3 prompty × úlohy; P2 na testu 3×) plus pilot navíc.
Pilot je hotový; plný experiment přesahoval dostupný čas a rozpočet. Níže je postup, kterým jej lze bez změny návrhu provést.

## Brány

Tři brány dávají studii pevné pořadí a zabraňují ladění na testu.

| Brána | Co se zmrazí | Kdy |
| --- | --- | --- |
| **G1** | Protokol, data, rubrika, P1/P2 a kód | před prvním analytickým během |
| **G2** | Vítězný prompt P3_final | před otevřením testovací sady |
| **G3** | Konec hodnocení a audit neshod | před finálním skórováním |

## Role

| Role | Odpovědnost | Omezení |
| --- | --- | --- |
| Koordinátor / analytik | Protokol, metadata, skripty, bootstrap, reprodukovatelný balíček | – |
| Správce dat a ověřovatel referencí | Soukromý test, hash, zaslepení listů, ověření RF/OF | Nesdílí test s autorem promptu |
| Autor promptu | P2, kandidáti P3, changelog | Neotevře test před zmrazením P3 |
| Hodnotitelé | Nezávislé ratingy, dvojité hodnocení ≥ 25 % | Nehodnotí vlastní běhy |

Plánovaní hodnotitelé jsou René Mrákava a Jan Dub (správce soukromého testu: René, autor promptu: Jan). Nikolas Nosál
zajišťuje analýzu, dokumentaci a sběr. Přiřazení rolí není provedené hodnocení ani podpis brány.
Pilotní odpovědi sbíral AI operátor v Chromu; jeho výstupy hodnotí lidé.

## Rozšíření na plný experiment

1. Lidská kontrola referencí (RF/OF s locatorem, datem a snapshotem) a schválení soukromého testu.
2. Nezávislá kalibrace obou hodnotitelů na pilotních odpovědích a vyplnění připravených listů.
3. Sladění konfigurace účtů a podpis **G1**; sběr dev/val, volba P3, **G2**, test, **G3**.
4. `score.py --final`: přesnost, úplnost, správnost, intervaly, H1/H2, analýza chyb.

## Selhání a opakování

| Typ selhání | Příklad | Opakování | Jak se počítá |
| --- | --- | --- | --- |
| Výstup modelu | Odmítnutí, bez citací, halucinace | Ne | Hodnotí se (bez citací = přesnost 0) |
| Neplatný formát | P2 bez sekce ZDROJE | Ne | Hodnotí se, zapíše se validita formátu |
| Chyba nástroje / limit / výpadek | „Vyhledávání se nezdařilo", denní limit | 1× | První pokus i výsledek zvlášť |
| Chyba studenta | Špatný prompt, zapnutý hloubkový výzkum | Svázaná náhrada | Původní řádek zůstává |

Každé selhání a ruční zásah je v metadatech (`failure_type`, `retries`, `manual_intervention`); neúspěšné pokusy se nemažou.
Úplné příkazy s manifesty a soukromými cestami jsou v `HANDOFF.md`.


## Aktualizace 13. 10. 2026

Doplňkový sběr nyní dokládá 40 různých měřených úloh a 84 věcných odpovědí. Pět nových úloh má Gemini P1/P2/P3A. Dostupný AI audit a intervaly jsou v kapitole [](#results), metoda v [](#supplement). Původní úplná matice a skutečné lidské hodnocení nejsou dokončené; starší plánované počty v této kapitole nejsou aktuální počet uložených odpovědí.
