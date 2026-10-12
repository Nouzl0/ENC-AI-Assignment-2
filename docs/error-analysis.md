(error-analysis)=
# Analýza osmi skutečných pilotních úloh

Rozbor nyní pokrývá **8 unikátních task_id**: CIT-001, CIT-003, CIT-004,
CIT-005, CIT-008, CIT-012, CIT-013 a CIT-020. Obsahuje úspěchy, konkrétní
citační problémy i provozní selhání. Jde o doplňkovou analýzu AI operátora
z původního pilotu a odděleného rozšířeného pilotu před G1. Není nezávislým
lidským ratingem ani výsledkem finální testovací sady.

| Úloha / skutečný run | Pozorování v originálu | Kontrola a závěr AI operátora |
| --- | --- | --- |
| CIT-001 / legacy `dev-CIT-001-P2-perplexity-r1` | Inline DOI `NEJMoa2200674` se liší od seznamu `NEJMoa2034577` | Konkrétní riziko záměny citací (E4); správných 95 % v hlavní větě tento rozpor neodstraňuje. Odpověď i oba cíle byly zachovány. Mechanismus vzniku: unknown. |
| CIT-003 / avast-v2 `dev-CIT-003-P2-chatgpt-r1`, C1–C3 | Poločas přibližně 5 730 let, přeměna na dusík-14 a definice poločasu s odkazem na NIST | [NIST](https://www.nist.gov/how-do-you-measure-it/how-do-you-know-age-fossils-and-other-old-things), odstavce o half-life a carbon-14, tyto údaje podporuje. Pozitivní protipříklad: přípustná hodnota není automaticky chyba jen proto, že jiná evaluace uvádí 5 700 ±30 let. Grok navíc rozlišil historické hodnoty; všechny jeho dobrovolné podrobnosti ještě vyžadují samostatnou kontrolu. |
| CIT-004 / avast-v2 `dev-CIT-004-P2-grok-r1`, T1–T4; ChatGPT první pokus | Grok správně rozlišil 1 603,296 m a trigonometrický bod 1 602,02 m. T2 navíc tvrdí polohu u kaple a vzdálenost 3,5 m. ChatGPT po částečném textu přešel do chyby načtení. | [Zeměměřický úřad](https://cuzk.gov.cz/Aktuality-resort/20140225/Snezka.aspx), PDF s. 1, podporuje oba výškové údaje a rozdíl bodů. Uvedený PDF nepodporuje doplněnou kapli ani 3,5 m: T2 je třeba rozdělit, nelze celé bez kontroly přijmout jako S2 (nález E2). ChatGPT je failed/tool_error, ne regenerovaná náhrada; partial/raw a terminální JSON/TXT jsou uchovány. |
| CIT-005 / avast-v2 `dev-CIT-005-P2-grok-r1`, T1–T3; ChatGPT T1–T2 | Odpovědi odlišují 1. 1. 2024 od plné aplikace 1. 7. 2024. Grok používá právní agregátory i obecní/odborné potvrzení. | [MMR](https://mmr.gov.cz/cs/ostatni/web/novinky/novy-stavebni-zakon-zacal-platit-i-pro-bezne-stavb), úvod zprávy 1. 7. 2024, podporuje hlavní datum pro běžné stavby. Pozitivní práce s přechodným režimem. Správná hlavní odpověď ještě neznamená, že každý její vlastní odkaz je primární nebo podporuje všechny podrobnosti. |
| CIT-008 / avast-v2 `dev-CIT-008-P2-chatgpt-r1`, ODPOVĚĎ a T1; Perplexity ODPOVĚĎ | ChatGPT výslovně opravuje 35 let na 40 a rozlišuje Sněmovnu (21) a Senát (40). Perplexity také opravuje věk, ale připisuje hranici čl. 16 odst. 2. | [Ústava na PSP](https://www.psp.cz/docs/laws/constitution.html), čl. 19 odst. 1–2, potvrzuje opravu ChatGPT; jde o pozitivní protipříklad k E10. Čl. 16 odst. 2 řeší 81 senátorů a šestileté období, nikoli věkovou hranici: Perplexity má správné číslo s chybným locatorem (E5). Jeho původní text zůstává nezměněný. Dobrovolné tvrzení o druhém dni voleb se posuzuje zvlášť. |
| CIT-012 / avast-v2 `dev-CIT-012-P2-chatgpt-r1`, T1–T3 | Správně uvádí SBOM, EO 14028 z 12. 5. 2021 a odděluje publikaci 17. 5. 2021. Zmiňuje i licenční analýzu. | [Původní EO ve Federal Register](https://www.govinfo.gov/content/pkg/FR-2021-05-17/html/2021-10460.htm), hlavička, §4(e)(vii), §4(f) a §10(j), podporuje definici, data a použití SBOM včetně licencí. Úspěch konkrétního primárního zdroje; datum podpisu a publikace se nesmějí zaměnit za E5. |
| CIT-013 / avast-v2 `dev-CIT-013-P2-chatgpt-r1`, T1–T2 | Přesné číslo 10 524 167 a půlnoc 26./27. 3. 2021 | [ČSÚ](https://csu.gov.cz/produkty/csu-predstavil-prvni-vysledky-scitani-2021), první dva odstavce, potvrzuje hlavní údaje. Pozitivní příklad přesnosti čísla a času. Samotná stránka má rozpor roku vydání v textu a metadatech; ten není důvodem označit správný počet za chybný. Dostupnost vlastní citované URL produktu hodnotí každý pár zvlášť. |
| CIT-020 / avast-v1 `dev-CIT-020-P2-perplexity-r1`, C3; nové odpovědi čtyř produktů | Produkty odlišily neznámé narození, doložený křest a tradici 23. 4. Perplexity C3 navíc používá „earliest plausible birth date“. | [Shakespeare Birthplace Trust](https://www.shakespeare.org.uk/explore-shakespeare/shakespedia/william-shakespeare/when-was-shakespeare-born/), Parish Register a vysvětlení tradice, podporuje práci s nejistotou. Silnější tvrzení o nejdřívějším možném dni vyžaduje další zdrojovou kontrolu (riziko E3). Původní citační karusely jsou doložené; text se neopravoval. |

Zdroje pro tento rozbor byly skutečně staženy se snapshoty, časem a SHA-256
mimo Git; veřejná provenance je součástí exportu rozšířeného pilotu. Kanonický
kontrolní zdroj v tabulce není automaticky důkazem S2 pro jinou URL, kterou
citoval produkt. Nezávislí hodnotitelé musí posoudit každý původní pár, celý text
odpovědi a všechny dobrovolné doplňky. Kódy chyb zde označují nálezy nebo výslovná
rizika k přezkumu, nikoli vyplněné ratingy pod identitou Reného a Jana.

U ChatGPT CIT-004 se interval od odeslání do terminálního pozorování chyby
137,738 s odděluje od původního částečného zachycení po 18,878 s. Ani jeden
není přesná generační latence. Některé snímky zachycují jen prompt nebo neúplný
viewport; raw odpovědi a terminální JSON/TXT jsou autoritativní.

Srovnání P1/P2/P3, systematická četnost chyb, lidská shoda a finální test zůstávají
nedokončené. Retrieval/attribution/generation jsou hypotézy; bez přímého důkazu
uvádíme unknown. Osm unikátních pilotních úloh nenahrazuje celou analytickou matici.
