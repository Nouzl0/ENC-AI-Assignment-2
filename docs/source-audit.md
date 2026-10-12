(source-audit)=
# Kontrola referencí před G1

Datum kontroly: 12. 10. 2026. Read-only AI reviewer prošel všech 30 veřejných
dev/val případů; operátor zkontroloval významné nálezy. Tato kontrola připravuje
podklady pro nezávislého lidského ověřovatele. Není lidskou verifikací, ratingem
produktových odpovědí ani úplným `source_evidence.csv` se snapshoty všech RF/OF.

| Úloha | Přečtený podklad a locator | Zjištění / zbývající mezera |
| --- | --- | --- |
| CIT-001 | [Originální článek, Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7745181/fullTextXML), Abstract Results a Table 2 | 95 %, 95% credible interval 90,3–97,6. NEJM přímo vracel 403. |
| CIT-002 | [WHO](https://www.who.int/news/item/04-03-2015-who-calls-on-countries-to-reduce-sugars-intake-among-adults-and-children), Strong/Conditional recommendation | Volné cukry <10 % energie; <5 % podmíněné doporučení; guideline 2015. |
| CIT-003 | [NNDC ENSDF](https://www.nndc.bnl.gov/nudat3/getdecaydataset.jsp?dsid=14c+bM+decay&nucleus=14N), parent 14C; [Stuiver–Polach](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D686D7894B8BAC3212589AFE418E147E/S0033822200003672a.pdf/div-class-title-discussion-reporting-of-span-class-sup-14-span-c-data-div.pdf), § 3 | 5 700 ±30 let; historický konsenzus 5 730 ±40 a konvenční Libbyho hodnota 5 568 se nesmějí zaměnit. |
| CIT-004 | [Zeměměřický úřad](https://cuzk.gov.cz/Aktuality-resort/20140225/Snezka.aspx), odstavec měření a staré kóty | 1 603,296 m; 1 602 je zaokrouhlená kóta jiného trigonometrického bodu 1 602,02 m. Měření je z 2014. |
| CIT-005 | [MMR](https://mmr.gov.cz/cs/ostatni/web/novinky/novy-stavebni-zakon-zacal-platit-i-pro-bezne-stavb), úvod; [text zákona](https://mmr.gov.cz/getmedia/498e23d0-8d99-4025-a2f4-dccd56fdd3d9/Stavebni-zakon_cistopis_195-152-465-126.pdf.aspx?ext=.pdf), § 334a–335 | Běžné stavby od 1. 7. 2024; formální účinnost a přechodné režimy odlišeny. |
| CIT-006 | [e-Sbírka](https://e-sbirka.gov.cz/sb/2009/40?odkazId=41211349&zalozka=text), § 230 odst. 1 | Přímé otevření neposkytlo čitelný text. Současná dvouletá sazba je zatím jen indexovaný podklad. Starý policejní PDF má jinou sazbu. |
| CIT-007 | [GFŘ PDF](https://financnisprava.gov.cz/assets/cs/prilohy/d-seznam-dani/Informace_GFR_ke_zmenam_sazeb_DPH_od_1_1_2024.pdf), § 2.2, s. 3–4 | RF jídlo 12 % potvrzen. OF nápoje opraveno o výjimky; historické OF „předtím 10 %“ ještě samostatně ověřit. |
| CIT-008 | [Ústava, PSP](https://www.psp.cz/docs/laws/constitution.html), čl. 19 odst. 2 | Věk 40 let; premisa 35 je chybná. |
| CIT-009 | [NVD API](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-44228), cvssMetricV31, Primary NVD | CVSS 3.1: 10.0, CRITICAL. |
| CIT-010 | [Microsoft ESU](https://www.microsoft.com/en-us/windows/extended-security-updates), úvod a How to get Windows 10 ESU | Konec podpory 14. 10. 2025, nynější spotřebitelské ESU do 12. 10. 2027. Historické OF původně 13. 10. 2026 zbývá ověřit; blog vracel 403. |
| CIT-011 | [UCLA / Kleinrock](https://www.lk.cs.ucla.edu/internet_first_words.html), úvod a IMP log | „lo“, 29. 10. 1969, UCLA → SRI. |
| CIT-012 | [GovInfo EO](https://www.govinfo.gov/content/pkg/FR-2021-05-17/pdf/2021-10460.pdf), § 4; [NTIA](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom), úvod | SBOM definice, EO 14028 z 12. 5. 2021; NTIA minimum elements 12. 7. 2021. |
| CIT-013 | [ČSÚ první výsledky](https://csu.gov.cz/produkty/csu-predstavil-prvni-vysledky-scitani-2021), první dva odstavce | 10 524 167; půlnoc 26./27. 3. 2021. Stránka má rozpor textového roku vydání a metadat, nikoli počtu. |
| CIT-014 | [Eurostat původní release](https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/ddn-20241219-3); [aktuální API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ind_ren?geo=EU27_2020&nrg_bal=REN&unit=PC&sinceTimePeriod=2020), rok 2023 | Původně 24,5 %, databáze aktualizovaná 15. 9. 2026: 24,579 %, zaokrouhleně 24,6 %. Hodnotit správnou verzi, ne trestat doloženou revizi. |
| CIT-015 | [ECB Bulletin 6/2026](https://www.ecb.europa.eu/press/economic-bulletin/html/eb202606.en.html), Summary → Monetary policy decisions a metadata | MRO 2,65 % od 16. 9.; publikace 24. 9. splňuje 30 dnů k datu kontroly. Zpráva 10. 9. již nikoli. |
| CIT-016 | [Bitslog původní analýza](https://bitslog.com/2013/04/17/the-well-deserved-fortune-of-satoshi-nakamoto/), metodické předpoklady | Odhad těžby nedokazuje přesné současné vlastnictví BTC. Celý OF rozsah 0,6–1,1 milionu nebyl ověřen, BitMEX vracel 404. |
| CIT-017 | [Historie UK](https://cuni.cz/UK-103.html), rok 1348 | 7. 4. 1348, Karel IV. |
| CIT-018 | [Archiv Národního divadla](https://archiv.narodni-divadlo.cz/inscenace/5693), světová premiéra | 29. 10. 1787, Stavovské divadlo; historický název Nosticovo tento odstavec samostatně nepotvrdil. |
| CIT-019 | [MZV](https://mzv.gov.cz/jnp/cz/o_ministerstvu/historie_a_osobnosti_ceske_diplomacie/leden_1993_rozpad_ceskoslovenska_a_vznik.html); [PSP federace](https://www.psp.cz/eknih/1969fs/rejstrik/info.htm), Úvod | Samostatný stát 1. 1. 1993, federace od 1. 1. 1969. Přesný den přejmenování 6. 3. 1990 dosud pouze index e-Sbírky. |
| CIT-020 | [Shakespeare Birthplace Trust](https://www.shakespeare.org.uk/explore-shakespeare/shakespedia/william-shakespeare/when-was-shakespeare-born/), Parish Register | Přesné narození není zaznamenáno; křest 26. 4. 1564, tradice narozenin 23. 4. |
| CIT-021 | [Nobel Foundation](https://www.nobelprize.org/prizes/physics/1921/einstein/facts/), Prize motivation | Zákon fotoelektrického jevu, cena za 1921, převzetí 1922. |
| CIT-022 | [EHT release](https://eventhorizontelescope.org/press-release-april-10-2019-astronomers-capture-first-image-black-hole), úvod | EHT, M87*, 10. 4. 2019. |
| CIT-023 | [EUR-Lex](https://eur-lex.europa.eu/legal-content/CS/TXT/HTML/?uri=CELEX:32016R0679), čl. 83 odst. 5 | Limit doplněn o podnik a předchozí finanční rok. Přímé HTML/PDF končilo robot challenge; nejde o dokončené primární ověření. |
| CIT-024 | [Evropská komise](https://climate.ec.europa.eu/areas-action/european-climate-law_en), 2030 climate target | Alespoň −55 % čistých emisí proti 1990. OF čl. 4 odst. 1 přímo v EUR-Lex neotevřen. |
| CIT-025 | [Originální arXiv](https://arxiv.org/abs/2005.11401), metadata a abstrakt | Název, Patrick Lewis et al., NeurIPS 2020, arXiv:2005.11401. Absolutní historická priorita termínu samostatně neprokázána. |
| CIT-026 | [RFC Editor](https://www.rfc-editor.org/rfc/rfc9114.html), hlavička | RFC 9114, červen 2022. |
| CIT-027 | [ČSÚ srpen](https://csu.gov.cz/rychle-informace/miry-zamestnanosti-nezamestnanosti-a-ekonomicke-aktivity-srpen-2026), Míra nezaměstnanosti; [ÚP září](https://up.gov.cz/nezamestnanost-v-cesku-zari-2026), odrážky 1–2 | ČSÚ VŠPS 15–64 očištěně 3,4 % za srpen; ÚP PNO 5,0 % za září. ČSÚ 15–74 varianta 3,2 %. Čísla/období/definice odlišit. |
| CIT-028 | [MPSV](https://mpsv.gov.cz/minimalni-mzda-se-v-pristim-roce-vyrazne-zvysi-o-1-900-kc-na-20-800-kc-mesicne-schvalila-vlada-v-narizeni), titul a mechanismus | 20 800 Kč měsíčně pro 2025. |
| CIT-029 | [UK](https://karel700.cuni.cz/KAREL-56.html), historický odstavec | Stavba 1357–1402. RF „přesnou cenu v dnešních Kč nelze určit“ není přímo podpořen zdrojem; potřebuje přezkoumání metodiky převodu a nákladů. |
| CIT-030 | [Nobel Foundation](https://www.nobelprize.org/prizes/literature/1984/summary/), laureát | Jaroslav Seifert, 1984. |

Následná kontrola operátora doplnila dvě historické mezery: [Finanční správa,
6. 6. 2023](https://financnisprava.gov.cz/assets/cs/prilohy/fs-financni-sprava-cr/EtR_DPH_20230606.pdf),
s. 2, dokládá 10 % pro stravování; [Microsoft News Center,
30. 6. 2025](https://news.microsoft.com/de-de/mit-windows-11-copilot-pcs-und-windows-365-sicher-bleiben/),
první varianta spotřebitelského ESU, dokládá původní konec 13. 10. 2026.
Historický konsenzus uhlíku-14 5 730 ±40 let dokládá také [Radiocarbon,
Notice to Readers](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D7E740C89FB80857FD23924A5C0050CD/S0033822200001120a.pdf/rdc_volume_14_issue_1_cover_and_front_matter.pdf),
PDF s. 3; tento přesný údaj neodvozujeme jen ze Stuiver–Polach.

Před podpisem G1 je třeba vyřešit ostatní uvedené mezery a získat lidskou kontrolu
každého RF i OF s konkrétní hodnotou, locatorem, datem a soukromým snapshotem/hash.
Žádné přístupové selhání není důkazem neexistence zdroje. Dynamické reference
se navíc ověřují podle UTC dne každého analytického běhu.
