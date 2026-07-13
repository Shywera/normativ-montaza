"""
pages/kompleti.py  —  Kompleti (montaža etiketa na arku)
"""
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from montaza_calc import (
    TIPOVI_PAPIRA, DEFAULT_PAPIRI,
    ucitaj_papire, spremi_papire,
    izracunaj, compute_ocjene,
    draw_montaza, export_montaza_pdf,
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1B3A5C; }
[data-testid="stSidebar"] * { color: #E8F0F8 !important; }
div[data-baseweb="select"] > div {
    background: #1e2235 !important; border: 1px solid #404468 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
if 'papiri' not in st.session_state:
    st.session_state.papiri = ucitaj_papire()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Postavke")
    odabrani_tip = st.selectbox("Tip papira", TIPOVI_PAPIRA)
    broj_etiketa = st.radio("Broj etiketa u kompletu", [1, 2, 3], index=2, horizontal=True)

    st.divider()
    st.header("📏 Etikete")

    st.caption("Etiketa A")
    v_a = st.number_input("Visina A (mm)", min_value=0, value=0)
    s_a = st.number_input("Širina A (mm)", min_value=0, value=0)

    st.caption("Etiketa B" + ("" if broj_etiketa >= 2 else "  *(neaktivno)*"))
    v_b = st.number_input("Visina B (mm)", min_value=0, value=0, disabled=(broj_etiketa < 2))
    s_b = st.number_input("Širina B (mm)", min_value=0, value=0, disabled=(broj_etiketa < 2))
    if broj_etiketa < 2:
        v_b = s_b = 0

    st.caption("Etiketa C" + ("" if broj_etiketa == 3 else "  *(neaktivno)*"))
    v_c = st.number_input("Visina C (mm)", min_value=0, value=0, disabled=(broj_etiketa < 3))
    s_c = st.number_input("Širina C (mm)", min_value=0, value=0, disabled=(broj_etiketa < 3))
    if broj_etiketa < 3:
        v_c = s_c = 0

    st.divider()
    st.header("📐 Napusti")
    c1, c2 = st.columns(2)
    mg   = c1.number_input("Gore (mm)",   min_value=0, value=8)
    md   = c2.number_input("Dolje (mm)",  min_value=0, value=12)
    ml   = c1.number_input("Lijevo (mm)", min_value=0, value=5)
    mdes = c2.number_input("Desno (mm)",  min_value=0, value=5)
    odmak = st.number_input("Odmak bez napusta (mm)", min_value=0, value=0,
                            help="Dodaje se na sve napuste")

    st.divider()
    izracunaj_btn = st.button("Izračunaj", type="primary", use_container_width=True)

    st.divider()
    st.caption("Ocjena rezultata")
    k_ocjena = st.slider("Težina skarta (k)", 0.0, 1.0, 0.5, 0.05,
                         disabled=(broj_etiketa == 1),
                         help="0 = samo broj kompleta, 1 = maksimalno kažnjava škart i višak")

# ─── Validacija i izračun ─────────────────────────────────────────────────────
eff_mg, eff_md, eff_ml, eff_mdes = mg + odmak, md + odmak, ml + odmak, mdes + odmak
filtrirani_papiri = [p for p in st.session_state.papiri if p.get('tip') == odabrani_tip]

if izracunaj_btn:
    greska = None
    if v_a <= 0 or s_a <= 0:
        greska = "Unesite dimenzije etikete A."
    elif broj_etiketa >= 2 and (v_b <= 0 or s_b <= 0):
        greska = "Unesite dimenzije etikete B."
    elif broj_etiketa == 3 and (v_c <= 0 or s_c <= 0):
        greska = "Unesite dimenzije etikete C."
    elif not filtrirani_papiri:
        greska = f"Nema papira tipa '{odabrani_tip}'."

    if greska:
        st.error(greska)
    else:
        rezultati, montaza_podaci = [], []
        with st.spinner("Izračunavam..."):
            for p in filtrirani_papiri:
                r = izracunaj(p, broj_etiketa, v_a, s_a, v_b, s_b, v_c, s_c,
                              eff_mg, eff_md, eff_ml, eff_mdes)
                if r and r['kompleta'] > 0:
                    kol = "Ukupno kom" if broj_etiketa == 1 else "Ukupno kompleta"
                    row = {
                        "Format": p['naziv'], kol: int(r['kompleta']),
                        "A (stupci×redovi)": f"{r['stupaca_a']}×{r['u_visinu_a']} = {r['ukupno_a']} kom",
                    }
                    if broj_etiketa >= 2:
                        row["B (stupci×redovi)"] = f"{r['stupaca_b']}×{r['u_visinu_b']} = {r['ukupno_b']} kom"
                    if broj_etiketa == 3:
                        row["C (stupci×redovi)"] = f"{r['stupaca_c']}×{r['u_visinu_c']} = {r['ukupno_c']} kom"
                    if broj_etiketa == 2:
                        row["Višak A/B"] = f"{int(r['ukupno_a']-r['kompleta'])} / {int(r['ukupno_b']-r['kompleta'])}"
                    elif broj_etiketa == 3:
                        row["Višak A/B/C"] = (f"{int(r['ukupno_a']-r['kompleta'])} / "
                                              f"{int(r['ukupno_b']-r['kompleta'])} / "
                                              f"{int(r['ukupno_c']-r['kompleta'])}")
                    row["Škart"] = f"{r['skart_postotak']}%"
                    rezultati.append(row)
                    montaza_podaci.append({
                        "naziv": p['naziv'], "papir": p, "rezultat": r,
                        "v_a": v_a, "s_a": s_a, "v_b": v_b, "s_b": s_b,
                        "v_c": v_c, "s_c": s_c, "broj_etiketa": broj_etiketa,
                        "mg": eff_mg, "md": eff_md, "ml": eff_ml, "mdes": eff_mdes,
                    })

        if rezultati:
            kol_sort = "Ukupno kom" if broj_etiketa == 1 else "Ukupno kompleta"
            st.session_state.montaza_podaci = montaza_podaci
            st.session_state.rezultati_df   = pd.DataFrame(rezultati).sort_values(kol_sort, ascending=False)
        else:
            st.session_state.pop('montaza_podaci', None)
            st.session_state.pop('rezultati_df', None)
            st.error("Nijedna etiketa ne stane s obzirom na zadane napuste.")

# ─── Prikaz rezultata ─────────────────────────────────────────────────────────
st.title("Kompleti")

if st.session_state.get('rezultati_df') is not None and st.session_state.get('montaza_podaci'):
    df      = st.session_state.rezultati_df.copy()
    podaci  = st.session_state.montaza_podaci
    ocjene  = compute_ocjene(podaci, k_ocjena)
    df['Ocjena'] = df['Format'].map(ocjene)
    df = df.sort_values('Ocjena', ascending=False).reset_index(drop=True)

    def _stil(row):
        if row.name == 0:
            return ['background-color: #1a3a1a; color: #5ddf8a; font-weight: bold'] * len(row)
        return [''] * len(row)

    st.dataframe(df.style.apply(_stil, axis=1), use_container_width=True, hide_index=True)

    # ── Grafički prikaz ────────────────────────────────────────────────────────
    st.subheader("Grafički prikaz montaže")
    nazivi = [d['naziv'] for d in podaci]
    ocjene_graf = compute_ocjene(podaci, k_ocjena)
    najbolji = max(ocjene_graf, key=ocjene_graf.get) if ocjene_graf else None

    col1, col2, col3 = st.columns([4, 1, 1.5], vertical_alignment="bottom")
    odabrani_prikaz = col1.selectbox(
        "Odaberi format:", nazivi,
        format_func=lambda n: ("🟢 " + n) if n == najbolji else n,
    )
    prikazi = col2.toggle("Prikaži graf", value=False)

    if prikazi:
        d = next((x for x in podaci if x['naziv'] == odabrani_prikaz), None)
        if d:
            with st.spinner("Generiranje grafa..."):
                pdf_buf = export_montaza_pdf(
                    d['papir'], d['rezultat'],
                    d['v_a'], d['s_a'], d['v_b'], d['s_b'], d['broj_etiketa'],
                    d['v_c'], d['s_c'], d['mg'], d['md'], d['ml'], d['mdes'],
                )
                col3.download_button("🖨️ Preuzmi PDF", data=pdf_buf,
                                     file_name=f"montaza_{d['naziv']}.pdf",
                                     mime="application/pdf")
                fig = draw_montaza(
                    d['papir'], d['rezultat'],
                    d['v_a'], d['s_a'], d['v_b'], d['s_b'], d['broj_etiketa'],
                    d['v_c'], d['s_c'], d['mg'], d['md'], d['ml'], d['mdes'],
                )
                st.pyplot(fig, use_container_width=False)
                plt.close(fig)

else:
    st.info("Unesite dimenzije etiketa i klikni **Izračunaj**.")

# ─── Baza papira ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("📋 Aktivni formati")

grupe = {tip: [] for tip in TIPOVI_PAPIRA}
for idx, p in enumerate(st.session_state.papiri):
    grupe[p.get('tip', TIPOVI_PAPIRA[0])].append((idx, p))

for tip in TIPOVI_PAPIRA:
    if not grupe[tip]:
        continue
    with st.expander(f"{tip}  ({len(grupe[tip])})"):
        for idx, p in grupe[tip]:
            confirm = st.session_state.get('_confirm_del')
            edit    = st.session_state.get('_edit_idx')
            if confirm == idx:
                cc = st.columns([5, 2, 2])
                cc[0].warning(f"Obrisati **{p['naziv']}**?")
                if cc[1].button("Da", key=f"da_{idx}", type="primary"):
                    st.session_state.papiri = [p2 for i2, p2 in enumerate(st.session_state.papiri) if i2 != idx]
                    spremi_papire(st.session_state.papiri)
                    del st.session_state['_confirm_del']
                    st.rerun()
                if cc[2].button("Ne", key=f"ne_{idx}"):
                    del st.session_state['_confirm_del']
                    st.rerun()
            elif edit == idx:
                ec = st.columns([3, 2, 2, 2, 2])
                ec[0].selectbox("Tip", TIPOVI_PAPIRA, key="ed_tip",
                                index=TIPOVI_PAPIRA.index(st.session_state.get("ed_tip", TIPOVI_PAPIRA[0])))
                ec[1].number_input("Visina", min_value=1, key="ed_v")
                ec[2].number_input("Širina", min_value=1, key="ed_s")
                if ec[3].button("Spremi", key=f"sav_{idx}", type="primary"):
                    papiri_c = list(st.session_state.papiri)
                    papiri_c[idx] = {"naziv": f"{st.session_state.ed_v}x{st.session_state.ed_s}",
                                     "v": st.session_state.ed_v, "s": st.session_state.ed_s,
                                     "tip": st.session_state.ed_tip}
                    st.session_state.papiri = papiri_c
                    spremi_papire(st.session_state.papiri)
                    del st.session_state['_edit_idx']
                    st.toast("Papir spremljen!", icon="✅")
                    st.rerun()
                if ec[4].button("Odustani", key=f"can_{idx}"):
                    del st.session_state['_edit_idx']
                    st.rerun()
            else:
                cols = st.columns([8, 1, 1])
                cols[0].write(p['naziv'])
                if cols[1].button("✏️", key=f"ed_{idx}"):
                    st.session_state._edit_idx = idx
                    st.session_state.ed_v  = p['v']
                    st.session_state.ed_s  = p['s']
                    st.session_state.ed_tip = p.get('tip', TIPOVI_PAPIRA[0])
                    st.rerun()
                if cols[2].button("🗑️", key=f"del_{idx}"):
                    st.session_state._confirm_del = idx
                    st.rerun()

with st.expander("➕ Dodaj novi papir"):
    c1, c2, c3 = st.columns(3)
    n_tip = c1.selectbox("Tip", TIPOVI_PAPIRA, key="novi_tip")
    n_v   = c2.number_input("Visina (mm)", min_value=0, value=0, key="novi_v")
    n_s   = c3.number_input("Širina (mm)", min_value=0, value=0, key="novi_s")
    if st.button("Spremi papir"):
        if n_v <= 0 or n_s <= 0:
            st.error("Dimenzije moraju biti veće od 0.")
        else:
            st.session_state.papiri = st.session_state.papiri + [
                {"naziv": f"{n_v}x{n_s}", "v": n_v, "s": n_s, "tip": n_tip}
            ]
            spremi_papire(st.session_state.papiri)
            st.toast(f"Papir {n_v}x{n_s} dodan!", icon="✅")
            st.rerun()

with st.expander("⚠️ Reset baze papira"):
    st.warning("Vraća originalne formate.")
    potvrda = st.checkbox("Potvrđujem reset")
    if st.button("Resetiraj", disabled=not potvrda):
        st.session_state.papiri = [p.copy() for p in DEFAULT_PAPIRI]
        spremi_papire(st.session_state.papiri)
        st.success("Baza resetirana.")
        st.rerun()
