# Historie verzí promptů

Každá změna promptu = nový záznam. Hash SHA-256 spočítá `scripts/make_run_plan.py` (sloupec `prompt_sha256`) nebo ručně: `sha256sum prompts/<soubor>.txt`.

| Verze | Soubor | Datum | Autor | Změna | Důvod (typ chyby z vývojové sady, počet výskytů) | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| P1 v1.0 | P1_baseline_cs.txt / _en.txt | 2026-09-29 | tým | Šablona ze zadání + věta o formátu | Povinná společná výchozí podmínka | doplnit |
| P2 v1.0 | P2_structured_cs.txt / _en.txt | 2026-09-29 | tým | Role, cíl, 8 pravidel, schéma výstupu, postup při nejistotě | Napsáno před prvním během, bez znalosti dat | doplnit |
| P3-A v0.1 (návrh) | P3A_candidate_cs.txt / _en.txt | 2026-09-29 | tým | Pravidlo 2: doslovný úryvek ze zdroje (≤ 25 slov) ke každému tvrzení | Předpoklad: E2/E5 (nepodporující zdroj, zkreslené číslo). **Potvrdit na vývojové sadě (≥ 3 výskyty), jinak upravit.** | doplnit |
| P3-B v0.1 (návrh) | P3B_candidate_cs.txt / _en.txt | 2026-09-29 | tým | P3-A + pravidlo 9: kontrola tvrzení před odesláním | Předpoklad: E2/E3. **Potvrdit na vývojové sadě.** | doplnit |
| P3 v1.0 (FINÁLNÍ) | P3_final_cs.txt / _en.txt | po validaci | autor promptu | Vítězný kandidát z validační sady | Výsledek validace: doplnit (přesnost P2 / P3-A / P3-B) | doplnit – **zmrazit před testem** |

## Pravidla

1. Úprava P3 je povolena jen proti typu chyby, který se na vývojové sadě objevil alespoň třikrát.
2. Žádné pokyny pro konkrétní případy, žádné informace z testovací sady.
3. Žádné úpravy specifické pro jeden systém (cíl 0; pokud nutné, zapsat sem zvlášť).
4. Výběr kandidáta: vyšší citační přesnost na validační sadě; rozdíl < 2 p. b. → kratší prompt.
   Pokud žádný kandidát nepřekoná P2, použije se lepší z nich a neúspěšná optimalizace se vykáže jako výsledek;
   jedno další kolo úprav je povolené jen na vývojové sadě.
5. Po výběru zkopírovat vítěze do `P3_final_cs.txt` a `P3_final_en.txt`, zapsat hash do `PROTOCOL.md` a teprve pak spustit `make_run_plan.py --phase test`.
