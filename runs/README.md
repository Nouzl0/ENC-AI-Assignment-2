# Jak spustit a zaznamenat běh

Každý řádek `run_plan_<fáze>.csv` = jeden běh. Plán vytvoří `python3 scripts/make_run_plan.py --phase <dev|val|test|repeat>`.
Řádky jděte **v pořadí `seq`** (pořadí systémů a podmínek je náhodně zamíchané).

## Před prvním během (jednou)

1. Pro každý systém nový účet na stejné úrovni předplatného (výchozí: bezplatná).
2. Vypnout paměť, personalizaci, vlastní instrukce, bio a styly (viz tabulka v návrhu projektu).
3. Stejný prohlížeč, česká síť, čeština rozhraní. Pořídit snímek obrazovky nastavení každého systému (`runs/screenshots/setup_<systém>.png`).

## Jeden běh

1. Otevřete **nový chat v režimu bez paměti** (Temporary / Incognito / Private chat). Hloubkový výzkum nechte vypnutý. U ChatGPT zapněte nástroj Search, u Claude přepínač Web search (pokud ho rozhraní má).
2. Zkopírujte celý text ze sloupce `prompt_text` a vložte ho beze změny.
3. Spusťte stopky při odeslání, zastavte je, když systém dopíše odpověď → `latency_s`.
4. Pokud se systém doptá, odpovězte jen: „Pokračujte podle svého nejlepšího úsudku." a zapište `turns = 2`.
5. Uložte **snímek obrazovky** (`runs/screenshots/<run_id>.png`) a pokud jde, **odkaz na sdílení** (`share_link`).
6. Uložte **odpověď** do `runs/answers/<run_id>.txt` (formát níže).
7. Vyplňte metadata v řádku: `model_visible` (název modelu, který rozhraní ukazuje), `plan_tier`, `datetime_start` a `datetime_end` (Europe/Prague, `2026-10-12 14:03`), `search_used` (yes/no/unclear), `n_sources_shown`, `turns`, `tool_calls_visible` (počet zobrazených vyhledávání, pokud je rozhraní ukazuje), `retries`, `failure_type`, `first_attempt_ok`, `manual_intervention`, `operator`, `cost_note`, `notes`.

## Formát souboru s odpovědí

- P2/P3 odpovědi mají formát už z promptu – zkopírujte je celé.
- P1 odpovědi **normalizujte**: vložené odkazy nebo „čipy" se zdroji nahraďte značkami `[1]`, `[2]` v místě, kde byly, a na konec přidejte seznam zdrojů. Text odpovědi neměňte.

```text
První zprávu přes ARPANET („lo“) odeslali 29. 10. 1969 z UCLA do SRI [1]. Systém spadl po dvou písmenech [1][2].

ZDROJE:
[1] The Day the Infant Internet Uttered its First Words – https://www.lk.cs.ucla.edu/internet_first_words.html
[2] The First Message Transmission – https://www.icann.org/en/blogs/details/the-first-message-transmission-29-10-2019-en
```

Skript si poradí i s běžnými variantami (tučné nadpisy, `### Zdroje`, číslovaný nebo odrážkový seznam zdrojů, holé URL,
markdown odkazy `[text](url)`, horní indexy ¹²). Po spuštění `check_citations.py` zkontrolujte sloupec `parsed_sources`
v `answers_to_rate.csv`; pokud zdroje chybí, opravte soubor s odpovědí a skript spusťte znovu (ID odpovědí se nezmění).

- Pokud systém zdroje jen vypíše na konci bez značek v textu, značky **nepřidávejte** – jen seznam `ZDROJE:`. Skript takové citace označí jako nepřiřazené.
- URL berte z panelu zdrojů nebo z exportu (Perplexity/Gemini export do PDF/Markdown), celé, bez zkracování.

## Selhání

| `failure_type` | Kdy | Opakovat? |
| --- | --- | --- |
| `none` | Běh proběhl | — |
| `model_output` | Odmítnutí, odpověď bez citací, zjevná halucinace | Ne – hodnotí se |
| `invalid_format` | P2/P3 odpověď nedodrží formát | Ne – hodnotí se |
| `tool_error` | „Vyhledávání se nezdařilo" | 1× ihned |
| `rate_limit` | Vyčerpaný limit | 1× do 24 h |
| `timeout` | Bez odpovědi do 180 s | 1× ihned |
| `product_outage` | Chyba serveru, výpadek | 1× v rámci 24h okna |
| `student_error` | Špatný prompt, zapnutý hloubkový výzkum | Spustit znovu správně; po opakování zapsat `student_error_rerun` (nepočítá se systému, `retries` nezvyšovat) |
| `evaluation_error` | Chyba při zápisu | Opravit záznam |

Při opakování: původní pokus **nemažte**. Uložte ho jako `runs/answers/<run_id>__attempt1.txt` (a snímek `<run_id>__attempt1.png`),
odpověď z posledního pokusu jako `runs/answers/<run_id>.txt`. Do `retries` zapište počet opakování, do `first_attempt_ok` `no`
a do `notes` popis prvního pokusu. Úspěšnost na první pokus i po opakování vykazuje `score.py` zvlášť.

## Časová okna

- Jeden případ projde všemi systémy během 24 hodin.
- Celá testovací sada (fáze `test`) do 72 hodin; opakování (`repeat`) v následujících 72 hodinách.
- Hodnocení do 7 dní od běhu (web se mění).
