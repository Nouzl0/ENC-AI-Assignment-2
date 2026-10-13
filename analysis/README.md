# Analýza chyb

Aktuální [rozbor osmi skutečných pilotních úloh](../docs/error-analysis.md)
již obsahuje úspěchy, citační problémy a provozní selhání s kontrolními
pasážemi primárních zdrojů. Jde o pomocnou analýzu AI před G1; níže je
postup pro návaznou finální analýzu po úplném benchmarku a lidských ratingech.

Vyberte **alespoň 8 unikátních task_id** (ne osm odpovědí na tutéž otázku). Doporučení: 12–16 odpovědí
z ≥8 úloh, alespoň dvě za každý systém a alespoň tři úspěšné; pokrýt dostupné okrajové typy.
Pokud všechny typy nejsou v testu, doplnit dev/val a tyto příklady jasně označit. Není nutné předstírat,
že deset testovacích úloh obsahuje všechny okrajové situace.

Správce dat vybírá podle **results/answer_metrics.csv** a finálních párů, ne z agregované tabulky systémů.
Před výběrem stanovit pravidla (např. extrémy + typické případy), nezamlčet protipříklady a úspěchy.

Zapište výňatek, explicitní citaci, rating, kód a důkaz příčiny. `likely_cause` může být retrieval,
attribution, generation **nebo unknown**; z finálního výstupu obvykle nelze spolehlivě zjistit,
co systém skutečně našel/četl. Přidat cause_evidence a cause_confidence, hypotézu nezaměnit za pozorování.

`P3_outcome` = observed_improvement / unchanged / worsened / not_comparable pro stejný task_id + systém.
Jedna lepší odpověď P3 je pozorované zlepšení, **ne prokázané odstranění mechanismu chyby**.
Výsledek uvést i při zhoršení a rozlišit další čas běhu či změnu dostupnosti zdrojů.

## Zaslepené podklady doplňkového sběru

`supplement_review.py` připravuje offline podklady pro skutečné nezávislé lidské
hodnocení z kanonického JSONL registru. Neprovádí ratingy ani kontrolu zdrojů a
nepotvrzuje G1/G2/G3. Použijte samostatné absolutní adresáře mimo worktree:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 analysis/supplement_review.py \
  --registry runs/canonical-2026-10-13/registry.jsonl \
  --cases data/cases_dev.jsonl --cases data/cases_val.jsonl \
  --cases runs/reference-correction-2026-10-13/cases_supplement_v2.jsonl \
  --out-dir /absolute/private/annotation-new \
  --key-dir /absolute/private/key-new
```

Cestu posledního souboru úloh nastavte podle skutečné kanonické verze.
Výstupní adresáře nesmějí existovat; klíč nesmí být uvnitř předávaného balíčku.
Hodnotiteli předejte pouze jeho `rater1/` nebo `rater2/`. První dostane všechny
vybrané dokončené odpovědi, druhý nejméně 25 % v každém stratu
fáze × produkt × podmínka, se zaokrouhlením nahoru. Identické sdílené vstupy mají
stejná zaslepená ID a všechny ratingy začínají prázdné. Klíč, výběr, identity,
provozní selhání, kontrolní hashe a manifest zůstávají výhradně u správce.

Celý text odpovědi se zachová. Navržené citační řádky jsou pouze návrhy k lidské
segmentaci; neobvyklé a nativní značky se nepřečíslují. Katalog URL přebírá jen
skutečně zaznamenané cíle z odpovědi a jejích zdrojových artefaktů. Pro nativní
popover nebo mapu odkazů použijte v registru `citation_artifact_file` a
`citation_artifact_sha256`; artefakt musí obsahovat pouze zachycenou odpověď a
její zdroje. Nejde o důkaz podpory ani o automatické přiřazení jiné reference.
Před vytvořením výstupu se ověří vstupní hashe, unikátní ID a bezpečné cesty.
Neznámé provozní údaje se nedopočítávají a nevkládají do listů hodnotitelů.

`verify_exploratory.py` provádí samostatnou read-only kontrolu kanonického registru.
Používá stejné `--registry` a opakované `--cases`, nevytváří anotační výstupy a
vypisuje JSON report. Ověřuje identitu `collection/run_id`, bezpečné cesty a hashe
všech deklarovaných artefaktů, přesné vykreslení otázky ze šablony a evidence
dokončených vybraných odpovědí. Zachovává také plánované, neúspěšné a vyřazené
řádky. Kontrola nehodnotí správnost odpovědí ani nepotvrzuje metodické brány.
Po stagingu přidejte `--staged` pro porovnání se skutečnými bajty Git indexu;
pro kontrolu konkrétního commitu použijte místo něj `--git-ref <ref>`.
