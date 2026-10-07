# Výzkumný protokol – návrh před G1

**Dosud nezmrazeno; nejsou výsledky ani podepsané brány.** Tento soubor a rubrika jsou
aktuální normativní podklad. Původní DOCX je historický návrh. Skutečné schválení,
časové údaje a hashe uloží správce do soukromých manifestů podle `freeze/README.md`.

## 1. Otázka, rozsah a interpretace

Na účelovém mixu ≥40 faktických CZ/EN úloh z pěti domén: jak často citovaný zdroj
skutečně podporuje přiřazené tvrzení u pěti rešeršních AI produktů a jak výsledek mění
společný strukturovaný a obecně optimalizovaný prompt? Měřeným výsledkem je podíl
explicitních S2 dvojic; praktický význam je důvěryhodnost atribuce při běžné rešerši,
ne důkaz pravdivosti všeho, co produkt napsal.
Směr B; **porovnání produktů**, nikoli základních modelů nebo čistého vlivu vyhledávání.

ChatGPT, Gemini, Claude, Perplexity, Grok; výchozí bezplatná úroveň, běžný chat s dostupným
vyhledáváním, bez Deep Research. Aktuální rozhraní, účty a dostupnost nástrojů ověří
operátor a doloží nastavení před G1; názvy přepínačů se mohou změnit. Systémové instrukce,
teplota či limit výstupu, které UI neukazuje, jsou výchozí/neznámé, ne domyšlené hodnoty.
Rozdíly zahrnují model, retrieval, účet, region, UI a výchozí nastavení produktu.

Čtyři produkty jen s předem písemně doloženým důvodem přístupu/nedostupnosti/nevhodnosti
pátého; samotná úspora práce není takovým důvodem. Seznam i H1 focus se uloží do G1,
nevybírají se podle dosažených výsledků. Pokud předepsané podmínky nelze splnit, zaznamenat
odchylku a dopad nebo změnit návrh před G1, ne tiše změnit experiment.

## 2. Data a prevence leakage

- Dev 20 (CIT-001–020), val 10 (CIT-021–030), nový soukromý test ≥10; celkem ≥40.
- Záměrný mix pěti domén, CZ/EN/cs+en, faktů/primárních dokumentů/syntéz a obtížností;
  ≥20 % edge případů **v každé sadě**. Popsat skutečné počty a způsob týmového výběru,
  nejde o náhodný reprezentativní vzorek všech uživatelských dotazů.
- `published_test_candidates.jsonl` obsahuje veřejné historické CIT-031–040, není holdout.
  Nové testy vytvoří nezávislý správce mimo Git, bez kopírování zveřejněných otázek.
  Kontrola překryvu ID/Jaccard je pojistka, nikoli důkaz nepřítomnosti kontaminace.
- Autor promptu nevidí holdout ani jeho reference před G2. Správce provádí CLI, které
  pro kontrolu hashů potřebuje přístup k soukromým souborům; autor dostává jen dev/val výstupy.
- Schéma v2: `required_facts` = pouze požadavky otázky, `optional_facts` = bonus. Opuštění
  bonusu se netrestá; chybná dobrovolná fakta se hodnotí. `key_facts` je alias required.
- Nezávislý ověřovatel před G1 doloží **všechny RF/OF** všech úloh: hodnotu, primární
  zdroj, locator, čas s offsetem, krátký úryvek/vlastní shrnutí, soukromý snapshot + SHA-256.
  Původní datované texty a URL nejsou důkaz, že byla tato kontrola dokončena.
- RUN_DAY hodnoty se ověřují pro každou dokončenou úlohu a den **v UTC**, zvlášť přes
  `run_day_evidence.csv`, přesně RF/OF a s kontrolou tentýž den. Zmrazený gold nepřepisovat.
  Hodnotitel musí dostat odpovídající denní reference, ne použít starý orientační údaj.

## 3. Prompty a adaptace

