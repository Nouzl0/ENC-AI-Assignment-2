# Závěrečná zpráva – šablona k vyplnění po benchmarku

**Toto není výsledek experimentu.** Všechna `DOPLNIT` nahradit skutečnými údaji,
odkazy na auditní artefakty nebo výslovným „nezjištěno“ s důvodem. Žádná syntetická
fixture ani softwarový test se nevydává za výkon produktů. Pomocný `report.md` ze
score.py není náhradou za tuto interpretaci.

## 1. Shrnutí a výzkumná otázka

- Tým, role, období měření, verze balíčku / Git commit: DOPLNIT.
- Otázka: správnost explicitních citací rešeršních produktů na definovaném mixu
  faktických CZ/EN úloh; změna při P1/P2/obecném P3. Přesný rozsah: DOPLNIT.
- Jedna hlavní a dvě vedlejší metriky podle zmrazeného protokolu: DOPLNIT.
- Hlavní zjištění včetně velikosti efektu, 95% CI a n, nikoli jen pořadí: DOPLNIT.
- Co data **neprokazují** (čistou schopnost modelu, nejlepší AI obecně): DOPLNIT.

## 2. Návrh, data a férovost

- Směr B, návrh podle schopností produktu, nikoli parita nástrojů: DOPLNIT režimy.
- Zahrnuté produkty / zdůvodnění případného vyloučení pátého: DOPLNIT.
- Skutečné počty dev/val/test, domén, obtížností, jazyků, typů a edge případů: DOPLNIT.
- Původ a způsob výběru úloh; nereprezentativnost účelového vzorku: DOPLNIT.
- Nový soukromý holdout, správce, přístupová pravidla, kontrola překryvů; publikovaní
  CIT-031–040 nejsou tajný test. Kdo co viděl a kdy: DOPLNIT.
- Nezávislé ověření každého RF/OF, platnost, snapshoty a RUN_DAY evidence: DOPLNIT.
- Odkazy/hashe G1, G2, G3 a jejich nezávislé archivní kopie: DOPLNIT.
- Časová okna, skutečné odchylky a jejich dopad: DOPLNIT.

| Zdroj pozorované výkonnosti | Co návrh drží stejné | Co se liší / nelze izolovat |
| --- | --- | --- |
| Model | DOPLNIT | Viditelné názvy, neznámé interní verze; DOPLNIT |
| Prompt | Společné CZ/EN verze a pořadí podmínek; DOPLNIT | Délka, formát, doptání; DOPLNIT |
| Produkt | Úroveň účtu, rozhraní, nastavení kde proveditelné; DOPLNIT | UI, bezpečnostní vrstvy, region, limity; DOPLNIT |
| Nástroje | Povolený společný režim; DOPLNIT | Retrieval, dostupnost/viditelnost volání; DOPLNIT |

## 3. Prompty a sběr

- Přesné texty/verze/hashe P1/P2/P3, délky CZ/EN: DOPLNIT.
- Dev důvody každé úpravy P3: ≥3 chybné odpovědi, jejich run_id/task_id/kódy;
  hypotéza mechanismu versus přímý důkaz: DOPLNIT.
- Val výsledky všech plánovaných kandidátů, délky, použití pravidla výběru a
  freeze před prvním testem (i pokud vítěz nezlepšil P2): DOPLNIT.
- Počet systémově specifických úprav, přenositelnost, další kola/nástroje: DOPLNIT.
- Nové chaty, instrukce, paměť, přílohy, teplota/max output (neznámé výslovně),
  modely, účty a rozhraní: DOPLNIT; propojit s jednotlivými run metadata.
- První/final pokusy, provozní selhání, chyby formátu, retry, náhrady operátorských
  chyb a ruční zásahy; žádné odstraněné nepohodlné běhy: DOPLNIT.

## 4. Hodnocení a spolehlivost

- Hlavní přesnost = explicitní S2 / všechny explicitní dvojice; NA/FAB v jmenovateli,
  bez citací 0. Úplnost = podpořená unikátní tvrzení / všechna tvrzení celé odpovědi.
  Správnost = podíl correctness=2. Uvést skutečné jmenovatele/n: DOPLNIT.
- RF versus bonus, S2 není nutně pravda, `*` pouze diagnostika: DOPLNIT příklady.
- Automatické kontroly: URL/redirecty, datum, entity-match, opakovaná nedostupnost,
  snapshoty/ořezání a jejich limity; co bylo skutečně spuštěno: DOPLNIT.
- Pilot/kalibrace, zaslepení a jeho limity, randomizace, identity/nezávislost lidí,
  stratifikovaný ≥25% vzorek a nulová vlastní hodnocení běhů: DOPLNIT.
- Raw IRR: kappa S2/ostatní, pět kategorií a správnost, surová shoda a n, ztráta
  srovnatelnosti při segmentaci; nedefinovanou kappu uvést jako nedefinovanou: DOPLNIT.
- Audit neshod a všech změn final oproti raw1; kdo rozhodl, verze rubriky: DOPLNIT.
- Úlohový bootstrap 10 000 / seed 2026, párování, Wilson, první běhy a oddělená
  opakování; chybějící údaje a odchylky: DOPLNIT.

## 5. Výsledky testu a hypotézy

