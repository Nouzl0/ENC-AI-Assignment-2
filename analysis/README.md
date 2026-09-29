# Analýza chyb

Vyberte 12 případů (zadání vyžaduje alespoň 8):

- alespoň 2 za každý systém,
- alespoň 3 úspěšné odpovědi (správnost 2 a přesnost ≥ 0,8),
- alespoň jeden případ z každého typu okrajové podmínky,
- přednostně z testovací sady; výběr provádí správce dat podle `results/metrics.csv` a `annotation/pairs_rated.csv`.

Do `error_analysis.csv` (kopie šablony) zapište ke každému případu výňatek odpovědi, citaci, hodnocení, kód chyby (E1–E11)
a pravděpodobnou příčinu: `retrieval` (zdroj nenašel), `attribution` (našel, ale připojil špatně), `generation` (zdroj měl, ale text zkreslil).
Ve sloupci `fixed_by_P3` uveďte, zda chybu odstranila podmínka P3 u stejného případu a systému.
Ve zprávě shrňte opakující se vzorce (např. E6 u případů s nedávnou změnou faktu, E2 u českých dotazů).