P1 společná výchozí šablona; P2 společný strukturovaný prompt; P3 obecná optimalizace
na dev chybách. P3A/P3B v repo jsou **předběžné hypotézy**, ne prokázaná zlepšení.
Přesné CZ/EN texty, jejich délky a hashe uchovat; cs+en používá českou šablonu.

P3 úprava musí mít důvod doložený alespoň ve třech chybných dev odpovědích, s ID a
kódem chyby v CHANGELOG. Žádné instrukce pro konkrétní úlohu či konkrétní produkt;
stejná verze pro všechny produkty. Důkazy mechanismu rozlišit od pouhého kódu chyby.
P1/P2, data, rubrika i kód jsou od G1 neměnné; P3 kandidáti se upravují jen v dev.

Před G1 zvolit jeden kandidát (P3A nebo P3B), nebo oba. Jedna plánovaná validační
matice P2+kandidáti. Vybrat vyšší průměr hlavní metriky přes všechny systémy a úlohy;
při rozdílu <0,02 vybrat kratší průměrnou délku CZ/EN šablony, při shodě P3A.
Jeden kandidát se vybere i bez zlepšení P2 a neúspěch se uvede. **Po validaci už žádné
nové ladění na val/test**; další iterace by byla nový deklarovaný experiment.
P3_final musí být přesná CZ/EN kopie vybraného skutečně měřeného kandidáta → G2.

## 4. Hypotézy a alternativy (pouze finální test)

- **H1:** bodový odhad přesnosti předem zvoleného focus (výchozí Perplexity) v P2 − průměr ostatních předem zahrnutých
  produktů je ≥0,10 a dolní mez 95% párového bootstrap CI je >0.
- **H2:** bodový odhad P2 − P1, průměrovaný přes předem zahrnuté produkty, je ≥0,05,
  dolní mez CI >0 a kladný odhad je u ≥4/5 (≥3/4) produktů.
- Navrhovaný mechanismus H1: hypoteticky lepší propojení retrievalu a citovaných
  pasáží v rešeršním produktu. H2: instrukce přiřadit důkaz každému tvrzení a přiznat
  nejistotu hypoteticky omezí nepodporující atribuce. **Nejde o ověřené vlastnosti**
  produktů ani příčinně identifikované mechanismy; podporu směrového výsledku lze
  přiznat jen po G3 na nových testových úlohách podle výše uvedených kritérií.
  Při zdůvodněné nedostupnosti Perplexity změnit focus i formulaci jeho mechanismu
  ještě před G1, uvést důvod a shodný focus v G1/CLI; ne volit až podle výsledků.
- To jsou pravidla podpory prakticky relevantního **odhadu**, ne důkaz, že skutečný
  efekt je alespoň 10/5 p. b. Silnější diagnostika `ci_above_margin` vyžaduje dolní
  mez CI ≥ příslušný margin; nemění původní pravidlo. Obě předem uvedené hypotézy
  prezentovat jednotlivě, ne jako jediný test s garantovanou společnou chybovostí.
- Ostatní jednotlivá porovnání, P3 přenositelnost, žebříčky a indexy jsou explorační.
- A1: přesnost roste jen díky menšímu počtu tvrzení → vykázat úplnost, pokrytí RF,
  tvrzení/citace na odpověď a deskriptivní Spearmanovu korelaci; ta neprokazuje příčinu.
- A2: dostupnost/jazyk/doména → NA a výsledky podle jazyka. CZ/EN nejsou párované
  překlady, cs+en se ve výstupu slučuje do CZ; rozdíl není čistý jazykový efekt.

## 5. Metriky a nejistota

