(overview)=
# Shrnutí

Studie sleduje podporu tvrzení jejich citovanými zdroji u rešeršních AI produktů.
Aktuální balíček obsahuje **40 různých měřených úloh a 84 věcných odpovědí**:
33 původních pilotních a 51 doplňkových. Jde o 20 vývojových, 10 validačních
veřejných otázek a 10 nových otázek připravených odděleně po zmrazení šablon.
Náhrada chybně zachyceného snímku není další úloha.

Původní pilot zahrnuje odpovědi ChatGPT, Gemini, Grok a Perplexity; Claude neměl
dokončenou odpověď. Doplňkový sběr používá dostupná rozhraní, uchovává přístupové
chyby a rozdíly účtů. Pět nových úloh má Gemini ve všech třech podmínkách
P1/P2/P3A, ostatní pokrytí je neúplné. P3A je předem fixovaný kandidát;
nejde o zpětně vyhlášeného vítěze validace.

## Doložené výsledky

- Pomocné AI obsahové posouzení původního pilotu: 47 ze 48 povinných faktů správně;
  průměr pokrytí po 33 odpovědích 0,9848, deskriptivní 95% interval 0,9516–1,0000.
- Atomizovaný účelový subset 11 odpovědí na třech úlohách: 61 faktických jednotek
  a 87 explicitních citačních párů. Průměrné meze precision 0,7141–0,8050;
  intervaly a nejistota nedostupných zdrojů jsou v kapitole [](#results).
- Kvalitativně se opakuje správné číslo s chybným odkazem/locatorem, neověřená
  bonusová tvrzení a nestandardní citační značky. U časově omezené úlohy správná
  hodnota sama nedokazuje požadované stáří publikace.

## Rozsah interpretace

Hodnocení je výslovně **AI hodnocení**. Lidské ratingy, jejich shoda a původní
G1/G2/G3 nejsou dokončené. Subset není reprezentativní, intervaly nezahrnují
chybu AI hodnotitele a nemají platnost obecného žebříčku produktů. Výsledky
původního pilotu a doplňku se neslévají do jediného skóre.

Balíček odstraňuje chybějící počet měřených úloh a přidává skutečné odpovědi,
AI audit a aktualizované dokumenty. Zbývá plná vyvážená matice a zadáním
vyžadovaná skutečná lidská složka. Časová tíseň není schválenou výjimkou.