Vložit výsledky skutečného G3 `metrics.csv`, `answer_metrics.csv`, `hypotheses.csv`,
`agreement.csv`. Dev/val neprezentovat jako nezávislý test; opakování nenavyšují n úloh.

| Produkt | Podmínka | n úloh / selhání | Přesnost [95% CI] | Úplnost [95% CI] | Správnost [95% CI] |
| --- | --- | --- | --- | --- | --- |
| DOPLNIT pro všechny produkty | P1/P2/P3 | DOPLNIT | DOPLNIT | DOPLNIT | DOPLNIT |

- H1 focus P2 − ostatní: odhad, párový CI, n, podpora dle bodového margin + CI>0,
  odděleně `ci_above_margin`: DOPLNIT.
- H2 P2 − P1: odhad, párový CI, n, podpora včetně počtu zlepšených produktů,
  odděleně `ci_above_margin`: DOPLNIT.
- Kritérium podpory neznamená důkaz skutečného efektu ≥ margin; společná chybovost
  H1/H2 není garantována. Malé n / široký CI neznamenají rovnost: DOPLNIT interpretaci.
- P3 − P2: celkový a každý produkt, n a párové CI; zhoršení se nezamlčuje: DOPLNIT.
- A1: tvrzení/citace, RF pokrytí a Spearman; jen deskriptivně: DOPLNIT.
- A2: NA, jazyk/doména/obtížnost; nepárované CZ/EN (cs+en v CZ), ne čistý jazykový efekt: DOPLNIT.
- Opakování P2: předem vybraný subset, n společných úloh, SD/změny správnosti;
  pozdější období směšuje náhodnost a změny produktu/zdrojů: DOPLNIT.

## 6. Provoz, náklady a práce lidí

| Produkt / podmínka | První / final úspěch | Retry | Latence medián / p90 a n | Anotace min a n | Cena a co zahrnuje |
| --- | --- | --- | --- | --- | --- |
| DOPLNIT | DOPLNIT | DOPLNIT | DOPLNIT | DOPLNIT | DOPLNIT / neznámá s důvodem |

- Oddělit předplatné, mezní poplatky a lidskou práci; cena neznámá není nula.
- Viditelné tokeny/kredity/volání, kola, náklady retry a přípravy: DOPLNIT.
- `check_minutes` je anotace, **ne uživatelský čas opravy**. Ten nebyl změřen, pokud
  nebyl doplněn samostatný předem deklarovaný postup.
- Pareto přesnost×latence; případný explorační annotation_effort_index a jeho pevné
  váhy, chybějící hodnoty a relativní normalizace, nikoli obecný užitek: DOPLNIT.

## 7. Analýza ≥8 unikátních úloh včetně úspěchů

Předem popsat výběr, aby šlo dohledat reprezentativní/typické příklady i protipříklady.
Podle analysis/README.md ideálně 12–16 odpovědí; vždy alespoň 8 různých task_id,
zastoupené systémy a úspěšné i chybné výstupy. Případný dev/val původ jasně označit.

| task_id / split / run_id | Výňatek a explicitní citace | Rating / kód / zdrojový důkaz | Příčina a jistota | Srovnání P3 |
| --- | --- | --- | --- | --- |
| DOPLNIT 1 | DOPLNIT | DOPLNIT | unknown, není-li doklad | improvement/unchanged/worsened/not_comparable |
| DOPLNIT 2–8+ (různá task_id) | DOPLNIT | DOPLNIT | DOPLNIT | DOPLNIT |

Retrieval/attribution/generation jsou hypotézy bez přímého dokladu. Jedna lepší P3
odpověď neprokazuje odstranění příčiny chyby. Uvést úspěchy, zhoršení a limity srovnání.

## 8. Závěr, alternativy a omezení

- Přímá odpověď na otázku, konkrétní velikost efektu a praktické doporučení omezené
  na měřené produkty, úroveň účtu, režim, úlohy/jazyky a období: DOPLNIT.
- Alternativní vysvětlení: méně tvrzení, zdrojová dostupnost, retrieval, UI, prompt
  formát/částečné zaslepení, jazyky/domény, změny v čase: DOPLNIT.
- Limity malého n, účelového výběru, segmentace/ratingu a neznámých nastavení: DOPLNIT.
- Co by nový, větší či kontrolovanější experiment ověřoval; bez nového ladění tohoto testu: DOPLNIT.

## 9. Reprodukce, etika a balíček k odevzdání

- Přesný postup od uložených run/rating dat ke skóre, verze Pythonu/commit,
  veřejné a oprávněně soukromé auditní soubory: DOPLNIT.
- Práva ke zdrojům, vlastní texty dotazů, žádné osobní údaje/tokeny; publikace testu
  až po G3, soukromé snapshoty sdílet jen oprávněně: DOPLNIT.
- Odkazy na **8 částí**: protokol, data/provenance, prompty/CHANGELOG, run metadata,
  kód/rubrika, výsledky/CI/repeats/úsilí, analýza ≥8 úloh, tato zpráva: DOPLNIT.
- Přiznat automatickou/AI pomoc při přípravě, lidská rozhodnutí a neověřené údaje:
  DOPLNIT. Reprodukovatelnost skórování není opakovatelnost budoucího cloudového produktu.
