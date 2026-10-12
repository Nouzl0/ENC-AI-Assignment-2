(results)=
# Výsledky skutečného pilotu

Celkem jsou uložené **33 skutečné odpovědi na 8 unikátních úloh** ve třech
oddělených pilotních kolekcích. Původní sběr z 12. 10. 2026 obsahuje
**10 skutečných odpovědí na 2 unikátní úlohy**:
2 z původního anonymního pilotu a 8 z nového sběru v Avast Secure Browser 153.
Originální odpovědi, raw HTML/texty, metadata, snímky a SHA-256 jsou exportovány
v `runs/pilot-2026-10-12/`. Obě kolekce se uchovávají odděleně; nesléváme je do skóre.
Souhrn řádků je v `results/pilot/run_summary.csv`.
Část původních snímků zachytila jen aktuální viewport. Dodatečné zachycení je
odlišené časem a názvem; některé výřezy stále nejsou úplné. Raw text/HTML a skutečné
zdrojové karusely zůstávají autoritativním obsahem, snímek není sám úplným dokladem.

| Produkt | Nový CIT-001 / P2 | Nový CIT-020 / P2 | Skutečně viditelný model / tarif |
| --- | --- | --- | --- |
| ChatGPT | Odpověď uložena | Odpověď uložena | GPT-6, Střední; tarif unknown |
| Gemini | Odpověď uložena | Odpověď uložena | 3.6 Flash; Plus |
| Grok | Původní požadavek pokračoval po přístupovém ověření, odpověď uložena | Odpověď uložena | Fast; podkladový model a tarif unknown |
| Perplexity | Odpověď uložena | Odpověď uložena | Výchozí model bez zobrazeného názvu; Free |
| Claude | Odeslaný pokus skončil limitem, bez odpovědi | Zatím neodesláno kvůli známému limitu | Opus 5.5 Medium; tarif unknown |

Claude hlásil obnovení limitu 13. 10. v 19:00 a sdílení limitů s Claude Code.
Pokus je uchován v auditu, není kvalitativně hodnocen jako odpověď modelu.
Původní anonymní pilot navíc obsahuje odpovědi ChatGPT a Perplexity na CIT-001;
jejich raw/normalizované texty a snímky byly ověřeny po bytech.

## Rozšířený pilot 13. 10. 2026

Šest dalších veřejných dev úloh bylo určeno před odesláním v nové kolekci
`avast-v2`: CIT-003, CIT-004, CIT-005, CIT-008, CIT-012 a CIT-013, všechny v P2.
Spolu s původními CIT-001 a CIT-020 dávají osm unikátních úloh. Rozšíření je
přípravný pilot před G1; budoucí analytická dev sada se sbírá nově po zmrazení.
Originály jsou v soukromé složce, schválený export v `runs/pilot-2026-10-13/`.

| Produkt | Dokončené odpovědi / odeslané první pokusy | Provozní selhání | Neodeslané řádky |
| --- | --- | --- | --- |
| ChatGPT | 5 / 6 | 1 – chyba načtení odpovědi CIT-004 | 0 |
| Gemini | 6 / 6 | 0 | 0 |
| Grok | 6 / 6 | 0 | 0 |
| Perplexity | 6 / 6 | 0 | 0 |
| Claude | 0 / 0 | 0 nových pokusů | 6 – známý limit |

To je **23 dokončených odpovědí z 24 odeslaných prvních pokusů** (95,8 %)
a 6 neodeslaných řádků. Nebyl opakován žádný cloudový požadavek; úspěšnost na
první a konečný pokus je zde shodná. Jde o provozní výsledek pilotu, nikoli
citační přesnost nebo odhad spolehlivosti produktu v populaci úloh. Mezi kolekcemi
se lišilo nastavení i způsob zachycení, jejich kvalita se neslévá do jednoho skóre.

ChatGPT CIT-004 po částečném výstupu zobrazil skutečnou chybu načtení. Raw
partial je uchován; terminální pozorování a metadata mají interval 137,738 s,
původní částečný snímek 18,878 s je zvlášť doložen. U Perplexity CIT-008 byla
naopak odpověď již hotová: selhala až kamera kvůli skryté stránce. Kompletní text,
HTML a původní pozorování dokončení po 17,625 s zůstaly zachované; pozdější
snímek a citace se zachytily bez nového promptu. Emulace aktivity stránky se
použila jen po dokončení odpovědi při snímku/čtení karuselů a poté vypnula.
Část snímků zachycuje jen prompt, částečný viewport či černý výřez; úplný obsah
se posuzuje z raw textu/HTML a terminálních JSON/TXT.

