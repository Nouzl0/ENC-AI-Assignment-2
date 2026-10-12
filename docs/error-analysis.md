(error-analysis)=
# Analýza chyb

Analyzujeme 12 případů (zadání vyžaduje 8): alespoň 2 za každý systém, alespoň 3 úspěšné odpovědi a alespoň jeden případ z každého typu okrajové podmínky. Každé selhané dvojici tvrzení–citace přiřadíme jeden hlavní kód chyby.

| Kód | Typ chyby | Definice |
| --- | --- | --- |
| E1 | Vymyšlený zdroj | URL, DOI nebo dokument neexistuje |
| E2 | Nepodporující zdroj | Zdroj existuje, ale tvrzení neobsahuje |
| E3 | Přehnané zobecnění | Zdroj říká méně nebo něco užšího než tvrzení |
| E4 | Záměna citací | Fakt je v jiném citovaném zdroji než v tom, který je u tvrzení |
| E5 | Zkreslené číslo nebo datum | Zdroj uvádí jinou hodnotu, než jakou systém převzal |
| E6 | Zastaralý zdroj | Zdroj neodpovídá aktuálnímu stavu nebo porušuje časový limit |
| E7 | Méně kvalitní zdroj | Systém cituje agregátor nebo diskusi, i když existuje primární zdroj |
| E8 | Obecná citace | Domovská stránka nebo výsledky vyhledávání místo konkrétního dokumentu |
| E9 | Chybějící citace | Faktické tvrzení nemá žádný zdroj |
| E10 | Přijatý chybný předpoklad | Systém předpoklad neopravil a dokladá ho zdroji |
| E11 | Ignorovaný rozpor | Systém uvede jen jednu z protichůdných hodnot |

## Záznam analýzy

U každého analyzovaného případu zapíšeme do `analysis/error_analysis.csv`:

- ID případu, systém, podmínku,
- výňatek odpovědi, citaci a hodnocení,
- kód chyby,
- pravděpodobnou příčinu: **vyhledání** (zdroj nenašel), **přiřazení** (našel, ale připojil špatně) nebo **generování** (zdroj měl, ale text zkreslil),
- zda chybu opravila podmínka P3.

Hledáme opakující se vzorce, například zda se E6 soustředí u případů s nedávnou změnou faktu nebo E2 u českých dotazů.
