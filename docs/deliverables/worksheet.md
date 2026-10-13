---
title: AI Student worksheet - správnost citací
authors:
  - name: Tým ENC-AI
parts:
  abstract: >
    Pracovní odevzdávací worksheet: 40 různých měřených úloh, 93 uložených věcných odpovědí,
    oddělené AI hodnocení. Plná produktová matice a skutečná lidská složka
    zůstávají nedokončené; původní G1/G2/G3 se netvrdí.
exports:
  - format: pdf
    template: ../templates/lapreprint-typst
    output: worksheet.pdf
    kind: "CZAI Assignment 1"
    short_citation: "Tým ENC-AI"
---

# AI Student worksheet

**Verze: pracovní odevzdávací podklady (13. 10. 2026), pilot a označený doplněk.** Worksheet obsahuje skutečně změřené hodnoty z pilotu
(33 odpovědí, 8 úloh), doplněné o 60 dalších odpovědí; celkové pokrytí je 40 různých úloh a 93 uložených věcných odpovědí. Pole označená **Nevyhodnoceno** se týkají analytických běhů, které se kvůli omezenému času a rozpočtu
na využití produktů a AI agentů nestihly; hodnoty se neodhadují. Zdroj pravdy je [PROTOCOL.md](https://github.com/Nouzl0/ENC-AI-Assignment-2/blob/main/PROTOCOL.md).

## A. Project identity

**Project title:** Správnost citací AI asistentů s webovým vyhledáváním

**Team:** Tým ENC-AI (Mendelova univerzita v Brně, Provozně ekonomická fakulta)

**Roles:** Správce dat: správce skrytého testu, nezávislý ověřovatel referencí a hodnotitel; Autor promptu: autor promptu a hodnotitel (potvrzeno uživatelem 12. 10. 2026). Nový operátor: `codex-ui-2026-10-12`, AI agent ovládající chrome. Autor promptu před G2 nedostává obsah testu. Přiřazení role není provedený rating ani podpis brány. Viz [plan.md](../plan.md).

**Primary track:**

- **Ne:** Směr A: řízený text
- **Ano:** Směr B: výzkum podložený zdroji
- **Ne:** Směr C: vícejazyčné a regionální fungování
- **Ne:** Programování a agentní systémy
- **Ne:** Jiný

**Project scope:**

- **Ano:** Jedna schopnost: správnost a úplnost citací na úrovni tvrzení
- **Ano:** Návrh porovnání pěti produktů jako kompletních systémů, běžný chat s webovým vyhledáváním, bez Deep Research; skutečné účty nemají shodný tarif
- **Ne:** Dokončené měření 40 různých faktických úloh se všemi třemi promptovými podmínkami napříč zahrnutými produkty

**Worksheet version and date:** v0.3 (auditované podklady pro lidské hodnocení), 2026-10-13

---

## B. Research question

**Primary research question:** Jak často citovaný zdroj skutečně podporuje tvrzení, ke kterému ho asistent připojil (citační přesnost), u pěti AI asistentů s webovým vyhledáváním (ChatGPT, Gemini, Claude, Perplexity, Grok) na 40 faktických rešeršních dotazech v češtině a angličtině z pěti oblastí a o kolik ji mění strukturovaný a obecně optimalizovaný prompt?

**Capability being measured:** Správnost a úplnost citací na úrovni tvrzení (podporuje citovaný zdroj tvrzení?). Porovnáváme produkty jako celky (model + vyhledávání + rozhraní), ne samotné jazykové modely.

**Primary hypothesis (H1):** Za podmínek jednotného protokolu webového výzkumu (nový chat bez paměti, výchozí vyhledávací režim, strukturovaný prompt P2, stejný dotaz tentýž den) dosáhne předem zvolený focus produkt (výchozí Perplexity) bodového odhadu citační přesnosti alespoň o 0,10 vyšší než průměr ostatních zahrnutých produktů, protože hypoteticky lépe propojuje vyhledané pasáže s citovanými tvrzeními. Hypotézu budeme považovat za podpořenou pouze tehdy, pokud je dolní mez 95% párového bootstrapového intervalu rozdílu na testovací sadě držené stranou větší než 0. Mechanismus je hypotéza, ne ověřená vlastnost produktu.

Vedlejší hypotéza H2: strukturovaný prompt P2 zvýší přesnost oproti P1 v průměru napříč systémy alespoň o 0,05, dolní mez CI bude větší než 0 a kladný odhad bude u alespoň 4 z 5 produktů (3 ze 4).

**Alternative explanation:** A1: systém má vyšší přesnost jen proto, že tvrdí méně a obecněji nebo cituje méně. Kontrola: vždy vykazujeme úplnost, počet tvrzení a citací na odpověď a pokrytí požadovaných faktů. A2: rozdíl způsobuje dostupnost zdrojů a jazyk, ne kvalita přiřazení (kontrola přes hodnocení NA a výsledky podle jazyka). A3: zisk P2 odráží změnu formátu a atribuce, ne lepší vyhledávání (kontrola přes podíl odpovědí s explicitní citací a podmíněnou přesnost).

**What result would challenge our hypothesis?** Rozdíl focus produktu a ostatních pod 0,10, nebo dolní mez CI nejvýše 0, nebo rozdíl, který se neobjeví na testovací sadě držené stranou. Totéž pro H2 s prahem 0,05 a požadavkem na 4 z 5 produktů. U H1 také situace, kdy vyšší přesnost doprovází výrazně nižší úplnost a počet tvrzení (podpora alternativy A1).

---

## C. Measurement target

**Operational definition:** Dvojice tvrzení–citace je explicitní, pokud systém připojil zdroj ke konkrétnímu tvrzení (značka [n] nebo odkaz). Člověk hodnotí dvojici S2 (plně podpořeno), S1 (částečně), S0 (nepodpořeno nebo v rozporu), NA (zdroj nedostupný), FAB (zdroj neexistuje). Hlavní metrika je podíl explicitních S2 dvojic na odpověď.

**Unit of analysis:**

- **Ano:** Odpověď (průměr přes úlohy prvního běhu je agregace metriky)
- **Ano:** Dvojice tvrzení–citace (základ hodnocení)
- **Ano:** Faktické tvrzení (základ úplnosti)
- **Ano:** Úloha (klastr pro bootstrap a váha v průměru)
- **Ano:** Systém × podmínka (úroveň porovnání)
- **Ne:** Sada úloh jako celek
- **Ne:** Jiné

**Primary metric:** Přesnost explicitní atribuce = explicitní S2 dvojice / všechny explicitní dvojice odpovědi. Bez explicitních citací je hodnota 0. NA a FAB zůstávají ve jmenovateli. Vedlejší metriky: úplnost citací (tvrzení s alespoň jednou explicitní S2 citací / všechna faktická tvrzení celé odpovědi) a správnost odpovědi (rubrika 0–2, podíl odpovědí se skóre 2).

**Why is it valid?** Měří přesně to, co uživatel při rešerši předpokládá: že citace podporuje tvrzení, u kterého stojí. Opírá se o lidské posouzení obsahu zdroje, ne o pouhou dostupnost URL. Nepodporující citace vytváří falešnou důvěru, protože uživatelé citace často neotevřou.

**What important quality dimension does it fail to capture?** Pravdivost odpovědi jako celku. S2 dokládá atribuci, ne pravdu: zdroj může tvrzení podporovat a přitom být chybný. Neměří ani užitečnost a čitelnost odpovědi ani to, zda systém zvolil relevantní tvrzení. Pravdivost částečně pokrývá doplňková metrika správnosti.

---

## D. Systems and conditions

| System | Interface/API | Visible model/version | Tools enabled | Prompt adaptations | Date tested |
| --- | --- | --- | --- | --- | --- |
| ChatGPT | Webové rozhraní, Temporary chat (bez personalizace) | GPT-6, uvažování Střední | Search vynucen nástrojem; Deep research vyloučen | Žádné (cíl 0) | 12.–13. 10. 2026 (pilot) |
| Gemini | Webové rozhraní, Temporary chat | 3.6 Flash (tarif Plus) | Vyhledávání automaticky; Deep Research vyloučen | Žádné (cíl 0) | 12.–13. 10. 2026 (pilot) |
| Claude | Webové rozhraní, Incognito chat | Opus 5.5 Medium (bez odpovědi: limit) | Web search; Research vyloučen | Žádné (cíl 0) | 12.–13. 10. 2026 (pilot) |
| Claude Code | **Nezahrnut:** nástroj pro programování a agentní systémy, mimo směr B | – | – | – | – |
| Grok | Webové rozhraní, Private Chat | Fast (podkladový model neznámý) | Automaticky web a X; DeepSearch vyloučen | Žádné (cíl 0) | 12.–13. 10. 2026 (pilot) |
| Perplexity | Webové rozhraní, Incognito, režim Search | Výchozí Search, název modelu nezobrazen | Vždy Search; Research a Labs vyloučeny | Žádné (cíl 0) | 12.–13. 10. 2026 (pilot) |

Nastavení vychází z nápovědy výrobců k 29. 9. 2026. Viditelný model a datum jsou z pilotu 12.–13. 10. 2026 (Chrome); analytická konfigurace se ověří před G1.

**Comparison design:**

- **Ne:** Návrh s paritou nástrojů
- **Ano:** Návrh podle schopností produktu: každý systém používá své běžné webové vyhledávání a výsledek je výslovně porovnáním produktů
- **Ne:** Dvouvrstvý návrh (volitelné API rozšíření je jen možnost, nepočítá se do plánu)

**What cannot be made equal?** Vyhledávač, index, zobrazení citací, bezpečnostní vrstva, skryté systémové instrukce, teplota a limit výstupu, nastavení modelu v bezplatné úrovni a režim vyhledávání. Model nelze odpojit od vyhledávání a produkt od rozhraní.

**How will this limitation affect interpretation?** Rozdíly nelze připsat modelu. Závěry formulujeme jen o testovaných produktech, režimech, účtech, jazycích, oblastech a období. Neznámé hodnoty (skryté instrukce, teplota) zapisujeme jako „výchozí/neznámé", nikdy je nedomýšlíme.

---

## E. Data and test-set plan

**Total cases:** 40 skutečně měřených různých úloh: 30 veřejných dev/val a 10 nových oddělených AI vytvořených otázek. Původní pilot a doplněk jsou oddělené kolekce, nikoli kompletní původní analytická matice.

**Development cases:** 20 (CIT-001 – CIT-020)

**Validation cases:** 10 (CIT-021 – CIT-030)

**Held-out test cases:** alespoň 10. Nový soukromý holdout vytvoří nezávislý správce mimo Git. Historické CIT-031 – CIT-040 jsou veřejné kandidáty, ne skrytý test.

**Repeated-run cases:** 10 předem určených testových úloh (úsporná varianta 5), podmínka P2, běhy 2 a 3

| Stratum | Planned number | Dostupné / plánované | How selected |
| --- | --- | --- | --- |
| Ordinary (bez okrajové podmínky) | test: 5–6 z 10 | dev 11, val 6, test 6 (návrh) | Týmový účelový výběr |
| Difficult (hard) | test: 3 z 10 | dev 6, val 2, test 3 (návrh) | Podle `holdout_blueprint.json` |
| Edge or adversarial | ≥20 % v každé sadě; test: 4–5 z 10 | dev 9 (45 %), val 4 (40 %), test 4 (návrh) | Nepravdivý předpoklad, protichůdné zdroje, časové omezení, nedávná změna |
| Ambiguous or incomplete | bez samostatné kvóty | dev 3, val 2, test neevidováno | Nejednoznačné zadání a chybějící informace |
| Czech | test: 4–5 z 10 | dev 10, val 5, test 4 (návrh) | Podle blueprintu |
| English | test: 4–5 z 10 | dev 9, val 4, test 5 (návrh) | Podle blueprintu |
| Mixed language | test: 0–1 z 10 | dev 1, val 1, test 1 (návrh) | Podle blueprintu |
| Other relevant stratum: oblast | test: 2 z každé z 5 oblastí | dev 4 × 5, val 2 × 5, test 2 × 5 (návrh) | Věda a zdraví, právo, IT, ekonomika, historie a kultura |

**Data provenance:** Všechny dotazy jsou syntetické a vytvořil je tým. Ptáme se jen na veřejně dostupná fakta, bez osobních údajů, důvěrných dat a autorsky chráněných textů. U každého případu je v poli `source_or_provenance` původ a datum ověření. Datované reference u dev/val jsou návrh. Nezávislé ověření všech povinných a nepovinných faktů před G1 zatím není provedeno.

**Why is this dataset representative of the intended use?** Není reprezentativní vzorek všech uživatelských dotazů. Jde o účelový mix faktických rešeršních dotazů z pěti oblastí a obou jazyků s vědomě zvýšeným podílem realistických okrajových případů. Reprezentuje použití „najdi a dolož fakt" a nic dalšího.

**What leakage or contamination risks exist?** Veřejné CIT-031 – CIT-040 byly v Gitu a nelze je vydávat za skryté. Produkty mohou fakta znát bez vyhledávání. Autor promptu nesmí před G2 číst holdout. Kontrola překryvu ID a podobnosti otázek je jen pojistka. Správce navíc ručně kontroluje významové duplicity.

---

## F. Prompt protocol

Plné znění je v [prompts/](https://github.com/Nouzl0/ENC-AI-Assignment-2/tree/main/prompts/). Zde je české znění P1 a P2 a stav P3.

#### Common baseline prompt

```
Vyřešte níže uvedenou úlohu. Odpovězte pouze v požadovaném formátu.

Úloha:
{user_prompt}
Formát: stručná odpověď s odkazy na použité zdroje (URL).
```

#### Structured prompt

```
Jste pečlivý rešeršní asistent. Každé tvrzení dokládáte zdrojem, který jste v této konverzaci skutečně otevřeli.

Cíl: odpovězte přesně a stručně na otázku tak, aby si čtenář mohl každé tvrzení ověřit.

Otázka:
{user_prompt}

Pravidla:
1. Vyhledejte informace na webu. Necitujte zdroj, který jste neotevřeli, a nevymýšlejte URL.
2. Za každým faktickým tvrzením (číslo, datum, jméno, definice) uveďte odkaz na zdroj ve tvaru [1], [2].
3. Citujte konkrétní stránku nebo dokument, ne domovskou stránku ani výsledky vyhledávání.
4. Upřednostňujte primární a oficiální zdroje (zákon, úřad, původní studie, standard).
5. Pokud otázka obsahuje chybný předpoklad, nejprve ho opravte.
6. Pokud se zdroje liší, uveďte obě hodnoty, každou s vlastním zdrojem, a vysvětlete rozdíl.
7. Pokud otázka omezuje stáří zdrojů, použijte jen zdroje, které omezení splňují, a uveďte jejich datum.
8. Pokud spolehlivou odpověď nenajdete, napište to. Nehádejte.

Formát výstupu:
ODPOVĚĎ: 1–3 věty s přímou odpovědí.
TVRZENÍ:
T1: <jedno tvrzení> [n]
T2: <jedno tvrzení> [n]
ZDROJE:
[1] <název> – <vydavatel> – <datum vydání nebo „neuvedeno“> – <úplná URL>
JISTOTA: vysoká / střední / nízká – jedna věta proč.
```

#### Optimized prompt

```
P3_final nebyl vytvořen (omezený rozsah projektu: validační běh P2/P3 se nestihl). Vznikne jako přesná kopie vítěze mezi kandidáty
P3A (doslovný úryvek ze zdroje ≤ 25 slov ke každému tvrzení) a P3B (P3A + kontrola
tvrzení před odesláním) po validaci. Návrhy jsou v prompts/P3A_candidate_*.txt
a prompts/P3B_candidate_*.txt. Jsou to hypotézy, ne naměřená zlepšení.
```

**What remains constant?** Úloha (`{user_prompt}`), jazyk šablony (CZ/EN dvojice se stejným významem, smíšené úlohy používají českou šablonu), jedno kolo komunikace, nový chat bez paměti, stejná síť, prohlížeč a úroveň účtu, náhodné pořadí systémů a podmínek (seed 2026), stejná verze každého promptu pro všechny produkty.

**What is intentionally different?** Jen podmínka promptu: P1 (společný výchozí), P2 (role, pravidla, schéma výstupu, postup při nejistotě), P3 (obecná optimalizace P2 podle chyb na dev). Žádné úpravy specifické pro produkt (cíl 0).

**When will prompts be frozen?** P1, P2, data, rubrika a kód se zmrazí v G1 před prvním analytickým během; pilot proběhne před G1. P3 se zmrazí v G2 po validaci, před otevřením testovací sady. Po validaci už žádné další ladění.

**How will held-out cases remain protected?** Holdout vytvoří nezávislý správce dat mimo Git a autor promptu ho před G2 nevidí. Před prvním během se zapíše jeho SHA-256. Autor dostává jen výstupy z dev/val. Test se použije jednou.

---

## G. Prompt-change log

Podrobný záznam je v [prompts/CHANGELOG.md](https://github.com/Nouzl0/ENC-AI-Assignment-2/blob/main/prompts/CHANGELOG.md).

| Version | Date | Change | Evidence | Expected effect | Actual validation effect | Retained? |
| --- | --- | --- | --- | --- | --- | --- |
| v0 (P1 v1.0) | 2026-09-29 | Šablona ze zadání + věta o formátu | Povinná společná výchozí podmínka | Referenční úroveň | Neurčeno | Ano (zmrazí G1) |
| v1 (P2 v1.0) | 2026-09-29 | Role, cíl, 8 pravidel, schéma výstupu, postup při nejistotě | Návrh před měřením | Vyšší podíl explicitních a podpořených citací | Neurčeno | Ano (zmrazí G1) |
| v2 (P3-A / P3-B v0.1, v0.2) | 2026-09-29, pak přípravná revize | P3-A: doslovný úryvek ke každému tvrzení. P3-B: navíc kontrola tvrzení před odesláním | Hypotéza E2/E5. Chybí ≥3 chybné dev odpovědi, zatím nepotvrzeno | Méně citací bez opory | Bez validace | Neurčeno |
| v3 (P3_final) | nevytvořen | Přesná kopie vítěze validace (plán) | – | – | – | – |

---

## H. Evaluation plan

| Metric | Primary/secondary | Automatic/human/judge | Calculation | Calibration or validation | Limitation |
| --- | --- | --- | --- | --- | --- |
| Přesnost explicitní atribuce | Primární | Člověk (hodnocení S2–FAB) | Explicitní S2 dvojice / všechny explicitní dvojice odpovědi; průměr přes úlohy prvního běhu | Kalibrace na offline kotvách, pilot CIT-001 a CIT-020, druhý hodnotitel | S2 neznamená pravdivost odpovědi |
| Úplnost citací | Vedlejší 1 | Člověk | Tvrzení s ≥1 explicitní S2 citací / všechna faktická tvrzení celé odpovědi | Segmentace tvrzení se hodnotí zvlášť | Dělení na tvrzení je subjektivní |
| Správnost odpovědi (0–2) | Vedlejší 2 | Člověk | Podíl odpovědí se skóre 2 proti povinným faktům a požadavkům | Kalibrace, druhé hodnocení | Závisí na ověřené reference |
| Dostupnost URL, konkrétnost odkazu, shoda čísel a jmen, datum publikace, formát P2/P3 | Diagnostika | Automatická kontrola parserem | HTTP stav, příznaky, podíl nalezených entit | Porovnání s lidským hodnocením až po nezávislém ratingu | Automatika pravdivost nepotvrdí; paywall není nepodpořeno |

**Human raters:** Dva hodnotitelé. Hodnotitel 1 hodnotí všechny dokončené odpovědi. Hodnotitel 2 hodnotí předem náhodně vybraných ≥25 % v každém stratu fáze × produkt × podmínka (zaokrouhleno nahoru), přestože zadání vyžaduje 20 %. Nikdo nehodnotí vlastní běh.

**Blinding procedure:** Anotační list neukazuje název systému ani podmínku. Zaslepení je jen částečné, protože formát odpovědi může podmínku prozradit. Oba hodnotitelé dostávají stejné podklady bez automatických nápověd. Automatické kontroly zůstávají u správce.

**Response-order randomization:** Skript zamíchá odpovědi (seed 2026), aby hodnotitel neviděl odpovědi jednoho systému za sebou.

**Inter-rater agreement measure:** Cohenova kappa (S2 proti ostatním, cíl ≥ 0,6), procento shody, doplňkově pět kategorií a správnost. Při konstantní kategorii je kappa nedefinovaná, uvede se n a surová shoda. Původní nezávislé ratingy se zachovávají a každá neshoda se zapisuje do auditu.

**LLM-as-judge used?** Ano, pouze v odděleném pomocném AI hodnocení od 13. 10. 2026. Původní lidské listy zůstávají nevyplněné; nebyla naměřena shoda lidských hodnotitelů. Metoda a omezení: [supplement.md](../supplement.md).

Hlavní závěry stavíme jen na lidském hodnocení. LLM lze nanejvýš použít k předběžnému rozdělení P1 odpovědí na tvrzení, které člověk zkontroluje. Pokud se použije jako hodnotitel podpory citací, uvedeme model a verzi, rubriku, kalibrační vzorek 50 dvojic a rizika (délka odpovědi, pořadí, sebepreference).

---

## I. Failure and retry policy

**What counts as a failed run?** Běh po nejvýše jednom provozním opakování bez použitelné odpovědi kvůli chybě nástroje, limitu požadavků, časovému limitu (180 s) nebo výpadku produktu. Odmítnutí, odpověď bez citací, věcně chybná odpověď a špatný formát jsou dokončené běhy a hodnotí se.

**Are retries allowed?** Ano, jen u selhání mimo model (chyba nástroje, limit, časový limit, výpadek). Neopakuje se výstup modelu ani neplatný formát.

**Maximum retries:** 1 (u limitu požadavků do 24 hodin, u výpadku v rámci 24hodinového okna)

**How will first-attempt and eventual success be reported?** Vždy zvlášť: úspěšnost na první pokus a výsledná úspěšnost po opakování. Neúspěšný pokus se nemaže ani po úspěšném opakování. Selhaný běh má nulu hlavních metrik a zůstává v matici.

**Which product or infrastructure failures will be excluded, and why?** Vyloučeny jsou jen chyby operátora (špatný prompt, zapnutý hloubkový výzkum) s důkazem a svázaným náhradním řádkem. Důvod: chyba není vlastností produktu. Chyby evaluace (špatně zkopírovaná URL) se opravují zápisem do záznamu. Produktová selhání se nevylučují.

---

### J. Logging checklist

Checklist níže potvrzuje připravená metadata, nikoli provedení všech běhů.

- **Ano:** Produkt a viditelný název modelu
- **Ano:** Rozhraní nebo API
- **Ano:** Datum a čas s offsetem; run_day v UTC
- **Ano:** Podmínka promptu a verze s hashem SHA-256
- **Ano:** Systémová instrukce (výchozí/neznámá)
- **Ano:** Oprávnění k používání nástrojů
- **Ano:** Kontextové soubory (žádné)
- **Ano:** Teplota nebo ekvivalent (výchozí/neznámá)
- **Ano:** Maximální délka výstupu (výchozí/neznámá)
- **Ano:** Počet kol komunikace
- **Ano:** Počet volání nástrojů (zobrazených vyhledávání)
- **Ano:** Latence (první a end-to-end)
- **Ano:** Tokeny, kredity, náklady (cost_note)
- **Ano:** Opakování a selhání (`failure_type`, `retries`)
- **Ano:** Ruční zásahy (`manual_intervention`)
- **Ano:** Surový text odpovědi, normalizace a SHA-256
- **Ano:** Snímek obrazovky a odkaz na sdílení

**Storage location:** Originály zůstávají mimo Git u správce. Aktuální schválené exporty mají relativní cesty a SHA-256 v `runs/canonical-2026-10-13/`, `runs/completion-2026-10-13/` a původním doplňku. Podepsané originály se nepřepisují. Pravidlo utajeného holdoutu před G2 patří budoucímu potvrzujícímu protokolu; současné SUP otázky už jsou zveřejněné jako exploratorní doplněk.

**Anonymization and data-protection procedure:** Dotazy jsou veřejné fakty bez osobních údajů. Sběr používá existující účty a dočasné/anonymní chaty; rozdíly úrovní se evidují. Soukromé AX mohou obsahovat identifikátor přihlášeného účtu, proto zůstávají chráněné mimo export. Autorizované veřejné podklady jsou sanitizované. Klíče, původní ratingy a source snapshoty zůstávají u správce. Publikace až po G3 je pravidlo budoucího potvrzujícího experimentu; SUP je již zveřejněný doplněk s deklarovanými odchylkami, bez předstírání G1/G2/G3.

---

## K. Pilot review

**Pilot size:** Plán: CIT-001 a CIT-020 × 5 produktů = 10 odpovědí před G1. Původní sběr má dvě dokončené odpovědi CIT-001 (ChatGPT, Perplexity). Další pilotní sběr je evidován odděleně; aktuální doložené běhy jsou v [results.md](../results.md). Pilot není analytický dev.

**What failed in the pilot?** Původní přístup bez účtů: Grok vyžádal registraci, Gemini přesměroval na přihlášení, Claude neumožnil zadat dotaz. Uživatel následně zpřístupnil přihlášený Avast a jeho vzdálené ovládání. Provozní pokusy a screenshoty se zachovávají; nejsou zaměněné za selhání finálního benchmarku.

**Which cases were rewritten or removed?** Při této etapě žádné: dev/val případy a původní pilotní odpovědi zůstaly zachované.

**Which metric or rubric changes were made?** Normativní metriky a rubrika se neměnily. Dokumentace byla opravena podle PROTOCOL.md: všechna tvrzení, explicitní atribuce, oddělená opakování a zaslepené ratingy bez automatických nápověd.

**What evidence supports freezing the benchmark?** Skutečný pilot na 8 úlohách a 33 odpovědích, připravené nástroje a postup. Formální zmrazení G1 se pro omezený rozsah neprovedlo. Podmínky G1 jsou v [freeze/README.md](https://github.com/Nouzl0/ENC-AI-Assignment-2/blob/main/freeze/README.md): pilot, role, dostupnost, nezávislé reference, nový soukromý holdout, hashe.

**What remains uncertain?** Nový holdout, nezávislé ověření referencí, lidská kalibrace a G1 nebyly v rozsahu projektu dokončeny. Skutečné úrovně účtů musí být sladěné nebo odchylky deklarované před G1; V doplňku byl viditelný Flash-Lite; tarif není jednotně doložený.

---

## L. Results table

**Aktuální doplněk:** 93 uložených věcných odpovědí / 92 způsobilých podkladů / 40 úloh; 9 Gemini tripletů. Obsahový AI audit: 47/48 RF, makro 0,9848 (CI 0,9516–1,0000). Opravený atomizovaný subset v2: 11 odpovědí / 3 úlohy / 99 explicitních párů, precision 0,7954 (CI 0,7265–0,8433). S terminálním selháním jako nulou: 0.7291 / 12 pokusů. Zaslepené lidské listy jsou připravené, ratingy a shoda prázdné. Nejde o G3.

**Nevykázáno: agregovaná skóre vyžadují lidské ratingy a G3. Orientační provozní metriky a lexikální proxy podpory (nejde o rating) jsou v [results.md](../results.md) a `results/pilot/pilot_metrics.csv`.** Sloupce plné tabulky: System, Condition, N, Primary score, Interval or variation, Secondary score, Median latency, Cost, First-attempt success. Řádky: pět produktů × Baseline / Structured / Optimized (Claude Code se nehodnotí). Žádná hodnota se nevymýšlí ani nepřebírá ze syntetické ukázky.

---

### M. Error analysis

**Provedeno na pilotu (8 úloh, 33 odpovědí), viz [error-analysis.md](../error-analysis.md).** Plán pro plný experiment: nejméně 8 unikátních task_id, ideálně 12–16 odpovědí, alespoň 2 za každý systém, alespoň 3 úspěšné odpovědi a alespoň jeden případ z každého typu okrajové podmínky, s hlavním kódem chyby E1–E11. Postup a šablona jsou v [analysis/README.md](https://github.com/Nouzl0/ENC-AI-Assignment-2/blob/main/analysis/README.md).

**Most frequent error:** Nelze určit; pilot nemá lidské ratingy ani četnosti kódů. Pozorováno: nesoulad inline odkazu a seznamu zdrojů (CIT-001) a nadbytečná tvrzení nad referencí (CIT-004).

**Most consequential error:** Předběžně záměna zdroje u tvrzení (CIT-001, CIT-008), protože čtenář ji při běžném čtení nezachytí; k potvrzení lidským hodnocením.

**Did optimization change the error distribution?** Exploratorní P3A byl skutečně měřen: Gemini má 9 úplných tripletů a poslední triplet s terminálním selháním P1. Citační precision doplňku vyžaduje dokončení vazeb a lidské ratingy; úplná produktová matice ani validační výběr P3_final neproběhly.

---

## N. Practical recommendation

**Nevykázáno: vyžaduje G3 a lidská hodnocení.** Doporučení se smí týkat jen testovaných produktů, režimu, účtů, jazyků, oblastí a období. Nesmí tvrdit „nejlepší AI" ani se opírat o hypotézu, kterou data nepodpořila.

**Best system for the defined capability:** Nelze určit z pilotních dat; nevykazujeme.

**Best prompt condition:** Nelze určit z pilotních dat; nevykazujeme.

**Conditions under which this recommendation holds:** Nelze určit z pilotních dat; nevykazujeme.

**Important cost, latency, or human-effort trade-off:** Nelze určit z pilotních dat; nevykazujeme.

**What should a practitioner not infer from this study?** Předběžně: který jazykový model je lepší, že S2 znamená pravdivou odpověď, že výsledek platí pro jiné typy dotazů, jazyky, placené úrovně nebo pozdější verze produktů.

---

## O. Validity and limitations

(Předběžně, k aktualizaci po bězích.)

**Construct validity: are we measuring the intended capability?** Měříme podporu tvrzení citovaným zdrojem, ne pravdivost odpovědi. Dělení odpovědi na tvrzení je subjektivní, proto jsou pravidla v rubrice a segmentace se hodnotí zvlášť.

**Internal validity: could another factor explain the result?** Ano: opatrnost místo kvality (A1), dostupnost zdrojů a jazyk (A2), změna formátu atribuce (A3). Dále rozdíly v účtech, regionu, skrytých nastaveních produktů a pořadí zadávání.

**External validity: where might the result fail to generalize?** Jiné typy dotazů, jiné jazyky a regiony, placené úrovně, jiné režimy (Deep Research), pozdější verze produktů a víc než jedno kolo komunikace.

**Statistical uncertainty or sample-size limitation:** Deset testových úloh dává hrubé intervaly a nízkou sílu. Rozdíly pod zhruba 0,15 pravděpodobně nepůjde rozlišit. Nevýznamnost není důkaz rovnosti a konstantní bootstrap CI není nulová nejistota.

**Product or model-version drift:** Model, rozhraní i vyhledávání se mohou změnit během dnů. Zmírňujeme to 72hodinovým oknem, záznamem viditelného modelu a data a snímky obrazovky.

**Evaluation bias or judge bias:** Plánovaní lidští hodnotitelé jsou studenti a u odborných zdrojů mohou chybovat; jejich kalibrace, nezávislé ratingy a audit neshod nejsou dokončené. Doplňkový AI hodnotitel není zaslepený vůči produktu, může chybně posoudit význam a vykazovat sebepreferenci. Jeho hodnocení je oddělené; intervaly nezohledňují tuto systematickou chybu.

**Most important follow-up experiment:** Opakování na větší nezávislé sadě s nezávisle ověřenými referencemi a rozšíření o API vrstvu s ekvivalentními nástroji (dvouvrstvý návrh).
