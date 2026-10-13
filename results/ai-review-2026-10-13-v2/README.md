# Opravená verze AI hodnocení pilotu

Tato verze nahrazuje v1 pro obsahové závěry a citační metriky vybraného subsetu. V1 zůstává historický auditní záznam. Nejde o lidské ratingy, G3 ani potvrzení H1/H2. Zahrnuje 11 dokončených odpovědí na 3 záměrně vybrané úlohy (CIT-004, CIT-008, CIT-013), nikoli celý sběr. Vynechané terminální selhání ChatGPT CIT-004 není v tomto jmenovateli; průchodnost je nutné uvést zvlášť.

Znovu byly ověřeny přesně citované stránky, případně totožný dokument v ověřeném zrcadle; přístupová chyba nebyla vydávána za nepravdivost. Byla opravena chybná interpretace ČSÚ, ústavy, nařízení o SBOM a minimálních prvků NTIA. Atomizace zahrnuje dříve vynechané faktické podmínky mimo CLAIMS; důkazové citované úryvky se nepovažují za další tvrzení. Originály odpovědí se nemění.

Explicitních párů je 99: 78 S2, 1 S1, 20 S0 a 0 NA. Makro přesnost po odpovědích je 0,7954; 95% percentilový bootstrap po úlohách 0,7265–0,8433. Pouze tři klastry mají hrubé diskrétní rozdělení. Interval popisuje variabilitu tohoto subsetu a nezahrnuje chyby AI ratingu ani populaci produktů. Seed 20261013, 10000 replikací. Podrobné řádky a nové zdrojové důkazy jsou v CSV a audit-evaluation.json.

Původní soukromé snapshoty se nepublikují; public záznamy obsahují přesný cited/evidence URL, locator, datum a hash. Před použitím jako lidská reference je nutná nezávislá kontrola. Část syntaxe, současné metadata a nativní bindingy nadále vyžadují plné lidské posouzení.

Obsahové posouzení je samostatně provedeno na všech 33 pilotních odpovědích / 8 úlohách. Pro 12 prvních pokusů vybraného citačního subsetu, při započtení terminálního selhání ChatGPT CIT-004 jako nuly, je makro precision 0.7291; bootstrap CI 0.6175–0.8433. Dokončený subset je citlivý na vynechání selhání, proto je tento diagnostický jmenovatel uveden zvlášť.
