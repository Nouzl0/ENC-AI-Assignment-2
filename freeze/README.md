# Brány jsou připravené, nikoli splněné

Žádný G1/G2/G3 manifest ani P3_final nyní nevzniká. Podepisuje je až kolega po skutečných
lidských kontrolách a bězích. `freeze_protocol.py` nevykonává žádné produktové benchmarky.

## Soukromá pracovní složka

Použijte absolutní cestu **mimo tento Git worktree**, také po rozlišení symlinků, např.
`WORK="$HOME/czai-private"`. `.gitignore` je pojistka proti omylu, ne řízení přístupu.
Správce dat nastaví oprávnění, oddělí klíč od hodnotitelů a předá učiteli nezávisle
archivované kopie manifestů (nepřepisovat je). Soukromé manifesty obsahují cesty a ID holdoutu.

Původní `cases_test.jsonl` zůstává v historii a nyní jako `data/published_test_candidates.jsonl`.
Je to **zveřejněný kandidátní test**, ne tajný holdout. Správce vytvoří ≥10 nových případů
schématu v2 mimo repo; nesmí kopírovat publikované kandidáty. G1 kontroluje ID a hrubé
textové překryvy s dev/val i publikovanými případy. Není to důkaz neexistence tréninkové kontaminace.

## Příkazy (provádí kolega až po splnění podmínek)

```bash
python3 scripts/freeze_protocol.py --template G1 --out "$WORK/G1.config.json"
# Vyplnit config, role, soukromé cesty, skutečné signed_by/signed_at a potvrzení.
python3 scripts/freeze_protocol.py --seal "$WORK/G1.config.json" --out "$WORK/G1.json"
python3 scripts/freeze_protocol.py --verify "$WORK/G1.json"
```

Obdobně `--template G2` a `G3`; `parent_path` odkazuje na předchozí manifest. Všechny
časové údaje jsou ISO-8601 s UTC offsetem. Skript odmítne nevyplněné podpisy/potvrzení,
neúplné reference, změněné hashe a existující výstup. Podpis je **lidské prohlášení,
nikoli kryptografické ověření identity**. Pokud někdo úmyslně přepíše manifest i hashe,
odhalí to až nezávisle archivovaná původní kopie.

- **G1:** pilotní kalibrace zaznamenána; autor promptu odlišný od správce holdoutu a
  nezávislého ověřovatele referencí; ≥40 úloh / ≥10 test, ≥20 % edge v každé sadě.
  Test navíc splňuje předem zmrazené veřejné kvóty data/holdout_blueprint.json.
  `source_evidence.csv` má přesně RF/OF všech aktuálních úloh, `verified`, přesný fact_text
  a zvlášť skutečně ověřenou reference_value; valid_as_of podle statické reference nebo
  UTC dne kontroly u RUN_DAY. Správnost hodnoty potvrzuje člověk, ne textová rovnost.
  Dále
  URL, čas, locator, krátký úryvek nebo vlastní shrnutí a snapshot + SHA-256. Nové reference
  musí být skutečně ověřeny člověkem. `repeat_task_ids`, systémy a validační kandidáti jsou
  předem stanovené; checked_at zdrojové kontroly nesmí následovat podpis G1.
  Při 4 systémech je potřeba věcný důvod vyloučení, ne pouze menší pracnost.
  Zmrazí se protokol, rubrika, dev/val, soukromý test, P1/P2, zdrojové důkazy a hodnoticí kód.
- **G2:** vývojová analýza, validační metriky a záznam volby vítěze se uloží jako důkazy.
  P3_final musí být přesná kopie vybraného předem plánovaného kandidáta v obou jazycích;
  hashe P3 a CHANGELOG se nově svážou s G1. Existence P3 souboru sama nestačí.
- **G3:** úplná předem daná matice všech čtyř fází, včetně nulových provozních selhání;
  raw/final odpovědi, screenshoty, neúspěšné pokusy a SHA-256; nezávislé ratingy před diskusí,
  ≥25 % dvojitě hodnocených odpovědí v každém stratu; nikdo nehodnotí vlastní běh; doklady
  neshod i každé změny finálního ratingu oproti raw1 (také při shodě dvou hodnotitelů
  nebo jediném hodnocení), oddělené aktuální RUN_DAY reference. Nové/odebrané jednotky
  se auditují polem `present` (`yes`/`no`); log obsahuje raw hodnoty i finální rozhodnutí.
  RUN_DAY má právě jeden řádek pro každé RF/OF každé dokončené úlohy a dne v UTC,
  s kontrolou provedenou tentýž UTC den, hodnotou, URL, locatorem, úryvkem/shrnutím a
  snapshotem + SHA-256; čas kontroly nesmí předcházet údajnému dni ani následovat G3.
  Soukromé ratingy
  musí mít `rater` shodný v answer i pair řádcích. Provozní a source artefakty se zahashují.
  Časové odchylky 24/72/72 h se zachovají v manifestu a reportu; záznam odchylek je povinný
  i pokud uvádí „žádné“. Zdrojové rozhodnutí se dokládá do 7 dní po běhu.

