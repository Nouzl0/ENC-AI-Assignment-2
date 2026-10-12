# Úvod a výzkumná otázka

## Shrnutí

Projekt měří, jak často citace AI asistentů s webovým vyhledáváním skutečně podporují tvrzení, ke kterým jsou připojeny. Volíme **Směr B: Výzkum podložený zdroji** a jednu schopnost: správnost a úplnost citací. Porovnáváme produkty jako celky (model + vyhledávání + rozhraní), nikoli samotné jazykové modely.

## Výzkumná otázka

:::{important}
Jak často citovaný zdroj skutečně podporuje tvrzení, ke kterému ho asistent připojil (**citační přesnost**), u pěti AI asistentů s webovým vyhledáváním (ChatGPT, Gemini, Claude, Perplexity, Grok) na 40 faktických rešeršních dotazech v češtině a angličtině z pěti oblastí a o kolik ji mění strukturovaný a optimalizovaný prompt?
:::

| Prvek otázky | Naše volba |
| --- | --- |
| Hodnocená schopnost | Správnost citací na úrovni tvrzení (podporuje citovaný zdroj tvrzení?) a úplnost citací |
| Populace úloh | 40 faktických rešeršních dotazů, CZ/EN, 5 oblastí, 45 % okrajových případů |
| Systémy a podmínky | 5 asistentů × 3 podmínky promptu (P1 společný, P2 strukturovaný, P3 optimalizovaný) |
| Měřitelný výsledek | Citační přesnost = podíl dvojic tvrzení–citace hodnocených jako „plně podpořeno" |
| Význam | Uživatelé citace často neotevřou a berou je jako důkaz. Nepodporující citace tak vytváří falešnou důvěru. Výsledek ukáže, kterému produktu a jakému zadání lze při rešerši víc věřit. |

Neptáme se, který asistent je obecně „nejlepší". Závěry platí jen pro tuto sadu dotazů, tento protokol a období běhů.

## Cíle

1. Změřit citační přesnost a úplnost citací pěti produktů na stejné sadě dotazů.
2. Zjistit, zda strukturovaný (P2) a optimalizovaný (P3) prompt citační přesnost zvyšuje, a zda je zlepšení přenositelné mezi systémy.
3. Popsat, jaké typy chyb citací se opakují (viz [](#error-analysis)).

## Hypotézy

Předem registrujeme jednu hlavní hypotézu o systémech, jednu vedlejší o promptech a dvě alternativní vysvětlení. Všechny se vyhodnocují na testovací sadě držené stranou.

:::{admonition} H1 (hlavní)
:class: note
Za podmínek jednotného protokolu webového výzkumu (nový chat bez paměti, výchozí vyhledávací režim, strukturovaný prompt P2, stejný dotaz tentýž den) dosáhne **Perplexity alespoň o 10 procentních bodů vyšší citační přesnosti** než průměr čtyř obecných konverzačních asistentů (ChatGPT, Gemini, Claude, Grok).

Důvodem je, že produkt je postaven kolem vyhledávání a váže věty na konkrétní vyhledané úryvky. Hypotézu budeme považovat za podpořenou pouze tehdy, pokud se rozdíl projeví také na testovací sadě držené stranou a 95% bootstrapový interval rozdílu nebude obsahovat nulu.
:::

:::{admonition} H2 (vedlejší)
:class: note
Strukturovaný prompt P2 **zvýší citační přesnost oproti P1** v průměru napříč systémy alespoň o 5 procentních bodů.

Důvodem je, že vyžaduje citaci u každého tvrzení a zakazuje citovat neotevřené zdroje. Podpořena je pouze tehdy, pokud se zlepšení projeví na testovací sadě alespoň u 4 z 5 systémů (3 ze 4 v úsporné variantě) a 95% bootstrapový interval průměrného zlepšení nebude obsahovat nulu.
:::

### Alternativní vysvětlení

| Alternativní vysvětlení | Jak by vypadalo v datech | Jak ho kontrolujeme |
| --- | --- | --- |
| **A1 – opatrnost místo kvality:** systém má vyšší přesnost jen proto, že dělá méně a obecnějších tvrzení nebo cituje méně | Vysoká přesnost, ale nízká úplnost citací a málo tvrzení na odpověď | Vždy vykazujeme přesnost spolu s úplností, počtem tvrzení a pokrytím klíčových faktů (kolik faktů z `key_facts` odpověď uvádí a dokládá citací S2) |
| **A2 – dostupnost zdrojů:** rozdíl způsobí paywally, blokování crawlerů nebo slabší index českých stránek, ne přiřazování citací | Rozdíly se soustředí v českých dotazech a v kategorii „nedostupný zdroj" | Nedostupné zdroje evidujeme zvlášť (hodnocení NA) a výsledky rozdělujeme na CZ a EN |

```{raw-typst}
#set page(margin: auto)
```
