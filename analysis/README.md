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
