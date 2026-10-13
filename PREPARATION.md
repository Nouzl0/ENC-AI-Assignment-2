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

## 12. 10. 2026 – skutečný pilot a export do projektu

Uživatel autorizoval reálný sběr v Avast Secure Browser a přenos runů do tohoto
projektu. Export obsahuje 2původní anonymní a 8 nových skutečných odpovědí, tedy
10 odpovědí na 2 unikátní úlohy P2. Originály se nepřepisovaly; zachovány raw text/HTML,
metadata, první exporty, snímky, provozní audit a SHA-256. Perplexity sdružené
citace byly věrně rozbaleny z původních UI karuselů s auditovanou normalizací v2.
Zbytek soukromé složky (browser queue, osobní ověření/profily, klíč, holdout) se nepublikuje.

Připraveny dva stejné zaslepené listy pro 8 nových odpovědí, parser 54 řádků / 3 necitovaná
tvrzení a skutečné HTTP kontroly 11 unikátních URL. Listy nejsou vyplněné. Komentář
týmu v první osobě je výslovně návrh AI pro následnou úpravu autorů, nikoli provedené
lidské hodnocení. Claude měl vyčerpaný limit; jeho pokus zůstává auditní evidencí.

René potvrzen jako správce testu/reference a hodnotitel, Jan jako autor promptu
a hodnotitel. Operátor uchovává klíč/auto nápovědy odděleně od obou lidí. Po čtení
soukromých kandidátů nesmí dále navrhovat nebo ladit P3. Soukromý AI návrh 10 nových
případů splňuje schéma a kvóty; čeká na Reného lidské ověření. Read-only AI kontrola
primárních zdrojů odhalila a napravila nepřesnosti dev/val, další mezery jsou přiznané
v docs/source-audit.md. Hashy 89 zdrojových snapshotů byly ověřeny, nejde o lidské ověření faktů.

Kritický read-only reviewer ověřil všech 58 prvotních exportních hashů/velikostí, prázdné ratingy
a nepřítomnost osobních údajů/klíče/holdoutu; prohlédl 11 snímků. Operátor následně
přidal 3 nové snímky a 3 časové doklady, celkem 64 artefaktů; ořezání a částečné
snímky jsou přiznané. Každý nový hash ověřen. Report po opravách
jasně uvádí 2 unikátní úlohy a dosud nesplněný požadavek analýzy ≥8 úloh.

Kontroly: WSL Python 3.12.3, **87 unittestů OK (119,324 s)**; veřejný validátor OK;
Ruff 0.16.1 check a format --check OK; git diff --check OK. MyST PDF sestavené přes
uv/mystmd 1.11.0 a Typst 0.15.1, 28 stran, text bez náhradních znaků a DOPLNIT.
PDF/obrázky mají výslovné binární Git atributy; zabráněno převodu jejich bytes na LF.
Vzdálené CI nebylo ověřeno: GitHub connector pro tento privátní repozitář vrátil 404.
Softwarové syntetické fixture výsledky nejsou benchmarkovými výsledky.

G1/G2/G3, skutečné lidské ratingy, P3_final a analytické dev/val/test/repeat běhy
zatím nejsou dokončené; nebylo předstíráno score --final ani kompletní assignment.


## 13. 10. 2026 – rozšířený skutečný pilot a osm případů

Před novými odpověďmi byl zaznamenán samostatný pre-G1 plán na šesti dalších
veřejných dev úlohách v P2 (SCOPE + původní plán + immutable manifest).
V dostupných produktech skutečně odesláno 24 prvních požadavků: 23 completed,
1 failed/tool_error (ChatGPT CIT-004), 6 Claude řádků neodesláno kvůli známému
limitu. Originální partial chybového výstupu je uchován; terminální metadata
137,738 s jsou opravená s auditem a oddělená od partial capture 18,878 s.
U Perplexity CIT-008 se po hotové odpovědi nezdařila kamera skryté stránky;
původní text/HTML a probe zůstaly uložené, pozorování dokončení 17,625 s bylo
obnoveno bez nového cloudového požadavku. Focus emulation se použila pouze
po odpovědi pro snímek/čtení skutečných karuselů, potom obnovila původní stav.
Původní uživatelské karty zůstaly otevřené; uzavřené byly jen nové operátorem
vytvořené karty po zachycení, aby se uvolnily prostředky. Vyřízená stará CDP
queue byla archivována soukromě, bez přehrávání původních mutací.