| Role | Definice na odpověď |
| --- | --- |
| Hlavní: přesnost explicitní atribuce | explicitní S2 dvojice / všechny explicitní dvojice; 0 bez explicitních citací, NA/FAB zůstávají ve jmenovateli |
| Vedlejší 1: úplnost citací | unikátní faktická tvrzení s ≥1 explicitní S2 / všechna unikátní faktická tvrzení celé odpovědi; 0 bez tvrzení |
| Vedlejší 2: správnost odpovědi | podíl odpovědí s rubric correctness=2; required_facts, ne nevyžádané bonusy |
| Diagnostiky | pokrytí RF explicitní S2 + JSON RF→pair_id, FAB, NA, primární zdroje, časová vhodnost, nejistota, délka/tvrzení/citace, formát P2/P3, viditelné vyhledávání |
| Provoz | první i konečný úspěch, retry, selhání, první/end-to-end latence medián a p90, kola/nástroje, cost_note, čas anotace |

Všechna tvrzení celé odpovědi, bez limitu osmi; ruční segmentace a konzervativní deduplikace
podle rubriky. Úryvky P3 jsou důkaz, ne další tvrzení. S2 dokládá atribuci, nemusí být pravdou.
Neatributovaný seznam zdrojů (`*`) je pouze `unlinked_support`; hodnotitel jej nesmí použít
k opravě hlavní přesnosti, úplnosti, RF pokrytí ani hlavní kappy.

Agregace = průměr přes úlohy **prvního běhu**, stejné váhy úloh, ne pooling citací.
Bootstrap 10 000, seed 2026, klastr task_id; rozdíly párované na stejných úlohách,
produkty nejsou další nezávislé replikace otázky. Správnost a podíly odpovědí: Wilson.
P2 opakování zvlášť, SD průměrů běhů a změny správnosti jen na společných úlohách všech
opakování. Pozdější okno směšuje náhodnost, změny zdrojů a produktu, ne čistý modelový šum.
Deset testových úloh dává hrubé intervaly a nízkou sílu; nevýznamnost není důkaz rovnosti.

Explorační `annotation_effort_index` = přesnost − 0,1·L_norm − 0,1·T_norm;
L/T jsou mediány end-to-end latence/času anotace dělené maximem mediánů mezi produkty
v dané sadě/podmínce. Váhy předem, index závisí na zahrnutých produktech; **není obecný
užitek ani uživatelský čas oprav**. Historický CSV sloupec `utility` zůstává aliasem.
Chybějící čas nezískává nulovou penalizaci. Pareto pouze přesnost × latence.
Náklady oddělit: předplatné, případný mezní poplatek, lidská práce; neznámá cena není nula.

## 6. Matice a proveditelnost

| Fáze | Úloh | Podmínky | Běhy | Standard 5 produktů |
| --- | --- | --- | --- | --- |
| dev | 20 | P2 | 1 | 100 |
| val | 10 | P2, P3A, P3B | 1 | 150 |
| test | 10 | P1, P2, P3 | 1 | 150 |
| repeat | 10 předem určených testových | P2 | 2 a 3 | 100 |

Standard: **500 analytických + 10 pilotních navíc**. Pilot = 2 dev úlohy × produkty
před G1 pro kalibraci; po G1 celá dev sada nově. Úsporný, předem zdůvodněný návrh:
4 produkty, val P2+1 kandidát, opakování na 5 předem určených nových testech →
80+80+120+40 = **320 analytických + 8 pilotních navíc**. Nevybírat repeat úlohy podle výsledků.

Pokud vše skončí odpovědí, ceil(25 % v každém stratu fáze×produkt×podmínka) =
**140** druhých hodnocení standard / **92** úsporně. Hrubý rozpočet při 10 min
na odběh+první anotaci a 7 min na druhou: **99,7 h / 64,1 h**, nikoli původních 98 h.
Nejde o naměřený čas; **navíc** pilot, příprava a ověřování referencí, správa dat,
řešení neshod, analýza a zpráva, čekání na limity a náhradní běhy. Před G1 ověřit kapacitu
lidí a účtů, rozdělit role a rezervovat 72h okna; jinak neslibovat proveditelnost.

## 7. Sběr, lidé a integrity gates

