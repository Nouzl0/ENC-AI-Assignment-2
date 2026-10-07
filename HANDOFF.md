# Předání kolegovi: co provést a co ještě není hotové

**My připravujeme software/metodiku, ty provedeš skutečný benchmark.** Žádné výsledky,
nezávisle schválené reference, G1/G2/G3 ani vítězný P3 nyní nejsou hotové. Neodevzdávat
syntetické testy jako výsledky produktů. Postup číst spolu s PROTOCOL.md a rubrikou.

Reprodukce na jiné cestě/počítači: viz freeze/README.md, `--path-map` pouze pro ověření
a finální replay. Předat učiteli autorizovaný kompletní soukromý balíček i přesný commit;
nepřepisovat původní absolutní cesty uvnitř podepsaných souborů.

## 0. Role a izolovaný pracovní prostor

- Správce dat vytvoří nový holdout a provádí CLI; nezávislý ověřovatel kontroluje reference.
  Oba se liší od autora promptu. Správce/ověřovatel mohou být stejný člověk, pokud je to
  nezávislé na autorovi promptu; popsat limity a zajistit dvojí rating bez hodnocení vlastních běhů.
- Operátor se nesmí stát hodnotitelem svých odpovědí. Pro dvojité hodnocení nebo nevyřešené
  neshody zajistit externího člověka, pokud role uvnitř týmu nelze oddělit.
- Autor promptu dostává pouze dev/val podklady; G1 manifest i source_evidence obsahují
  citlivé cesty/reference holdoutu. Scriptové ověřování manifestu potřebuje číst i holdout,
  proto je nespouští autor promptu. Samotný `.gitignore` nebo slib nenahrazuje oprávnění.

Příkazy provádí správce z kořene aktuálního repozitáře. `WORK` je absolutní cesta mimo Git,
**ne symlink zpět do repozitáře**. Vybrat novou verzovanou složku:

```bash
umask 077
export WORK="$HOME/czai-private-v1"
export FOCUS=perplexity  # H1 focus: předem zvolený zahrnutý produkt; musí souhlasit s G1.config.focus.
mkdir -p "$WORK"/{runs,annotation,key,results,records,calibration}
cp -n data/source_evidence_TEMPLATE.csv "$WORK/source_evidence.csv"
cp -n annotation/disagreements_TEMPLATE.csv "$WORK/annotation/disagreements.csv"
cp -n annotation/run_day_evidence_TEMPLATE.csv "$WORK/annotation/run_day_evidence.csv"
# Jen hlavičky pro pozdější skutečné vyplnění; existující obsah nepřepisovat.
python3 scripts/validate_cases.py --no-test
python3 -m unittest discover -s tests -v  # pouze software; žádné produkty
```

## 1. Před G1: skutečné lidské kontroly

- [ ] Zvolit 5 dostupných produktů nebo předem věcně zdůvodnit 4; ověřit úroveň účtu,
  vyhledávání, paměť/personalizaci, limity, region a rozhraní. Zapsat do pilot/setup záznamu,
  uložit soukromé screenshoty; immutable plán obsahuje zamýšlený režim, ne automaticky
  ověřenou aktuální dostupnost. Povinné změny konfigurace zaznamenat před G1.
  Pokud nelze zahrnout Perplexity, před G1 změnit i H1/focus a jeho hypotetický mechanismus
  v protokolu, nastavit FOCUS na zahrnutý produkt a stejnou hodnotu v G1 config.
  Focus se nikdy nevybírá podle výsledků. Všechny score příkazy níže nesou --focus.
- [ ] Vytvořit ≥10 nových testových úloh v `$WORK/holdout.jsonl`, schéma v2,
  development_validation_test_split=test, nové unikátní task_id; agregované kvóty podle
  data/holdout_blueprint.json (včetně 4–5 edge na 10) a ruční kontrola významových duplikátů.
  Případnou změnu kvót věcně odůvodnit před G1, nikdy podle výsledků.
  Nekopírovat CIT-031–040 z publikovaných kandidátů ani dev/val. U nových task_id není
  předepsaný prefix CIT, není však dovoleno použít DEMO pro reálné výsledky.
- [ ] Nezávisle ověřit každý RF/OF dev/val/nového testu. Aktualizace návrhového gold je
  možná **před G1**, s odůvodněním v data/CHANGES.md, nikoli podle toho, co odpověděl produkt.
  Reference na budoucí či aktuální data nelze zaměnit za staré znalosti: vždy primární zdroj.