Export do projektu má 183 byte-identických artefaktů. Původní kolekce 64
artefaktů se nemění. Dohromady 33 odpovědí na osm unikátních úloh; summary má
42 řádků včetně 2 skutečných selhání a 7 neodeslaných řádků. Šest Perplexity
výstupů zachovává 44 původních skupin a 57 skutečných zdrojových vazeb v
normalizaci v2, v1/raw se nemění. Parser připravil 23 zaslepených odpovědí a
148 řádků, 15 necitovaných tvrzení a HTTP kontroly 49 unikátních URL. Oba lidé
mají totožné prázdné listy pro všech 23 odpovědí; pojmenované originály v Git
omezují zaslepení pilotu. Nejde o provedené ratingy. Klíč, nápovědy, queue,
přístupové údaje, nesouvisející historie, zdrojové články a holdout se nepublikují.

Uživatelem popsaný smíšený názor Reného a příznivější názor Jana jsou rozepsané
v první osobě jako návrhy k revizi. Pomocná AI kontrola osmi veřejných úloh má
skutečné primární snapshoty, čas a hash; není vydávána za lidskou verifikaci.
René má soukromý review-before-G1-v1 s konkrétně připraveným návrhem branové
konfigurace; podpis/čas jsou prázdné a všechna potvrzení false. G1 se na něm
správně odmítne. Nezmrazený protokol opravuje rozpory držitele klíče: klíč i
auto kontroly má nehodnotící operátor, René jako správce je zároveň plánovaný rater.

Kritický read-only reviewer ověřil všech 183 nových i 64 starých hashů/velikostí,
30 immutable řádků a 24 submission hashů, blank ratingy bez nápověd, šest
normalizačních auditů a osm rizikových snímků bez účtů/historie. Opraveny summary
odkazy neodeslaných Claude řádků. Přidán konkrétní negativní protipříklad
Perplexity CIT-008: 40 let s nesprávným čl. 16 odst. 2 namísto 19 odst. 2,
proti správné opravě ChatGPT; originál zůstává zachovaný. Analýza má osm různých
úloh s pozitivními i negativními příklady a provozním selháním.

Kontroly: WSL Python 3.12.3, 87 unittestů OK (262,960 s), veřejný validátor OK,
Ruff check + format --check OK (60 souborů), git diff --check OK. MyST/Typst
pracovní PDF sestavené, 32 stran, bez DOPLNIT a náhradních znaků; zdroje i PDF
zůstávají v projektu. Upstream upozornění Typst na latinské číslování nebrání
sestavení. Vzdálené CI není potvrzené. Syntetické testové skóre se nepublikuje
jako experiment. Finální analytická matice, G1/G2/G3, lidské ratingy a P3_final
zůstávají nedokončené; nepředstíráme splnění celého assignmentu.


## 13. 10. 2026 – doplňkový sběr a AI audit

Na výslovný pokyn uživatele paralelní sběr ve třech subagentech a kořenovém agentu: 51 nových věcných odpovědí, celkem40 různých úloh/84odpovědí. P1/P2/P3A stejného Gemini na5nových úlohách. Původní pilot/humanlisty neměněné. Atomizovaný AI subset11odpovědí, obsahový AI audit33pilotních a novézdrojové review. Žádné fiktivní ratingy, podpisy nebo G3. Aktualizované odevzdávací dokumenty a PDF. Testy, lint, původní validátor ani vzdálenéCI nebyly na přání uživatele spuštěny.

