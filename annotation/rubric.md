# Rubrika lidského hodnocení (v1.1, návrh před G1)

**Ještě není zmrazená.** Kalibrace na 2 dev úlohách × zahrnuté produkty (10 pilotních
odpovědí standard / 8 při zdůvodněných 4 produktech), navíc před G1; po G1 nová celá dev sada.
Po G1 nelze potichu měnit
kritéria. Nutná změna = datovaná odchylka, nové hashe a jednotné přehodnocení všech dotčených odpovědí,
nikoli pouze 25% dvojitě hodnoceného vzorku. Původní nezávislé ratingy uchovat.

Hodnotitelé nevidí systém, podmínku ani klíč. Pořadí je náhodné. **Zaslepení je částečné:** formát
odpovědi či styl citace může podmínku/produkt naznačit; neodhadovat identitu. Druhý hodnotitel
nedostává automatické nápovědy. Každý citovaný zdroj otevřít, automatika nikdy není lidský rating.

## 1. Jednotka hodnocení: všechna unikátní faktická tvrzení

- Číslo, datum, jméno, definice, vztah nebo kauzální výrok, který lze ověřit. Projít **celou odpověď**,
  nejen seznam TVRZENÍ/CLAIMS. Není limit osmi tvrzení.
- Skript navrhne věty z ODPOVĚĎ/ANSWER i seznam tvrzení. Exact duplicity sjednotí; významové duplicity
  sjednotí člověk. Počítat stejný fakt jednou, zachovat jeho skutečně přiřazené citace.
- Složený výrok rozdělit na atomické tvrzení (T2a/T2b); nezdědit citaci, která patřila jen jinému výroku.
- Citovaný úryvek P3 slouží jako důkaz, není dalším tvrzením asistenta. Ověřit věrnost i relevanci úryvku.
- Doplnit přehlédnuté tvrzení (Tx1, …); odstranit nefaktickou vatu. Odmítnutí může mít n_claims=0.
- Každý řádek musí mít **unikátní** `pair_id = <blind_answer_id>-<claim_id>-<citation_n nebo none>`.
  Při rozdělení změnit i pair_id: např. A123-T2a-1 a A123-T2b-1. Jinak skórování skončí chybou.
- Aktualizovat `n_claims` na počet unikátních claim_id a potvrdit `segmentation_reviewed=yes`.

Stejný postup platí pro P1, P2 i P3. Počet navržených tvrzení není hotová lidská segmentace.

## 2. Rating explicitní dvojice tvrzení–citace

Otevřít URL → najít pasáž → zvolit první vyhovující kategorii:

| Rating | Pravidlo | Kotva z dev |
| --- | --- | --- |
| FAB | URL/DOI/dokument skutečně neexistuje ani po druhé kontrole a hledání v archivu; nebo značka nemá zdroj | Vymyšlený DOI, [3] bez zdroje |
| NA | Obsah nelze ověřit: paywall bez abstraktu, login, 403, nečitelné PDF; nedostupnost není důkaz neexistence | Nepřístupný plný článek CIT-001; dostupný abstrakt naopak lze hodnotit |
| S2 | Zdroj výslovně uvádí tvrzení nebo z něj přímo plyne; stejná přesnost čísel | ČÚZK 1603,296 m → 1603 m (CIT-004) |
| S1 | Podporuje jen část nebo užší/slabší výrok | Vyhrazené stavby zaměněné za všechny (CIT-005) |
| S0 | Tvrzení neobsahuje nebo mu odporuje | NNDC 5700 ± 30 oproti tvrzení 5568 (CIT-003) |

Zaokrouhlení podle uvedené přesnosti je S2, jiné číslo S0, nikoli S1. Datum musí sedět v přesnosti tvrzení.
Starý zdroj, který opravdu tvrdí starou hodnotu, může být S2, ale nese E6 a snižuje správnost odpovědi.
S2 hodnotí vztah ke zdroji, **není automaticky pravda nebo správná odpověď**.

Více explicitních citací = každý pár zvlášť; úplnost vyžaduje aspoň jednu explicitní S2 u tvrzení.
`citation_n` prázdné = nevyplňovat rating, označit E9. URL může být chybějící, pokud je FAB kvůli neexistující značce.

