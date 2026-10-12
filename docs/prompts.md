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
2. Před G1 zvolíme jednoho nebo oba kandidáty. Předběžný **P3-A** přidává úryvek ≤25 slov ke tvrzení; **P3-B** navíc kontrolu před odesláním. Jde o hypotézy, konečné změny musí doložit alespoň tři chybné dev odpovědi s ID a kódem chyby.
3. Proběhne jedna plánovaná validace P2 a kandidátů. Výběr se přepočte v plné přesnosti z archivovaného `scoring_inputs.json`. Při rozdílu <0,02 rozhodne kratší průměrná délka CZ/EN šablony včetně whitespace, při shodě P3A.
4. Vítěze přesně zkopírujeme v CZ/EN do P3_final, zaznamenáme důkazy/hashe a podepíšeme G2 před otevřením testu. I při nezlepšení P2 se vybere měřený kandidát a neúspěch se přizná. **Po validaci není další ladění povolené.** Změny patří do `prompts/CHANGELOG.md`.

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
- dodatečná viditelná volání nástrojů a jejich pokrytí.

Prompt, který jednomu systému pomůže a ostatním uškodí, vykazujeme jako platný výsledek, ne jako lepší obecný prompt.
