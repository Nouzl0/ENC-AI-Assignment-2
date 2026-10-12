# Příprava balíčku (bez provedení benchmarku)

G1/G2/G3 dosud **nejsou splněny**. Nevytváříme výsledky produktů, vítězný P3 ani podpisy kolegy.

| Etapa | Rozsah | Stav |
| --- | --- | --- |
| 1 | Integrita skórování, selhání, úplnost matice, regresní testy | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 2 | Rubrika, povinné vs. doplňkové fakty, explicitní citace, důkazy | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 3 | Soukromý holdout, ověřitelné brány a ochrana artefaktů | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 4 | End-to-end testy, konzistentní dokumentace a předání kolegovi | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |

Po každé etapě: kritický subagent → oprava nálezů → lokální testy → commit → push.
Testy používají jen lokální syntetické vstupy. Aktuální příkaz: `python3 -m unittest discover -s tests -v`.

## Kontrola etapy 1

Opravené nálezy subagenta: přejmenované kopie hodnoticích jednotek v raw IRR, neplatný/chybějící
počet tvrzení a normalizace desetinné čárky v run_index. Re-kontrola bez blokujícího nálezu.
Ověřeno: 14 unittestů, validace dev/val, offline syntetický smoke v dočasné kopii, `git diff --check`.
Smoke náhodných CSV zatím není plný end-to-end test; ten nahradí etapa 4.

## Kontrola etapy 2

Opravené nálezy subagenta: podpůrné úryvky v ANSWER i CLAIMS, konzervativní deduplikace
zachovávající významové symboly a zaokrouhlení vzorku druhého hodnotitele nahoru (≥25 %).
Re-kontrola bez blokujícího nálezu. Ověřeno: 26 unittestů, validace dev/val, offline
syntetický smoke v dočasné kopii a `git diff --check`. Zdroje všech referencí nadále musí
nezávisle ověřit kolega; nová rubrika není podepsané G1 ani hotové hodnocení.

## Kontrola etapy 3

Opravené nálezy subagenta: číselná pole plan sidecaru versus CSV, nezmrazený náhradní
gold při anotaci, stratifikace druhého hodnocení i po fázích, audit každé změny finálního
ratingu a úplné denní RF/OF důkazy v UTC. Re-kontrola bez blokujícího nálezu.
Ověřeno: 40 unittestů, validace dev/val, izolované offline reprodukce a `git diff --check`.
Test G1→G2→G3 používá výhradně dočasné syntetické artefakty; žádná skutečná brána ani
produktové výsledky nevznikly. Veřejný starý test je přejmenován na kandidáty, historie zůstává.

## Kontrola etapy 4

Náhodná výsledková CSV nahradila deterministická skutečná CLI pipeline s 500 lokálními
fixture záznamy, parserem, zaslepeným exportem, ratingy a kontrolou očekávaných metrik.
Přibyly HTTP kontroly výhradně na loopbacku, finální scoring v dočasné falešné G3 kopii,
konzistentní metodika, HANDOFF.md a REPORT_TEMPLATE.md. Ratingy fixtures nejsou lidské
posudky a žádná dočasná brána není skutečné schválení.

Opravené nálezy subagenta: předání předem zvoleného focus do všech handoff score příkazů,
poctivá FAB evidence chybějícího zdrojového záznamu bez vymyšlené URL a odmítnutí
referenční kontroly datované po podpisu G1. Re-kontrola bez blokujícího nálezu.
Ověřeno: 49 unittestů na Pythonu 3.11.16 i 3.14.7, wrapper demo/run_demo.sh, samostatná
dočasná CLI fixture, validace dev/val, syntaxe Pythonu 3.9 a `git diff --check`.
Skutečný runtime Pythonu 3.9 ani vzdálené CI zde ověřeny nebyly; CI workflow je pouze
připravený. Reálné benchmarky jsme nespustili.

## Druhá revize po kritickém auditu

