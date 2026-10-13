(introduction)=
# Výzkumná otázka a hypotézy

AI asistenti s webovým vyhledáváním (ChatGPT, Gemini, Claude, Perplexity, Grok) připojují k odpovědím
odkazy, které působí jako důkaz. U rešerše je ale důležité, zda zdroj skutečně podporuje právě to tvrzení,
u kterého stojí. Zadání nás vede k porovnání **produktů jako celků** (model + vyhledávání + rozhraní),
ne izolovaných modelů; schopnost modelu bez vyhledávání neměříme.

:::{important} Výzkumná otázka
Jak často citovaný zdroj skutečně podporuje tvrzení u pěti produktů na 40 faktických
rešeršních úlohách v češtině a angličtině a jak tuto podporu mění strukturovaný prompt (P2)
a prompt optimalizovaný na vývojových datech (P3) oproti společné výchozí podmínce (P1)?
:::

**Praktický význam:** uživatel se na odkaz spoléhá a ověřuje jej jen výjimečně; zajímá nás, kdy je to oprávněné.

## Hlavní metrika

**Citační přesnost** = podíl explicitně citovaných dvojic tvrzení–zdroj, které zdroj plně podporuje (S2).
Je to průměr přes odpovědi, každá úloha má stejnou váhu. Vedlejší metriky jsou úplnost citací a správnost
odpovědi; S2 neznamená, že je tvrzení pravdivé. Definice jsou v [](#evaluation).

## Hypotézy

Obě hypotézy se vyhodnotí **výhradně na držené testovací sadě** po zmrazení protokolu a promptu.

| | Tvrzení | Rozhodovací pravidlo |
| --- | --- | --- |
| **H1** | Předem zvolený produkt (výchozí Perplexity), který je postaven na vyhledávání, má v P2 vyšší přesnost než průměr ostatních. | Rozdíl ≥ 0,10 a dolní mez 95% párového bootstrapového CI > 0 |
| **H2** | Strukturovaný prompt P2 zvyšuje přesnost oproti P1 napříč produkty. | Průměrný rozdíl ≥ 0,05, dolní mez CI > 0 a kladný odhad u ≥ 4 z 5 produktů |

Mechanismy (lepší vazba retrievalu na pasáže u H1; pokyn přiřadit důkaz u H2) jsou hypotézy. P3 a žebříčky jsou explorační.

**H1 ve znění zadání:** Za podmínek P2 a stejných úloh dosáhne Perplexity vyšší citační přesnosti než průměr ostatních produktů o ≥ 0,10, protože je vyhledávání jeho jádrem. Hypotézu budeme považovat za podpořenou, jen pokud se výsledek projeví na držené testovací sadě. **H2:** Za týchž podmínek zvýší P2 přesnost oproti P1 o ≥ 0,05, protože žádá přiřazení důkazu a přiznání nejistoty; podpora vyžaduje shodu na testovací sadě.

**Co by hypotézy vyvrátilo:** rozdíl H1 pod 0,10 nebo interval zahrnující nulu; H2 s kladným efektem jen u 1–2 produktů
nebo se zhoršením jiných. Prompt, který jednomu produktu pomůže a ostatním uškodí, hlásíme jako platný výsledek.

## Alternativní vysvětlení

| Alternativa | Jak ji kontrolujeme |
| --- | --- |
| A1: Produkt cituje méně tvrzení, proto „přesněji" | Úplnost citací, počet tvrzení a citací na odpověď |
| A2: Rozdíl dělá dostupnost zdrojů, jazyk nebo obor | Podíl NA, členění podle jazyka a oboru (CZ/EN nejsou párované překlady) |
| A3: P2 jen změní formát citování | Podíl explicitně citovaných odpovědí a přesnost podmíněná jejich výskytem |
