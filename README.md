# Normativi — kalkulator proizvodnih normativa i montaže etiketa

Streamlit aplikacija koja u jednom alatu objedinjuje dva ključna izračuna za
offset tisak samoljepljivih etiketa:

1. **Normativ (jedna etiketa)** — vrijeme i brzina proizvodnje po stroju
   (araka/h, etiketa/h) za tisak, štancanje i rezanje, prema parametrima stroja
   i naloga (naklada, broj boja, format...).
2. **Montaža (kompleti)** — optimalan raspored etiketa na tiskovni arak:
   maksimizira broj kompleta (A+B etikete različitih dimenzija) po araku,
   kroz 30+ formata papira, uz zadane napuste i margine.

Rezultati se izvoze u **PDF izvještaj** (reportlab).

## Pokretanje

```bash
pip install -r requirements.txt
streamlit run app.py        # ili dvoklik na pokreni.bat (Windows)
```

## Struktura

```
app.py             # navigacijska ljuska (Streamlit multipage)
pages/
  jedna_etiketa.py # normativ za jednu etiketu
  kompleti.py      # montaža kompleta (A+B optimizacija)
normativ_calc.py   # jezgra izračuna normativa (čista logika, bez UI)
montaza_calc.py    # jezgra optimizacije montaže
pdf_export.py      # PDF izvještaj
papiri.json        # formati papira (dimenzije + margine)
params.json        # parametri strojeva (vremena pripreme, brzine...)
```

Kalkulacijska logika je odvojena od UI-ja (`*_calc.py` moduli se mogu koristiti
samostalno — ista jezgra pogoni i [ERP](https://github.com/Shywera/erp) modul normativa).

## Kontekst

Alat iz stvarne proizvodnje — zamjenjuje ručno računanje normativa i ručno
slaganje montaže u grafičkom editoru. Dio šireg skupa alata:
[alati](https://github.com/Shywera/tools) · [WMS](https://github.com/Shywera/wms) ·
[Reklamacije/QMS](https://github.com/Shywera/reklamacije)