| Etapa revize | Rozsah | Stav |
| --- | --- | --- |
| 1 | Férové RF/OF/RC, evidenční kontrakt, předem dané kvóty holdoutu | hotovo; kritická re-kontrola bez blokujících/středních nálezů |
| 2 | Parser a přenositelná reprodukce | hotovo; kritická re-kontrola bez blokujících/středních nálezů |
| 3 | Výběr P3, ratingy a interpretační diagnostiky | hotovo; kritická re-kontrola bez blokujících/středních nálezů |
| 4 | Konzistentní dokumentace a předání | hotovo; kritická kontrola bez blokujících/středních nálezů |

Revize 1: opraveny skryté požadavky, překryv RF a nezapsané rozšíření referencí,
odděleny zdrojové/formální RC, fact_text vs skutečná ověřená reference_value.
Holdout blueprint je veřejný agregát, nikoli vytvořený test. Kritický subagent našel
bypass whitespace správnosti, chybějící referenční data, duplicitní JSON klíče a zbylá
skrytá expected_properties; opraveno a re-kontrolováno. Ověřeno 54 unittestů na
Pythonu 3.11.16 i 3.14.7, validace dev/val a git diff --check. Žádné nové ověření gold
na webu ani produktové běhy neproběhly.

Revize 2: původní URL/text, nevyřazené [0], read-only mapa cest pro G3 replay bez
změny podepsaných bytes a se záznamem rodičovského hashe. Kritická kontrola odhalila
závorky v markdown URL, tučné zdrojové řádky, záměnu primárního odkazu za mirror a
cross-overlap mapy; opraveno a re-kontrolováno. Ověřeno 61 unittestů na Pythonu
3.11.16 i 3.14.7, dvě přesunutí se smazanými původními cestami, loopback HTTP,
validace dev/val a git diff --check. Žádný produktový benchmark neproběhl.

Revize 3: G2 znovu počítá volbu P3 z neměnného snapshotu ratingů v plné přesnosti,
váže všechny kandidáty a G3 odmítá pozdější změny validačních ratingů. Oba hodnotitelé
dostávají stejné podklady bez automatických nápověd; nové offline kotvy pokrývají všechny
kategorie. Povinné diagnostické enumy mají vykázané pokrytí; report odděluje atribuci od
podmíněné přesnosti a varuje u konstantního bootstrap vzorku. Přibyl pozitivní kompletní
G1→G2→G3 test a jeho dvě přenesené reprodukce, stále výhradně na smyšlených fixtures.
Kritický subagent odhalil validační source check datovaný po podpisu G2: opraven společný
guard úplnosti/hashů/časů při seal i verify a regresní test. Opraveny také hraniční tolerance
volby P3 a zbylá textová nápověda. Re-kontrola bez blokujících/středních nálezů.
Ověřeno 70 unittestů na Pythonu 3.11.16 i 3.14.7, validace dev/val, syntaxe 3.9 a
git diff --check. Runtime 3.9 ani vzdálené CI nebyly ověřeny; produktové běhy neproběhly.

Revize 4: sjednoceny README, HANDOFF a šablona zprávy s aktuálními guardy, rubrikou,
výběrem P3, diagnostikami a přenositelnou reprodukcí. Doplněno explicitní mapování všech
osmi povinných výstupů zadání a krátké vysvětlení pro kolegu. Úsporná varianta zachovává
všech pět produktů: 400 analytických + 10 pilotních běhů, při všech completed odpovědích
115 druhých hodnocení; 80,1 h je hrubý předpoklad, nikoli měření či úplný rozpočet.
Čtyři produkty zůstávají možné jen s věcným písemným odůvodněním vyloučení pátého.
Nová vyplněná offline DEMO evidence ukazuje RF/OF, statickou i RUN_DAY platnost a
snapshoty/hashy, ale status DEMO_NOT_VERIFIED záměrně neprojde jako ověřený gold.
P3B návrh nyní uznává transparentní přímé vyplývání/zaokrouhlení stejně jako rubrika;
nejde o dev optimalizaci ani naměřené zlepšení. Čtyři nové regresní testy kontrolují
evidenci, odmítnutí přepsání/nepřípustných cest a skutečný syntetický generátor úsporné
matice se vzorkem rater2. Kritická kontrola bez blokujících/středních nálezů.
Ověřeno 74 unittestů na Pythonu 3.11.16 i 3.14.7, validace dev/val, syntaxe 3.9
(21 souborů) a git diff --check. Runtime 3.9 ani vzdálené CI nebyly ověřeny;
žádné skutečné gold ověření, podpisy bran ani produktové benchmarky neproběhly.