FAB explicitní značka bez URL i zdrojového záznamu může mít prázdné evidence_url;
ostatní evidence je povinná: původní odpověď/log dokládající absenci, locator,
shrnutí, čas, snapshot a hash. U FAB s uvedenou URL, NA a ostatních ratingů URL
zůstává povinná. Nevymýšlet adresu jen pro průchod validátorem.

## Plány a anotace

`make_run_plan.py --freeze G1/G2 --out "$WORK/runs/run_plan_<phase>.csv"` vytvoří CSV i
`.manifest.json`: experimentální pole, vyrenderovaný prompt a jeho hash se nesmějí měnit,
operátor vyplňuje jen metadata. Hashy promptů se kontrolují i proti souborům použitým při
plánování. Plány před měřením nezávisle archivujte. Po G1 nelze měnit protokol ani kód;
oprava vyžaduje deklarovanou novou verzi a srovnatelné přehodnocení, ne přepsání hashů.

Pilot používá explicitně `--pilot --phase dev --only ...`, bez zmrazení. Je to kalibrace
navíc, nikoli finální dev skóre: po G1 se sbírá celá dev sada podle zmrazené rubriky.
Syntetická výjimka `--synthetic` vyžaduje DEMO-* a anonymní sys_*; není povolena s `score --final`.

Při chybě operátora uchovejte řádek `excluded/student_error`, vysvětlení a artefakt; zapište
`replacement_run_id`. Přidejte nový řádek se stejnými experimentálními poli, novým run_id,
seq a answer_file, `replaces_run_id=<původní ID>`. Nejde o provozní retry. Neautorizované
řádky, vymazané běhy či změna podmínky se odmítnou.

`check_citations.py` vyžaduje stejnou bránu a soukromé `--out-dir` / `--key-dir`.
Produkční export používá výhradně zmrazený `data` adresář repozitáře; náhradní gold
nelze podstrčit přes `--data-dir`. Výběr ≥25 % se stratifikuje podle fáze×systému×podmínky,
také při společném exportu více fází. Export nesmí přepsat hotové listy;
opakovaný run_id je chyba. Klíč se kumuluje napříč
fázemi; původní čtyři `*_to_rate*.csv` zachovejte, ratingy pište do kopií. Výběr druhého
hodnotitele a hashe originálů se uloží do soukromého `annotation_batch.json`. HTTP pokusy
ukládají snapshoty, timestamp, finální URL a hash; ořezání 3 MB je označené. Automatické
snapshoty ani entity-match nejsou důkaz S2, člověk musí zkontrolovat obsah a případné ořezání.

`score.py` bez `--final` je vždy předběžná analýza. Finální potvrzování H1/H2 vyžaduje G3,
jeho přesnou sadu plánů/ratingů, plnou matici a zmrazené parametry. Výstupy ukládejte do
nové verzované soukromé složky. Publikace patří až po G3 a po kontrole soukromých údajů.

## Reprodukce na jiném počítači (až po G3)

Učitel/správce s oprávněním dostane přesný zmrazený commit repozitáře a **kompletní
soukromý balíček**, včetně nezávisle archivovaných manifestů, původních plánů, zdrojových
snapshotů, raw odpovědí, screenshotů, klíče a ratingů. Nestačí veřejný Git. Před G2 tím
nezpřístupňovat holdout autorovi promptu. Sanitizovaný veřejný export je jiný odvozený
artefakt, nikoli ověřitelný kompletní podepsaný G3 balíček.

Při jiných absolutních cestách se **nemění žádný podepsaný JSON/CSV ani jeho hashe**.
Nový soukromý map.json mapuje původní repo a pracovní složku na dva existující,
nepřekrývající se absolutní cíle (jeden je aktuální repo):

```json
{"schema_version":1,"prefixes":[
  {"from":"/original/ENC-AI-Project","to":"/new/ENC-AI-Project"},
  {"from":"/original/czai-private-v1","to":"/new/czai-private-v1"}
]}
```

Z aktuálního přesného klonu a s původními parametry G1:

```bash
python3 scripts/freeze_protocol.py --verify "$WORK/G3.json" --path-map "$WORK/map.json"
python3 scripts/score.py --final --path-map "$WORK/map.json" --freeze "$WORK/G3.json" \
  --runs "$WORK/runs/run_plan_*.csv" --annotation-dir "$WORK/annotation" \
  --key-dir "$WORK/key" --focus "$FOCUS" --out "$WORK/results/replay-v1"
```

WORK nyní ukazuje na nový fyzický adresář; `--out` musí být nová fyzická cesta mimo
annotation/key. Mapa se používá jen při čtení, včetně rekurzivního řetězce G1→G2→G3,
kontroly hashů a původních vazeb. Únik přes symlink a kolize vazeb se odmítají.
`--path-map` nelze použít ke sběru či podpisu nové brány. `replay_provenance.json`
uvádí SHA-256 původního G3, mapy a odvozených výstupů; **není to nový podpis ani schválení**.
