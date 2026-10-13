# AI kontrola 22 nových veřejných úloh

**Nejde o lidské ratingy, finální precision, CI ani splnění G3.** AI operátor otevřel skutečné URL citované produkty a zapsal podporu požadovaných faktů, nepodporované bonusy, nečitelnou evidenci a formátové vady. Orientační gold nenahrazuje podporu konkrétní citace.

JSON/CSV pokrývá 22 nově měřených veřejných úloh: CIT-002, 006, 007, 009–011, 014–019 a 021–030. Verdikty jsou kvalitativní; nejsou úplnou atomickou segmentací celé odpovědi. Číselné precision a lidská correctness proto zůstávají null.

Gemini často uvádí značky typu `[1.1.2]` místo `[n]`; některé štítky chybí v ZDROJE. Tyto vady zůstávají v originálech. CIT-015 uvádí doloženou sazbu, ale datum účinnosti neprokazuje stáří publikace do 30 dní. CIT-019 obsahuje nedoložené tvrzení o rostoucí záměně s rokem 1918. CIT-017 potřebuje odděleně ověřit dodatečnou zmínku o papežské bule. P1 ChatGPT CIT-002 má zdroje bez explicitního spojení; správný fakt neznamená automaticky S2.

Nedostupnost zůstává označena: Nobel vrací 403, EUR-Lex u CIT-023/024 poskytl shell bez textu předpisu a NVD prázdný obsah. MZe u CIT-006 při prvním otevření poskytl uložený název části zákona, následné čtení vracelo 404. Nečitelný zdroj se neoznačuje FAB jen kvůli nedostupnosti.

Doklady jsou krátké vlastní parafráze a locatory přečtených stránek v JSON/CSV. Slabší sekundární zdroj může podporovat atribuci, ale sám neprokazuje pravdivost. Testy a lint nebyly spuštěny.
