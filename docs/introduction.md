# Úvod a výzkumná otázka

Projekt plánuje porovnání pěti produktů s webovým vyhledáváním ve směru B:
správnost a úplnost citací na faktických CZ/EN rešeršních úlohách z pěti
oblastí. Měřením je podpora tvrzení skutečně přiřazeným zdrojem, nikoli
čistá schopnost samotného modelu. Existuje 20 dev + 10 val návrhů;
nový nezávislý holdout ≥10 a finální experiment zatím nejsou dokončené.

## Výzkumná otázka

Jak často citovaný zdroj skutečně podporuje tvrzení u ChatGPT, Gemini,
Claude, Perplexity a Groku na definovaném mixu ≥40 úloh a jak tuto
atribuci mění společný P1, strukturovaný P2 a obecně optimalizovaný P3?
Praktickým významem je ověřitelnost citací při rešerši. Závěry se omezí
na měřené produkty, účty, režimy, úlohy, jazyky a období.

Hlavní metrika je průměr explicitní citační přesnosti po odpovědích
prvního běhu, se stejnými vahami úloh. Vedlejší metriky jsou úplnost
citací celé odpovědi a správnost proti RF/RC. S2 neznamená pravdivost.

## Předem definované hypotézy

**H1:** Bodový odhad přesnosti předem zvoleného focus produktu
(výchozí Perplexity) v P2 minus průměr ostatních zahrnutých produktů
je ≥0,10 a dolní mez 95% párového bootstrapového CI je >0.
Navrhovaný mechanismus je hypoteticky lepší vazba retrievalu a citovaných
pasáží; není zde vydáván za ověřenou vlastnost produktu.

**H2:** Bodový odhad P2 minus P1, průměrovaný přes zahrnuté produkty,
je ≥0,05, dolní mez CI je >0 a kladný odhad má ≥4/5 produktů
(≥3/4 při předem zdůvodněném čtyřproduktovém návrhu).
Hypotetickým mechanismem jsou instrukce přiřadit důkaz a přiznat nejistotu.

Obě hypotézy se vyhodnotí **výhradně na novém testu po G3**. Dev/val
nejsou potvrzující test a nepřidávají se do jeho n. Uvedená pravidla
podpory praktického odhadu nejsou důkazem populačního efektu ≥margin.
Silnější diagnostika `ci_above_margin` se uvede odděleně; společná
chybovost H1/H2 není garantována. P3 a další žebříčky jsou explorační.

## Alternativní vysvětlení

| Alternativa | Kontrola v reportu |
| --- | --- |
| A1: méně tvrzení místo lepší atribuce | Úplnost, RF pokrytí, počet tvrzení/citací a deskriptivní Spearman |
| A2: zdrojová dostupnost, jazyk a doména | NA a členění podle jazyka/domény; CZ/EN nejsou párované překlady |
| A3: změna formátu atribuce při P2 | Podíl explicitně citovaných odpovědí a podmíněná přesnost s n |

Korelace ani lepší P3 odpověď samy neprokazují příčinu. Účelový malý
vzorek, rozdílné účty a skryté nastavení produktů omezují interpretaci.
Přesná metodika a pravidla zmrazení jsou v `PROTOCOL.md`.
