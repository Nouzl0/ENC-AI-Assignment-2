# Metriky

Hlavní metrikou je citační přesnost na úrovni tvrzení. Vedlejší metriky jsou úplnost citací a správnost odpovědi. Všechny definice a váhy platí od zmrazení protokolu, před prvním testovacím během.

## Jednotky hodnocení

**Tvrzení**
: Atomický faktický výrok: číslo, datum, jméno, definice nebo vztah. Složené věty dělíme. Skript navrhne dělení (u P2 a P3 ze seznamu TVRZENÍ, u P1 po větách), hodnotitel ho pak u všech podmínek upraví podle stejných pravidel v rubrice. Jinak by rozdíl P1 a P2 měřil i způsob dělení. Hodnotíme nejvýš 8 tvrzení na odpověď v pořadí výskytu.

**Dvojice tvrzení–citace**
: Tvrzení a zdroj, který k němu systém připojil. Uvede-li systém zdroje jen souhrnně na konci, spárujeme tvrzení s nejlépe odpovídajícím uvedeným zdrojem a označíme citaci jako nepřiřazenou.

**Hodnocení dvojice**
: **S2** plně podpořeno, **S1** částečně podpořeno, **S0** nepodpořeno nebo v rozporu, **NA** zdroj nedostupný, **FAB** zdroj neexistuje.

## Hlavní metrika – citační přesnost

Pro každou odpověď $a$ počítáme podíl dvojic hodnocených S2, pro systém a podmínku pak průměr přes případy. Každý případ má stejnou váhu a opakované běhy nejprve zprůměrujeme v rámci případu.

$$
\text{Přesnost}_a = \frac{\lvert \text{dvojice odpovědi } a \text{ s hodnocením S2} \rvert}{\lvert \text{všechny dvojice odpovědi } a \rvert}
$$ (eq-precision)

NA a FAB se počítají jako selhání, protože čtenář si tvrzení nemůže ověřit. Odpověď bez jediné citace má přesnost 0, protože citace byly součástí zadání. V citlivostní analýze přesnost přepočítáme bez NA.

## Vedlejší metriky

**Úplnost citací** měří, kolik tvrzení je podloženo alespoň jednou citací S2. Tvrzení bez citace má hodnotu 0.

$$
\text{Úplnost}_a = \frac{\lvert \text{tvrzení odpovědi } a \text{ s alespoň jednou citací S2} \rvert}{\lvert \text{všechna hodnocená tvrzení odpovědi } a \rvert}
$$ (eq-completeness)

**Správnost odpovědi** je podíl odpovědí se skóre 2 na škále 0–2 proti referenci a `key_facts`. U nepravdivého předpokladu musí systém předpoklad opravit. U chybějící informace musí přiznat, že přesná odpověď neexistuje.

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

Medián a 90. percentil latence (od odeslání po dokončení odpovědi, měřeno stopkami), počet kol, počet zobrazených vyhledávání, odhad nákladů (cena plánu dělená počtem dotazů), míra opakování a čas lidské kontroly na odpověď.

Užitek má váhy stanovené předem. $L_\text{norm}$ je medián latence systému dělený nejvyšším mediánem, $T_\text{norm}$ je medián času lidské kontroly dělený nejvyšším mediánem. Vedle užitku uvedeme i Pareto-frontu přesnosti proti latenci.

$$
\text{Užitek} = \text{Přesnost} - 0{,}1 \cdot L_{\text{norm}} - 0{,}1 \cdot T_{\text{norm}}
$$ (eq-utility)
