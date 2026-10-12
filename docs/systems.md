# Porovnávané systémy a přístup k nástrojům

Volíme návrh podle schopností produktu: každý asistent používá své běžné webové vyhledávání a výsledky prezentujeme výslovně jako **porovnání produktů**. Paritu nástrojů ve spotřebitelských rozhraních zajistit nelze, protože každý produkt má vlastní vyhledávač, index a zobrazení citací. Claude Code nezahrnujeme, protože jde o nástroj pro programování.

| Systém | Jak zajistit vyhledávání | Režim bez paměti | Vyloučený režim |
| --- | --- | --- | --- |
| ChatGPT | Vynutit nástrojem Search (menu nástrojů nebo „/") | Temporary chat, varianta Unpersonalized | Deep research |
| Gemini | Automaticky, přepínač není zdokumentován | Temporary chat (osobní účet) | Deep Research |
| Claude | Přepínač Web search, v novém rozhraní automaticky | Incognito chat a smazané preference a styly profilu | Research |
| Perplexity | Vždy, režim Search | Incognito | Research, Labs |
| Grok | Automaticky (web a X) | Private Chat | DeepSearch |

:::{note}
Nastavení odpovídá nápovědě výrobců k 29. 9. 2026. První den běhů ho ověříme snímkem obrazovky, protože se rozhraní mění.
:::

## Pravidla běhu

1. Každý dotaz začíná v novém chatu v režimu bez paměti, bez vlastních instrukcí, bia a stylů. To je plán analytické konfigurace. Nový pilot používá existující přihlášené účty v Chromu; jejich skutečná úroveň a nastavení jsou evidované odchylky.
2. Původní analytický plán předpokládá stejnou, výchozí bezplatnou úroveň. Nový pilot u Gemini ukázal Plus; homogenita účtů není ověřena a musí se vyřešit před G1. Model necháme na automatickém výběru a zaznamenáme jeho viditelný název.
3. Použijeme stejný prohlížeč, českou síť a češtinu rozhraní. Pořadí systémů pro každý případ losuje skript (seed 2026).
4. Jeden případ projde všemi pěti systémy během 24 hodin, celou testovací sadu zvládneme do 72 hodin.
5. Platí jedno kolo komunikace. Pokud se systém doptá, odpovíme větou „Pokračujte podle svého nejlepšího úsudku." a kolo navíc zaznamenáme.
6. Uložíme text odpovědi, všechny URL citací (z panelu zdrojů nebo exportu), snímek obrazovky a odkaz na sdílení.

## Co lze od čeho oddělit

| Zdroj výkonnosti | Oddělíme ho? | Jak |
| --- | --- | --- |
| Vliv promptu | Ano | Stejný systém v podmínkách P1, P2 a P3 |
| Vliv nástrojů | Částečně | Evidujeme, zda proběhlo vyhledávání a kolik zdrojů systém zobrazil |
| Schopnost modelu | Ne | Ve spotřebitelském rozhraní model nelze odpojit od vyhledávání |
| Vliv produktu | Ne | Rozhraní, bezpečnostní vrstva a vyhledávač tvoří celek |

## Metadata běhů

Metadata každého běhu zapisujeme do `runs/run_plan_<fáze>.csv`:

- systém, viditelný název modelu, rozhraní a úroveň předplatného,
- datum a čas (Europe/Prague),
- podmínku a verzi promptu s hashem SHA-256 a systémovou instrukci („výchozí, neviditelná"),
- oprávnění nástrojů, kontextové soubory (žádné), teplotu a délku výstupu („výchozí, nenastavitelné"),
- počet kol, počet zobrazených vyhledávání, latenci, náklady,
- opakování, typ selhání a ruční zásahy.

## Volitelné rozšíření: API

Stejnou sadu lze spustit přes API s nástroji pro webové vyhledávání (OpenAI, Gemini, Anthropic, xAI). API dovolí nastavit teplotu a délku výstupu a vrací strukturovaná metadata citací. Výsledky API bychom vykazovali odděleně jako druhou vrstvu (dvouvrstvý návrh) a neslévali je s výsledky produktů.
