# Podmínky promptů

Všechny tři podmínky dostanou stejnou otázku a liší se jen obalem kolem ní. Anglické případy používají překlad stejného textu, všechny verze jsou v `prompts/`. Systémově specifické úpravy nepovolujeme (cíl je 0).

## P1 – společná výchozí podmínka

Šablona ze zadání a jedna věta o formátu:

```text
Vyřešte níže uvedenou úlohu. Odpovězte pouze v požadovaném formátu.

Úloha:
{user_prompt}
Formát: stručná odpověď s odkazy na použité zdroje (URL).
```

## P2 – strukturovaný prompt

Verze 1.0, napsána před prvním během:

```text
Jste pečlivý rešeršní asistent. Každé tvrzení dokládáte zdrojem, který jste v této konverzaci skutečně otevřeli.

Cíl: odpovězte přesně a stručně na otázku tak, aby si čtenář mohl každé tvrzení ověřit.

Otázka:
{user_prompt}

Pravidla:
1. Vyhledejte informace na webu. Necitujte zdroj, který jste neotevřeli, a nevymýšlejte URL.
2. Za každým faktickým tvrzením (číslo, datum, jméno, definice) uveďte odkaz na zdroj ve tvaru [1], [2].
3. Citujte konkrétní stránku nebo dokument, ne domovskou stránku ani výsledky vyhledávání.
4. Upřednostňujte primární a oficiální zdroje (zákon, úřad, původní studie, standard).
5. Pokud otázka obsahuje chybný předpoklad, nejprve ho opravte.
6. Pokud se zdroje liší, uveďte obě hodnoty, každou s vlastním zdrojem, a vysvětlete rozdíl.
7. Pokud otázka omezuje stáří zdrojů, použijte jen zdroje, které omezení splňují, a uveďte jejich datum.
8. Pokud spolehlivou odpověď nenajdete, napište to. Nehádejte.

Formát výstupu:
ODPOVĚĎ: 1–3 věty s přímou odpovědí.
TVRZENÍ:
T1: <jedno tvrzení> [n]
T2: <jedno tvrzení> [n]
ZDROJE:
[1] <název> – <vydavatel> – <datum vydání nebo „neuvedeno"> – <úplná URL>
JISTOTA: vysoká / střední / nízká – jedna věta proč.
```

## P3 – optimalizovaný prompt

P3 vznikne z P2 jen na základě vývojové a validační sady:

1. Po běhu P2 na vývojové sadě sečteme typy chyb (taxonomie viz [](#error-analysis)). Úprava je povolená jen proti typu chyby, který se objevil alespoň třikrát.
2. Připravíme dva kandidáty. Předpokládaný **P3-A** přidá ke každému tvrzení doslovný úryvek ze zdroje (nejvýš 25 slov). **P3-B** přidá navíc kontrolu před odesláním: tvrzení, které citovaná stránka neobsahuje, se odstraní nebo označí jako nepodložené. Konečné úpravy určí data z vývoje.
3. Kandidáty spustíme na validační sadě spolu s P2. Vybereme kandidáta s vyšší citační přesností; při rozdílu pod 2 procentní body rozhodne kratší prompt.
4. Vítěze zmrazíme, zapíšeme jeho hash SHA-256 a teprve pak otevřeme testovací sadu. Pokud žádný kandidát nepřekoná P2, použijeme lepšího z nich a vykážeme neúspěšnou optimalizaci jako výsledek. Jedno další kolo úprav je povolené jen na vývojové sadě. Každou změnu a její důvod zapíšeme do `prompts/CHANGELOG.md`.

:::{warning}
P3 nesmí obsahovat pokyny pro konkrétní případy ani informace, které by prozradily odpovědi.
:::

## Přenositelnost

Přenositelnost vykazujeme pro P2 i P3:

- průměrné zlepšení oproti P1,
- zlepšení podle jednotlivých systémů a na testovací sadě,
- délku promptu ve znacích,
- počet systémově specifických úprav,
- dodatečná kola komunikace.

Prompt, který jednomu systému pomůže a ostatním uškodí, vykazujeme jako platný výsledek, ne jako lepší obecný prompt.
