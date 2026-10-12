# Analýza pilotních výstupů

Skutečná data zatím pokrývají **2 unikátní úlohy a 10 odpovědí**. Tato analýza
nenaplňuje požadavek zadání na alespoň 8 unikátních úloh; deset odpovědí na dvě
otázky se za osm různých případů nevydává. Níže jsou konkrétní pozorování AI
operátora, která mají lidé přezkoumat. Nejde o nezávislé lidské ratingy.

| Úloha / kolekce | Konkrétní pozorování | Interpretace a omezení |
| --- | --- | --- |
| CIT-001 / původní Perplexity | Inline DOI a DOI v seznamu se liší | Riziko nesprávné atribuce; zachovat oba původní odkazy. Příčina retrievalu/generování není doložena: unknown. |
| CIT-001 / původní ChatGPT | Hlavní účinnost 95 %; text používá confidence interval | Originální studie používá Bayesian credible interval; přesnou terminologii a závažnost musí posoudit hodnotitel. |
| CIT-001 / nový ChatGPT | Hlavní účinnost 95 %; výstup přiznává blokované otevření plného textu | Úspěch hlavního údaje a transparentní omezení přístupu; samotná deklarace neprokazuje přečtení všech zdrojů. |
| CIT-001 / nový Grok a Gemini | Hlavní údaj 95 %; citace na PubMed záznam původní studie | Pozitivní protipříklad pro hlavní odpověď; všechna dobrovolná tvrzení musí být ověřena zvlášť. |
| CIT-020 / nové produkty | Přesné narození přiznávají jako neznámé a odlišují křest od tradice narozenin | Pozitivní práce s nejistotou; tradiční datum se nevydává za jistý rodný záznam. |
| CIT-020 / nový Perplexity | Tvrzení „earliest plausible birth date“ jde nad prosté odlišení tradice od dokladu | Požaduje kontrolu zdrojové pasáže; bez ní nepřidělujeme S2. Úplné sdružené citace jsou zachovány v normalizaci v2. |
| CIT-020 / nový ChatGPT a Grok | Dobrovolné historické podrobnosti nad hlavní otázku | Více tvrzení zvyšuje rozsah nutné verifikace; nejsou dalšími povinnými RF. |

Pro finální analýzu je stále nutných ≥8 různých task_id, včetně úspěchů,
selhání a protipříkladů, vazby na run_id/pair_id a doložené zdrojové pasáže.
Retrieval/attribution/generation jsou hypotézy; bez přímého důkazu se uvádí unknown.
Lepší P3 sám neprokazuje opravu mechanismu. Pilotní případy nejsou finální test.
