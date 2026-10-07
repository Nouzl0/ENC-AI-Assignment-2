# Příprava balíčku (bez provedení benchmarku)

G1/G2/G3 dosud **nejsou splněny**. Nevytváříme výsledky produktů, vítězný P3 ani podpisy kolegy.

| Etapa | Rozsah | Stav |
| --- | --- | --- |
| 1 | Integrita skórování, selhání, úplnost matice, regresní testy | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 2 | Rubrika, povinné vs. doplňkové fakty, explicitní citace, důkazy | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 3 | Soukromý holdout, ověřitelné brány a ochrana artefaktů | hotovo; kritická kontrola + re-kontrola bez blokujících nálezů |
| 4 | End-to-end testy, konzistentní dokumentace a předání kolegovi | čeká |

Po každé etapě: kritický subagent → oprava nálezů → lokální testy → commit → push.
Testy používají jen lokální syntetické vstupy. Aktuální příkaz: `python3 -m unittest discover -s tests -v`.

## Kontrola etapy 1

Opravené nálezy subagenta: přejmenované kopie hodnoticích jednotek v raw IRR, neplatný/chybějící
počet tvrzení a normalizace desetinné čárky v run_index. Re-kontrola bez blokujícího nálezu.
Ověřeno: 14 unittestů, validace dev/val, offline syntetický smoke v dočasné kopii, `git diff --check`.
Smoke náhodných CSV zatím není plný end-to-end test; ten nahradí etapa 4.

## Kontrola etapy 2

Opravené nálezy subagenta: podpůrné úryvky v ANSWER i CLAIMS, konzervativní deduplikace
zachovávající významové symboly a zaokrouhlení vzorku druhého hodnotitele nahoru (≥25 %).
Re-kontrola bez blokujícího nálezu. Ověřeno: 26 unittestů, validace dev/val, offline
syntetický smoke v dočasné kopii a `git diff --check`. Zdroje všech referencí nadále musí
nezávisle ověřit kolega; nová rubrika není podepsané G1 ani hotové hodnocení.

## Kontrola etapy 3

Opravené nálezy subagenta: číselná pole plan sidecaru versus CSV, nezmrazený náhradní
gold při anotaci, stratifikace druhého hodnocení i po fázích, audit každé změny finálního
ratingu a úplné denní RF/OF důkazy v UTC. Re-kontrola bez blokujícího nálezu.
Ověřeno: 40 unittestů, validace dev/val, izolované offline reprodukce a `git diff --check`.
Test G1→G2→G3 používá výhradně dočasné syntetické artefakty; žádná skutečná brána ani
produktové výsledky nevznikly. Veřejný starý test je přejmenován na kandidáty, historie zůstává.
