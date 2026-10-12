# Testovací sada

Existuje **20 dev a 10 val případů** a nově **10 soukromých AI kandidátů**
připravených pro správce Reného. Návrh obsahuje 40 různých úloh; schválený
nezávisle lidsky ověřený holdout a dokončená evidence všech RF/OF zatím chybí. Historické veřejné CIT-031–040 nejsou skrytý test. Validátor ověřuje
schéma a stratifikaci, nikoli pravdivost referencí. Datum v návrhu reference
není důkaz dokončené nezávislé kontroly.

:::{table} Složení testovací sady
:label: tbl-dataset
:align: center

| Vlastnost | Vývoj: skutečnost (20) | Validace: skutečnost (10) | Test: soukromý návrh (10) |
| --- | --- | --- | --- |
| Oblasti: věda a zdraví / právo / IT / ekonomika / historie a kultura | 4 / 4 / 4 / 4 / 4 | 2 / 2 / 2 / 2 / 2 | 2 / 2 / 2 / 2 / 2 |
| Jazyk: CZ / EN / CZ+EN | 10 / 9 / 1 | 5 / 4 / 1 | 4 / 5 / 1 |
| Typ: fakt / primární zdroj / syntéza | 10 / 6 / 4 | 3 / 4 / 3 | 5 / 3 / 2 |
| Obtížnost: snadná / střední / těžká | 3 / 11 / 6 | 4 / 4 / 2 | 1 / 6 / 3 |
| Okrajové případy | 9 (45 %) | 4 (40 %) | 4 (40 %) |
:::

Soukromý návrh splňuje kvóty `data/holdout_blueprint.json`, schéma i kontrolu
překryvů. Kritický AI reviewer neidentifikoval sémantickou duplicitu s veřejnými
40 případy. To není lidské schválení ani důkaz nepřítomnosti tréninkové kontaminace.
Následující příklady a počty jsou pouze z veřejných dev/val; obsah testu se před G2 nezveřejňuje.

## Okrajové případy

| Okrajový případ | Dev + val: skutečný počet | Příklad z vývojové sady | Co je správné chování |
| --- | --- | --- | --- |
| Nepravdivý předpoklad | 2 | „Proč musí mít kandidát do Senátu ČR alespoň 35 let?" | Opravit na 40 let, čl. 19 odst. 2 Ústavy |
| Protichůdné zdroje | 2 | Nadmořská výška Sněžky (1602 vs. 1603 m) | Uvést obě hodnoty a důvod rozdílu |
| Chybějící informace | 3 | Přesné datum narození Shakespeara | RF: přiznat, že přesné datum není známo; křest je pouze OF |
| Nejednoznačné zadání | 2 | „Kdy vznikla Česká republika?" | RF: samostatná ČR 1. 1. 1993; 1969/1990 jsou pouze OF |
| Časové omezení | 1 | Aktuální sazba ECB, jen zdroje z posledních 30 dní | Uvést hodnotu, datum účinnosti a datum zdroje |
| Nedávná změna faktu | 1 | Podpora Windows 10 a program ESU | Ověřit stav pro daný produkt a datum |
| Kombinace češtiny a angličtiny | 2 | Co znamená SBOM a který exekutivní příkaz ho prosadil | Odpovědět česky, termíny ponechat |

## Schéma případu

Schéma obsahuje všech 13 polí zadání: `task_id`, `capability`, `task_type`,
`difficulty`, `language`, `development_validation_test_split`, `user_prompt`,
`context_or_files`, `expected_properties`, `reference_answer_or_tests`,
`edge_case_type`, `evaluation_method`, `source_or_provenance`. V2 navíc
odděluje `required_facts` (RF), `optional_facts` (OF) a
`required_constraints` (RC). `key_facts` je alias RF. Vynechání OF se netrestá.

## Ochrana testovací sady

- Nový návrh vznikl přímo mimo Git pro správce Reného; čeká na jeho kontrolu. Historické zveřejněné kandidáty nelze použít jako skrytý test ani po přejmenování.
- Autor promptu P3 soubor neotevře, dokud není P3 zmrazený.
- Hash SHA-256 souboru zapíšeme do protokolu před prvním během. Skript `validate_cases.py` hlídá, aby se test nepřekrýval s vývojem (podobnost otázek nad 0,5).

:::{note} Navedení v otázce
Část dev případů s protichůdnými zdroji rozpor v otázce nenaznačuje. U soukromého návrhu jsou doložené agregované počty; lidské potvrzení významu
okrajových případů a referencí zůstává součástí G1.
:::

:::{note} Dynamické případy
RUN_DAY reference se doloží zvlášť pro každý UTC den dokončených běhů,
se skutečnou hodnotou, locatorem, časem a snapshotem/SHA-256. Původní
zmrazená reference se nepřepisuje.
:::

## Etika dat

Všechny dotazy jsou syntetické a vytvořil je tým. Ptáme se jen na veřejně dostupná fakta, bez osobních údajů, důvěrných dat a autorsky chráněných textů. Ke každému případu uvádíme původ a datum ověření.
