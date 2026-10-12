(results)=
# Výsledky skutečného pilotu

Sběr z 12. 10. 2026 obsahuje **10 skutečných odpovědí na 2 unikátní úlohy**:
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
