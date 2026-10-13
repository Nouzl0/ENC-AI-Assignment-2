# CZAI Assignment 1 – Správnost citací AI asistentů

**Aktuálně: 40 různých skutečně měřených úloh a 84 věcných odpovědí.**
Původní pilot má 33 odpovědí na osm úloh; doplňkový sběr přidává 51 odpovědí
na zbývající veřejné otázky a deset nových oddělených otázek. Náhradní zachycení
nepřidává další task_id. Jedno autentizační odmítnutí a dvě chyby bez odpovědi
jsou evidovány zvlášť. [Přesné pokrytí](runs/supplement-2026-10-13/README.md),
[registry](runs/supplement-2026-10-13/run_registry.jsonl) a
[zpráva](docs/exports/project.pdf).

**Hodnocení je označené jako AI, nikoli práce Reného a Jana.** Obsahově bylo
posouzeno všech 33 původních odpovědí i nové úlohy; citační metriky a intervaly
jsou dostupné pro výslovně vymezený atomizovaný subset. Pět nových otázek má
stejný produkt v P1/P2/P3A. Matice všech produktů a promptů není úplná,
P3A není validační vítěz původního protokolu, lidské ratingy a G1/G2/G3 nejsou
splněné. Dosažení 40 úloh samo o sobě neznamená splnění všech požadavků zadání.
[Metoda doplňku](docs/supplement.md), [AI audit](results/ai-review-2026-10-13/README.md),
[worksheet](docs/deliverables/worksheet.md).

Testy a lint se při této etapě na přání uživatele nespouštěly. Původní raw
pilotní exporty a lidské anotační listy se nepřepisují.

## Co je autoritativní

- [PROTOCOL.md](PROTOCOL.md): návrh metodiky k lidskému schválení a zmrazení na G1.
- [Rubrika](annotation/rubric.md), [offline kalibrační kotvy](annotation/calibration.md),
  [brány a integrita](freeze/README.md),
  [běhy a metadata](runs/README.md), [historie promptů](prompts/CHANGELOG.md).
- [PREPARATION.md](PREPARATION.md): etapy úprav a jejich kritické kontroly.
- Původní DOCX je **historický návrh**, nikoli aktuální zmrazený protokol. Vnější původní
  odkaz na návrh není nutný pro spuštění ani reprodukci balíčku.

## Lokální kontrola bez benchmarků

Python 3.9+, pouze standardní knihovna; žádné API klíče ani účty produktů:

```bash
python3 scripts/validate_cases.py --no-test
bash demo/run_demo.sh
# Samostatná integrační kontrola v dočasné složce:
python3 scripts/make_demo_data.py
# Volitelné zachování syntetických artefaktů v NOVÉ složce mimo repo:
python3 scripts/make_demo_data.py --out "$HOME/czai-synthetic-v1"
# Vyplněná reference evidence na smyšlených datech (žádné ověření gold):
python3 scripts/make_evidence_example.py --out "$HOME/czai-evidence-DEMO-v1"
```

Testy zahrnují skutečné CLI řetězce plán → syntetická odpověď → parser → zaslepený
export → fixture ratingy → skórování. Očekávané hodnoty se kontrolují pro každý záznam;
nejde o nezávisle vygenerované náhodné výsledkové CSV. HTTP testy používají pouze
krátkodobý server na `127.0.0.1`, nikoli veřejný web. Výchozí artefakty se odstraní.
Režim `--synthetic` používá DEMO-* / sys_*, nepotvrzuje H1/H2 a nesmí s `--final`.
Gate test navíc kontroluje finální scoring v izolované falešné kopii repo s testovacími
identitami pro selhání i úspěšné odpovědi a dva read-only replaye po přesunutí;
tím neuděluje skutečné G1/G2/G3. CI workflow je nastavený na stejné
softwarové testy, nikoli produktové benchmarky; stav vzdáleného CI ověřit zvlášť.

Replay testy spouštějí přenesené CLI v nových procesech po odstranění původních
adresářů a porovnávají všech pět výsledkových souborů po bytech. Syntetická pipeline
se opakuje s jiným `PYTHONHASHSEED` a časovou zónou. Test checkoutu simuluje
`core.autocrlf=true`; bez dostupného Gitu se pouze tento test přeskočí.

## Lokální statické kontroly a formátování

Ruff **0.16.1** je připnutý jako vývojový nástroj v `pyproject.toml` a `uv.lock`.
Konfigurace pokrývá všechny Python skripty a testy: chyby Pyflakes/pycodestyle,
řazení importů, kompatibilní modernizace, Bugbear, comprehensions, zjednodušení,
PIE a pravidla Ruff. Formátování používá 88 znaků; dlouhé literály se násilně
nedělí. Záměrné znaky `–`, `−` a `×` zůstávají zachované, nikoli zaměněné za ASCII.

```bash
# Jen Ruff, bez instalace nástrojů pro dokumentaci a pytest:
uv run --locked --only-group dev ruff check .
uv run --locked --only-group dev ruff format --check .
# Lokální bezpečné automatické opravy a formátování:
uv run --locked --only-group dev ruff check . --fix
uv run --locked --only-group dev ruff format .
git diff --check
```

