"""
pages/jedna_etiketa.py  —  Normativ rada (jedna etiketa)
"""
import streamlit as st
from normativ_calc import (
    calc_layout, calc_strip_cut, calc_sc20, calc_mcs115,
    calc_stancanje, calc_tisak,
    DEFAULT_PARAMS, ucitaj_params, spremi_params,
)
from pdf_export import generate_pdf

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1B3A5C; }
[data-testid="stSidebar"] * { color: #E8F0F8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label { color: #A8C4E0 !important; }
div[data-testid="metric-container"] {
    background: #F0F6FF; border-radius: 8px;
    padding: 10px 16px; border-left: 4px solid #2E6DA4;
}
h3 { color: #1B3A5C; border-bottom: 2px solid #2E6DA4; padding-bottom: 4px; }
</style>
""", unsafe_allow_html=True)


def _sfmt(sec):
    if sec < 3600:
        return f"{sec // 60} min"
    return f"{sec // 3600}h {(sec % 3600) // 60:02d}min"


# ─── Session state ────────────────────────────────────────────────────────────
if 'params' not in st.session_state:
    st.session_state.params = ucitaj_params()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✂️ Unos podataka")
    naziv = st.text_input("Naziv proizvoda", value="primjer etikete")

    st.markdown("---")
    st.markdown("**Papir**")
    gramatura  = st.number_input("Gramatura (g/m²)", value=68, min_value=30, max_value=200, step=1)
    tip_papira = st.selectbox("Tip papira", ["metal", "bijeli"])

    st.markdown("---")
    st.markdown("**Format arka**")
    c1, c2 = st.columns(2)
    arka_x = c1.number_input("X (mm)", value=970, min_value=100, max_value=1500, step=1)
    arka_y = c2.number_input("Y (mm)", value=685, min_value=100, max_value=1500, step=1)

    st.markdown("---")
    st.markdown("**Format etikete**")
    cA, cB = st.columns(2)
    et_xn = cA.number_input("X netto (mm)", value=60.0, min_value=1.0, step=0.5, format="%.1f")
    et_yn = cB.number_input("Y netto (mm)", value=73.0, min_value=1.0, step=0.5, format="%.1f")
    et_xb = cA.number_input("X brutto (mm)", value=60.0, min_value=1.0, step=0.5, format="%.1f")
    et_yb = cB.number_input("Y brutto (mm)", value=73.0, min_value=1.0, step=0.5, format="%.1f")
    grajfer = st.number_input("Strojni grajfer (mm)", value=20, min_value=0, max_value=50, step=1)

    st.markdown("---")
    st.markdown("**Dorada — Rezanje**")
    naklada_dorada = st.number_input("Naklada dorada (kom)", value=10_000_000,
                                     min_value=1_000, max_value=100_000_000, step=100_000)
    odabir_rez    = st.selectbox("Odabir reza", ["X", "Y"])
    brutto_araka  = st.number_input("Broj brutto araka", value=72_000,
                                    min_value=100, max_value=10_000_000, step=100)

    st.markdown("---")
    st.markdown("**Dorada — Pakiranje**")
    et_u_kutiji      = st.number_input("Etiketa u kutiji (kom)", value=58_000,
                                       min_value=100, max_value=1_000_000, step=1000)
    kutija_na_paleti = st.number_input("Kutija na paleti", value=48, min_value=1, max_value=200, step=1)
    st.text_input("Kutija tip", value="k-26+k-27")
    st.text_input("Paleta tip", value="IND. 1200x1000")

    st.markdown("---")
    st.markdown("**Tisak**")
    naklada_tisak = st.number_input("Naklada tisak (kom)", value=30_000_000,
                                    min_value=1_000, max_value=100_000_000, step=100_000)
    broj_boja = st.number_input("Broj boja", value=5, min_value=1, max_value=8, step=1)
    lakirano  = st.selectbox("Lakirano", ["NE", "DA"])
    prolazi   = st.number_input("Broj prolaza kroz stroj", value=1, min_value=1, max_value=10, step=1)


# ─── Izračun ──────────────────────────────────────────────────────────────────
P = st.session_state.params

layout = calc_layout(arka_x, arka_y, et_xb, et_yb, grajfer, et_xn, et_yn,
                     naklada_dorada, brutto_araka)

r137 = calc_strip_cut(P['POLAR_137'], layout, gramatura, tip_papira, odabir_rez, brutto_araka)
sc   = calc_sc20(layout, gramatura, tip_papira, odabir_rez, brutto_araka,
                 naklada_dorada, et_u_kutiji, kutija_na_paleti,
                 p_strip=P['SC20_STRIP'], p_finish=P['SC20_FINISH'])
mcs  = calc_mcs115(layout, gramatura, tip_papira, odabir_rez, brutto_araka,
                   naklada_dorada, et_u_kutiji, kutija_na_paleti,
                   p_strip=P['MCS_115_STRIP'], p_finish=P['MCS_115_FINISH'])

stanc_results = [
    ("POLAR DC 11",            calc_stancanje(P['POLAR_DC_11'],       layout, gramatura, odabir_rez, brutto_araka, naklada_dorada, et_u_kutiji, kutija_na_paleti)),
    ("BLUMER ATLAS 1110 DUAL", calc_stancanje(P['BLUMER_1110_DUAL'],  layout, gramatura, odabir_rez, brutto_araka, naklada_dorada, et_u_kutiji, kutija_na_paleti)),
    ("BLUMER ATLAS 110",       calc_stancanje(P['BLUMER_110'],        layout, gramatura, odabir_rez, brutto_araka, naklada_dorada, et_u_kutiji, kutija_na_paleti)),
]
tisak_results = [
    ("CX 104 6+LX", calc_tisak(P['CX_104'], layout, gramatura, tip_papira, naklada_tisak, broj_boja, lakirano, prolazi)),
    ("CX 102 5+LX", calc_tisak(P['CX_102'], layout, gramatura, tip_papira, naklada_tisak, broj_boja, lakirano, prolazi)),
    ("CD 102 6+LX", calc_tisak(P['CD_102'], layout, gramatura, tip_papira, naklada_tisak, broj_boja, lakirano, prolazi)),
]

# ─── Naslov + PDF ─────────────────────────────────────────────────────────────
st.title(f"Normativ — {naziv}")

_, _col_pdf = st.columns([6, 1])
with _col_pdf:
    _inputs = dict(
        gramatura=gramatura, tip_papira=tip_papira,
        arka_x=arka_x, arka_y=arka_y,
        et_xn=et_xn, et_yn=et_yn, et_xb=et_xb, et_yb=et_yb,
        grajfer=grajfer, odabir_rez=odabir_rez,
        brutto_araka=brutto_araka, naklada_dorada=naklada_dorada,
        naklada_tisak=naklada_tisak, broj_boja=broj_boja,
        lakirano=lakirano, prolazi=prolazi,
    )
    _pdf_buf = generate_pdf(naziv, _inputs, layout, r137, sc, mcs, stanc_results, tisak_results)
    st.download_button("🖨️ Printaj PDF", data=_pdf_buf,
                       file_name=f"normativ_{naziv.replace(' ','_')}.pdf",
                       mime="application/pdf", use_container_width=True)

with st.expander("📐 Layout arka", expanded=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Etiketa na arku",    f"{layout['et_na_arku']:,}")
    c2.metric("Po X osi",           f"{layout['et_po_x']}")
    c3.metric("Po Y osi",           f"{layout['et_po_y']}")
    c4.metric("Bočno D/L (mm)",     f"{layout['bocno_desno']:.1f}")
    c5.metric("Gornji napust (mm)", f"{layout['gornji_napust']:.1f}")
    if layout['et_na_arku'] == 0:
        st.error("⚠️  Etiketa ne stane na arku — provjeri dimenzije!")
    elif layout['gornji_napust'] < 0:
        st.warning("⚠️  Gornji napust je negativan — provjeri grajfer i dimenzije!")
    c1, c2 = st.columns(2)
    c1.metric("Netto araka (dorada)", f"{layout['netto_araka']:,}")
    c2.metric("Brutto araka (unos)",  f"{brutto_araka:,}")


# ─── Tabovi rezultata ─────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["✂️ Rezanje", "🔲 Štancanje", "🖨️ Tisak"])


# ══ TAB 1 — REZANJE ══════════════════════════════════════════════════════════
with tab1:

    st.markdown("### POLAR 137")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Normativ rezanja (ar/h)",   f"{int(r137['normativ_final']):,}", help="Korigirano za 0,5h pauzu")
    c2.metric("Ukupno araka/smjenu (7h)",  f"{int(r137['normativ_final']*7):,}")
    c3.metric("Broj paleta",               r137['broj_paleta'])
    c4.metric("Broj kanti za otpad",       r137['broj_kanti'])

    with st.expander("Detalji POLAR 137"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Broj rezova (traka)",    r137['broj_rezova'])
        c2.metric("Otpad ukupno (kg)",      f"{r137['ukupno_otpada']:.1f}")
        c3.metric("Ponavljanja (×1000 ar)", r137['ponavljanja'])
        c1, c2, c3 = st.columns(3)
        c1.metric("Priprema",       f"{r137['priprema_sec']//60} min")
        c2.metric("Ukupno rezanje", f"{r137['total_sec']//3600:.1f} h")
        c3.metric("Vibriranje",     f"{r137['vibriranje_total_sec']//3600:.1f} h")

    with st.expander("Dodatni detalji POLAR 137"):
        _freq = r137['ponavljanja'] // max(r137['broj_kanti'], 1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pražnjenje kante",  f"{r137['broj_kanti']}×")
        c2.metric("Učestalost kante",  f"svakih {_freq:,} × 1000 ar")
        c3.metric("Transport paleta",  f"{r137['broj_paleta']} pal × 2")
        c4.metric("Dulja operacija",
                  "Vibriranje" if r137['vibriranje_total_sec'] > r137['total_sec'] else "Rezanje")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Priprema",          _sfmt(r137['priprema_sec']))
        c2.metric("Ukupno rezanje",    _sfmt(r137['total_sec']))
        c3.metric("Ukupno vibriranje", _sfmt(r137['vibriranje_total_sec']))
        c4.metric("Otpad po 1000 ar",  f"{r137['kg_otpad']:.2f} kg")

    st.markdown("---")

    st.markdown("### SC20  (trake + na gotovo + pakiranje)")
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Kombinirani normativ (et/h)", f"{sc['norm_ukupno']:,}")
    c2.metric("Normativ traka (ar/h)",     f"{int(sc['strip']['normativ_final']):,}")
    c3.metric("Normativ na gotovo (et/h)", f"{sc['finish']['normativ_finish']:,}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pakiranje — 1 operater (et/h)", f"{sc['finish']['normativ_pak_1op']:,}")
    c2.metric("Pakiranje — 2 operatera (et/h)", f"{sc['finish']['normativ_pak_2op']:,}")
    c3.metric("Kontra os (finish)", sc['finish']['kontra_os'])

    with st.expander("Detalji SC20 — Trake"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rezovi (traka/ar)", sc['strip']['broj_rezova'])
        c2.metric("Ponavljanja",       sc['strip']['ponavljanja'])
        c3.metric("Paleta (trake)",    sc['strip']['broj_paleta'])
        c4.metric("Otpad trake (kg)",  f"{sc['strip']['ukupno_otpada']:.1f}")

    with st.expander("Dodatni detalji SC20 — Trake"):
        _fSC = sc['strip']['ponavljanja'] // max(sc['strip']['broj_kanti'], 1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pražnjenje kante", f"{sc['strip']['broj_kanti']}×")
        c2.metric("Učestalost kante", f"svakih {_fSC:,} × 1000 ar")
        c3.metric("Transport paleta", f"{sc['strip']['broj_paleta']} pal × 2")
        c4.metric("Priprema",         _sfmt(sc['strip']['priprema_sec']))

    with st.expander("Detalji SC20 — Na gotovo + pakiranje"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Max traka u stroju", sc['finish']['max_traka'])
        c2.metric("Rezovi finish",      sc['finish']['br_rez_finish'])
        c3.metric("Ponavljanja finish", sc['finish']['ponavljanja_finish'])
        c4.metric("Međurez", "DA" if sc['finish']['medurez'] else "NE")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ukupno bunteva",    f"{sc['finish']['uk_buntevi']:,}")
        c2.metric("Broj kutija",       f"{sc['finish']['broj_kutija']:,}")
        c3.metric("Paleta gotova roba", sc['finish']['paleta_gotova'])
        c4.metric("Otpad finish (kg)", f"{sc['finish']['otpad_finish']:.1f}")

    with st.expander("Dodatni detalji SC20 — Na gotovo + pakiranje"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pražnjenje kante (finish)", f"{sc['finish']['kanti_finish']}×")
        c2.metric("Ponavljanja finish",        f"{sc['finish']['ponavljanja_finish']:,}")
        c3.metric("Otpad finish",              f"{sc['finish']['otpad_finish']:.1f} kg")
        c4.metric("Međurez", "DA" if sc['finish']['medurez'] else "NE")

    st.markdown("---")

    st.markdown("### MCS 115  (trake + na gotovo + pakiranje)")
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Kombinirani normativ (et/h)", f"{mcs['norm_ukupno']:,}")
    c2.metric("Normativ traka (ar/h)",     f"{int(mcs['strip']['normativ_final']):,}")
    c3.metric("Normativ na gotovo (et/h)", f"{mcs['finish']['normativ_finish']:,}")
    c1, c2 = st.columns(2)
    c1.metric("Pakiranje — 1 operater (et/h)", f"{mcs['finish']['normativ_pak_1op']:,}")
    c2.metric("Kontra os (finish)", mcs['finish']['kontra_os'])

    with st.expander("Detalji MCS 115"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rezovi traka",       mcs['strip']['broj_rezova'])
        c2.metric("Max traka u stroju", mcs['finish']['max_traka'])
        c3.metric("Bunteva ukupno",     f"{mcs['finish']['uk_buntevi']:,}")
        c4.metric("Kutija",             f"{mcs['finish']['broj_kutija']:,}")

    with st.expander("Dodatni detalji MCS 115"):
        _fMCS = mcs['strip']['ponavljanja'] // max(mcs['strip']['broj_kanti'], 1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pražnjenje kante (trake)", f"{mcs['strip']['broj_kanti']}×")
        c2.metric("Učestalost kante",         f"svakih {_fMCS:,} × 1000 ar")
        c3.metric("Transport paleta",         f"{mcs['strip']['broj_paleta']} pal × 2")
        c4.metric("Priprema trake",           _sfmt(mcs['strip']['priprema_sec']))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pražnjenje kante (finish)", f"{mcs['finish']['kanti_finish']}×")
        c2.metric("Ponavljanja finish",        f"{mcs['finish']['ponavljanja_finish']:,}")
        c3.metric("Otpad finish",              f"{mcs['finish']['otpad_finish']:.1f} kg")
        c4.metric("Paleta gotova roba",        f"{mcs['finish']['paleta_gotova']}")


# ══ TAB 2 — ŠTANCANJE ════════════════════════════════════════════════════════
with tab2:

    for name, r in stanc_results:
        st.markdown(f"### {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 Normativ štancanja (et/h)", f"{r['normativ_stanc']:,}", help="Korigirano za 0,5h pauzu")
        c2.metric("Normativ pakiranja (et/h)", f"{r['normativ_pak']:,}")
        c3.metric("Broj kutija", f"{r['broj_kutija']:,}")
        c4.metric("Broj paleta",  r['broj_paleta'])

        with st.expander(f"Detalji {name}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rezovi/traci",       r['broj_rezova'])
            c2.metric("Broj traka (×1000)", f"{r['broj_traka']:.1f}")
            c3.metric("Kanti otpad",        r['broj_kanti'])
            c4.metric("Otpad ukupno (kg)",  f"{r['ukupno_ot']:.1f}")
            c1, c2 = st.columns(2)
            c1.metric("Štancanje ukupno", f"{r['total_stanc_sec']//3600:.1f} h")
            c2.metric("Pakiranje ukupno", f"{r['total_pak_sec']//3600:.1f} h")

        with st.expander(f"Dodatni detalji {name}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pražnjenje kante", f"{r['broj_kanti']}×")
            c2.metric("Broj traka",       f"{r['broj_traka']:.0f} × 1000")
            c3.metric("Rezovi po traci",  r['broj_rezova'])
            c4.metric("Otpad ukupno",     f"{r['ukupno_ot']:.1f} kg")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Priprema",         _sfmt(r['priprema_sec']))
            c2.metric("Ukupno štancanje", _sfmt(r['total_stanc_sec']))
            c3.metric("Ukupno pakiranje", _sfmt(r['total_pak_sec']))
            c4.metric("Broj paleta",      r['broj_paleta'])

        st.markdown("---")


# ══ TAB 3 — TISAK ════════════════════════════════════════════════════════════
with tab3:

    for name, r in tisak_results:
        st.markdown(f"### {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 Normativ tiska (ar/h)", f"{r['normativ_tisk']:,}", help="Korigirano za 7,5h smjenu")
        c2.metric("Priprema",         f"{r['priprema_h']:.2f} h")
        c3.metric("Pranje stroja",    f"{r['pranje_h']:.2f} h")
        c4.metric("Brutto za izdati", f"{r['brutto_izdati']:,}")

        with st.expander(f"Detalji {name}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Netto araka",      f"{r['netto_araka']:,}")
            c2.metric("Za doradu",        f"{r['za_doradu']:,}")
            c3.metric("Očekivani brutto", f"{r['ocekivani_brutto']:,}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Paleta ulaganje",  r['paleta_ulaz'])
            c2.metric("Paleta izlaganje", r['paleta_izlag'])
            c3.metric("Prolaganja",       r['prolaganja'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Škart (arci)",   f"{r['skart']:,}")
            c2.metric("Ukupno tisak",   f"{r['uk_tisak_sec']//3600:.1f} h")
            c3.metric("Priprema (sec)", f"{r['priprema_sec']:,}")

        with st.expander(f"Dodatni detalji {name}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Prolaganja", r['prolaganja'], help="Zaustavljanje svakih 3000 ar")
            c2.metric("Zamjena paleta (ul+izl)", f"{r['paleta_ulaz'] + r['paleta_izlag']}×")
            c3.metric("Škart arci",   f"{r['skart']:,}")
            c4.metric("Ukupno tisak", _sfmt(r['uk_tisak_sec']))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Priprema",         _sfmt(r['priprema_sec']))
            c2.metric("Pranje stroja",    _sfmt(r['pranje_sec']))
            c3.metric("Očekivani brutto", f"{r['ocekivani_brutto']:,}")
            c4.metric("Za doradu",        f"{r['za_doradu']:,}")

        st.markdown("---")


# ─── Parametri strojeva ───────────────────────────────────────────────────────
st.divider()
st.subheader("⚙️ Parametri strojeva")

_LABELS = {
    'pregled_naloga': 'Pregled naloga (sec)',
    'priprema_robe': 'Priprema robe (sec)',
    'priprema_rm': 'Priprema radnog mjesta (sec)',
    'priprema_programa': 'Priprema programa (sec)',
    'priprema_alata': 'Priprema alata (sec)',
    'nulto_uvlacenje': 'Nulto uvlačenje (sec)',
    'strojno_uvlacenje': 'Strojno uvlačenje (sec)',
    'presanje_x': 'Prešanje po X osi (sec)',
    'presanje_y': 'Prešanje po Y osi (sec)',
    'kontrola_reza': 'Kontrola reza (sec)',
    'kontrola_svakog': 'Kontrola svakog reza (sec)',
    'obrez_1': 'Obrez 1 (sec)',
    'obrez_2': 'Obrez 2 (sec)',
    'obrez_3': 'Obrez 3 (sec)',
    'okret_4': 'Okret 4 (sec)',
    'slaganje_traka': 'Slaganje traka (sec)',
    'vibriranje': 'Vibriranje (sec)',
    'pregledavanje': 'Pregledavanje (sec)',
    'praznjenje_kante': 'Pražnjenje kante (sec)',
    'dovoz_odvoz': 'Dovoz/odvoz palete (sec)',
    'araka_paleta_metal': 'Araka/paleti — metal',
    'araka_paleta_bijeli': 'Araka/paleti — bijeli',
    'tezina_kante': 'Težina kante (kg)',
    'vrijeme_1_reza': 'Vrijeme 1 reza (sec)',
    'uvlacenje_max_traka': 'Uvlačenje max traka (sec)',
    'postavljanje_max_traka': 'Postavljanje max traka (sec)',
    'najlon_sec': 'Stavljanje najlona/kutiji (sec)',
    'deklariranje_sec': 'Deklariranje/kutiji (sec)',
    'pakiranje_1_bunt': 'Pakiranje 1 bunt (sec)',
    'kontrola_1_bunt': 'Kontrola 1 bunt (sec)',
    'priprema_rm_pakiranje': 'Priprema RM pakiranje (sec)',
    'broj_osoba_pakiranje': 'Broj osoba pakiranje',
    'dohvat_trake': 'Dohvat trake (sec)',
    'ulaganje_1_trake': 'Ulaganje 1 trake (sec)',
    'slaganje_kutije': 'Slaganje kutije (sec)',
    'QC_pregled': 'QC pregled (sec)',
    'priprema_ploca': 'Priprema ploča (sec)',
    'priprema_boja': 'Priprema boje (sec)',
    'priprema_laka': 'Priprema laka (sec)',
    'ovjera_QC': 'Ovjera QC (sec)',
    'provjera_povrat': 'Provjera povrata (sec)',
    'pranje_stroj': 'Pranje stroja (sec)',
    'pranje_boja': 'Pranje boje (sec)',
    'pranje_lak': 'Pranje laka (sec)',
    'ulaz_metal': 'Araka/paleti ulaz — metal',
    'ulaz_bijeli': 'Araka/paleti ulaz — bijeli',
    'izlaganje_metal': 'Araka/paleti izlaganje — metal',
    'izlaganje_bijeli': 'Araka/paleti izlaganje — bijeli',
    'prolaganje_svakih': 'Prolaganje svakih (araka)',
    'prolaganje_sec': 'Prolaganje (sec)',
    'zamjena_palete': 'Zamjena palete (sec)',
    'neispravni_prolaganje': 'Neispravni — prolaganje',
    'neispravni_gore': 'Neispravni — gore',
    'neispravni_dolje': 'Neispravni — dolje',
    'dodatak_dorada': 'Dodatak dorada',
    'dodatak_tisak': 'Dodatak tisak',
    'dodatak_fiksan': 'Dodatak fiksan (arci)',
    'dodatak_fiksan_boja': 'Dodatak fiksan/boji (arci)',
    'brzina_metal': 'Radna brzina — metal (ar/h)',
    'brzina_bijeli': 'Radna brzina — bijeli (ar/h)',
}


def _param_form(key, machine_name):
    p = dict(P[key])
    nums = [(k, v) for k, v in p.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    strs = [(k, v) for k, v in p.items() if isinstance(v, str)]

    changed = dict(p)

    for i in range(0, len(nums), 3):
        cols = st.columns(3)
        for j, (k, v) in enumerate(nums[i:i + 3]):
            lbl = _LABELS.get(k, k)
            if isinstance(v, float):
                changed[k] = cols[j].number_input(lbl, value=float(v), format="%.4f",
                                                   step=0.001, key=f"{key}_{k}")
            else:
                changed[k] = int(cols[j].number_input(lbl, value=int(v),
                                                       min_value=0, step=1, key=f"{key}_{k}"))

    for k, v in strs:
        if k == 'najlon':
            changed[k] = st.selectbox('Najlon (DA/NE)', ['DA', 'NE'],
                                       index=0 if v == 'DA' else 1, key=f"{key}_najlon")

    c1, c2 = st.columns(2)
    if c1.button("💾 Spremi", key=f"sav_{key}", type="primary", use_container_width=True):
        st.session_state.params[key] = changed
        spremi_params(st.session_state.params)
        st.toast(f"{machine_name} — parametri spremljeni!", icon="✅")
        st.rerun()
    if c2.button("↩️ Reset stroja", key=f"rst_{key}", use_container_width=True):
        st.session_state.params[key] = dict(DEFAULT_PARAMS[key])
        spremi_params(st.session_state.params)
        st.toast(f"{machine_name} — resetiran na zadano!", icon="✅")
        st.rerun()


ptab_r, ptab_s, ptab_t = st.tabs(["✂️ Rezanje", "🔲 Štancanje", "🖨️ Tisak"])

with ptab_r:
    with st.expander("POLAR 137"):
        _param_form('POLAR_137', 'POLAR 137')
    with st.expander("SC20 — Rezanje na trake"):
        _param_form('SC20_STRIP', 'SC20 Trake')
    with st.expander("SC20 — Rezanje na gotovo + pakiranje"):
        _param_form('SC20_FINISH', 'SC20 Na gotovo')
    with st.expander("MCS 115 — Rezanje na trake"):
        _param_form('MCS_115_STRIP', 'MCS 115 Trake')
    with st.expander("MCS 115 — Rezanje na gotovo + pakiranje"):
        _param_form('MCS_115_FINISH', 'MCS 115 Na gotovo')

with ptab_s:
    with st.expander("POLAR DC 11"):
        _param_form('POLAR_DC_11', 'POLAR DC 11')
    with st.expander("BLUMER ATLAS 1110 DUAL"):
        _param_form('BLUMER_1110_DUAL', 'BLUMER 1110 DUAL')
    with st.expander("BLUMER ATLAS 110"):
        _param_form('BLUMER_110', 'BLUMER 110')

with ptab_t:
    with st.expander("CX 104 6+LX"):
        _param_form('CX_104', 'CX 104')
    with st.expander("CX 102 5+LX"):
        _param_form('CX_102', 'CX 102')
    with st.expander("CD 102 6+LX"):
        _param_form('CD_102', 'CD 102')

with st.expander("⚠️ Reset svih parametara"):
    st.warning("Vraća originalne normativne parametre za sve strojeve.")
    potvrda = st.checkbox("Potvrđujem reset svih parametara")
    if st.button("Resetiraj sve", disabled=not potvrda):
        st.session_state.params = {k: dict(v) for k, v in DEFAULT_PARAMS.items()}
        spremi_params(st.session_state.params)
        st.success("Svi parametri resetirani na zadane vrijednosti.")
        st.rerun()
