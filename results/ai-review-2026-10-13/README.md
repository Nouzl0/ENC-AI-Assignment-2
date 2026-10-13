# Doplňkový AI audit pilotu (13. 10. 2026)

Tento adresář obsahuje **AI hodnocení**, nikoli ratingy Reného nebo Jana,
nezávislou lidskou verifikaci nebo splnění G1/G2/G3. Původní prázdné lidské
anotační listy, raw odpovědi a jejich manifesty zůstávají beze změny.

Rozsah: 33 skutečně dokončených odpovědí P2 z osmi veřejných pilotních úloh.
Neúspěšný export CIT-004 ChatGPT se nepočítá jako odpověď. Dva legacy běhy
CIT-001 jsou popsány kvalitativně; 31 odpovědí má již existující návrh segmentace.
Hodnocení není zaslepené a nezávislá mezihodnotitelská shoda nebyla měřena.

`answer_review.csv` obsahuje poznámku ke každé dokončené odpovědi.
`draft_pair_review.csv` je **diagnostika dosavadního parserového návrhu**, nikoli
finální atomická segmentace rubriky. Obsahuje duplicity a složené výroky;
`segmentation_reviewed=no` je proto povinně zachováno. Řádky bez citace nejsou FAB;
jsou označené NONE, a UI fragmenty nejsou hodnocena jako fakta.

S2/S1/S0 se přiděluje pouze po přečtení skutečně citované stránky/pasáže.
Jiný správný zdroj neopravuje chybnou nebo nedostupnou citaci. NA označuje
nepřístupný obsah (403, cookie challenge, JS shell); REVIEW_PENDING označuje
načtený obsah bez dokončeného sémantického posouzení. Tyto stavy nejsou důkaz
neexistence. FAB bez druhé kontroly a archivního hledání nepřidělujeme.
`source_access.csv` uvádí kontrolovanou URL, výsledek přístupu a SHA-256;
snapshoty a plný text jsou mimo repo v soukromém pracovním adresáři.

Deskriptivní precision meze platí pouze pro **31 existujících návrhů párů**:
dolní = S2 / všechny explicitní návrhy, horní = (S2 + NA + REVIEW_PENDING) /
všechny explicitní návrhy, nejprve po odpovědích a pak jejich průměr.
Nejde o hlavní precision podle protokolu, protože atomizace/duplicity nejsou
uzavřené. Žádný recall, correctness gold ani kappa nejsou dopočítány odhadem.
Bootstrap používá 10 000 výběrů s vracením osmi úloh (seed 20261013) a zachovává
všechny odpovědi dané úlohy společně. CI vystihuje jen variabilitu tohoto malého
vybraného pilotu; nezahrnuje chybu AI ratingů ani nejistotu neověřených zdrojů.

## Obsahové hodnocení celého pilotu

`content_review.csv` hodnotí RF všech 33 skutečných odpovědí a zachovává rozdíl
mezi obsahovou správností a podporou skutečně citovaným zdrojem. Primární referenční
URL je samostatně uvedena; nenahrazuje NA citace. Z 48 RF je obsahově správně 47;
Perplexity CIT-008 má chybně čl.16 odst.2 místo19 odst.2. RF úplnost po odpovědích
je jiná metrika než citační recall. `content_metrics.csv` obsahuje deskriptivní
průměr a bootstrap po úlohách. Correctness je publikována jako dolní/horní mez
při nerozhodnuté obsahové/RC nejistotě; nejde o final gold.

Dokončený obsahový průchod návrhů má 113 S2, 35 S1, 3 S0, 32 NA a19 NONE,
**žádný REVIEW_PENDING**. NA zůstávají skutečné přístupové problémy. Původní
parserové jednotky nebyly vydávány za úplnou atomickou lidskou segmentaci.
Zdroje byly otevírány samostatně; doménové jméno nebo jiný správný zdroj se
nepoužily jako náhrada za nepřístupnou/nesprávnou citaci.

## Omezená sémantická analýza po rozdělení tvrzení

`restricted_atomic_pairs.csv` a `restricted_atomic_answers.csv` obsahují samostatné
AI rozdělení a sjednocení opakovaných faktů pro **11 dokončených odpovědí na tři
úlohy CIT-004, CIT-008 a CIT-013**. Celkem jde o 61 faktických jednotek a87
explicitních dvojic. `segmentation_audit.csv` dokládá původní citovaný řádek,
ověřovanou parafrázi a rozdělení; původní texty a anotační návrhy se nemění.
Výběr je účelový, omezený dostupným časem, a není reprezentativní pro celý pilot.
Pro tuto část se nedopočítává recall ani pořadí produktů.

Průměr po odpovědích: doložená S2 precision **0,7141**; při hypoteticky plné podpoře
všech skutečně nepřístupných NA párů horní mez **0,8050**. Jmenovatel zahrnuje
S2/S1/S0/NA explicitní páry a nezahazuje nedostupné zdroje. Bootstrap po třech
úlohách (10000 výběrů, seed20261013) má percentilové95% intervaly0,6000–0,8006
pro dolní a0,7634–0,8500 pro horní mez; jde o dvě distribuce mezí, nikoli jediný
interval pokrývající veškerou neznámou podporu. Se třemi účelově vybranými úlohami
mají CI jen popisný význam. Tento výsledek se **nesmí vydávat za precision všech33
odpovědí ani za finální benchmark**. Přesná čísla jsou v `restricted_atomic_metrics.csv`.
