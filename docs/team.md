# Harmonogram a role

Projekt trvá 10 týdnů a má tři brány, za které se nevracíme. Role jsou rozdělené tak, aby autor promptu neviděl testovací sadu.

## Brány

| Brána | Co se zmrazí | Kdy |
| --- | --- | --- |
| **G1** | Zmrazení protokolu | Před prvním během |
| **G2** | Zmrazení P3 | Před otevřením testovací sady |
| **G3** | Konec hodnocení | Před výpočtem výsledků |

:::{note}
Týdny jsou relativní; tým je přepíše na data semestru. Pevné je jen pořadí: G1 před prvním během, G2 před otevřením testovací sady, G3 před výpočtem výsledků.
:::

## Role

| Role | Odpovědnost | Omezení |
| --- | --- | --- |
| Koordinátor protokolu | Protokol, metadata běhů, dodržení 72hodinového okna | — |
| Správce dat | Testovací sada, hash, validace případů, zaslepení anotačního listu | Nesdílí testovací případy s autorem promptu |
| Autor promptu | P2, kandidáti P3, changelog | Neotevře testovací sadu před zmrazením P3 |
| Analytik | Skripty, bootstrap, grafy, reprodukovatelnost balíčku | — |
| Hodnotitelé (všichni) | Lidské hodnocení, dvojité hodnocení 25 % odpovědí | Nehodnotí běhy, které sami spouštěli |

Ve dvoučlenném týmu spojíme koordinátora se správcem dat a autora promptu s analytikem.
