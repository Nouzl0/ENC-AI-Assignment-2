# Rubrika lidského hodnocení (verze 1.0)

Zmrazení: na bráně G1 po kalibraci na 10 pilotních odpovědích. Pozdější upřesnění (v1.x) jen před hodnocením validační sady a vždy se zápisem v historii dole.

Hodnotíme dvě věci: **dvojice tvrzení–citace** (`pairs_to_rate.csv`) a **odpověď jako celek** (`answers_to_rate.csv`).
Hodnotitel nevidí systém ani podmínku. Každý zdroj otevře v prohlížeči, i když automatická kontrola něco navrhuje.
Kotvy pocházejí jen z vývojové sady.

## 1. Dělení na tvrzení (stejná pravidla pro všechny podmínky)

Skript navrhne výchozí dělení: u P2/P3 převezme seznam `TVRZENÍ` / `CLAIMS` (`segmentation = system`),
u P1 rozdělí text po větách (`segmentation = auto_sentence`). **Hodnotitel pak u každé odpovědi, bez ohledu na podmínku,
použije stejná pravidla:**

- Faktické tvrzení = číslo, datum, jméno, definice, vztah nebo kauzální výrok, který lze ověřit.
- Složené tvrzení se dvěma fakty rozdělí na dva řádky (kopie řádku, `claim_id` T2a/T2b; citace zůstává u obou).
- Faktické tvrzení z části ODPOVĚĎ, které v seznamu TVRZENÍ chybí, doplní jako nový řádek (`claim_id` Tx1, …).
- Větu bez faktického obsahu („Doufám, že to pomůže.") smaže.
- Zachová nejvýš 8 tvrzení v pořadí výskytu v celé odpovědi.

Shodu v dělení (počet tvrzení na odpověď) mezi hodnotiteli vykazuje `score.py`, protože rozdílné dělení v P1 a P2 by jinak
mohlo zkreslit hypotézu H2.

## 2. Hodnocení dvojice tvrzení–citace (`rating`)

Postup: otevřete URL → najděte místo, které tvrzení dokládá → zvolte první sedící kategorii.

| Hodnocení | Pravidlo | Kotva (vývojová sada) |
| --- | --- | --- |
| **FAB** | URL/DOI neexistuje (404/410/DNS i při druhém pokusu) a stránku nenajdete ani v archivu (web.archive.org); nebo značka [n] nemá záznam ve zdrojích | Vymyšlený DOI; `[3]` v textu, ale ve zdrojích jen [1] a [2] |
| **NA** | Stránka existuje, ale obsah nelze přečíst: paywall bez abstraktu, přihlášení, 403, nečitelné PDF | Článek NEJM (CIT-001) za paywallem bez abstraktu |
| **S2** | Zdroj tvrzení výslovně uvádí nebo z něj přímo plyne; čísla sedí v uvedené přesnosti | „Sněžka měří 1603 m" + stránka ČÚZK s 1603,296 m (CIT-004) |
| **S1** | Zdroj podporuje jen část tvrzení, nebo je tvrzení silnější či obecnější než zdroj | „Nový stavební zákon platí od 1. 1. 2024 pro všechny stavby" + zdroj, který mluví jen o vyhrazených stavbách (CIT-005) |
| **S0** | Zdroj tvrzení neobsahuje nebo mu odporuje | „Poločas rozpadu C-14 je podle NNDC 5 568 let" + stránka NNDC s 5 700 ± 30 let (CIT-003) |

**Tolerance čísel:** zaokrouhlení na přesnost, kterou tvrzení uvádí, je S2 (1603,296 m → „1603 m"). Jiná hodnota je S0, nikoli S1.
Data musí sedět přesně (den, měsíc, rok), pokud je tvrzení uvádí. Procenta: rozdíl jen zaokrouhlením = S2.

**Zastaralý, ale podporující zdroj:** pokud starý zdroj tvrzení opravdu uvádí, je to **S2** (citace je správná), ale do `error_code` napište **E6** a správnost odpovědi snižte. Příklad: „ESU končí 13. 10. 2026" + článek z roku 2025 (CIT-010).

**Nepřiřazené citace** (`citation_n = *`, zdroje jen na konci odpovědi): do `rater_source_n` napište číslo zdroje, který tvrzení podporuje nejlépe, a hodnoťte tento zdroj. Pokud žádný, napište nejbližší a dejte S0.

**Více citací u jednoho tvrzení:** každá dvojice se hodnotí zvlášť. Tvrzení je „podložené" (úplnost), pokud má aspoň jednu S2.

**Necitované tvrzení** (`citation_n` prázdné): nehodnotí se `rating`, jen případně `error_code = E9`.

## 3. Další sloupce dvojice

| Sloupec | Hodnoty | Pravidlo |
| --- | --- | --- |
| `source_tier` | 1 / 2 / 3 | 1 = primární nebo oficiální (zákon, úřad, původní studie, standard, instituce sama o sobě); 2 = renomovaný sekundární (encyklopedie, velké médium, odborný web); 3 = ostatní (agregátor, blog, diskuse, SEO web) |
| `time_ok` | yes / no / prázdné | Jen u `time_constraint_case = yes`: splňuje zdroj limit stáří? Datum hledejte na stránce, `auto_published` je jen nápověda |
| `error_code` | E1–E11 | U každé dvojice s hodnocením jiným než S2 (a u E6/E9 viz výše). Jeden hlavní kód |
| `comment` | text | Krátce: kde ve zdroji je / není doklad |

## 4. Hodnocení odpovědi (`answers_to_rate.csv`)

| Sloupec | Hodnoty | Pravidlo |
| --- | --- | --- |
| `correctness` | 0 / 1 / 2 | 2 = všechny `key_facts` správně a chybný předpoklad opraven; 1 = část klíčových faktů chybí nebo je nepřesná, nebo odpověď nevysvětlí nejednoznačnost; 0 = chybná odpověď, přijatý chybný předpoklad, vymyšlená přesná hodnota tam, kde neexistuje, nebo žádná odpověď |
| `key_facts_supported` | 0 … `n_key_facts` | Kolik z `key_facts` odpověď **uvádí správně a zároveň dokládá citací hodnocenou S2**. Slouží ke kontrole alternativy A1 (systém, který řekne méně, nemá vyšší pokrytí) |
| `acknowledges_uncertainty` | yes / no / na | U `missing_info` a `ambiguous`: přizná odpověď nejistotu nebo rozliší výklady? Jinak `na` |
| `check_minutes` | číslo | Čas hodnocení celé odpovědi včetně všech jejích dvojic (stopky), v minutách |

**Kotvy správnosti (vývojová sada):**

- CIT-008 (Senát, chybný předpoklad 35 let): 2 = opraví na 40 let a cituje čl. 19 Ústavy; 0 = vysvětluje, „proč 35".
- CIT-020 (Shakespeare): 2 = datum narození není známo, křest 26. 4. 1564; 1 = uvede 23. 4. jako tradici bez zmínky o křtu; 0 = „narodil se 23. 4. 1564" jako fakt.
- CIT-019 (vznik ČR): 2 = rozliší 1969, 1990, 1993; 1 = jen 1. 1. 1993 se zdrojem; 0 = jiné datum.

U dynamických případů (`reference_valid_as_of = RUN_DAY`) ověřte referenci na oficiální stránce v den běhu a do `comment` napište hodnotu, kterou jste ověřili.

## 5. Kódy chyb

| Kód | Typ chyby |
| --- | --- |
| E1 | Vymyšlený zdroj (URL, DOI nebo dokument neexistuje) |
| E2 | Nepodporující zdroj (existuje, tvrzení neobsahuje) |
| E3 | Přehnané zobecnění (zdroj říká méně / něco užšího) |
| E4 | Záměna citací (fakt je v jiném citovaném zdroji) |
| E5 | Zkreslené číslo nebo datum |
| E6 | Zastaralý zdroj / porušení časového limitu |
| E7 | Méně kvalitní zdroj, i když existuje primární |
| E8 | Obecná citace (domovská stránka, výsledky vyhledávání) |
| E9 | Chybějící citace u faktického tvrzení |
| E10 | Přijatý chybný předpoklad |
| E11 | Ignorovaný rozpor mezi zdroji |

## 6. Kalibrace, dvojité hodnocení a neshody

1. **Kalibrace (pilot, týden T3):** tým spustí 2 vývojové případy na všech 5 systémech (10 odpovědí, jsou součástí fáze dev). Všichni hodnotitelé je ohodnotí, porovnají výsledky a upřesní tuto rubriku. Pak se rubrika zmrazí (G1).
2. **Samostatné hodnocení:** 1. hodnotitel vyplní `pairs_to_rate.csv` a `answers_to_rate.csv` a **před jakoukoli diskusí** je uloží jako `pairs_rated_rater1.csv` a `answers_rated_rater1.csv`. 2. hodnotitel samostatně vyplní `*_to_rate_rater2.csv` (25 % odpovědí) a uloží je jako `pairs_rated_rater2.csv` a `answers_rated_rater2.csv`.
3. **Shoda:** `score.py` spočítá Cohenovu kappu mezi soubory `*_rater1.csv` a `*_rater2.csv`, tedy před smířením. Cíl: kappa (S2 vs. ostatní) ≥ 0,6. Při nižší hodnotě upřesnit rubriku a dvojitě hodnocené odpovědi ohodnotit znovu.
4. **Neshody:** hodnotitelé je proberou; když se nedohodnou, rozhodne třetí. Každou zapsat do `disagreements.csv`. Výsledné (dohodnuté) hodnoty jdou do finálních `pairs_rated.csv` a `answers_rated.csv`; soubory `*_rater1.csv` se už nemění.

## Historie rubriky

| Verze | Datum | Změna | Důvod |
| --- | --- | --- | --- |
| 1.0 | 2026-09-29 | První verze | — |
