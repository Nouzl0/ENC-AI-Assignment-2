# Revize dat před G1

Změny se týkají **pouze dev/val**, nikoli tvorby nebo ladění nového holdoutu podle známých výsledků.
Původní data zůstávají v git historii. Nové referenční hodnoty ani údajné dokončené ověření nevymýšlíme.

- Všech 30 případů dev/val: schema_version=2; required_facts, optional_facts; key_facts je alias povinných faktů.
- CIT-001 interval, CIT-002 podmíněných 5 %, CIT-005 přechodné období, CIT-007 starší DPH/nápoje,
  CIT-010 datum konce ESU, CIT-012 NTIA/datum EO, CIT-013 přesný okamžik sčítání, CIT-016 odhady,
  CIT-019 federace/přejmenování, CIT-020 křest/tradice, CIT-021 rok ocenění, CIT-029 stavební data:
  nevyžádané podrobnosti přesunuty mimo povinný jmenovatel. Pokud jsou uvedeny, stále musí být správné.
- CIT-003: nenutí všechny historické hodnoty v otázce, která je nežádá; přijatelné hodnoty z původní reference
  zůstávají, konvenční Libbyho hodnota není automaticky totéž jako současné měření.
- CIT-012: povinná definice SBOM, nejen rozepsaná zkratka; CIT-025 libovolný odkaz na originál, ne jen konkrétní arXiv ID.
- CIT-027: jednoznačně určený ukazatel, nikoli nevyžádané srovnání obou ukazatelů.
- CIT-002: odstraněno chybné synonymum „(přidaných)“. WHO pod volné cukry zahrnuje i cukry přirozeně přítomné
  v medu, sirupech a šťávách, nejen přidané. [Primární definice a doporučení WHO](https://www.who.int/news-room/detail/04-03-2015-who-calls-on-countries-to-reduce-sugars-intake-among-adults-and-children).

## Druhá kritická revize: férovost a evidenční kontrakt (před G1)

- CIT-002: povinná hodnota + libovolný odpovídající oficiální WHO podklad, nikoli skrytě
  konkrétní dokument 2015/označení síly doporučení; dokument 2015 je OF.
- CIT-004: dvě nepřekrývající se RF (výška + vysvětlení rozdílu), ne dvakrát stejná výška.
- CIT-001/014/015/025 a další explicitní požadavky na zdroj/formát přesunuty do RC;
  CIT-027 nevyžádané určení vydavatele odstraněno, CIT-028 rok zahrnut do hodnoty bez duplicity.
- CIT-025: názvy požadovaných polí nahrazeny konkrétními draft hodnotami již uvedenými
  v původní referenci. Nejde o nové nezávislé ověření.
- Všech 30 referenčních textů nyní pouze RF/OF; nezapsaná rozšíření (např. ceny ESU,
  novela cíle 2040) odstraněna, nikoli označena za nepravdivá. Nová fakta vyžadují OF + důkaz.
- expected_properties sjednoceny s RF + RC ve všech 30 případech; nevynucují nevyžádaného
  vydavatele (CIT-027) ani konkrétní portál pro text GDPR (CIT-023).
- Evidence rozlišuje přesný fact_text a skutečnou reference_value. Zavedena předem
  zveřejněná agregovaná stratifikace nového holdoutu; žádná nová otázka nevytvořena.

**Ještě provést:** správce dat ověří každý povinný i volitelný fakt a zdroj před G1, vyplní source_evidence.csv.
Prázdná šablona není důkaz dokončené kontroly. Dynamické hodnoty navíc ověřit v den skutečného běhu.

## Kontrola primárních podkladů 12. 10. 2026 (před G1)

Read-only AI kontrola prošla všech 30 veřejných případů. Jde o podklady pro lidi,
nikoli lidskou verifikaci G1. Výsledek a mezery jsou v `docs/source-audit.md`.

- CIT-007: opraveno příliš obecné OF o nápojích. GFŘ § 2.2 uvádí výjimky pro
  kohoutkovou pitnou vodu a zákonem vybrané mléčné/rostlinné nápoje; RF jídlo 12 % se nemění.
- CIT-015: doplněn ECB Economic Bulletin 6/2026 z 24. 9. 2026. Původní zpráva
  z 10. 9. již k datu kontroly nesplňuje RC ≤30 dnů. Požadavek otázky se nemění;
  bulletin dokládá MRO 2,65 % od 16. 9. 2026. RUN_DAY zůstává povinný.
- CIT-023: RF2/alias/expected_properties doplněny o podmínku podniku a předchozí
  finanční rok, protože otázka požaduje přesné znění limitu. Přímé otevření EUR-Lex
  bylo zablokované; oprava odpovídá indexovanému primárnímu textu, úplná lidská kontrola zbývá.
- CIT-027: přidány novější konkrétní zdroje ČSÚ (srpen) a ÚP (září) s přesným
  označením odlišných ukazatelů. Starší odkazy zachovány jako historické podklady.
  Nezměněn požadavek jednoznačně pojmenovat ukazatel a měsíc; čísla nejsou zmrazený RUN_DAY gold.
- CIT-007 OF1: doplněn skutečně otevřený historický přehled Finanční správy
  z 6. 6. 2023, s. 2, který uvádí 10 % pro stravování.
- CIT-010 OF1: doplněna datovaná zpráva Microsoft News Center z 30. 6. 2025,
  která dokládá původní konec spotřebitelského ESU 13. 10. 2026; aktuální a historický stav se nepletou.

Neúplně doložené bonusy ani negativní závěry CIT-016/029 nebyly potichu označeny za
ověřené či odstraněny. Po jejich přezkoumání je nutná další výslovná před-G1 revize.
