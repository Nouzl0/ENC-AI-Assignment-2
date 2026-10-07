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

## Co nadále provede kolega (platí i po revizi)

Nový soukromý holdout, nezávislé ověření RF/OF, dostupnost a nastavení produktů, pilot,
skutečné podpisy/archivace G1/G2/G3, dev/val výběr P3_final, produktové běhy, lidské ratingy,
výsledky a závěrečná zpráva. Dokončení čtyř přípravných etap není dokončení experimentu.
