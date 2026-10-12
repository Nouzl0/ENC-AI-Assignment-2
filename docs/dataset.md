# Testovací sada

Sada má 40 případů v rozdělení 20/10/10 (vývoj / validace / test držený stranou) a 18 z nich (45 %) testuje okrajovou podmínku. Každá část pokrývá všech pět oblastí rovnoměrně. Referenční odpovědi a zlaté zdroje jsme ověřili na otevřených primárních zdrojích 29. 9. 2026.

:::{table} Složení testovací sady
:label: tbl-dataset
:align: center

| Vlastnost | Vývoj (20) | Validace (10) | Test držený stranou (10) |
| --- | --- | --- | --- |
| Oblasti: věda a zdraví / právo / IT / ekonomika / historie a kultura | 4 / 4 / 4 / 4 / 4 | 2 / 2 / 2 / 2 / 2 | 2 / 2 / 2 / 2 / 2 |
| Jazyk: CZ / EN / CZ+EN | 10 / 9 / 1 | 5 / 4 / 1 | 5 / 5 / 0 |
| Typ: fakt / primární zdroj / syntéza | 10 / 6 / 4 | 3 / 4 / 3 | 5 / 4 / 1 |
| Obtížnost: snadná / střední / těžká | 3 / 11 / 6 | 4 / 4 / 2 | 3 / 3 / 4 |
| Okrajové případy | 9 (45 %) | 4 (40 %) | 5 (50 %) |
:::

## Okrajové případy

| Okrajový případ | Počet | Příklad z vývojové sady | Co je správné chování |
| --- | --- | --- | --- |
| Nepravdivý předpoklad | 3 | „Proč musí mít kandidát do Senátu ČR alespoň 35 let?" | Opravit na 40 let, čl. 19 odst. 2 Ústavy |
| Protichůdné zdroje | 3 | Nadmořská výška Sněžky (1602 vs. 1603 m) | Uvést obě hodnoty a důvod rozdílu |
| Chybějící informace | 4 | Přesné datum narození Shakespeara | Přiznat, že není známo; uvést křest 26. 4. 1564 |
| Nejednoznačné zadání | 2 | „Kdy vznikla Česká republika?" | Rozlišit 1969, 1990 a 1993 |
| Časové omezení | 2 | Aktuální sazba ECB, jen zdroje z posledních 30 dní | Uvést hodnotu, datum účinnosti a datum zdroje |
| Nedávná změna faktu | 2 | Podpora Windows 10 a program ESU (prodloužen do 2027) | Uvést aktuální stav, ne zastaralý |
| Kombinace češtiny a angličtiny | 2 | Co znamená SBOM a který exekutivní příkaz ho prosadil | Odpovědět česky, termíny ponechat |

## Schéma případu

Schéma odpovídá zadání: `task_id`, `capability`, `task_type`, `difficulty`, `language`, `development_validation_test_split`, `user_prompt`, `context_or_files`, `expected_properties`, `reference_answer_or_tests`, `edge_case_type`, `evaluation_method` a `source_or_provenance`. Přidali jsme `domain`, `key_facts`, `gold_sources` a `reference_valid_as_of`.

## Ochrana testovací sady

- Testovací případy v tomto dokumentu neuvádíme. Jsou jen v souboru `data/cases_test.jsonl`. Správce dat ho po stažení balíčku přesune mimo sdílenou složku a do G2 v ní nechá jen hash.
- Autor promptu P3 soubor neotevře, dokud není P3 zmrazený.
- Hash SHA-256 souboru zapíšeme do protokolu před prvním během. Skript `validate_cases.py` hlídá, aby se test nepřekrýval s vývojem (podobnost otázek nad 0,5).

:::{note} Navedení v otázce
Část případů s protichůdnými zdroji rozpor v otázce záměrně nenaznačuje. Jinak by P2 (pravidla 5–8) zvýhodňovalo jen to, že systém dostane nápovědu. Testovací sada pokrývá 5 ze 7 typů okrajových případů; nejednoznačné zadání a kombinaci češtiny s angličtinou vyhodnotíme jen popisně na vývoji a validaci.
:::

:::{note} Dynamické případy
Sazba ECB a míra nezaměstnanosti se mění. Hodnotitel proto ověří referenci v den běhu na oficiální stránce uvedené v `gold_sources`.
:::

## Etika dat

Všechny dotazy jsou syntetické a vytvořil je tým. Ptáme se jen na veřejně dostupná fakta, bez osobních údajů, důvěrných dat a autorsky chráněných textů. Ke každému případu uvádíme původ a datum ověření.
