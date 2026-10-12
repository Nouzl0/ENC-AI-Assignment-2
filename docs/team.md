# Harmonogram a role

Projekt trvá 10 týdnů a má tři brány, za které se nevracíme. Role jsou rozdělené tak, aby autor promptu neviděl testovací sadu.

## Brány

| Brána | Co se zmrazí | Kdy |
| --- | --- | --- |
| **G1** | Zmrazení protokolu | Před prvním analytickým během (pilot navíc je před G1) |
| **G2** | Zmrazení P3 | Před otevřením testovací sady |
| **G3** | Konec hodnocení | Před finálním scoringem (val scoring před G2) |

:::{note}
Týdny jsou relativní; tým je přepíše na data semestru. Pevné je jen pořadí: G1 před prvním analytickým během, G2 před otevřením testovací sady, G3 před výpočtem výsledků.
:::

## Role

| Role | Odpovědnost | Omezení |
| --- | --- | --- |
| Koordinátor protokolu | Protokol, metadata běhů, dodržení 72hodinového okna | — |
| Správce dat | Testovací sada, hash, validace případů, zaslepení anotačního listu | Nesdílí testovací případy s autorem promptu |
| Autor promptu | P2, kandidáti P3, changelog | Neotevře testovací sadu před zmrazením P3 |
| Analytik | Skripty, bootstrap, grafy, reprodukovatelnost balíčku | — |
| Hodnotitelé (všichni) | Lidské hodnocení, dvojité hodnocení 25 % odpovědí | Nehodnotí běhy, které sami spouštěli |

## Potvrzené přiřazení a sběr

Uživatel 12. 10. 2026 určil Reného Mrákavu a Jana Duba jako dva plánované
lidské hodnotitele a pověřil agenta skutečným sběrem v Chrome.
Operátor nového pilotu je `codex-ui-2026-10-12`; jeho výstupy budou
hodnotit lidé. Přiřazení rolí není doklad provedené kalibrace nebo ratingů.
Správce nového skrytého testu a nezávislý ověřovatel referencí dosud
nejsou jmenovitě potvrzeni; musí se lišit od autora promptu.

Původní pilot jiného operátora se uchovává odděleně. Nový sběr používá
existující přihlášené účty; jejich skutečné úrovně se zapisují do metadat
(u Gemini byl pozorován Plus). Původní plán bezplatné úrovně proto nelze
prohlásit za ověřený. Definitivní srovnávací konfigurace patří před G1.