## Kontrola reprodukovatelnosti (2026-10-12)

Výchozí `main` byl čistý, `git pull --ff-only origin main` bez změn; vstupní commit
`274661c63d47a1e670818446c5b57c89f3367c6a`. Původních 74 testů prošlo na Pythonu
3.14.7 a z dočasného `git archive` také na 3.12.12. Audit byl pouze softwarový/offline;
HTTP testy používaly loopback, nikoli produktové nebo referenční zdroje.

Nalezen a reprodukován problém: checkout stejného commitu s `core.autocrlf=true`
měnil LF na CRLF v protokolu, rubrice, promptech i Pythonu, čímž porušoval zmrazené
SHA-256. `.gitattributes` nyní vynucuje LF. Nová izolovaná Git-index regrese před
opravou selhala a po opravě prošla; kontroluje také zachování binárních bytes.
Nepotřebuje síť ani commit a bez Gitu se přeskočí jen tato kontrola.

Pipeline nyní výslovně porovnává všech pět výsledkových souborů včetně
`answer_metrics.csv`, s různým `PYTHONHASHSEED` a TZ. Gate fixture obsahuje skutečné
CLI skripty už před falešným G1; po každém ze dvou přesunů a odstranění původních
adresářů běží `score.py --final` a následné `freeze_protocol.py --verify` v nových
procesech mimo repo. Kontrolují se CLI výchozí cesty, shoda všech pěti výstupů,
neměnnost původních soukromých fixture souborů, provenance a odmítnutí změny zdroje.
Kritická read-only kontrola opravila izolaci Git prostředí a zachovala ověření G3
**po** replayi; re-kontrola bez zbývajících blokujících/středních nálezů.

Po opravách: **75/75 testů** na Pythonu **3.14.7 i 3.12.12**; druhý běh z nové
dočasné kopie (`git archive` vstupního commitu + aktuální diff), bez `.git` či
generovaných artefaktů původního worktree. Samostatné porovnání CLI fixtures mezi
těmito runtime verzemi dalo po bytech stejné výsledkové soubory (500 smyšlených
záznamů, 58 konečných selhání, 35 agregátů). Ověřeny i dev/val validace, relevantní
regrese, odkazy změněné dokumentace, gramatika Pythonu 3.9 (21 souborů) a
`git diff --check`. Runtime 3.9, skutečný Windows/macOS ani vzdálené CI ověřeny nebyly.

To dokládá reprodukci přípravy a analýzy uložených syntetických vstupů v testovaném
prostředí, **ne** opakovatelnost online odpovědí produktů, pravdivost referencí nebo
skutečné G1/G2/G3. Reálný autorizovaný replay vyžaduje kompletní soukromý G3 balíček;
žádné produktové běhy, nové lidské ratingy ani skutečné podpisy zde nevznikly.

## Adversariální doublecheck reprodukovatelnosti (2026-10-12)

Vstupní `main` byl čistý, `git pull --ff-only origin main` bez změn; commit
`8adf16c8ae0703894cd9e5f5fa3fa13b31d7b765`. Tři nezávislí read-only subagenti
kontrolovali přípravu/locale, adversariální replay/soukromí a adversariální scoring/G2.
Původních 75 testů prošlo, ale cílené útoky odhalily skutečné mezery:

