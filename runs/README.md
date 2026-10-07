# Sběr a metadata skutečného běhu

Plán vytvoří správce mimo Git, `--phase dev|val --freeze G1` nebo
`--phase test|repeat --freeze G2`, vždy `--out` s absolutní soukromou cestou.
Viz HANDOFF.md. Pilot je zvlášť s `--pilot`, není součástí analytického dev.
CSV a `.manifest.json` před měřením nezávisle archivovat; **nepřepisovat plán**.
Řádky procházet v pořadí seq, nikoli podle očekávaného výkonu produktu.

## Před sběrem

Ověřit skutečnou dostupnost/nastavení všech produktů: stejná úroveň účtu kde možné,
nový chat bez paměti/personalizace/vlastních instrukcí, žádný Deep Research, stejný
prohlížeč/síť/region. Snímky nastavení a viditelné modely uložit do soukromého setup
záznamu přiloženého k pilot_record. Názvy UI přepínačů jsou proměnlivé, nezaměnit
zamýšlené tool_permissions z plánu za důkaz, že se vyhledávání skutečně použilo.
Nedostupný nástroj nebo nutný odlišný účet vyřešit a zdůvodnit před G1.

## Jeden řádek = jeden analytický běh

1. Nový chat, vložit **přesný prompt_text**. Neměnit question, condition, pořadí ani
   systém. prompt_file/prompt_sha256/rendered_prompt_sha256 jsou kontrolované.
2. Spustit čas při prvním odeslání. Zastavit po konečné odpovědi nebo konečném selhání.
   Při doptání max. jednou odpovědět pouze „Pokračujte podle svého nejlepšího úsudku.“
   / „Proceed using your best judgment.“ podle jazyka, turns=2, čas pokračuje.
3. Uložit původní text/export jako raw_answer_file, snímek celé odpovědi/zdrojového
   panelu jako screenshot_file, share_link pokud existuje. Uchovat i pokus 1 při retry.
4. Normalizovaný text uložit do **předem daného answer_file**. Převádět pouze skutečné
   odkazy/čipy na [n] a seznam zdrojů, neměnit obsah, nedoplňovat neexistující atribuci.
5. Vyplnit konečný stav a metadata, spočítat SHA-256 souborů (např. `sha256sum <cesta>`).
   Všechny artefaktové cesty mají být absolutní, existující, mimo Git.

## Pole

| Pole | Vyplnění |
| --- | --- |
| run_status | planned / completed / failed / excluded podle pravidel níže |
| model_visible, plan_tier | skutečně viditelné označení/úroveň; výslovně unknown, pokud údaj UI nedává |
| datetime_start, datetime_end | ISO-8601 **s offsetem**, např. 2026-10-12T14:03:00+02:00; žádné neurčité lokální časy |
| latency_s | celý interval od prvního odeslání do konečného výsledku, včetně čekání na retry/doptání |
| first_attempt_latency_s | první pokus, bez čekání na pozdější opakování |
| first_attempt_ok, final_attempt_ok | yes/no = vznik odpovědi, ne správnost jejího obsahu |
| retries | 0 nebo 1, pouze provozní retry; opakování fáze repeat je run_index, ne retries |
| failure_type | none, model_output, invalid_format, tool_error, rate_limit, timeout, product_outage; zvlášť chyba operátora |
| search_used | yes/no/unclear podle viditelného průběhu, ne podle dojmu z odpovědi |
| n_sources_shown, tool_calls_visible | nezáporný celý počet nebo unknown; ne nula místo neznámého |
| turns | 1 nebo 2; zdůvodnit standardní doptání v notes |
| operator | skutečná stabilní identita operátora, odlišná od jeho hodnotitelů |
| manual_intervention | none nebo konkrétní popis povolené normalizace/doptání/chyby; nepřepisovat obsah |
| cost_note | skutečný mezní poplatek + měna/metoda, nebo unknown; předplatné samostatně, čas týmu zvlášť |
| share_link, notes | odkaz pokud možný, datované odchylky a kontext; ne osobní údaje/tokeny |
| answer_sha256 | hash normalizovaného answer_file pro completed |
| raw_answer_file, raw_answer_sha256 | původní text/export pro completed; může být tentýž soubor, pokud nebyla normalizace |
| screenshot_file, screenshot_sha256 | snímek odpovědi/zdrojů, nebo chyby; pro všechny konečné stavy |
| attempt1_file, attempt1_sha256 | zachovaný první neúspěšný pokus při retries=1 |
| failure_artifact_file, failure_artifact_sha256 | původní protokol/snímek chyby při failed/excluded |
| replacement_run_id, replaces_run_id | svázaná náhrada chyby operátora, nikdy výmaz původního řádku |

