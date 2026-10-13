(results)=
# Výsledky skutečného pilotu

Pilot ověřil, že lze od všech pěti produktů získat věrně uložené odpovědi včetně citací, a poskytl první
pozorování chyb citací. Je to **provozní a kvalitativní výsledek na malém vzorku**, ne odhad citační přesnosti
produktů. Originály (text, HTML, snímek, metadata, SHA-256) jsou v `runs/pilot-2026-10-12/` a
`runs/pilot-2026-10-13/`, souhrn řádků v `results/pilot/run_summary.csv`.


:::{important} Výsledky v kostce
- **33 skutečných odpovědí** na **8 úloh** od **5 produktů**, každá uložená s textem, HTML, snímkem a SHA-256.
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