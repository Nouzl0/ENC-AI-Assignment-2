# Metriky

Hlavní metrikou je citační přesnost na úrovni tvrzení. Vedlejší metriky jsou úplnost citací a správnost odpovědi. Všechny definice a váhy platí od zmrazení protokolu, před prvním testovacím během.

## Jednotky hodnocení

**Tvrzení**
: Atomický faktický výrok: číslo, datum, jméno, definice nebo vztah. Složené věty dělíme a významové duplicity konzervativně sjednocujeme. Hodnotitel kontroluje všechna faktická tvrzení celé odpovědi, včetně ODPOVĚĎ, nikoli jen TVRZENÍ. Limit osmi tvrzení neplatí. Úryvky P3 jsou důkaz, nikoli další tvrzení.

**Dvojice tvrzení–citace**
: Tvrzení a zdroj, který k němu systém skutečně připojil. Nepřiřazený seznam zdrojů (`*`) je pouze diagnostika `unlinked_support`; nepočítá se do hlavní přesnosti, úplnosti, RF pokrytí ani hlavní kappy. Hodnotitel atribuci nedoplňuje.

**Hodnocení dvojice**
: **S2** plně podpořeno, **S1** částečně podpořeno, **S0** nepodpořeno nebo v rozporu, **NA** zdroj nedostupný, **FAB** zdroj neexistuje.

## Hlavní metrika – citační přesnost

Pro odpověď $a$ počítáme podíl **explicitních** S2 dvojic ze všech explicitních dvojic včetně NA/FAB. Agregace je průměr přes úlohy prvního běhu se stejnými vahami. Opakování P2 se vykazují zvlášť a nezvyšují počet nezávislých úloh.

$$
\text{Přesnost}_a = \frac{\lvert \text{explicitní S2 dvojice odpovědi } a \rvert}{\lvert \text{všechny explicitní dvojice odpovědi } a \rvert}
$$ (eq-precision)

NA a FAB zůstávají ve jmenovateli. Bez explicitních citací a při konečném provozním selhání je přesnost nula. S2 měří podporu zdrojem, nikoli pravdivost tvrzení.

## Vedlejší metriky

**Úplnost citací** měří, kolik tvrzení je podloženo alespoň jednou citací S2. Tvrzení bez citace má hodnotu 0.

$$
\text{Úplnost}_a = \frac{\lvert \text{tvrzení odpovědi } a \text{ s alespoň jednou citací S2} \rvert}{\lvert \text{všechna hodnocená tvrzení odpovědi } a \rvert}
$$ (eq-completeness)

**Správnost odpovědi** je podíl odpovědí se skóre 2 na škále 0–2. Skóre 2 vyžaduje všechny RF a splněné RC; vynechání OF se netrestá, dobrovolně uvedená chybná fakta se hodnotí. U chybných předpokladů a chybějících informací platí pravidla rubriky.

## Diagnostické metriky

| Diagnostická metrika | Definice | Proč ji sledujeme |
| --- | --- | --- |
| Míra neexistujících zdrojů | Podíl citací s hodnocením FAB | Halucinace citací |
| Míra nedostupných zdrojů | Podíl citací s hodnocením NA | Kontrola alternativy A2 |
| Kvalita zdrojů | Podíl citací na primární nebo oficiální zdroj | Upřednostnění důvěryhodných zdrojů |
| Dodržení časového omezení | Podíl citací, které splňují limit stáří | Případy s časovým omezením |
| Vhodné přiznání nejistoty | Podíl odpovědí na chybějící nebo nejednoznačné dotazy, které nejistotu přiznají | Práce s nejistotou |
| Tvrzení a citace na odpověď | Průměrný počet | Kontrola alternativy A1 |
| Nepřiřazené citace | Podíl citací uvedených jen souhrnně | Granularita citování |

## Provozní metriky

Medián a p90 první i celkové latence, první/konečná úspěšnost, retry, kola a viditelná volání nástrojů. Mezní poplatky, předplatné a lidská práce se vykazují odděleně. Neznámé tokeny, kredity a ceny nejsou nula. Čas anotace `check_minutes` není uživatelský čas oprav.

Explorační `annotation_effort_index` má předem stanovené váhy. $L_\text{norm}$ a $T_\text{norm}$ jsou mediány latence a anotace dělené maximem příslušných mediánů mezi produkty v dané sadě a podmínce. Chybějící čas nezíská nulovou penalizaci. Nejde o obecný užitek; Pareto-fronta používá přesnost a latenci.

$$
\text{Index anotačního úsilí} = \text{Přesnost} - 0{,}1 \cdot L_{\text{norm}} - 0{,}1 \cdot T_{\text{norm}}
$$ (eq-utility)

Bootstrap používá celé `task_id`, 10 000 převzorkování a seed 2026.
Konstantní interval [p,p] není nulová populační nejistota; vykazují se
diagnostické příznaky a n. Binární podíly mají Wilsonovy intervaly.
U source/time/ack se hlásí `checked/expected`; unknown není pozitivní
kontrola. H2 doplní podíl explicitně citovaných odpovědí a jejich
podmíněná přesnost s n, aby se odlišila změna formátu atribuce.