Pokud raw a normalizovaný hash nejsou stejné, manual_intervention nemůže být none.
Čas konce nesmí předcházet začátku, celková latence odpovídá intervalu (tolerance 5 s).
Neznámé provozní počty jsou unknown; časy, konečné stavy a artefakty neodhadovat.
Při chybě evidence nejdřív napravit dokumentaci, ne zapsat „0“ nebo vynechat běh.

## Stavy a selhání

- **completed:** konečná odpověď existuje. I věcná chyba, odmítnutí, chybějící citace
  nebo invalid_format se běžně hodnotí; **neopakovat za účelem lepšího výsledku**.
- **failed:** konečná provozní chyba bez odpovědi; zůstává v matici, přesnost/úplnost/
  správnost/pokrytí=0. Nevyrábět falešnou odpověď nebo anotaci.
- **excluded:** pouze doložený student_error; původní řádek uchovat, stejné experimentální
  pole s novým run_id, seq a answer_file v náhradním řádku. Oba odkazy vyplnit,
  náhrada completed/failed. Bez náhrady G3 odmítne neúplnou matici.
- **planned:** ještě neprovedeno; finální analýza je nepřijme.

| Provozní typ | Povolené opakování (nejvýše jedno) |
| --- | --- |
| tool_error | ihned |
| timeout | žádná odpověď do 180 s; opakovat ihned |
| rate_limit, product_outage | jednou v rámci 24h okna, uchovat čekání v latency_s |
| model_output, invalid_format | ne, completed a běžný rating |

Při retries=1 musí první pokus být neúspěšný a zachovaný v attempt1_file; první/konečné
latence a úspěšnosti zůstávají oddělené. Úspěšné zotavení má completed/final=yes,
ale zachovává typ první provozní chyby a first=no. Při retries=0 se first/final shodují.
Pokud artefaktové záznamy potřebují opravu (evaluation_error), dát důvod do notes a
verzovaného auditu; není to nová produktová odpověď ani důvod k selektivnímu vyloučení.

## Normalizace a export

P1 může mít markdown odkazy, horní indexy nebo zdrojové čipy. Normalizace zachovává
místo skutečné atribuce a celé URL; původní export+screenshot jsou autoritativní.
Seznam bez přiřazení k tvrzení ponechat bez značek, parser vytvoří diagnostické `*`.
P2/P3 kopírovat celé, nejen seznam CLAIMS/TVRZENÍ. Parser nemá limit osmi tvrzení;
člověk kontroluje všechny části, složené výroky, významové duplicity a quote evidence.

Po `check_citations.py` zkontrolovat parsed_sources. Chyba parseru se řeší **auditovanou
novou verzí workspace/exportu** se zachováním původních souborů, nikoli přepsáním
zahashovaných listů, mazáním soli nebo opětovným exportem stejných ID do stejného klíče.
Nelze tajně přečíslovat citace nebo doplnit zdroj, který produkt vůbec necitoval.

Parser zachovává přesné markdown URL včetně koncových podtržítek, pořadí/enkódování
query a parametrů utm; text pro hodnotitele je původní, nikoli přepsaný. U prostého URL
bez markdown oddělovače je koncová větná interpunkce nejednoznačná: porovnat s originálem.
Značka `[0]` se nepřečísluje ani nevyřadí z hodnocení: je zaznamenána jako neplatný formát,
ale vztah ke skutečně uvedenému zdroji se hodnotí normálně. Samotná nula není důkaz FAB.

Hodnotitelům předat jen jejich 2 listy. key_dir nesmí být uvnitř složky předávané
hodnotitelům; sůl, klíč, format metadata, batch manifesty, run plány a výsledky zůstávají
u správce. Doporučení: oddělené adresáře `$WORK/annotation` a `$WORK/key`.

## Časy a odchylky

Každá úloha napříč systémy/podmínkami do 24 h, fáze test do 72 h; repeat v následujících
72 h po konci testu. Zdrojové ratingy do 7 dnů od odpovědi. RUN_DAY reference pokrývají
všechny RF/OF každého potřebného dne v UTC, včetně dev/val, ne pouze testu.
G3 zachová porušení časových oken v manifestu/reportu; odchylka a dopad jsou povinné,
nikoli změna časových razítek tak, aby validátor „vyšel“.