## 13. 10. 2026 – auditovaný sběr, opravy a skutečné lidské podklady

Kanonický registr má 116 řádků (včetně 15 neodeslaných plánů), 93 uložených
věcných odpovědí / 92 způsobilých podkladů na 40 úlohách. Poslední sběr přidal
9 skutečných odpovědí a uchoval 3 selhání i jediné povolené retry. Gemini SUP
matice má 29 dokončených podmínek a 1 terminální chybu, 9 úplných tripletů.
Čtyři clipboard chyby obnovené z původního AX/PNG, originály neměněné.

Nové CLI supplement_review.py a verify_exploratory.py ověřují hashy/promptové
vazby, zvláštní identitu collection/run_id, zaslepené listy a Git bytes. RUN_DAY
se pro lidský časový kontext řeší pouze z aware startu v UTC, ne odhadem. V3
human export má 92/27 odpovědí a 559/167 návrhů párů, přesně ceil(25 %) po
11 stratech; ratingy jsou prázdné, překryvy totožné a 124 zaznamenaných href
zachované. Původní případové soubory beze změny, klíč zůstává mimo Git.

Opravený AI audit v2: obsah všech 33 pilotních odpovědí, citační subset
CIT-004/008/013 s 11 dokončenými odpověďmi, 99 explicitními páry a precision
0,7954; samostatně 12 prvních pokusů se selháním jako nulou, precision 0,7291.
SUP RF obsah 52/52 ve 29 dokončených podmínkách není citační podpora RF.
Telemetry URL zůstávají soukromé hypotézy; nativní značky bez zachycených cílů
nejsou dodatečně označené S2/S0. Plné copyrighted snapshoty se nepublikují.

Kontroly: všech 114 softwarových testů prošlo na Pythonu 3.14.8 (82,654 s);
Ruff 0.16.1, formát, veřejný dev/val validátor a diff check prošly. Diskový
peer audit ověřil 116 záznamů a 403 unikátních registrovaných souborů.
Typst/MyST sestaví aktuální zprávu a worksheet; jejich vykreslené stránky byly
zkontrolované a přetékající tabulkové položky opravené. Přesné staged/Git
hash kontroly jsou součástí závěrečného commitu. Vzdálené CI netvrdíme.

Skutečné lidské ratingy, nezávislé reference, úplná produktová matice, validační
P3_final a G1/G2/G3 nejsou vyrobené ani zpětně schválené. Nové pokyny pro tým
jsou bez jmen; zajišťují nezávislé hodnocení před diskusí o neshodách.


## Dostupná adresa projektu a PDF odkazy (13. 10. 2026)

Aktivní gh účet má právo WRITE do `Nouzl0/ENC-AI-Assignment-2`; stará adresa
`Nouzl0/ENC-AI-Project` vracela 404. Historie main se shodovala s lokálním
rodičem 5671247, origin byl opraven a audit ee336d7 úspěšně odeslán.

Aktualizovaná zpráva a worksheet používají tuto dostupnou adresu. Šablona
Typst odstraňuje escapování `_` a `&` pouze z exportovaných hypertextových
cílů a převádí odkazy na kapitoly na vnitřní PDF cíle; samostatný worksheet
odkazuje na další dokumenty v GitHubu. Původní měření, jejich URL a ratingy
se neměnily. Dva chybně vysázené symboly ve zdrojovém auditu nahrazuje text.

Oba PDF exporty prošly sestavením: zpráva 23 stran, worksheet 13. Kontrola
PDF anotací ověřila 50 externích URI a 26 platných vnitřních cílů zprávy,
10 externích URI worksheetu a žádné zbylé escapované či relativní webové cíle.
Viditelný text se změnil jen na stranách 1 a 21 zprávy a 11 worksheetu;
tyto strany prošly vizuální kontrolou. `git diff --check` prošel. Dřívějších
114 lokálních softwarových testů zůstává výsledkem předchozí etapy;
kvůli těmto dokumentačním opravám se celá sada znovu nespouštěla.
