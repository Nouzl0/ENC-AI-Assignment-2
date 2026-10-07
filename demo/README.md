# Lokální kontrola softwaru, nikoli benchmark

```bash
bash demo/run_demo.sh  # unittesty včetně skutečné CLI pipeline na fixtures
# Totéž: python3 -m unittest discover -s tests -v
python3 scripts/make_demo_data.py  # samostatná pipeline, dočasná data se odstraní
```

Žádné produktové API, účty ani externí web. HTTP testy používají jen vlastní server
na loopbacku. Pipeline vytváří 40 syntetických DEMO úloh, 500 plánovaných fixture běhů,
skutečně parsuje texty přes check_citations a skóruje nezávisle očekávané metriky.
Ratingy jsou deterministické testovací hodnoty, **ne lidské posudky**. Včetně retry,
selhání, S2/S1/S0/NA/FAB, necitovaných a neatributovaných tvrzení; H1/H2 nejsou potvrzovány.
Gate testy vyrábějí pouze dočasné falešné testovací identity/doklady, ne skutečné schválení.

Pro inspekci lze zachovat novou fixture složku mimo Git:

```bash
python3 scripts/make_demo_data.py --out "$HOME/czai-synthetic-inspection-v1"
```

Existující složka se nepřepisuje. Ani její metriky nejsou výsledky produktů.
`example/` je historický ilustrační CSV a tři texty; **není platný současný run plan**
(chybí sidecar, plná matice i povinné artefaktové metadata). Nepoužívat jej pro ostrý
postup ani prezentovat jako validovaný E2E test. Neexistuje režim ONLINE benchmarku.
