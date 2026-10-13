(evaluation)=
# Hodnocení: metriky, lidé a nejistota

Citace metod jsou v [](#references).

```{figure} figures/citation-flow.svg
:label: fig-flow
:alt: Postup hodnocení citací od odpovědi po přesnost
:width: 100%

Postup hodnocení. Citace se nikdy neopravují ani nedoplňují.
```

## Jednotky a hodnocení

**Tvrzení** je atomický faktický výrok (číslo, datum, jméno, definice, vztah); hodnotí se celá odpověď,
ne jen sekce TVRZENÍ. **Dvojice** je tvrzení a zdroj, který k němu produkt skutečně připojil; souhrnný
seznam zdrojů bez vazby je jen diagnostika. Každá dvojice dostane jedno hodnocení:

| Rating | Pravidlo |
| --- | --- |
| S2 | Zdroj plně podporuje tvrzení v uvedené přesnosti |
| S1 | Podporuje jen část nebo užší tvrzení |
| S0 | Tvrzení neobsahuje nebo mu odporuje |
| NA | Obsah zdroje se nepodařilo přečíst (např. paywall); nepočítá se jako nepravda |
| FAB | Zdroj neexistuje (doložená halucinace) |

Úplná pravidla a kalibrační kotvy jsou v `annotation/rubric.md` a `annotation/calibration.md`.

## Metriky

**Citační přesnost** (hlavní metrika) – NA a FAB zůstávají ve jmenovateli; bez explicitních citací nebo při konečném selhání je přesnost nula.

$$
\text{Přesnost}_a = \frac{\lvert \text{explicitní S2 dvojice odpovědi } a \rvert}{\lvert \text{všechny explicitní dvojice odpovědi } a \rvert}
$$ (eq-precision)

**Úplnost citací** – podíl tvrzení s alespoň jednou citací S2 (tvrzení bez citace = 0).

$$
\text{Úplnost}_a = \frac{\lvert \text{tvrzení s alespoň jednou citací S2} \rvert}{\lvert \text{všechna hodnocená tvrzení} \rvert}
$$ (eq-completeness)

**Správnost odpovědi** – skóre 0–2 proti referenci; 2 vyžaduje všechna povinná fakta (RF) a splněné požadavky (RC).
Vynechání nepovinných faktů se netrestá.

**Diagnostika:** podíl FAB a NA, kvalita zdrojů (primární/oficiální), dodržení časového omezení, přiznání nejistoty,
počet tvrzení a citací na odpověď. **Provoz:** první a konečná úspěšnost, latence, opakování, náklady;
neznámé hodnoty (tokeny, kredity) se uvádějí jako *unknown*, nikdy jako nula.

**Automatizované kontroly:** parser odpovědí a citací zachovává původní text a URL, validátor schématu a stratifikace (`validate_cases.py`) hlídá duplicity a překryv sad, HTTP kontrola URL je jen diagnostika. Automatika nikdy nepředvyplňuje ratingy.

**Přenositelnost promptu** (P2 a P3 oproti P1): průměrné zlepšení, zlepšení po produktech a na testu, délka promptu, počet úprav pro konkrétní produkt (cíl 0) a dodatečná kola či volání nástrojů.

**Kvalita vs. úsilí:** předem stanovený explorační index `přesnost − 0,1·L_norm − 0,1·T_norm` (normalizovaná latence a čas anotace); při chybějících časech místo něj uvádíme Pareto-frontu přesnosti a latence.

(human-rating)=
## Dva nezávislí hodnotitelé

Hodnotí **René Mrákava a Jan Dub**; operátor, který odpovědi sbíral, je nehodnotí. Oba dostanou stejné zaslepené
listy v náhodném pořadí (seed 2026) bez automatických nápověd, produkt a podmínka jsou skryté. První hodnotitel
posoudí všechny odpovědi, druhý předem náhodně vybraných **≥ 25 % v každém stratu** (fáze × produkt × podmínka;
zadání vyžaduje nejméně 20 %). Původní ratingy zůstanou zachované před diskusí; Cohenova kappa (Cohen, 1960; S2 vs. ostatní)
a surová shoda se počítají z nich, ne z konsenzu. Neshody se auditují a nevyřešené rozhoduje třetí člověk.
Automatické kontroly (HTTP dostupnost, shoda entit) slouží jen správci. LLM jako jediný hodnotitel
se nepoužívá; AI pomoc je oddělená a označená.

## Nejistota

- **Párový bootstrap po úlohách** (Efron, 1979; 10 000 převzorkování, seed 2026) pro H1 a H2 – všechny produkty řeší stejné úlohy, takže párování odstraní rozptyl obtížnosti.
- **Wilsonův 95% interval** (Wilson, 1927) pro binární podíly.
- **Variabilita běhů:** P2 se na testu opakuje 3×; hlásíme směrodatnou odchylku a změny správnosti mezi běhy.
- S 10 testovacími úlohami budou intervaly široké; rozdíly pod zhruba 15 procentních bodů pravděpodobně nerozlišíme. Uvádíme proto velikost efektu a interval, ne jen „signifikanci".

## Selhání a opakování

Neúspěšný běh je součástí dat. Opakování je povoleno jen u selhání mimo model (chyba nástroje, limit požadavků,
výpadek produktu, časový limit) a vždy se hlásí **úspěšnost na první pokus i po opakování**. Výstup modelu
(odmítnutí, chybějící citace, halucinace) se neopakuje a hodnotí se normálně. První pokusy se nemažou ani po úspěšném opakování.