- [ ] Vyplnit `$WORK/source_evidence.csv` z `data/source_evidence_TEMPLATE.csv`:
  přesný fact_id RF1…/OF1…, reference_kind, fact_text přesně podle RF/OF, zvlášť
  reference_value jako skutečná ověřená hodnota (ne zástupný požadavek), valid_as_of
  podle statické reference nebo UTC data kontroly u RUN_DAY, skutečný ověřovatel,
  URL, checked_at s offsetem, locator, shrnutí/krátký
  úryvek, snapshot_file + SHA-256, verification_status=verified. Pro G1 mají všechny
  řádky verified_by identitu deklarovaného reference_checker. Nevydávat header za důkaz.
  checked_at nesmí následovat skutečné signed_at G1; nelze schválit kontrolu z budoucnosti.
- [ ] Předem vybrat repeat_task_ids (10 standard / 5 úsporně), jeden/dva P3 kandidáty,
  účetní postup pro ceny a kapacitu lidí na 72h okna. Odhad práce viz protokol.

Kontrolu soukromého testu provádí jen správce (výstup obsahuje ID, ne celé otázky):

```bash
python3 scripts/validate_cases.py --test-file "$WORK/holdout.jsonl"
```

Nejprve oba hodnotitelé samostatně projdou [offline kotvy](annotation/calibration.md),
včetně S1/S0/NA/FAB a correctness=1, a zaznamenají neshody/závěr. Poté skutečný pilot:
dvě dev úlohy × zahrnuté produkty (běžná opora + chybějící informace), kalibrace a nové
ohodnocení po poslední úpravě rubriky. Pilot je **navíc**, klíč/plány/listy oddělené
od analytických dat. Příklad pro 5 produktů:

```bash
python3 scripts/make_run_plan.py --pilot --phase dev --only CIT-001,CIT-020 \
  --out "$WORK/calibration/run_plan_pilot.csv"
# Skutečně provést pilot, vyplnit všechny stavy/artifact metadata podle runs/README.md.
python3 scripts/check_citations.py --pilot --runs "$WORK/calibration/run_plan_pilot.csv" \
  --out-dir "$WORK/calibration/annotation" --key-dir "$WORK/calibration/key"
# Vyplnit ratingové kopie, uložit kalibraci, role, nastavení a závěr do records/pilot.txt.
```

V úsporné variantě přidat `--systems` se čtyřmi předem zvolenými identifikátory.
G1 šablonu vyplnit pravdivě, včetně config/roles/inputs (holdout, evidence a pilot_record):

```bash
python3 scripts/freeze_protocol.py --template G1 --out "$WORK/G1.config.json"
# Lidské vyplnění a schválení; signed_at např. skutečný čas ISO-8601 s UTC offsetem.
python3 scripts/freeze_protocol.py --seal "$WORK/G1.config.json" --out "$WORK/G1.json"
python3 scripts/freeze_protocol.py --verify "$WORK/G1.json"
```

Manifest a snapshoty **nezávisle archivovat** (např. kopie u vedoucího týmu/učitele).
Podepsaný text není kryptografická identita ani důkaz, že nebyl test přečten. Od G1
needitovat zmrazený protokol, rubriku, data, P1/P2 ani hodnoticí kód.

## 2. Dev po G1

```bash
python3 scripts/make_run_plan.py --phase dev --freeze "$WORK/G1.json" \
  --out "$WORK/runs/run_plan_dev.csv"
# Nově provést všech 20 dev úloh; nepřevzít kalibrační pilot.
python3 scripts/check_citations.py --freeze "$WORK/G1.json" \
  --runs "$WORK/runs/run_plan_dev.csv" --out-dir "$WORK/annotation/dev" --key-dir "$WORK/key"
# Nezávislé lidské ratingy, poté audit a final kopie.
python3 scripts/score.py --freeze "$WORK/G1.json" --runs "$WORK/runs/run_plan_dev.csv" \
  --annotation-dir "$WORK/annotation" --key-dir "$WORK/key" --focus "$FOCUS" --out "$WORK/results/dev-v1"
```