S již dostupným Ruffem 0.16.1 lze použít přímo `ruff check .` a
`ruff format --check .`. Prostředí `uv` pro vývoj/dokumentaci podle
`.python-version` používá Python 3.14; samotné skripty a unittesty nadále potřebují
jen Python 3.9+ a standardní knihovnu. Ruff proto výslovně cílí na `py39`, nikoli
na verzi vývojového prostředí. Lint ani formatter nenahrazují softwarové testy
a neověřují reference nebo experimentální výsledky. CI se touto lokální úpravou nemění.

## Data a soukromí

V Git je **20 dev + 10 val** ve schématu v2 a **10 historických zveřejněných testových
kandidátů** v `data/published_test_candidates.jsonl`. Ty nejsou skutečným skrytým testem.
Přejmenování neodstranilo historii. Operátor připravil 10 nových soukromých kandidátů pro Reného; návrh čeká na
jeho nezávislou lidskou kontrolu a schválení. Nejde o již zmrazený holdout.
Číselné a datované reference se musí nezávisle doložit; samotný validátor neověřuje pravdu.
[Vyplněné příklady evidence](data/evidence_examples.md) ukazují rozdíl fact_text/hodnota,
statické RF/OF a RUN_DAY se snapshoty/hashy. Výstupy DEMO_NOT_VERIFIED jsou záměrně
neschválitelné, nelze je přejmenovat na skutečné gold důkazy.

Všechny reálné plány, odpovědi, ratingy, klíče, snapshoty i výsledky jsou **mimo worktree**.
`.gitignore` není řízení přístupu. Holdout a jeho důkazy nesmí vidět autor promptu před G2;
CLI s manifesty provádí správce dat. Hodnotitelům předává jen jejich zaslepené listy,
nikoli celý pracovní adresář nebo `answer_metrics.csv` s názvy systémů.

## Postup dokončení experimentu

1. Role, dostupnost produktů, nový holdout, nezávislé zdrojové důkazy a pilot navíc.
2. Podepsat a nezávisle archivovat **G1**; poté nově sebrat celou dev sadu.
3. Analýza dev → obecné změny P3 → jednorázová plánovaná validace.
4. Přepočet P3 z archivovaného scoring_inputs.json v plné přesnosti, kontrola časů
   validačních zdrojových rozhodnutí, přesná kopie vítěze CZ/EN, záznam volby → **G2**.
5. Test P1/P2/P3 a oddělená opakování P2; uchovat selhání i první pokusy.
6. Nezávislé ratingy, ≥25 % po fázi×systému×podmínce, audit neshod/změn → **G3**.
7. `score.py --final` s G3 → výsledky, analýza ≥8 unikátních úloh, závěrečná zpráva.

Přesné soukromé příkazy jsou v [HANDOFF.md](HANDOFF.md). Žádná šablona ani existence
P3 souboru sama o sobě neotevře test či finální analýzu.

## Mapování na odevzdání

| Povinný výstup | Připraveno zde | Co ještě musí vzniknout |
| --- | --- | --- |
| Výzkumný protokol | PROTOCOL.md + freeze/README.md | skutečně schválené a archivované G1/G2/G3 |
| Benchmarková data | dev 20 + val 10, soukromý návrh 10 nových testů, schéma a evidence | schválení holdoutu a nezávislé ověření všech referencí |
| Prompty a verze | prompts/ + CHANGELOG | dev důvody úprav, validační výběr, P3_final |
| Metadata běhů | generátor, 33 skutečných pilotních odpovědí a hashované exporty | kompletní analytická matice a její původní artefakty |
| Hodnoticí postup/kód | scripts/, rubrika, kalibrační kotvy, tests/ | skutečné nezávislé ratingy a zdrojová rozhodnutí |
| Výsledky s nejistotou | score.py, provozní pilotní souhrny a docs/results.md | finální G3 metriky a CI, kvalita vs. úsilí |
| Analýza chyb | konkrétní rozbor 8 unikátních pilotních úloh v docs/error-analysis.md | návazná analýza finálních analytických výsledků |
| Závěrečná zpráva | MyST zdroje a pracovní PDF se skutečným pilotem | dokončení závěrů po plném benchmarku |

Celá standardní matice má **500 analytických + 10 pilotních** záznamů. Doporučená
úsporná varianta zachová všech 5 produktů: jeden P3 kandidát a 5 repeat úloh před G1 →
**400 + 10**, odhad práce 80,1 místo 99,7 h. Pouze při doložené nedostupnosti/nevhodnosti
pátého je možných 320 + 8 se čtyřmi produkty; samotná úspora práce nestačí.
Hrubý plán v protokolu není naměřený čas a nezahrnuje přípravu referencí a další práce;
dostupnost, role a harmonogram ověřit před G1. Detail konfigurace: HANDOFF §1 / PROTOCOL §6.

Interpretace výsledků má odlišit atribuci od pravdivosti: H2 doplnit podílem odpovědí
s explicitní citací a podmíněnou přesností s n; diagnostiky source/time/ack vykázat
spolu s pokrytím. Konstantní bootstrap CI není důkaz jistoty. Oba hodnotitelé dostávají
stejné zaslepené podklady bez automatických nápověd.

Oprávněná reprodukce na jiném počítači vyžaduje **kompletní soukromý G3 balíček**,
přesný commit, read-only mapu cest a původní parametry; podepsané JSON/CSV nepřepisovat.
Postup a `replay_provenance.json`: [freeze/README.md](freeze/README.md).