Nové chaty ověřily ChatGPT GPT-6/Střední/Bez personalizace, Grok Private/Fast,
Gemini Temporary/Flash a Perplexity Incognito/výchozí Search. Gemini nový header
neukázal přesnou verzi a tarif; dřívější pozorování 3.6 Flash/Plus je od aktuálního
štítku oddělené. Totéž platí pro dříve pozorovaný Free u Perplexity. Neviditelné
hodnoty se nepřevádějí na odhad.

Šest nových Perplexity odpovědí obsahovalo **44 skutečných citačních skupin a
57 zdrojových vazeb**; všechny byly zachyceny z původních UI karuselů. Originální
v1/raw a auditované v2 zůstaly oddělené. Parser nové kolekce připravil **148
anotačních řádků**, identifikoval 15 necitovaných tvrzení a provedl HTTP kontroly
49 unikátních URL. Oba lidé mají stejné nevyplněné listy pro všech 23 odpovědí
(100% pilotní překryv). Formálně zaslepené listy nezaručují zaslepení lidí, kteří
již četli pojmenované zdrojové odpovědi v projektu. Automatické kontroly a klíč
zůstávají mimo Git; žádné nezávislé ratingy se tím nevykazují.

[Analýza osmi úloh](#error-analysis) obsahuje konkrétní pozitivní i negativní
pozorování s primárními kontrolními pasážemi. Soukromé zdrojové snapshoty mají
čas a SHA-256; pomocná kontrola AI nenahrazuje lidskou verifikaci před G1.

## Provozní výsledky a jejich meze

Nový plán má 10 řádků: 8 completed, 1 failed (rate limit), 1 planned.
Nevyplněný řádek není selhání. Nebyla provedena žádná regenerace věcně chybné
odpovědi ani náhrada neúspěšného pokusu lepším textem. Grok pokračoval v původním
požadavku, nikoli v novém retry.

Většina uložených intervalů zahrnuje prodlevu zachycení nebo opravu pozorovacího
nástroje, proto jsou označené jako horní meze, nikoli přesná generační latence.
U CIT-020 bylo dokončení Grok pozorováno po 19,006 s a Perplexity po 11,954 s;
i tyto hodnoty zahrnují polling. Dva případy a rozdílné účty nestačí pro žebříček latence.
Náklady, tokeny a kredity, které UI nezobrazilo, zůstávají unknown.

CIT-001 ChatGPT měl před odesláním stále štítek Personalizovaný; vypnutí nebylo
ověřeno. U čerstvého CIT-020 již UI výslovně potvrdilo Bez personalizace.
Gemini používal Plus. Tyto odchylky jsou zachované, nikoli prohlášené za homogenní
měření bezplatných účtů. Další analytický sběr vyžaduje schválené nastavení G1.

## Integrita citací a automatická kontrola

Původní Perplexity CIT-001 má v inline odkazu DOI `NEJMoa2200674`, zatímco textový
seznam uvádí `NEJMoa2034577`. Rozdíl je zachovaný; odkaz se neopravoval.
Nový Perplexity CIT-020 má sdružené citační čipy. Operátor otevřel jejich skutečné
UI karusely: 9 skupin obsahovalo 15 původních zdrojových vazeb. Normalizace v2
zachovává všechny cílové URL na původních místech; původní v1, raw HTML a doklad
karuselů zůstaly uložené. Jde o opravu exportu, nikoli modelové odpovědi.

`check_citations.py --pilot` zpracoval 8 nových odpovědí: 54 anotačních řádků,
3 automaticky identifikovaná necitovaná tvrzení a HTTP kontroly 11 unikátních URL.
Oba lidé mají připravené totožné podklady pro všech 8 odpovědí; proto je rozsah
druhého pilotního hodnocení 100 %. Parserové jednotky
musí lidé přezkoumat; automatický HTTP stav neprokazuje zdrojovou oporu ani pravdivost.
Listy jsou dosud nevyplněné, nejde o provedené nezávislé ratingy.

## Co z těchto dat nelze vypočítat

G1/G2/G3 nejsou splněny. Chybí analytická matice dev/val/test/repeat, lidské ratingy,
P3_final a schválený holdout. Proto není vykázána finální citační precision/recall,
správnost s CI, H1/H2, přenos P3, repeat variabilita, raw IRR ani Pareto/index úsilí.
`score.py --final` nebyl spuštěn na skutečných datech bez G3. Syntetické výsledky
softwarových testů se do výsledků produktů nepřidávají.

## Návrh komentáře týmu

:::{include} ../results/pilot/team_commentary.md
:heading-offset: 2
:::