### Nepřiřazený seznam zdrojů (`citation_n=*`)

Člověk může do `rater_source_n` vybrat nejlépe podporující zdroj a ohodnotit jej. To měří pouze
**diagnostickou dohledatelnou podporu** (`unlinked_support`), nikoli správnost atribuce asistenta.
Tyto řádky nevstupují do hlavní přesnosti, úplnosti, pokrytí povinných faktů ani hlavní kappy.
Nejsou-li žádné explicitní dvojice, hlavní přesnost je 0. Značky do originální odpovědi nedoplňovat.

## 3. Důkaz a diagnostika dvojice

| Pole | Vyplnění |
| --- | --- |
| source_tier | 1 primární/oficiální; 2 renomovaný sekundární; 3 ostatní |
| time_ok | yes/no u time_constraint; datum stránky ověřit člověkem, auto_published je jen nápověda |
| evidence_url | Skutečně čtená URL; může být archiv/abstrakt téhož dokumentu. Změnu doložit. Prázdné jen při FAB explicitní značce bez URL i zdrojového záznamu; nevymýšlet URL. |
| evidence_checked_at | Datum a čas v ISO 8601 s časovým pásmem |
| evidence_locator | Stránka PDF, odstavec, tabulka nebo oddíl; u S0 popis zkontrolovaného rozsahu |
| evidence_excerpt | Krátký vlastní popis nebo nejvýše 25 slov z jednoho zdroje; respektovat práva |
| evidence_snapshot, evidence_sha256 | Cesta k uloženému snímku/exportu a SHA-256; neukládat jen URL k měnící se stránce |
| evidence_archive_url | Archivovaná URL, pokud existuje a lze ji použít |
| error_code | Jeden hlavní E1–E11; E6/E7 může být i při S2 |
| rater, comment | Identifikátor hodnotitele a zdůvodnění |

Doklad nedostupnosti je také důkaz (např. snímek 403), nikoli falešná pasáž. Snapshoty s copyrightem
uchovat pro kontrolu soukromě, veřejný balíček nemusí zveřejňovat celý obsah stránky.
U FAB značky bez zdroje musí locator a evidence_excerpt popsat chybějící [n] v originálu
a jeho seznamu, evidence_snapshot + hash je skutečný doklad této absence (odpověď/log).
Čas kontroly a všechny tyto doklady zůstávají povinné; prázdná URL není výjimka pro
NA/S2 ani pro neexistující stránku s uvedenou URL. Tam zaznamenat kontrolovanou URL.

## 4. Odpověď a povinné vs. doplňkové fakty

`required_facts` (alias `key_facts`) jsou pouze požadavky otázky a nutné opravy chybných předpokladů.
`optional_facts` a rozšiřující referenční text jsou bonusový kontext. **Jejich vynechání nesnižuje skóre.**
Správné parafráze přijmout; fakt může být jednoznačný z otázky a odpovědi, není nutné opakovat rok otázky.
Chybný dobrovolně přidaný fakt se ale počítá jako chyba.

| Pole | Pravidlo |
| --- | --- |
| correctness | 2: všechny povinné fakty správné, žádná podstatná věcná chyba; 1: částečná odpověď/mírná nepřesnost; 0: chybně zodpovězený hlavní dotaz, neopravený falešný předpoklad, vymyšlená přesná hodnota nebo žádná odpověď |
| n_key_facts | Počet required_facts; **neměnit** |
| key_facts_supported | Počet správně uvedených povinných faktů s explicitní S2 podporou |
| key_fact_evidence | JSON mapování RF1, RF2… na pair_id S2, např. {"RF1":["A123-T1-1"]}; bez podpory `{}`. Počet klíčů musí být key_facts_supported. Jeden pár může dokládat více faktů, jen pokud to zdroj skutečně umožňuje. |
| acknowledges_uncertainty | yes/no u missing_info/ambiguous, jinak na |
| check_minutes | Skutečný čas **anotace**, ne uživatelský čas opravy; včetně všech dvojic |

