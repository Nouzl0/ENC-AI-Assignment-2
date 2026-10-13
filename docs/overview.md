(overview)=
# Shrnutí

AI asistenti s vyhledáváním dnes odpovídají s odkazy na zdroje. Odkaz ale ještě neznamená,
že zdroj tvrzení skutečně podporuje. Navrhli jsme a připravili benchmark, který to u pěti
produktů (ChatGPT, Gemini, Claude, Perplexity, Grok) měří na úrovni jednotlivých tvrzení,
a ověřili jsme jej **skutečným pilotem**: 33 odpovědí na 8 úloh.

:::{important} Co jsme udělali
- **Metodika:** hlavní metrika (citační přesnost), hypotézy H1/H2 a plán nejistoty jsou předem definované a zdokumentované.
- **Data:** 40 úloh v češtině a angličtině z pěti oborů, 43 % okrajových případů; reference prověřené proti primárním zdrojům (kontrola AI, lidské potvrzení zbývá).
- **Nástroje:** parser citací, zaslepené listy pro dva hodnotitele, skórování s intervaly a automatické testy.
- **Pilot:** 33 reálných odpovědí zachycených z webových rozhraní, každá s textem, HTML, snímkem a otiskem SHA-256.
:::

## Hlavní zjištění pilotu

1. **Správné číslo nestačí.** Perplexity u CIT-001 uvedl v textu správné DOI studie, ale
   odkaz přímo u tvrzení vedl na jiný článek. Takový rozpor lze při běžném čtení snadno přehlédnout.
2. **Produkty umějí přiznat nejistotu.** U CIT-020 (datum narození Shakespeara) rozlišily
   nedoložené narození, doložený křest a tradiční datum, místo jednoho sebejistého čísla.
3. **Rozdílné hodnoty umějí vysvětlit.** U CIT-004 (výška Sněžky) odlišily 1 603,296 m
   (vrchol) od 1 602 m (trigonometrický bod); dobrovolné doplňky ale přidávají další
   tvrzení, která je nutné samostatně ověřit.
4. **Provozní spolehlivost je v pilotu vysoká, ale nerovnoměrná.** 23 z 24 odeslaných
   prvních pokusů rozšířeného pilotu skončilo odpovědí (95,8 %). Claude zůstal bez odpovědi kvůli
   limitu využití a ChatGPT jednou selhal při načtení odpovědi.
5. **Orientační proxy podpory** (lexikální shoda tvrzení se stránkou, ne rating) vyšla 0,49–0,76 podle produktu; slouží jen jako předběžný odhad a rozdíly na 7–8 odpovědích nejsou průkazné.
6. **Věrný export je výzkumný problém sám o sobě.** Perplexity sdružuje citace pod
   „+1/+2"; 44 skupin a 57 zdrojových vazeb jsme museli zachytit z původních karuselů UI.

:::{note} Stav a rozsah
Plný experiment (500 analytických odpovědí a dva lidští hodnotitelé) přesahuje čas a rozpočet na využití produktů a AI agentů.
Projekt proto dodává kompletní metodiku, nástroje a **skutečný pilot**; **finální citační přesnost a test hypotéz nevykazuje**
(nezávislá lidská hodnocení a formální zmrazení G1–G3 jsou mimo rozsah). Pomocné kontroly AI jsou
označené jako takové a nenahrazují lidské hodnocení. Podrobně v kapitole [](#limits).
:::
