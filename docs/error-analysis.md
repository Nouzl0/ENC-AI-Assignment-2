(error-analysis)=
# Analýza osmi skutečných pilotních úloh

Rozbor pokrývá **8 unikátních úloh** z pilotu (CIT-001, 003, 004, 005, 008, 012, 013, 020) a obsahuje
úspěchy, citační problémy i provozní selhání. U každé úlohy je uveden konkrétní běh, pozorování v originální
odpovědi a kontrola proti primárnímu zdroji (snapshot s časem a SHA-256 mimo Git). Je to **doplňková analýza
s pomocí AI operátora před zmrazením protokolu**, ne nezávislý lidský rating ani výsledek finální testovací sady.

| Typ nálezu | Úlohy | Co ukazují |
| --- | --- | --- |
| Úspěch | CIT-003, CIT-012, CIT-013, CIT-020 | Správná hlavní hodnota podpořená primárním zdrojem; rozlišení časových údajů a přiznání nejistoty |
| Citační riziko | CIT-001, CIT-008 (Perplexity) | Inline odkaz nesouhlasí se seznamem zdrojů; hranice věku přisouzena jinému článku Ústavy |
| K lidskému přezkumu | CIT-004 (Grok), CIT-005 | Doplňková tvrzení nad rámec reference; zdroje typu agregátor místo úředního textu |
| Provozní selhání | CIT-004 (ChatGPT) | Chyba načtení po částečném výstupu; první pokus zachován |

### CIT-001 · riziko citace (Perplexity, původní pilot)
**Pozorování:** inline DOI `NEJMoa2200674` se liší od DOI v seznamu zdrojů, `NEJMoa2034577`.
**Kontrola:** správných 95 % v hlavní větě rozpor neodstraňuje; čtenář může odkaz s tvrzením zaměnit (E4). Odpověď i oba cíle jsou zachovány, mechanismus vzniku je *unknown*.

### CIT-003 · úspěch (ChatGPT, Grok)
**Pozorování:** poločas ≈ 5 730 let, přeměna na dusík-14, definice poločasu s odkazem na NIST.
**Kontrola:** [NIST](https://www.nist.gov/how-do-you-measure-it/how-do-you-know-age-fossils-and-other-old-things) údaje podporuje. Přípustná hodnota není chyba jen proto, že jiná evaluace uvádí 5 700 ±30 let. Dobrovolné podrobnosti Groku vyžadují samostatnou kontrolu.

### CIT-004 · smíšený výsledek a provozní selhání (Grok, ChatGPT)
**Pozorování:** Grok rozlišil 1 603,296 m a trigonometrický bod 1 602,02 m, ale T2 navíc tvrdí polohu u kaple a vzdálenost 3,5 m. ChatGPT po částečném textu skončil chybou načtení.
**Kontrola:** [Zeměměřický úřad](https://cuzk.gov.cz/Aktuality-resort/20140225/Snezka.aspx) podporuje oba výškové údaje, ne kapli ani 3,5 m; T2 je nutné rozdělit (E2). Selhání ChatGPT je `failed/tool_error`, ne nahrazený běh; částečný výstup je uchován.

### CIT-005 · úspěch s výhradou (Grok, ChatGPT)
**Pozorování:** odpovědi odlišují 1. 1. 2024 od plné aplikace 1. 7. 2024; Grok cituje i právní agregátory a obecní zdroje.
**Kontrola:** [MMR](https://mmr.gov.cz/cs/ostatni/web/novinky/novy-stavebni-zakon-zacal-platit-i-pro-bezne-stavb) podporuje hlavní datum. Správná odpověď ještě neznamená, že každý její odkaz je primární nebo podporuje všechny podrobnosti.

### CIT-008 · chybný předpoklad (ChatGPT úspěch, Perplexity chybný locator)
**Pozorování:** ChatGPT opraví 35 let na 40 a rozliší Sněmovnu (21) a Senát (40). Perplexity věk také opraví, ale přisoudí jej čl. 16 odst. 2.
**Kontrola:** [Ústava na PSP](https://www.psp.cz/docs/laws/constitution.html), čl. 19 odst. 1–2, opravu potvrzuje. Čl. 16 odst. 2 řeší počet senátorů a období, ne věk: správné číslo s chybným locatorem (E5). Text zůstává nezměněn.

### CIT-012 · úspěch (ChatGPT)
**Pozorování:** správně SBOM, EO 14028 z 12. 5. 2021, odlišená publikace 17. 5. 2021, zmínka o licenční analýze.
**Kontrola:** [původní EO ve Federal Register](https://www.govinfo.gov/content/pkg/FR-2021-05-17/html/2021-10460.htm), §4(e)(vii), §4(f), §10(j), podporuje definici, data i použití. Datum podpisu a publikace se nesmějí zaměnit (E5).

### CIT-013 · úspěch (ChatGPT)
**Pozorování:** přesné číslo 10 524 167 a rozhodný okamžik půlnoc 26./27. 3. 2021.
**Kontrola:** [ČSÚ](https://csu.gov.cz/produkty/csu-predstavil-prvni-vysledky-scitani-2021) údaje potvrzuje. Rozpor roku vydání v textu a metadatech stránky není důvodem označit počet za chybný.

### CIT-020 · práce s nejistotou (všechny čtyři produkty)
**Pozorování:** odlišena neznámá data narození, doložený křest a tradice 23. 4. Perplexity C3 navíc používá „earliest plausible birth date".
**Kontrola:** [Shakespeare Birthplace Trust](https://www.shakespeare.org.uk/explore-shakespeare/shakespedia/william-shakespeare/when-was-shakespeare-born/) přiznání nejistoty podporuje; silnější tvrzení o nejdřívějším dni vyžaduje další kontrolu (E3).

Zdroje pro tento rozbor byly skutečně staženy se snapshoty, časem a SHA-256
mimo Git; veřejná provenance je součástí exportu rozšířeného pilotu. Kanonický
kontrolní zdroj výše není automaticky důkazem S2 pro jinou URL, kterou
citoval produkt. Nezávislí hodnotitelé musí posoudit každý původní pár, celý text
odpovědi a všechny dobrovolné doplňky. Kódy chyb zde označují nálezy nebo výslovná
rizika k přezkumu, nikoli vyplněné ratingy pod identitou lidských hodnotitelů.

U ChatGPT CIT-004 se interval od odeslání do terminálního pozorování chyby
137,738 s odděluje od původního částečného zachycení po 18,878 s. Ani jeden
není přesná generační latence. Některé snímky zachycují jen prompt nebo neúplný
viewport; raw odpovědi a terminální JSON/TXT jsou autoritativní.

Retrieval, attribution a generation jsou hypotézy příčin; bez přímého důkazu uvádíme *unknown*. Systematická četnost
chyb, srovnání P1/P2/P3 a lidská shoda vyžadují plný experiment ([](#plan)); osm úloh jej nenahrazuje.
