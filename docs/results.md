(results)=
# Výsledky skutečného pilotu

Pilot zachytil odpovědi čtyř produktů a přístupové omezení pátého, a poskytl první
pozorování chyb citací. Je to **provozní a kvalitativní výsledek na malém vzorku**, ne odhad citační přesnosti
produktů. Originály (text, HTML, snímek, metadata, SHA-256) jsou v `runs/pilot-2026-10-12/` a
`runs/pilot-2026-10-13/`, souhrn řádků v `results/pilot/run_summary.csv`.


:::{important} Výsledky v kostce
- **33 skutečných odpovědí** na **8 úloh** od **4 odpovídajících produktů**; pátý měl přístupové omezení, každá uložená s textem, HTML, snímkem a SHA-256.
- **95,8 %** (23 z 24) odeslaných prvních pokusů rozšířeného pilotu skončilo odpovědí, bez jediného opakování.
- **183 citovaných dvojic** tvrzení–zdroj z 31 odpovědí zpracováno parserem, **59 unikátních URL** zkontrolováno.
- **Pět konkrétních nálezů** o chybách citací, přiznání nejistoty a věrnosti exportu ([](#error-analysis)).
- Orientační proxy podpory citací: **0,49–0,76** podle produktu (předběžné, bez lidských ratingů).
- **Rozsah:** finální citační přesnost a testy hypotéz nejsou součástí této verze (omezený čas a rozpočet), viz [](#limits).
:::

## Rozsah

| Sběr | Úlohy | Odpovědi | Poznámka |
| --- | --- | --- | --- |
| Původní pilot (12. 10.) | CIT-001, CIT-020 | 10 | 8 odpovědí (ChatGPT, Gemini, Grok, Perplexity) + 2 z původního anonymního pilotu; Claude: limit |
| Rozšířený pilot (13. 10.) | CIT-003, 004, 005, 008, 012, 013 | 23 z 24 odeslaných | Úlohy zvoleny před odesláním, všechny v P2; 6 řádků Claude neodesláno |
| **Celkem** | **8 unikátních úloh** | **33** | Kolekce se neslučují do jednoho skóre |

Šest úloh rozšířeného pilotu bylo určeno před odesláním. Pilot je navíc před zmrazením protokolu a do budoucí analytické
sady se nepřebírá. Sběr probíhal v Chromu v nových chatech v režimu bez paměti na existujících účtech.

```{figure} figures/pilot-outcomes.svg
:label: fig-outcomes
:alt: Dokončené odpovědi, selhání a neodeslané řádky podle produktu
:width: 95%

Výsledek všech řádků pilotu podle produktu (data: `results/pilot/operational_summary.csv`).
```

## Provozní výsledky

| Produkt | Rozšířený pilot: dokončeno / odesláno | Pozorování |
| --- | --- | --- |
| ChatGPT | 5 / 6 | 1 selhání: chyba načtení odpovědi CIT-004; částečný výstup zachován |
| Gemini | 6 / 6 | — |
| Grok | 6 / 6 | Po přístupovém ověření pokračoval původní požadavek, bez nového pokusu |
| Perplexity | 6 / 6 | Citace sdružené pod „+N" |
| Claude | 0 / 0 | Limit využití; 6 řádků neodesláno (v původním pilotu 1 odeslaný pokus skončil limitem) |

To je **23 dokončených odpovědí z 24 odeslaných prvních pokusů (95,8 %)**; žádný požadavek nebyl opakován,
takže úspěšnost na první a konečný pokus je shodná. Neodeslaný řádek není selhání. Latence jsou horní meze
(zahrnují polling a zachycení), na žebříček rychlosti nestačí. Náklady, tokeny a kredity, které rozhraní nezobrazilo, jsou *unknown*.

Zachycené nastavení: ChatGPT GPT-6 (střední), Gemini 3.6 Flash (Plus), Grok Fast, Perplexity výchozí Search,
Claude Opus 5.5 (Medium). Účty a tarify se liší; homogenita účtů není ověřena a je zachována jako odchylka.

## Pozorování k citacím

Perplexity: 6 odpovědí rozšířeného pilotu obsahovalo **44 citačních skupin a 57 zdrojových vazeb**, které
jsme museli zachytit z původních karuselů rozhraní. Parser připravil **148 anotačních řádků** a 15 necitovaných tvrzení;
HTTP kontroly 49 unikátních URL. Automatický stav URL neprokazuje podporu ani pravdivost.

Hlavní kvalitativní nálezy (úplný rozbor v [](#error-analysis)):

- **Rozpor DOI (CIT-001, Perplexity):** inline odkaz `NEJMoa2200674` ≠ seznam `NEJMoa2034577`; správných 95 % rozpor neodstraňuje. Zachováno beze změny.
- **Přiznání nejistoty (CIT-020):** odlišené narození / křest / tradice místo jednoho čísla.
- **Rozdílné hodnoty (CIT-004):** 1 603,296 m vs. 1 602 m vysvětleno trigonometrickým bodem; dobrovolné doplňky však přidaly tvrzení vyžadující vlastní ověření.
- **Chybný předpoklad (CIT-008):** ChatGPT opravil věk kandidáta do Senátu z 35 na 40 let a rozlišil Sněmovnu; Perplexity přisoudil hranici jinému článku Ústavy.

## Orientační agregované metriky (bez lidských ratingů)

Z dat v repozitáři lze spočítat provozní čísla a **lexikální proxy podpory**. Proxy není hodnocení S2: pro každou
citovanou dvojici ověřuje, zda stažená stránka obsahuje klíčová čísla (případně delší slova) z tvrzení. Nečte význam,
podporu spíše nadhodnocuje a stránky nečitelné prostým HTTP (403, JavaScript) vykazuje zvlášť jako *nečitelné*, ne jako nepodpořené.
Slouží jako **předběžný odhad, který nenahrazuje lidské ratingy ani hlavní metriku**.

:::{table} Orientační metriky pilotu podle produktu (31 odpovědí z listů pro hodnotitele)
:label: tbl-proxy

| Produkt | Odpovědi | Medián latence | Citované dvojice | Proxy: podpořeno / nečitelné | Podíl (všechny / čitelné) |
| --- | --- | --- | --- | --- | --- |
| ChatGPT | 8 | 12,8 s | 37 | 28 / 5 | 0,76 / 0,88 |
| Gemini | 8 | 10,2 s | 49 | 24 / 14 | 0,49 / 0,69 |
| Grok | 8 | 31,8 s | 51 | 33 / 5 | 0,65 / 0,72 |
| Perplexity | 7 | 9,6 s | 46 | 29 / 5 | 0,63 / 0,71 |
| Claude | 0 | – | – | – | – |
:::

```{figure} figures/pilot-proxy.svg
:label: fig-proxy
:alt: Orientační podpora citací podle produktu
:width: 95%

Podíl citovaných dvojic, jejichž klíčová čísla nebo slova lze najít na citované stránce (lexikální proxy, předběžné).
```

Jak to číst: u každého produktu zůstala zhruba čtvrtina až polovina citací lexikálně nepotvrzena (včetně nečitelných stránek), což potvrzuje, že odkaz bez kontroly nestačí. U Gemini je velká část stránek (14 z 49) strojově nečitelná, takže nižší podíl nelze číst jako horší citace. Rozdíly jsou na 7–8 odpovědích
a bez intervalů; **pořadí produktů z nich nevyvozujeme**. Latence jsou horní meze (včetně pollingu a zachycení); medián je robustnější než p90, které ovlivnily
jednotlivé extrémy (až 1 211 s u Groku). Claude nemá žádnou dokončenou odpověď. Výpočet je reprodukovatelný skriptem
`analysis/pilot_proxy.py`, výstup je v `results/pilot/pilot_metrics.csv`. Skutečná citační přesnost bude podíl lidských hodnocení S2.

## Aktuální sjednocené pokrytí

Celkem je **40 různých úloh, 93 uložených věcných odpovědí a 92
způsobilých podkladů pro hodnocení**. Rozdíl jedné odpovědi je původní operátorský
export SUP-H002/P2; jeho náhrada je započítaná jednou. Čtyři chybné clipboard
exporty byly věrně obnoveny z původního AX a snímku, nikoli znovu vygenerované.
Autentizační odmítnutí, časová selhání a neodeslané plány zůstávají v registru.

| Část | Věcné odpovědi | Unikátní úlohy | Význam |
| --- | --- | --- | --- |
| Původní pilot | 33 | 8 | Historické P2 |
| Doplňkový sběr a dokončování | 60 | 32 | Další veřejné otázky a 10 nových otázek |
| Celkem | 93 uložených / 92 způsobilých | 40 | Žádný společný produktový žebříček |

Gemini má 9 úplných tripletů na SUP-H001–009. Další tři veřejné otázky
mají P1/P3A na Gemini a P2 od jiného produktu, proto nejsou párovým měřením
promptového efektu. Poslední sběr uchovává skutečné přístupové/časové chyby;
operator-capture intervaly se nevydávají za generační latenci. Registr:
`runs/canonical-2026-10-13/registry.jsonl`, součty `coverage.json`.

## Opravený pomocný AI audit, verze 2

Obsahové posouzení zahrnuje všech 33 původních odpovědí. Atomizovaná citační
metrika se týká pouze 11 dokončených odpovědí na 3 účelově vybraných úlohách.
V1 je historická verze; pro aktuální čísla se používá v2. Přesně citované stránky
byly znovu kontrolované. Zrcadlo lze použít jen po doložení totožnosti dokumentu;
jiný správný zdroj nemůže opravit chybnou původní citaci.

| Výsledek | Rozsah | Odhad / meze | Deskriptivní 95% interval |
| --- | --- | --- | --- |
| Pokrytí RF po odpovědích | 33 odpovědí / 8 úloh; 47/48 RF | 0,9848 | 0,9516–1,0000 |
| Obsahová správnost 0–2 | 33 odpovědí / 8 úloh; nejisté RC zachovány | 1,8182–1,8788 | Dolní mez 1,7419–1,9032; horní 1,8056–1,9667 |
| Precision, dokončený atomizovaný subset | 11 odpovědí / 3 úlohy / 99 explicitních párů | 0,7954 | 0,7265–0,8433 |
| Precision, terminální selhání = 0 | 12 prvních pokusů / stejné 3 úlohy | 0.7291 | 0.6175–0.8433 |

Explicitní páry: **78 S2, 1 S1, 20 S0, 0 NA**. Všechny faktické jednotky zahrnují
úvod, závěr a dobrovolné doplňky; podpůrné citované úryvky nejsou nová tvrzení.
Počty jednotek závisejí na lidské kontrole segmentace. Subset tvoří CIT-004,
CIT-008 a CIT-013. Dokončený subset vynechává selhání ChatGPT/CIT-004; proto je
uvedena i samostatná verze s nulou za tento pokus, v souladu s protokolem.

Bootstrap: 10 000 výběrů celých úloh s vracením, seed 20261013. Tři klastry mají
hrubé diskrétní rozdělení; interval je popis tohoto subsetu, nezahrnuje chyby AI
hodnotitele ani nezávislou lidskou shodu. Úplnost RF není citační recall.
Žádné z těchto čísel není finální G3 skóre ani potvrzení H1/H2.

Podklady: `results/ai-review-2026-10-13-v2/`. Doplňkový audit zachovává nativní
značky, přesné href a neznámé vazby. Nestandardní formát sám o sobě neznamená
nepodporující zdroj; chybějící přiřazení se nesmí doplnit domněnkou.

## Obsah doplňkových promptových běhů

Na deseti SUP otázkách má Gemini 30 podmínek: **29 dokončených odpovědí a jedno
terminální selhání P1**. Aktivní P2 pro SUP-H002 je jeho doložená náhrada.
AI porovnání s referencí našlo v dokončených odpovědích správný obsah 52/52 RF.
Při zahrnutí selhání je mikro pokrytí 52/54 = 0,9630 a makro po podmínkách
29/30 = 0,9667. To měří obsah povinných faktů, **nikoli jejich citační podporu**
a nikoli plnou správnost zahrnující RC a dobrovolné údaje.

P3A má také konkrétní vady: SUP-H007 uvádí chybné datum dokumentu, SUP-H008
obsahuje 30slovný úryvek při limitu 25 a SUP-H010 má neověřenou oporu na
přesně uvedené URL. Nativní doménové značky ani telemetry se nepovažují za
zachycený cílový odkaz. Pro doplněk proto **citační precision není spočítaná**.
Podklady: `results/ai-review-2026-10-13-v2/supplement/`.

## Podklady pro skutečné lidi

Zaslepený export má 92 odpovědí, prázdné ratingy a oddělený privátní klíč.
Druhý hodnotitel pokrývá ≥25 % v každém stratu. Každý musí nezávisle zkontrolovat
celou odpověď, RF/RC, atomizaci a původní přiřazení zdroje. Postup [](#human-handoff).