- Float `sum` se mezi Pythonem 3.11 a 3.12 liší: stejný faux G3 na 3.11 odmítl
  přepočet G2; na hranicích se měnil i výběr P3 (0,02) a H1 (0,10). Součty metrických
  hodnot nyní používají `math.fsum`, bez změny prahů, definic nebo bootstrap RNG losování.
- Dangling výsledkový symlink mohl zapsat soukromý report do worktree. Před zápisem
  se všech sedm výsledkových jmen včetně provenance kontroluje přes `lexists`.
  Soukromé cesty nyní výslovně vyžadují absolutní tvar i při cwd mimo repo.
- Duplicitní JSON klíče v RF evidenci, manifestech, snapshotech, mapách i vstupních
  datech/blueprintu se mohly tiše přepsat. Všechny produkční JSON readers používají
  společný fail-closed hook; lazy import mapy zachovává acyklické načítání modulů.
- Raw listy neměly úplný guard RF počtů/evidence ani konečného nezáporného času
  anotace. Každý ze tří raw/final listů se nyní validuje vůči **vlastním** explicitním
  S2 párům. Odlišná nezávislá segmentace a vlastní časy hodnotitelů zůstávají povolené.
- Implicitní locale encoding rozbíjelo veřejnou kontrolu kandidátů a dekódování
  českých CLI diagnostik. Čtení/zápis těchto vstupů a zachycení CLI jsou explicitně UTF-8.

Přibylo 13 regresních testů. Cílené regrese pro duplicitní RF, raw časy, dangling
výstupy, ASCII locale a float hranice před příslušnými opravami skutečně selhaly.
Druhá kritická kontrola zachytila drobnou regresi normalizace `" s2 "` při extrakci
RF validátoru: opravena a pokryta pozitivním testem. Silný gate test přijímá raw2
vlastní odlišný S2 pár, ale odmítá RF odkaz na pár existující pouze u final/raw1.
Závěrečný kritický a adversariální re-review bez zbývajícího doloženého blockeru.

Skutečně provedené celé softwarové sady (bez přeskočených testů):

| Runtime a prostředí | Výsledek |
| --- | --- |
| Python 3.11.16, nová izolovaná `git archive HEAD` + diff kopie mimo repo | 88/88 OK, 69,433 s |
| Python 3.14.7, worktree | 88/88 OK, 62,297 s |
| Python 3.12.12, worktree, `LC_ALL=C`, UTF-8 mode/coercion vypnuté, stdout UTF-8 | 88/88 OK, 66,751 s |

Nezávislý actual-CLI replay jednoho izolovaného syntetického G3 balíčku s 500
dokončenými odpověďmi prošel na Pythonu 3.11.16, 3.12.12 i 3.14.7: všech pět
výsledkových souborů bylo byte-identických, včetně H1 přesně na hranici 0,10.
Změnily se hash seedy a TZ; hashe všech 569 původních soukromých fixture souborů
zůstaly shodné a G3 se ověřila i po každém replayi. Samostatné skutečné CLI útoky
na faux G3 s/bez mapy odmítly dangling symlink **před zápisem** a duplicitní manifest
i mapu; všech 27 private a 29 repo fixture souborů zůstalo beze změny.

Ověřeny veřejné dev/val (3.14 i 3.12 ASCII locale), 7 CLI `--help`, 14 lokálních
dokumentačních odkazů, gramatika Pythonu 3.9 (21 souborů) a `git diff --check`.
Data a prompty se neměnily. Dokumentace chrání původní pořadí řádků a přesný
zmrazený commit: staré manifesty se kvůli opravám kódu nepřepisují ani znovu nepečetí.
Runtime 3.9, Windows/macOS a vzdálené CI nebyly ověřeny. Veškerá evidence/ratingy
a schválení v testech jsou výhradně označené smyšlené fixtures mimo repo;
neproběhl benchmark, pilot, zdrojové ověřování ani skutečný podpis G1/G2/G3.