Nový chat, bez paměti/personalizace/vlastních instrukcí, bez příloh či skryté historie;
stejná síť/prohlížeč/úroveň účtu kde proveditelné. Před měřením archivovat nastavení.
Náhodné pořadí systémů a podmínek v rámci úlohy, seed 2026. Přesný prompt z plánu;
max. jedna standardní odpověď na doptání, významově stejná CZ/EN, metadata turns=2.

Completed zahrnuje věcně chybnou odpověď, odmítnutí, chybějící citace i špatný formát;
bez „opravného“ retry. Failed po nejvýše jednom provozním retry = nula hlavních metrik,
zůstává v matici. Chyba operátora = excluded s důkazem a svázaným náhradním řádkem.
Původní odpovědi/pokusy/screenshoty se nemažou; RAW i normalizace a SHA-256 jsou povinné.
Test do 72 h, každá úloha napříč podmínkami/produkty do 24 h; repeat v následujících
72 h. Source rating do 7 dní od odpovědi. Odchylky evidovat včetně dopadu na závěr.

Hodnotitel 1 všechny completed odpovědi, hodnotitel 2 předem náhodně vybrané ≥25 %
v každém stratu fáze×produkt×podmínka, zaokrouhleno nahoru. Nikdo nehodnotí vlastní běh;
v malém týmu může být nutný externí hodnotitel. Zaslepení je částečné, formát může
prozradit podmínku. Raw listy před diskusí zachovat, finální konsenzus není raw IRR.
Kappa S2/ostatní cíl ≥0,6, pět kategorií a správnost doplňkově, segmentace zvlášť;
konstantní kategorie → kappa nedefinovaná, uvést n a surovou shodu. Nesrovnatelné jednotky
jsou mimo kappu a pokrytí se hlásí. Každá změna final oproti raw1 a každá kategorická
neshoda potřebuje audit. Různý vlastní čas anotace dvou lidí není kategorická neshoda.

| Brána | Skutečné podmínky (podrobnosti freeze/README.md) | Nyní |
| --- | --- | --- |
| G1 | pilot, role, dostupnost, nezávislé reference, nový soukromý holdout, parametry a hashe protokolu/dat/rubriky/P1/P2/kódu | nesplněno |
| G2 | úplná validace, dev důvody změn, volba vítěze a přesná kopie CZ/EN P3, jeho hashe | nesplněno |
| G3 | úplná matice, provozní artefakty, původní nezávislé ratingy, audit neshod, source/RUN_DAY doklady, odchylky | nesplněno |

Manifest je lidské prohlášení s hashy, ne kryptografické ověření identity. Nezávisle
archivovat každý manifest i původní plány/listy. Není možné potichu přepsat protokol,
hashy nebo ratingy: nutná oprava = datovaná verze, důvod, dopad, jednotné přehodnocení
všech dotčených odpovědí a nové brány. `--allow-missing` je pouze explorace, nikdy --final.
Finální H1/H2 vyžadují G3 a přesnou úplnou matici, ne jen přítomnost výsledkových CSV.

## 8. Výstup a limity

`score.py` vytváří metriky, intervaly, provozní diagnostiky, per-run výstup, hypotézy,
raw IRR a pomocný report. Závěrečná zpráva podle REPORT_TEMPLATE.md jej interpretuje,
nikoli pouze kopíruje. Analýza ≥8 unikátních úloh včetně úspěchů/protipříkladů;
retrieval/attribution/generation jsou hypotézy, pokud chybí přímé důkazy, použít unknown.
Lepší P3 výstup sám neprokazuje opravu příčiny. Praktické doporučení omezit na testovaný
produkt/režim/účty/jazyky/domény/čas; nezobecňovat na „nejlepší AI“.
Soukromé snapshoty mohou být chráněné, sdílet jen oprávněně; žádné osobní údaje či
přístupové tokeny. Publikace testu a odsanitizovaných artefaktů až po G3 a souhlasu týmu.
