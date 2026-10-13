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

## Dokončený doplňkový sběr (13. 10. 2026)

Celkové pokrytí nyní činí **40 různých úloh a 84 věcných odpovědí**.
Doplněk přidává 51 odpovědí: všechny zbývající veřejné dev/val otázky a
10 nových samostatných otázek. Obsahuje také jednu oddělenou náhradu
operátorské chyby; náhrada není nový případ. Autentizační text a dvě chyby bez
odpovědi jsou mimo tento počet, ale zůstávají v datech.

| Kolekce | Věcné odpovědi | Unikátní úlohy | Interpretace |
| --- | --- | --- | --- |
| Původní pilot | 33 | 8 | Historické P2, účty a podmínky zachovány |
| Doplněk | 51 | 32 | Částečně překrývající se úlohy, včetně nových promptových běhů |
| Sjednocení ID | 84 | 40 | Počet uložených odpovědí; nikoli společné produktové skóre |

Pět nových otázek má Gemini P1/P2/P3A; další tři veřejné validační otázky mají
Gemini P1/P3A a původní doplňkový P2 z jiného produktu. Tyto tři se proto
nepovažují za párové měření promptového efektu. Registry a tabulky jsou v
`runs/supplement-2026-10-13/`. Přesné prompty jsou stejné jako ve fixovaných
kopiích; P3A není původní validačně vybraný P3_final. Metoda: [](#supplement).

## Skutečně provedené pomocné AI hodnocení

Všech 33 původních odpovědí má obsahové AI posouzení. Nových 22 veřejných
otázek má kvalitativní zdrojový audit, nová oddělená sada AI kontrolu hlavních
faktů a primárních referencí. Žádná z těchto tabulek není lidský rating.

| Výsledek | Rozsah | Odhad / meze | Deskriptivní 95% interval |
| --- | --- | --- | --- |
| Pokrytí povinných faktů po odpovědích | 33 odpovědí / 8 úloh; 47/48 RF správně | 0,9848 | 0,9516–1,0000 |
| Obsahová správnost, škála 0–2 | 33 odpovědí / 8 úloh; nejisté RC a bonusy zachovány | 1,6970–1,9091 | Dolní mez: 1,4211–1,9063; horní: 1,8333–1,9706 |
| Precision, atomizovaný subset | 11 odpovědí / 3 úlohy / 87 explicitních párů | 0,7141–0,8050 | Dolní mez: 0,6000–0,8006; horní: 0,7634–0,8500 |

Dolní precision ponechává nepřístupné citace ve jmenovateli, horní představuje
možnou plnou podporu těchto neověřených vztahů. Nejde o jeden interval spolehlivosti
0,7141–0,8050. Zvlášť jsou uvedeny bootstrapové intervaly každé meze
(10 000 výběrů úloh s vracením, seed 20261013). Atomizovaný subset tvoří
CIT-004, CIT-008 a CIT-013; byl vybrán účelově a neodhadujeme z něj pořadí
produktů. Úplnost RF není citační recall. Nejistota nezahrnuje chyby AI hodnotitele.

Všech 202 původních parserových návrhů bylo AI posouzeno: 113 S2, 35 S1,
3 S0, 32 NA a 19 NONE (necitovaná tvrzení nebo UI artefakty). Žádný řádek
nezůstal REVIEW_PENDING. Není to hlavní atomická segmentace celého pilotu;
původní parserové řádky i audit dělení zůstaly uchované.

Nejvýznamnější nové nálezy: chybný článek Ústavy při správném věku, rozhlasový
zdroj bez uvedené přesnosti výšky, nesoulad nativních značek Gemini se seznamem
zdrojů a nedoložené stáří publikace u CIT-015. Nečitelný zdroj je NA, nikoli FAB.
Podklady: `results/ai-review-2026-10-13/`, kolekční AI review v `runs/supplement-2026-10-13/`.

H1/H2 se nepotvrzují: chybí úplná párová matice a skutečné lidské hodnocení.
Přístupové limity a rozdílné konfigurace se zachovávají, jejich dopad se nezakrývá.