Hodnotitelé dostanou pouze své *_to_rate*.csv a rubriku/kalibrační kotvy/daily reference,
nikoli klíč či výsledky s názvy systémů. Oba hodnotí bez auto_suggestion, HTTP či match
nápověd; `pairs_auto_checks.csv` zůstává u správce. Původní čtyři exportované listy **neměnit**. Hodnocení uložit
jako *_rated_rater1.csv (před diskusí), *_rated_rater2.csv (jen vybraný vzorek); konsenzus
jako pairs_rated.csv a answers_rated.csv. Stejná identita rater v answer i pair.
Ruční segmentace: žádná nepřečtená část odpovědi, nové pair_id, n_claims a review=yes.
Vyplnit constraint_results přesně pro RC1…RCn; correctness=2 vyžaduje všechna yes.
U citovaných dvojic povinné source_tier=1/2/3/unknown; time_ok=yes/no/unknown u
time_constraint, jinak na. acknowledges_uncertainty=yes/no/unknown u ambiguous/
missing_info, jinak na. Prázdné pole nenahrazuje neznámý výsledek, report ukáže pokrytí.
Zdroj/formát nepočítat jako RF, vynechání OF nepenalizovat. V CIT-002 je přípustný
jakýkoli odpovídající oficiální WHO podklad, není povinný konkrétní dokument z roku 2015.
Pro každou citovanou/nedostupnou dvojici doložit zdrojové rozhodnutí podle rubriky.
FAB značka bez zdrojového záznamu/URL: evidence_url nechat prázdné, nikoli vymyslet;
locator a shrnutí popisují chybějící [n] v původní odpovědi/seznamu, snapshot + hash
jej dokládají. Výjimka není pro NA/S2 ani pro existující URL vracející chybu.

Dev analýzu předat autorovi P3; obecné změny doložit ≥3 chybnými dev odpověďmi,
ID/kódy/předpokládaným mechanismem v CHANGELOG. Předběžní P3A/B nejsou výsledek;
pokud dev důvody nejsou, přiznat to, ne zfalšovat jejich potvrzení.

## 3. Val a G2 (ještě bez přístupu autora k testu)

```bash
python3 scripts/make_run_plan.py --phase val --freeze "$WORK/G1.json" \
  --out "$WORK/runs/run_plan_val.csv"
# Provést kompletní předem zvolené P2 + kandidáty a lidské hodnocení.
python3 scripts/check_citations.py --freeze "$WORK/G1.json" --runs "$WORK/runs/run_plan_val.csv" \
  --out-dir "$WORK/annotation/val" --key-dir "$WORK/key"
# Klíč už zahrnuje dev i val: skórovat OBA dosud existující analytické plány.
python3 scripts/score.py --freeze "$WORK/G1.json" --runs "$WORK/runs/run_plan_*.csv" \
  --annotation-dir "$WORK/annotation" --key-dir "$WORK/key" --focus "$FOCUS" --out "$WORK/results/val-v1"
```

Score uloží vedle metrik `scoring_inputs.json` s původními vstupními řádky před
skórováním. Správce porovná snapshot s archivovanými finálními ratingy a plánem;
soubor dál neměnit a nepřepisovat jej později kumulovaným testovým klíčem.
G2 z něj znovu spočítá přesnost a podle pravidla v protokolu ověří vítěze, také při
nulovém/záporném zlepšení P2. Volba používá plnou přesnost, ne zaokrouhlené CSV.
Uložit písemný selection_record, metriku obou variant, délky a odůvodnění. Žádné další
val ladění. Vítěze **teprve nyní** přesně zkopírovat do prompts/P3_final_cs.txt a _en.txt,
zapsat skutečné hashe a dev/val důvody v CHANGELOG (nikoli editovat zmrazený PROTOCOL).

```bash
python3 scripts/freeze_protocol.py --template G2 --out "$WORK/G2.config.json"
# parent_path=G1, selected_candidate=P3A/P3B, skutečná potvrzení/podpis;
# inputs: development_analysis, selection_record, validation_metrics=val-v1/metrics.csv,
# validation_scoring_inputs=val-v1/scoring_inputs.json,
# validation_plans=[absolutní cesta k run_plan_val.csv].
python3 scripts/freeze_protocol.py --seal "$WORK/G2.config.json" --out "$WORK/G2.json"
python3 scripts/freeze_protocol.py --verify "$WORK/G2.json"
```

Znovu nezávisle archivovat manifest, snapshot i původní ratingy. Pozdější G3 odmítne
změnu validačního klíče/finálních ratingů vůči G2. Nutná oprava = deklarovaná nová
verze experimentu, ne tichý přepis. Existence souborů P3 bez G2 nestačí.

## 4. Test a opakování