## Lokální Ruff cleanup (2026-10-12)

Výchozí `main` byl čistý; `git pull --ff-only origin main` jej posunul na
`ab31d76`. Podle původního upřesnění uživatele byl cleanup nejdřív dokončen
lokálně, bez commitu a pushe. Následně uživatel požádal o commit a push na `main`;
souběžné cizí úpravy testů do tohoto commitu nepatří. CI, dosavadní závislosti
a Python 3.14 pro prostředí `uv` zůstaly zachované; Ruff 0.16.1 přibyl jako
připnutý vývojový nástroj.

Ruff cílí na kompatibilitu Pythonu 3.9 a kontroluje chyby, importy, kompatibilní
modernizace, Bugbear, comprehensions, zjednodušení, PIE a pravidla Ruff.
Všech 21 Python souborů je sjednoceno formatterem; dlouhé literály a záměrné
Unicode symboly zůstávají zachované. Opravy zahrnují nepoužité importy/proměnné,
pojmenování, ekvivalentní konstrukce a explicitní řetězení výjimek. Nepřibyly
výjimky `noqa`; odstranily se čtyři nepotřebné `noqa: E402`. Dvě nové HTTP regrese
chrání normalizaci Unicode oddělovačů tisíců a vyloučení podpůrných citovaných
úryvků z požadavků na entity po úpravě zápisu regexů.

Před úpravami prošlo 88/88 testů na Pythonu 3.14.7. Po úpravách byly skutečně
provedeny celé sady bez přeskočených testů:

| Runtime | Výsledek |
| --- | --- |
| Python 3.14.7 | 90/90 OK, 63,296 s |
| Python 3.12.12 | 90/90 OK, 68,663 s |

Po těchto kontrolách přibyly souběžné úpravy testů mimo tento cleanup, které nebyly
přepsány ani vráceny. Aktuální sada byla znovu ověřena: **87/87 OK** na Pythonu
3.14.7 (62,239 s) i 3.12.12 (67,922 s). Python soubory se během této kontroly
nezměnily a Ruff lint i formatter nadále prošly.

Pro následný commit byl samostatně ověřen snapshot bez souběžných cizích úprav:
90/90 OK na Pythonu 3.14.7 (63,037 s) i 3.12.12 (67,355 s), Ruff lint i formatter OK.
Kritická read-only kontrola potvrdila oddělení cizích změn a zachování původních testů.

Všech pět výsledkových souborů samostatné offline syntetické pipeline bylo před
a po úpravách byte-identických. Prošly také připnuté `ruff check .` a
`ruff format --check .`, `uv lock --check --offline`, validace veřejných 20 dev
a 10 val, všech sedm CLI `--help`, `bash -n demo/run_demo.sh`, odkazy README,
gramatika Pythonu 3.9 všech 21 souborů a `git diff --check`.

Nezávislý kritický read-only subagent prošel AST rozdíly všech Python souborů,
konfiguraci, lockfile a komentáře; parserové regexy mají identické kompilované
struktury a guard G3 zachovává podmínky. Bez blokujících/středních nálezů;
nezávisle prošlo také všech šest HTTP regresí na loopbacku.
Data, prompty, schéma, metrické definice ani metodika se neměnily.
Runtime Pythonu 3.9 ani vzdálené CI ověřeny nebyly. Neproběhl benchmark, pilot,
zdrojové ověřování ani skutečný podpis G1/G2/G3.

## Co nadále provede kolega (platí i po revizi)

Nový soukromý holdout, nezávislé ověření RF/OF, dostupnost a nastavení produktů, pilot,
skutečné podpisy/archivace G1/G2/G3, dev/val výběr P3_final, produktové běhy, lidské ratingy,
výsledky a závěrečná zpráva. Dokončení čtyř přípravných etap není dokončení experimentu.
