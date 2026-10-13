# Odevzdávací podklady CZAI Assignment 1

**Aktuální stav: 40 různých měřených úloh, 84 věcných odpovědí a označený AI audit.**
Původní pilot: 33 odpovědí. Doplněk: 51 odpovědí, včetně oddělené náhrady operátorské chyby.
Náhrada nepočítá novou úlohu. Přístupová odmítnutí a selhání jsou zachovány zvlášť.

| Požadavek | Stav a podklad |
| --- | --- |
| Výzkumný protokol | `PROTOCOL.md`; původní G1/G2/G3 nejsou splněny |
| ≥40 různých případů | 20 dev + 10 val + 10 nových oddělených otázek; skutečné pokrytí v `runs/supplement-2026-10-13/task_coverage.csv` |
| Test držený stranou | 10 nových otázek po fixaci šablon; vytvořené a kontrolované AI, bez nezávislého lidského schválení; původní zveřejněné kandidáty nepoužíváme jako holdout |
| ≥4 produkty | Odpovědi původního pilotu ze čtyř produktů; Claude měl limit/přístupové omezení |
| P1/P2/optimalizace | Pět nových úloh má Gemini P1/P2/P3A, další pokrytí je neúplné; P3A není validační vítěz původního protokolu |
| Hlavní a vedlejší metriky | Definované v protokolu; skutečný AI obsahový audit a atomizovaný účelový subset s intervaly v `results/ai-review-2026-10-13/` |
| Lidská složka | **Chybí.** AI hodnocení není rating Reného/ Jana; původní listy zůstávají nevyplněné |
| Analýza ≥8 úloh | `docs/error-analysis.md`, dále nové zdrojové AI review |
| Worksheet a zpráva | `worksheet.md`, `docs/exports/project.pdf`, `worksheet.pdf` |
| Metadata, selhání, opakování | Raw odpovědi, snímky, registry, hashe a audit; latence horní meze nebo unknown |

Splněný počet úloh neznamená splnění všech minimálních požadavků zadání.
Není dokončená vyvážená produktová matice ani zadáním vyžadovaná lidská složka.
Časová tíseň není schválená výjimka. AI ratingy se za lidské nevydávají a H1/H2
nejsou potvrzeny. Výsledky nejsou obecný žebříček AI produktů.

Balíček obsahuje aktuální zprávu a worksheet, veřejná data, prompty, nástroje,
původní pilot a odsanitizované doplňkové exporty. Neobsahuje účty, tokeny,
privátní snapshoty referencí, `.git`, `.venv` ani `_build`.
Testy a lint při této etapě nebyly na výslovný pokyn uživatele spuštěny.