Kotvy správnosti:
- CIT-008: 2 = opraví 35 na 40 a určí čl. 19; 0 = vysvětluje proč 35.
- CIT-019: 2 = 1. 1. 1993 jako vznik samostatného státu; 1969 a přejmenování 1990 nejsou povinné.
- CIT-020: 2 = přesné datum narození není doloženo; křest je bonus. 0 = 23. 4. uvedené jako doložený fakt.
- CIT-007: 2 = 12 % s odpovídajícím zdrojem; předchozí sazba ani nápoje nejsou povinné.

Dynamické reference RUN_DAY ověří správce dat v den běhu **odděleným datovaným záznamem**
(`run_day_evidence.csv`, šablona v annotation), přesně jeden řádek na RF/OF každé
dokončené úlohy × UTC den. Včetně dev/val i různých repeat dnů: hodnota/ukazatel/platnost,
URL, čas kontroly tentýž UTC den, locator, shrnutí/krátký úryvek a snapshot + SHA-256.
Hodnotitel dostává odpovídající denní referenci; zmrazenou referenci nepřepisovat.

## 5. Kódy chyb (jednou za unikátní tvrzení a kód)

E1 vymyšlený zdroj; E2 nepodporující zdroj; E3 přehnané zobecnění; E4 záměna citací;
E5 zkreslené číslo/datum; E6 zastaralost/časový limit; E7 nevhodná kvalita zdroje;
E8 obecná citace; E9 chybějící citace; E10 přijatý chybný předpoklad; E11 ignorovaný rozpor.

## 6. Kalibrace, nezávislost a neshody

1. Pilot z dev, kotvy a kalibrace **před G1**. Pilotní výstupy po poslední změně rubriky znovu ohodnotit.
2. Hodnotitel 1 hodnotí všechny dokončené odpovědi; hodnotitel 2 náhodný stratifikovaný
   vzorek ≥25 %, ceil v každém stratu fáze×produkt×podmínka. Předvybraná ID zachovat.
   Nikdo nehodnotí vlastní běhy; pro dvojité hodnocení a nerozhodnuté neshody zajistit externího hodnotitele,
   pokud dvoučlenný tým tyto role nezvládne oddělit. Po selhání bez odpovědi se nulové skóre odvozuje z manifestu.
3. Nezávislé listy před diskusí uložit jako *_rated_rater1.csv / *_rated_rater2.csv a dál je neměnit.
   Score odmítá duplicity. U různých segmentací počítá kappu jen ze srovnatelných odpovědí a ztrátu pokrytí hlásí.
   Počet tvrzení je jen hrubá diagnostika, ne důkaz shodných hranic. Je-li nutné sjednocení jednotek,
   provést je bez znalosti ratingů a nové nezávislé hodnocení verzi označit; původní data archivovat mimo aktivní vstup.
4. Kappa S2 vs ostatní cíl ≥0,6. Konstantní ratingy → kappa nedefinovaná (uvést surovou shodu a n).
   Nízká kappa po G1 je výsledek/limit, ne povolení přepsat jen problematický vzorek.
5. Kategorické neshody **i každou změnu final oproti raw1** zapsat do disagreements.csv
   podle šablony, také při raw shodě nebo jediném hodnocení. Přesná raw/final hodnota,
   field, resolution, resolved_by a note; nová/odebraná dvojice se audituje present=yes/no.
   Různý vlastní check_minutes dvou lidí není neshoda, jeho změna ve final ale audit vyžaduje.
   Nerozhodnuté řeší třetí člověk. Teprve poté vznikají finální pairs_rated.csv /
   answers_rated.csv. Finální konsenzus se nepoužije pro výpočet nezávislé shody.
6. Zdrojové rozhodnutí doložit do 7 dní po odpovědi. Zachovat čtyři původní exportované
   *_to_rate*.csv beze změny; ratingy zapisovat do kopií. Klíč a jeho adresář hodnotitelům
   nepředávat. Před G3 vyplnit audit/denní evidence, ne nahrazovat je prázdným headerem.

## Historie

| Verze | Změna |
| --- | --- |
| 1.0 (2026-09-29) | Původní návrh |
| 1.1 (příprava před G1) | Povinné/bonusové fakty, explicitní atribuce, všechna tvrzení, unikátní ID, evidenční mapování, neměnná rubrika a poctivé IRR |
