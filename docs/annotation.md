# Automatizované kontroly a lidské hodnocení

Skripty dělají mechanickou práci: rozdělí odpověď na tvrzení, zkontrolují URL a zaslepí listy. Hodnocení S2 až FAB a správnost odpovědi vždy zapisuje člověk.

## Automatizované kontroly

Skript `check_citations.py` zkontroluje každou citaci před lidským hodnocením a výsledky zapíše do anotačního listu. Automatika lidské hodnocení nenahrazuje, jen ho předvyplňuje a zrychluje. Konečné hodnocení vždy potvrzuje člověk.

| Kontrola | Co skript dělá | Výsledek |
| --- | --- | --- |
| Dostupnost URL | HTTP stav a přesměrování, dva pokusy s odstupem 10 minut | 404, 410 nebo chyba DNS: návrh FAB k ručnímu ověření; 401, 403 nebo paywall: návrh NA |
| Konkrétnost odkazu | Pozná domovskou stránku a stránku s výsledky vyhledávání | Příznak „obecná citace" |
| Shoda čísel a jmen | Vytáhne z tvrzení čísla, data a vlastní jména a hledá je v textu stránky (sjednotí „1 603" a „1603", čárku a tečku) | Podíl nalezených entit, předběžný příznak shody |
| Datum publikace | Čte metadata stránky (`article:published_time`, `datePublished`) | Kontrola časového limitu |
| Formát P2 a P3 | Ověří sekce ODPOVĚĎ, TVRZENÍ, ZDROJE a JISTOTA a že každé [n] má záznam ve zdrojích | Validita formátu jako diagnostika dodržování instrukcí |

Další dva skripty doplňují kontrolu dat a výpočet:

- `validate_cases.py` ověří schéma případů, velikost částí, podíl okrajových případů (alespoň 20 %), podobnost testu s vývojem a spočítá hash testovací sady.
- `score.py` spočítá metriky, intervaly nejistoty a shodu hodnotitelů.

**Validace automatiky:** na vývojové sadě porovnáme příznak shody čísel s lidským hodnocením S2. Pokud bude shoda slabá (kappa pod 0,4), použijeme příznak jen jako nápovědu pro hodnotitele.

(human-rating)=
## Lidské hodnocení

Člověk hodnotí to, co automatika spolehlivě nezměří: zda citovaný zdroj tvrzení skutečně podporuje. Rubrika platí od zmrazení protokolu a plné znění s dalšími příklady je v `annotation/rubric.md`.

| Hodnocení | Pravidlo | Kotva (příklad) |
| --- | --- | --- |
| **S2** plně podpořeno | Zdroj tvrzení výslovně uvádí nebo z něj přímo plyne; čísla sedí v uvedené přesnosti | „Sněžka měří 1603 m" + stránka ČÚZK s hodnotou 1603,296 m |
| **S1** částečně | Zdroj podporuje jen část tvrzení, nebo je tvrzení silnější či obecnější než zdroj | „Nový stavební zákon platí od 1. 1. 2024 pro všechny stavby" + zdroj uvádějící jen vyhrazené stavby |
| **S0** nepodpořeno | Zdroj tvrzení neobsahuje nebo mu odporuje | „Poločas rozpadu C-14 je podle NNDC 5 568 let" + stránka NNDC s hodnotou 5 700 ± 30 let |
| **NA** nedostupné | Stránka existuje, ale obsah nelze přečíst (paywall, přihlášení, chyba 403) | Článek NEJM za paywallem bez abstraktu |
| **FAB** neexistuje | URL ani DOI neexistuje a nenašli jsme ji ani v archivu | Vymyšlený DOI nebo URL s chybou 404 |

**Správnost odpovědi (0–2):**

- **2** = všechny `key_facts` správně a chybný předpoklad opraven,
- **1** = část klíčových faktů chybí nebo je nepřesná,
- **0** = odpověď je chybná, přijme nepravdivý předpoklad nebo vymýšlí přesnou hodnotu tam, kde neexistuje.

### Postup

1. **Kalibrace:** před ostrým hodnocením ohodnotí všichni hodnotitelé stejných 10 odpovědí z vývojové sady a sjednotí výklad rubriky.
2. **Zaslepení:** anotační list neukazuje název systému ani podmínku. Formátování odpovědí sjednotíme na prostý text s označením [n] a seznamem URL.
3. **Náhodné pořadí:** skript zamíchá odpovědi (seed 2026), aby hodnotitel neviděl odpovědi jednoho systému za sebou.
4. **Dva hodnotitelé** pro 25 % odpovědí, vybraných stratifikovaně podle systému a podmínky. Zadání vyžaduje 20 %. Shodu měříme Cohenovou kappou (S2 proti ostatním) a procentem shody. Cílem je kappa alespoň 0,6. Při nižší hodnotě rubriku upřesníme a dvojitě hodnocené odpovědi ohodnotíme znovu.
5. **Řešení neshod:** hodnotitelé neshodu proberou. Když se nedohodnou, rozhodne třetí hodnotitel. Každou neshodu a její řešení zapíšeme do `annotation/disagreements.csv`.

### Hodnocení pomocí LLM

Hlavní závěry stavíme jen na lidském hodnocení. LLM použijeme nanejvýš k předběžnému rozdělení P1 odpovědí na tvrzení, které člověk zkontroluje.

Pokud tým LLM hodnotitele použije i pro podporu citací, uvede model a verzi, použije tuto rubriku a zaslepené a zamíchané odpovědi. Kalibruje ho na 50 dvojicích ohodnocených člověkem a vykáže shodu s lidmi. Zkontroluje i vliv délky odpovědi a sebepreferenci, protože každý dostupný hodnoticí model patří některému z porovnávaných výrobců. LLM hodnotitel je měřicí nástroj s vlastní chybou.
