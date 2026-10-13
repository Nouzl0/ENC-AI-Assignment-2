(supplement)=
# Doplňkový sběr a výslovně označené AI hodnocení

## Proč vznikl samostatný doplněk

Dne 13. 10. 2026 tým požádal o další skutečné měření a rychlé dokončení podkladů.
Doplněk zachovává původní pilot i protokol. Není zpětným schválením G1, G2 nebo
G3. Nové odpovědi nejsou syntetické fixture a původní lidské anotační listy se
nepřepisují hodnocením AI.

Původních 33 dokončených odpovědí pokrývá osm různých úloh. Zadání požaduje
nejméně **40 různých případů**, nikoli 40 odpovědí na stejné otázky. Proto se při
doplňování sledují samostatně počty odpovědí, unikátních task_id a pokrytí
produkt × prompt × úloha. Neodeslané plány a přístupové chyby se za odpovědi
nepočítají.

## Sběr

Operátory jsou AI subagenti v prohlížeči Codex In-app Browser. Přednost dostává
22 dosud neměřených veřejných dev/val otázek. Další operátor odděleně připravuje
deset nových neveřejných otázek; původní publikované CIT-031–040 se za skrytý
test nevydávají. Nové otázky i jejich reference jsou vytvořeny s pomocí AI,
**nejsou nezávisle schváleny člověkem**.

Před konstrukcí nových otázek byly uchovány neměnné byte kopie a SHA-256
šablon P1, P2 a P3A v obou jazycích. P3A je v tomto doplňku předem zvolený
kandidát. Není vydáván za vítěze validačního porovnání ani za původní
`P3_final`. Otázky nesmí vést k následným úpravám promptu.

Sběr ukládá původní odpověď, skutečné časy, použitou šablonu, viditelnou
konfiguraci a snímek. Údaje, které rozhraní neukazuje, jsou `unknown`.
Rozdíly účtu, tarifu a rozhraní vůči původnímu pilotu jsou odchylky; výsledky
se neslévají do společného produktového žebříčku. Případná nemožnost přístupu
se dokládá konkrétní chybou, nikoli náhradní vymyšlenou odpovědí.

## Hodnocení

Aktuální výstupy v `results/ai-review-2026-10-13-v2/` představují **pomocné AI hodnocení**
podle existující rubriky. Nejsou prací Reného Mrákavy ani Jana Duba. Pokud
nebylo možné otevřít přesně citovaný zdroj, je tato skutečnost zachována;
jiný kontrolní zdroj nedokazuje podporu původní citace. Přístupové selhání
není důkazem FAB.

Skóre se vždy uvádí s počtem posouzených odpovědí, úloh a dvojic, rozsahem
zdrojové kontroly a identitou AI hodnotitele. Nejistota z převzorkování úloh
nezahrnuje chyby samotného AI hodnocení. Nelze ji vydávat za lidskou shodu
nebo použít pro potvrzující test H1/H2 podle původního protokolu.

## Co doplněk nenahrazuje

Zadání výslovně vyžaduje alespoň jednu složku skutečného lidského hodnocení.
AI může připravit ratingy, podklady i vysvětlení, ale nemůže tuto podmínku
splnit pod identitou členů týmu. Plné porovnání všech tří promptových
podmínek a všech produktů musí být doloženo vyplněnou maticí; samotná
existence šablon nebo dosažení 40 úloh úplnou matici nedokazuje.

Aktuální součty a dostupné tabulky jsou v kapitole [](#results). Uvedené
neúplnosti jsou stav dat, nikoli dodatečně odsouhlasené výjimky ze zadání.

## Audit exportů a příprava lidské práce

Kanonický registr používá collection/run_id, samostatné template a rendered
SHA a skutečná metadata. Původní chybné clipboard exporty jsou zachované; čtyři
odpovědi byly z dochovaných AX a PNG obnovené do nové verze. Nový sběr čte
přímo konkrétní response DOM a zachovává skutečné href. Odstraněn byl jediný
UI nadpis identifikující produkt v podkladu pro zaslepené hodnocení; odpověď
ani citace se nepřepisují. SUP-H002/P2 se ve výběru započítá pouze jeho náhradou.

Reference doplňku byly jednotně opravené po sběru a označené jako AI ověřené.
Deset otázek už je zveřejněných; není to neviděný test pro další ladění.
Zaslepený exportátor ověřuje všechny vstupní hashy, odděluje identifikační klíč
a nepředvyplňuje ratingy. Povinné skutečné lidské hodnocení: [](#human-handoff).
