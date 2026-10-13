# Historie verzí promptů

Každá změna promptu = nový záznam. Hash SHA-256 spočítá `scripts/make_run_plan.py`
(sloupec `prompt_sha256`) nebo `sha256sum prompts/*.txt`. Aktuální soubory jsou návrhy,
**ne výsledky dev/val**; P3_final neexistuje. Historické datum/autor v tabulce je původní
návrhový záznam, nikoli nezávislé schválení nebo datum budoucího benchmarku.

| Verze | Soubor | Datum | Autor | Změna | Důvod (typ chyby z vývojové sady, počet výskytů) | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| P1 v1.0 | P1_baseline_cs.txt / _en.txt | 2026-09-29 | tým | Šablona ze zadání + věta o formátu | Povinná společná výchozí podmínka | doplnit |
| P2 v1.0 | P2_structured_cs.txt / _en.txt | 2026-09-29 | tým | Role, cíl, 8 pravidel, schéma výstupu, postup při nejistotě | Návrh před měřením; znalost návrhových dat nelze vyloučit | zaznamenat při G1 |
| P3-A v0.1 (návrh) | P3A_candidate_cs.txt / _en.txt | 2026-09-29 | tým | Pravidlo 2: doslovný úryvek ze zdroje (≤ 25 slov) ke každému tvrzení | Hypotéza E2/E5; **doložit ≥3 chybnými dev odpověďmi, jinak upravit/přiznat nepotvrzení** | zaznamenat při val |
| P3-B v0.1 (návrh) | P3B_candidate_cs.txt / _en.txt | 2026-09-29 | tým | P3-A + pravidlo 9: kontrola tvrzení před odesláním | Hypotéza E2/E3, **zatím nepotvrzená** | zaznamenat při val |
| P3-B v0.2 (aktuální návrh před G1) | P3B_candidate_cs.txt / _en.txt | přípravná revize, před měřením | příprava s AI asistencí | Pravidlo 9 uznává výslovnou oporu i transparentní přímé vyplývání, zaokrouhlení/výpočet bez nedoložených předpokladů | Soulad s rubrikou; **není dev optimalizace ani naměřené zlepšení**, skutečné dev důvody nadále doplnit | zaznamenat při val |
| P3 v1.0 (budoucí, dosud nevytvořen) | P3_final_cs.txt / _en.txt | doplnit skutečné datum po val | doplnit autora | Přesná kopie vybraného změřeného kandidáta | Doplnit val metriky, délky a pravidlo výběru | skutečné CZ/EN hashe do G2 |

## Pravidla

1. Úprava P3 je povolena proti typu chyby doloženému alespoň ve třech **chybných dev odpovědích**,
   ne třemi tvrzeními téže odpovědi. Zapsat task_id/run_id, kód, počet a zdrojové doklady;
   domnělý mechanismus označit jako hypotézu, pokud chybí přímý důkaz.
2. Žádné pokyny pro konkrétní případy, žádné informace z testovací sady.
3. Žádné úpravy P3 specifické pro jeden systém. Nutná změna rozhraní musí být předem
   zdokumentovaná, ne skryté produktové ladění. Uvést délky CZ/EN a počet těchto rozdílů.
4. Před G1 zvolit jeden nebo oba kandidáty. Jedna val matice: vyšší průměr hlavní
   přesnosti přes všechny produkty/úlohy; rozdíl < 0,02 → kratší průměr CZ/EN délky
   šablony ve znacích, při stejné délce P3A. Jeden kandidát se vybere automaticky.
   Pokud žádný kandidát nepřekoná P2, použije se lepší z nich a neúspěšná optimalizace se vykáže jako výsledek;
   **po val není dovoleno další kolo ladění** v tomto experimentu. Další iterace = nový deklarovaný návrh.
5. Po výběru přesně zkopírovat vítěze do `P3_final_cs.txt` a `P3_final_en.txt`, zaznamenat
   skutečné hashe v tomto záznamu a G2, nikoli přepsat od G1 zmrazený PROTOCOL.md.
   Test lze plánovat až se skutečně schváleným G2 (`--freeze`).

## Záznam budoucí dev změny / finální volby

Pro každou změnu doplnit: skutečné datum, autor, stará/nová verze a CZ/EN SHA-256,
konkrétní obecná změna, ≥3 dev run_id a kódy, předpokládaný mechanismus/jistota,
val metriky všech plánovaných kandidátů a P2, délky, aplikované pravidlo výběru,
zlepšení nebo zhoršení a odkaz na selection_record/G2. Prázdná šablona není důkaz.


## 13. 10. 2026 – samostatný doplňkový sběr

P1/P2 a kandidát P3A byly byte/hash fixovány před vytvořením10nových oddělených otázek (záznam `runs/supplement-2026-10-13/gemini-grok/supplement_freeze.json`). Žádná šablona se po otevření těchto otázek neupravovala. Obecný mechanismus P3A (citovat konkrétní podpůrný úryvek) reaguje na skutečné dev nálezy v CIT001Perplexity(E4), CIT004Grok(E2) a CIT008Perplexity(E5), popsané v analýze a AI auditu; nejde o prokázané zlepšení. Kandidát byl zvolen předem, nikoli vyhlášen vítězem neprovedené validace. Pět nových otázek má skutečné P1/P2/P3A; kompletní přenositelnost napříč produkty nelze z této matice odhadnout. Původní P3_final a G2 se netvrdí.