```bash
python3 scripts/make_run_plan.py --phase test --freeze "$WORK/G2.json" \
  --out "$WORK/runs/run_plan_test.csv"
python3 scripts/make_run_plan.py --phase repeat --freeze "$WORK/G2.json" \
  --out "$WORK/runs/run_plan_repeat.csv"
# Skutečné běhy; repeat subset se načte z G1, není dovoleno vybírat úspěšné úlohy.
python3 scripts/check_citations.py --freeze "$WORK/G2.json" --runs "$WORK/runs/run_plan_test.csv" \
  --out-dir "$WORK/annotation/test" --key-dir "$WORK/key"
python3 scripts/check_citations.py --freeze "$WORK/G2.json" --runs "$WORK/runs/run_plan_repeat.csv" \
  --out-dir "$WORK/annotation/repeat" --key-dir "$WORK/key"
```

Všechna selhání i retry ponechat. Je dovoleno také jeden společný export test+repeat,
ale nikdy neexportovat znovu stejné run_id. Dodržet 24/72/72h a source checks do 7 dnů;
porušení zaznamenat, ne upravit časy. Automatický HTTP checker je diagnostika pro
správce a pozdější porovnání, ne nápověda nezávislým hodnotitelům ani důkaz S2.
`--offline` přeskočí HTTP; v ostrém experimentu pak chybí automatická validace shody,
což nelze prezentovat jako dokončenou. Paywall/403 nepovažovat automaticky za FAB.

## 5. Audit, RUN_DAY a G3

- [ ] Dokončené odpovědi všude ohodnoceny, selhání nulová bez fiktivních ratingů;
  všechny předepsané systémy/úlohy/podmínky/opakování přítomny.
- [ ] Raw ratingy zachované, vzorek druhého hodnotitele nesubstituovaný (ceil ≥25 %
  v každém stratu), nikdo neratuje vlastní běh. Zapsat kappu včetně n a segmentace;
  nedefinovanou/nízkou kappu nezamlčet ani neopravovat jen „špatný“ vzorek.
- [ ] disagreements.csv z šablony: každá kategorická neshoda a každá změna final oproti
  raw1, také při shodě raw1/raw2 či jednom ratingu. Pole/resolution/raw hodnoty musí
  souhlasit, resolved_by + note; změna existence páru polem present=yes/no.
- [ ] `$WORK/annotation/run_day_evidence.csv` podle šablony: právě jedna evidence na
  task_id × UTC datum × RF/OF všech completed RUN_DAY úloh, včetně dev a val a různých
  dnů repeat. Hodnota+ukazatel/měsíc, verified_by, URL, čas kontroly tentýž UTC den,
  locator, excerpt_or_summary, snapshot+hash; denní reference předat hodnotitelům.
- [ ] Záznam odchylek v `$WORK/records/deviations.md`, také „žádné“, a jejich dopady.
  Neměnit timestampy ani hashe kvůli průchodu validátorem.

```bash
python3 scripts/freeze_protocol.py --template G3 --out "$WORK/G3.config.json"
# parent_path=G2, run_plans=[všechny 4 absolutní analytické CSV],
# annotation_dir, key_dir, deviations_record; skutečná lidská potvrzení a podpis.
python3 scripts/freeze_protocol.py --seal "$WORK/G3.config.json" --out "$WORK/G3.json"
python3 scripts/freeze_protocol.py --verify "$WORK/G3.json"
python3 scripts/score.py --final --freeze "$WORK/G3.json" --runs "$WORK/runs/run_plan_*.csv" \
  --annotation-dir "$WORK/annotation" --key-dir "$WORK/key" --focus "$FOCUS" --out "$WORK/results/final-v1"
```

Znovu archivovat G3 a hodnocení. `--allow-missing` nikdy nepatří do finálního kroku.
Výstupy nepřepisovat; nový výstup má novou verzi. Po G3 přidání jakéhokoli souboru do
svázaných ratingových adresářů mění auditní sadu; nedávat reporty zpět do annotation/key.

## 6. Odevzdání a zpráva

Vyplnit REPORT_TEMPLATE.md skutečnými hodnotami a oddělit standardní kritérium H1/H2
od silnějšího tvrzení efekt≥margin. Nesmí chybět nejistota, n, provozní první/konečná
úspěšnost, neznámé ceny, lidská práce a ≥8 unikátních chybových/úspěšných úloh podle
analysis/README.md. Příčinu bez důkazu označit unknown; změna P3 není důkaz opravy mechanismu.
Praktické závěry omezit na testované produkty a období.

Učitel dostane propojené artefakty podle README, manifesty a kontrolovatelné důkazy.
Po G3 lze publikovat schválený odsanitizovaný balíček: bez tokenů, osobních údajů,
privátních cest, klíčů předčasného zaslepení a neautorizovaných úplných zdrojových textů.
Samotný `results/report.md` není hotová závěrečná práce.
