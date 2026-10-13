(human-handoff)=
# Předání nezávislým hodnotitelům

Správce rozdělí dva oddělené balíčky. První hodnotitel má všech 92
způsobilých odpovědí, druhý náhodný výběr ≥25 % z každého strata fáze × produkt
× podmínka. Identity produktů, podmínek, klíč a pomocné AI ratingy zůstávají
u správce. Hodnotitelé pracují samostatně do odevzdání původních listů.

1. Přečíst README, rubriku a kalibrační pravidla v balíčku. Ponechat anonymní ID.
2. V answers_to_rate.csv zkontrolovat celou odpověď, RF/OF/RC a nezávisle ověřit
   referenci. Zapsat correctness 0–2, fakta/evidenci, požadavky a skutečný čas práce.
3. V pairs_to_rate.csv zkontrolovat návrhy dělení, doplnit opomenutá tvrzení a
   přesné vztahy k citacím. Nehodnotit pouhou přítomnost URL jako podporu.
4. Pro každý skutečný pár uvést S2/S1/S0/NA/FAB, přesný důkaz, datum a locator.
   Podpůrná citovaná věta není další tvrzení modelu. Chybějící OF se netrestá.
5. Zachovat původní URL, značky a nepřístupné zdroje. Nativní cíle bez zachované
   vazby se nesmí doplnit domněnkou. Návrh, který není faktickým párem, označit NONE.
6. Odevzdat oba původní CSV samostatně správci. Teprve potom řešit neshody;
   shoda/kappa se vypočítá z původních nezávislých ratingů, nikoli konsenzu.

U časově omezených otázek se používá UTC datum doloženého odeslání v
reference_valid_as_of; jde o den běhu, ne den hodnocení. Původní RUN_DAY
reference zůstala beze změny.

CSV jsou UTF-8; pro otevření v tabulkovém editoru zvolit import s čárkou a
uvozovkami. Prázdná pole jsou určena k vyplnění, nikoli nuly. Všechny zveřejněné
zdrojové reference jsou zatím návrh k nezávislé kontrole. Nevydávat vyplněné
exploratorní listy za zpětné G1/G2/G3 nebo nově skrytý test.

Po návratu ratingů správce uchová originály mimo Git, připojí audit neshod,
spočítá výsledky se selháními a jasně označí exploratorní rozsah. Pro původní
plný potvrzující protokol je ještě potřeba nová skrytá sada, úplná produktová
matice, skutečný výběr P3 a včasná schválení bran.
