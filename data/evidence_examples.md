# Vyplněná ukázka reference evidence (pouze DEMO)

**Smyšlená offline data, ne nezávisle ověřený gold.** Ukázka vysvětluje vyplnění CSV,
RF/OF, oddělení požadavku od skutečné hodnoty, platnost a snapshot/hash. Neotevírá web,
nepoužívá produkty, neměří výkon ani nenahrazuje pilot či lidskou kontrolu.

Z kořene repozitáře vytvořte novou absolutní složku mimo Git a mimo ostrý `$WORK`:

```bash
python3 scripts/make_evidence_example.py --out "$HOME/czai-evidence-DEMO-v1"
```

Existující složka, cesta do repo i symlink zpět do repo se odmítnou. Výstup obsahuje
**vyplněné** `source_evidence.csv` (5 řádků), `run_day_evidence.csv` (4 řádky), dva celé
smyšlené zdroje, jejich skutečné SHA-256 a `reference_units_DEMO.json`. Poslední soubor
ukazuje jen referenční jednotky dvou příkladů, není úplná sada úloh ani holdout.

## Statická reference: jiný text požadavku a odpovědi

Stanici Alfa provozuje smyšlený Ústav Beta od roku 2010. Její výpis z 1. 1. 2026
uvádí 78 měření a průměrnou hloubku 12,34 m. Statická otázka žádá počet a provozovatele;
rok zahájení je bonus. Vygenerované řádky zahrnují:

| task_id | fact_id / reference_kind | fact_text | reference_value | valid_as_of |
| --- | --- | --- | --- | --- |
| DEMO-EVIDENCE-STATIC | RF1 / required | Počet měření stanice Alfa dne 2026-01-01 UTC. | 78 měření dne 2026-01-01 UTC | 2026-01-01 |
| DEMO-EVIDENCE-STATIC | RF2 / required | Provozovatel stanice Alfa. | Ústav Beta | 2026-01-01 |
| DEMO-EVIDENCE-STATIC | OF1 / optional | Rok zahájení provozu stanice Alfa. | 2010 | 2026-01-01 |

`fact_text` přesně odpovídá danému RF/OF; `reference_value` je doložená odpověď,
nikoli automatická kopie požadavku. Každý řádek má URL `fixture.invalid` (zástupná,
neotevírat), locator řádku, vlastní shrnutí, čas s UTC offsetem, absolutní cestu ke
snapshotu a SHA-256 právě jeho bytes. `archive_url` je prázdné, protože veřejný archiv
neexistuje. U skutečného zdroje se jeho existence nesmí vymyslet.

## RUN_DAY: zmrazený požadavek, oddělené aktuální hodnoty

Dynamická otázka žádá aktuální počet měření (RF1); hloubka je bonus (OF1).
Počáteční G1 reference má RF1=78 a OF1=12,34 m, `valid_as_of=2026-01-01`, protože jde
o UTC datum počáteční kontroly, nikoli doslovné `RUN_DAY`. Vygenerované denní řádky:

| task_id | run_date (UTC) | fact_id | reference_value |
| --- | --- | --- | --- |
| DEMO-EVIDENCE-DYNAMIC | 2026-01-01 | RF1 | 78 měření |
| DEMO-EVIDENCE-DYNAMIC | 2026-01-01 | OF1 | 12,34 m |
| DEMO-EVIDENCE-DYNAMIC | 2026-01-04 | RF1 | 82 měření |
| DEMO-EVIDENCE-DYNAMIC | 2026-01-04 | OF1 | 12,36 m |

Oba dny mají vlastní celý lokální snapshot/hash a `checked_at` v příslušném UTC dni.
Pozdější změna **nepřepisuje G1 CSV, reference ani snapshot**. Skutečné denní doklady
se získávají pro každý den dokončených RUN_DAY běhů včetně dev/val/repeat, právě jednou
na task_id×UTC den×RF/OF. Hodnotitel musí dostat správnou denní referenci.

## Co nahradit ve skutečném experimentu

Ukázka má **verification_status=DEMO_NOT_VERIFIED** a **verified_by=DEMO generator,
nikoli člověk**. Záměrně **neprojde G1/G3**. Ani správný hash neověřuje skutečný fakt.
Nesmí stačit přepsat tyto dvě buňky na `verified` a lidské jméno.

Nezávislý reference_checker získá skutečný zdroj, zkontroluje hodnotu, jednotky,
období, všechny RF/OF a oprávnění ke sdílení; uloží vlastní doklady/čas/identitu a teprve
pak `verification_status=verified`. Před podpisem G1 musí být vše hotové. RC požadavky
na typ zdroje či formát nejsou RF/OF: později patří do `constraint_results` ratingu
konkrétní odpovědi. Odkazy: [datový kontrakt](README.md), [brány](../freeze/README.md),
[praktický postup](../HANDOFF.md).
