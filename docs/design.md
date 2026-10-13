(design)=
# Návrh: produkty, data a prompty

```{figure} figures/design.svg
:label: fig-design
:alt: Návrh experimentu: 5 produktů, 3 prompty, 40 úloh
:width: 95%

Návrh studie. Produkt je celek model + vyhledávání + rozhraní.
```

## Porovnávané produkty

Používáme **běžné webové rozhraní** každého produktu s jeho vlastním vyhledáváním; paritu nástrojů
zajistit nelze (každý produkt má jiný index a zobrazení citací), proto jsou závěry formulované
o produktech. Claude Code je nástroj pro programování, a proto jej nezahrnujeme (mimo směr B).
Pilot probíhal v prohlížeči Chrome na existujících účtech.

| Produkt | Vyhledávání | Režim bez paměti | Vyloučený režim |
| --- | --- | --- | --- |
| ChatGPT | Vynucený nástroj Search | Temporary chat, bez personalizace | Deep research |
| Gemini | Automaticky | Temporary chat | Deep Research |
| Claude | Web search | Incognito chat | Research |
| Perplexity | Vždy, režim Search | Incognito | Research, Labs |
| Grok | Automaticky (web a X) | Private Chat | DeepSearch |

**Pravidla běhu:** každý dotaz v novém chatu bez paměti a vlastních instrukcí; jedno kolo
komunikace (při doptání odpovíme „Pokračujte podle svého nejlepšího úsudku."); uložíme text,
všechny URL citací, snímek a metadata (viditelný model, tarif, čas, selhání, opakování). Pořadí produktů
losuje skript (seed 2026); jeden případ projde všemi produkty do 24 h, celá sada do 72 h.
**Zvolený přístup k nástrojům:** *podle schopností produktu*; výsledky jsou výslovně porovnáním produktů, ne čisté měření modelu.

| Zdroj výkonnosti | Oddělíme? | Jak |
| --- | --- | --- |
| Vliv promptu | Ano | Stejný produkt v P1, P2 a P3 |
| Vliv nástrojů | Částečně | Evidujeme, zda proběhlo vyhledávání a kolik zdrojů se zobrazilo |
| Schopnost modelu | Ne | Ve spotřebitelském rozhraní nelze model odpojit od vyhledávání |
| Vliv produktu | Ne | Rozhraní, bezpečnostní vrstva a vyhledávač tvoří celek |

**Metadata každého běhu** (`runs/`): produkt a viditelný model, rozhraní a tarif, datum a čas, podmínka a verze promptu (SHA-256),
systémová instrukce („výchozí, neviditelná"), oprávnění nástrojů, kontextové soubory (žádné), teplota a délka výstupu („výchozí, nenastavitelné"),
počet kol a viditelných volání nástrojů, latence, náklady/tokeny (nebo *unknown*), opakování, typ selhání a ruční zásahy.

## Testovací sada

Návrh obsahuje **40 různých úloh**: 20 vývojových, 10 validačních a 10 soukromých testovacích.
Dev a val jsou veřejné v `data/`. Testovací sada je **uložená mimo Git** a autor promptu ji před zmrazením
P3 neotevře; po jejím zveřejnění nelze použít jako skrytý test. Validátor ověřuje schéma a stratifikaci,
nikoli pravdivost referencí.

Tato část popisuje plán plného experimentu. Aktuálních SUP-H001–010 už je
zveřejněných a všechny mají typ fact/medium; nenaplňují původní testové kvóty
ani utajení. Pro potvrzující experiment je třeba jiná nezávislá skrytá sada.


:::{table} Složení testovací sady
:label: tbl-dataset
:align: center

| Vlastnost | Vývoj: skutečnost (20) | Validace: skutečnost (10) | Test: soukromý návrh (10) |
| --- | --- | --- | --- |
| Oblasti: věda a zdraví / právo / IT / ekonomika / historie a kultura | 4 / 4 / 4 / 4 / 4 | 2 / 2 / 2 / 2 / 2 | 2 / 2 / 2 / 2 / 2 |
| Jazyk: CZ / EN / CZ+EN | 10 / 9 / 1 | 5 / 4 / 1 | 4 / 5 / 1 |
| Typ: fakt / primární zdroj / syntéza | 10 / 6 / 4 | 3 / 4 / 3 | 5 / 3 / 2 |
| Obtížnost: snadná / střední / těžká | 3 / 11 / 6 | 4 / 4 / 2 | 1 / 6 / 3 |
| Okrajové případy | 9 (45 %) | 4 (40 %) | 4 (40 %) |
:::


### Okrajové případy

Okrajové případy jsou záměrně zastoupeny ze 43 % (13 ze 30 veřejných úloh), aby měřily hranice chování
a ne jen snadné otázky.

- **Nepravdivý předpoklad** (2×): „Proč musí mít kandidát do Senátu ČR alespoň 35 let?" → Opravit na 40 let, čl. 19 odst. 2 Ústavy
- **Protichůdné zdroje** (2×): Nadmořská výška Sněžky (1602 vs. 1603 m) → Uvést obě hodnoty a důvod rozdílu
- **Chybějící informace** (3×): Přesné datum narození Shakespeara → RF: přiznat, že přesné datum není známo; křest je pouze OF
- **Nejednoznačné zadání** (2×): „Kdy vznikla Česká republika?" → RF: samostatná ČR 1. 1. 1993; 1969/1990 jsou pouze OF
- **Časové omezení** (1×): Aktuální sazba ECB, jen zdroje z posledních 30 dní → Uvést hodnotu, datum účinnosti a datum zdroje
- **Nedávná změna faktu** (1×): Podpora Windows 10 a program ESU → Ověřit stav pro daný produkt a datum
- **Kombinace češtiny a angličtiny** (2×): Co znamená SBOM a který exekutivní příkaz ho prosadil → Odpovědět česky, termíny ponechat

Každý případ má všech 13 polí schématu ze zadání (`task_id` … `source_or_provenance`) a původ dat. Reference mají tři části: **RF** (povinná fakta), **OF** (nepovinná fakta, jejich vynechání se netrestá) a
**RC** (požadavky na formát a zdroje). Dynamické případy mají samostatnou evidenci pro každý UTC den běhu.
Všechny dotazy jsou syntetické, jen o veřejných faktech, bez osobních údajů a autorských textů.
Stav kontroly referencí je v příloze [](#source-audit).

## Prompty

Všechny tři podmínky dostanou stejnou otázku; liší se jen obalem. Anglické úlohy používají překlad
stejné šablony (všechny verze jsou v `prompts/`). Úpravy pro konkrétní produkt jsou zakázány.

**P1 – společná výchozí podmínka:**

```text
Vyřešte níže uvedenou úlohu. Odpovězte pouze v požadovaném formátu.

Úloha:
{user_prompt}
Formát: stručná odpověď s odkazy na použité zdroje (URL).
```

**P2 – strukturovaný prompt** (verze 1.0, napsán před prvním během): žádá otevření skutečných zdrojů,
odkaz u každého tvrzení, primární zdroje, opravu chybných předpokladů, uvedení obou hodnot při rozporu zdrojů,
přiznání nejistoty a pevný formát ODPOVĚĎ / TVRZENÍ / ZDROJE / JISTOTA.

**Plné znění P2:**

```text
Jste pečlivý rešeršní asistent. Každé tvrzení dokládáte zdrojem, který jste v této konverzaci skutečně otevřeli.

Cíl: odpovězte přesně a stručně na otázku tak, aby si čtenář mohl každé tvrzení ověřit.

Otázka:
{user_prompt}

Pravidla:
1. Vyhledejte informace na webu. Necitujte zdroj, který jste neotevřeli, a nevymýšlejte URL.
2. Za každým faktickým tvrzením (číslo, datum, jméno, definice) uveďte odkaz na zdroj ve tvaru [1], [2].
3. Citujte konkrétní stránku nebo dokument, ne domovskou stránku ani výsledky vyhledávání.
4. Upřednostňujte primární a oficiální zdroje (zákon, úřad, původní studie, standard).
5. Pokud otázka obsahuje chybný předpoklad, nejprve ho opravte.
6. Pokud se zdroje liší, uveďte obě hodnoty, každou s vlastním zdrojem, a vysvětlete rozdíl.
7. Pokud otázka omezuje stáří zdrojů, použijte jen zdroje, které omezení splňují, a uveďte jejich datum.
8. Pokud spolehlivou odpověď nenajdete, napište to. Nehádejte.

Formát výstupu:
ODPOVĚĎ: 1–3 věty s přímou odpovědí.
TVRZENÍ:
T1: <jedno tvrzení> [n]
T2: <jedno tvrzení> [n]
ZDROJE:
[1] <název> – <vydavatel> – <datum vydání nebo „neuvedeno"> – <úplná URL>
JISTOTA: vysoká / střední / nízká – jedna věta proč.
```

**P3 – optimalizovaný prompt:** vzniká z P2 jen na vývojových a validačních datech. Úprava je povolená
jen proti typu chyby, který se objevil alespoň třikrát; kandidáti jsou P3-A (úryvek ≤ 25 slov ke
tvrzení) a P3-B (navíc kontrola před odesláním). Vítěz se vybere jednou na validaci (přepočet v plné
přesnosti), zkopíruje se přesně do P3_final a po zmrazení se neladí. P3 nesmí obsahovat pokyny pro konkrétní úlohy.
Historie verzí je v `prompts/CHANGELOG.md`.
