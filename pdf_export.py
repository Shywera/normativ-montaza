"""
pdf_export.py  —  Generira A4 landscape PDF normativa (crno-bijelo, jedna stranica)
Isti pristup kao Kompleti projekt: matplotlib → BytesIO → PDF
"""
import io
import datetime
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


def generate_pdf(naziv, inputs, layout, r137, sc, mcs, stanc_results, tisak_results):
    """
    Generira PDF u memoriji i vraća BytesIO buffer.

    stanc_results : list of (name, result_dict)
    tisak_results : list of (name, result_dict)
    """
    today = datetime.date.today().strftime("%d.%m.%Y.")

    fig = plt.figure(figsize=(11.69, 8.27), facecolor='white')
    fig.patch.set_facecolor('white')

    # ── Naslov ────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.975, f"NORMATIV  —  {naziv.upper()}",
             ha='center', va='top', fontsize=13, fontweight='bold', color='black',
             fontfamily='monospace')
    fig.text(0.5, 0.945, f"Datum: {today}",
             ha='center', va='top', fontsize=8.5, color='#555555',
             fontfamily='monospace')

    # Horizontalne linije
    def hline(y, lw=1.0, color='black'):
        fig.add_artist(mlines.Line2D([0.03, 0.97], [y, y],
                                     color=color, linewidth=lw,
                                     transform=fig.transFigure))

    hline(0.925)
    hline(0.07, lw=0.8, color='#888888')

    # Vertikalni razdjelnici (3 linije → 4 panela)
    panel_x = [0.03, 0.27, 0.51, 0.74, 0.97]   # rubovi 4 panela
    for x in panel_x[1:3]:
        fig.add_artist(mlines.Line2D([x, x], [0.07, 0.925],
                                     color='#aaaaaa', linewidth=0.6,
                                     transform=fig.transFigure))

    # ── Helperi za tekst ──────────────────────────────────────────────────────
    FS_H = 8.5   # font size header
    FS_T = 7.8   # font size tekst
    LH   = 1.55  # line height

    def ph(x, y, text):
        """Panel header (podebljano + tanka linija ispod)."""
        fig.text(x + 0.005, y, text,
                 ha='left', va='top', fontsize=FS_H, fontweight='bold',
                 color='black', fontfamily='monospace')
        fig.add_artist(mlines.Line2D([x + 0.003, x + 0.215], [y - 0.022, y - 0.022],
                                     color='#555555', linewidth=0.5,
                                     transform=fig.transFigure))

    def pt(x, y, lines):
        """Panel tekst — monospace, crno."""
        fig.text(x + 0.005, y - 0.03, '\n'.join(lines),
                 ha='left', va='top', fontsize=FS_T, color='black',
                 fontfamily='monospace', linespacing=LH)

    TOP = 0.915   # gornji rub sadržaja

    # ══ Panel 1: Ulazni parametri + Layout ═══════════════════════════════════
    px1 = panel_x[0]
    ph(px1, TOP, "ULAZNI PARAMETRI")
    lines1 = [
        f"Gramatura : {inputs['gramatura']} g/m\u00b2",
        f"Papir     : {inputs['tip_papira']}",
        f"Arak      : {inputs['arka_x']}\xd7{inputs['arka_y']} mm",
        f"Et. netto : {inputs['et_xn']}\xd7{inputs['et_yn']} mm",
        f"Et. brutto: {inputs['et_xb']}\xd7{inputs['et_yb']} mm",
        f"Grajfer   : {inputs['grajfer']} mm",
        f"Odabir rez: {inputs['odabir_rez']}",
        "",
        "\u2500" * 23,
        "LAYOUT",
        "\u2500" * 23,
        f"Et. na arku : {layout['et_na_arku']:>10,}",
        f"  Po X      : {layout['et_po_x']:>10}",
        f"  Po Y      : {layout['et_po_y']:>10}",
        f"Netto araka : {layout['netto_araka']:>10,}",
        f"Brutto araka: {inputs['brutto_araka']:>10,}",
        "",
        "\u2500" * 23,
        "NAKLADE",
        "\u2500" * 23,
        f"Dorada : {inputs['naklada_dorada']:>12,}",
        f"Tisak  : {inputs['naklada_tisak']:>12,}",
        f"Boje   : {inputs['broj_boja']:>12}",
        f"Lak    : {inputs['lakirano']:>12}",
        f"Prolazi: {inputs['prolazi']:>12}",
    ]
    pt(px1, TOP, lines1)

    # ══ Panel 2: Rezanje ═════════════════════════════════════════════════════
    px2 = panel_x[1]
    ph(px2, TOP, "REZANJE")
    lines2 = [
        "POLAR 137",
        f"  Normativ  : {int(r137['normativ_final']):>8,} ar/h",
        f"  Rezovi    : {r137['broj_rezova']:>8}",
        f"  Paleta    : {r137['broj_paleta']:>8}",
        f"  Otpad     : {r137['ukupno_otpada']:>8.1f} kg",
        "",
        "SC20  (trake)",
        f"  Normativ  : {int(sc['strip']['normativ_final']):>8,} ar/h",
        f"  Rezovi    : {sc['strip']['broj_rezova']:>8}",
        "",
        "SC20  (na gotovo)",
        f"  Normativ  : {sc['finish']['normativ_finish']:>8,} et/h",
        f"  Pak. 1op. : {sc['finish']['normativ_pak_1op']:>8,} et/h",
        f"  Pak. 2op. : {sc['finish']['normativ_pak_2op']:>8,} et/h",
        "",
        f"\u25ba SC20 kombinirani",
        f"  {sc['norm_ukupno']:,} et/h",
        "",
        "MCS 115  (trake)",
        f"  Normativ  : {int(mcs['strip']['normativ_final']):>8,} ar/h",
        f"  Rezovi    : {mcs['strip']['broj_rezova']:>8}",
        "",
        "MCS 115  (na gotovo)",
        f"  Normativ  : {mcs['finish']['normativ_finish']:>8,} et/h",
        f"  Pak. 1op. : {mcs['finish']['normativ_pak_1op']:>8,} et/h",
        "",
        f"\u25ba MCS 115 kombinirani",
        f"  {mcs['norm_ukupno']:,} et/h",
    ]
    pt(px2, TOP, lines2)

    # ══ Panel 3: Štancanje ════════════════════════════════════════════════════
    px3 = panel_x[2]
    ph(px3, TOP, "\u0160TANCANJE")
    lines3 = []
    for name, r in stanc_results:
        lines3 += [
            name,
            f"  Normativ  : {r['normativ_stanc']:>8,} et/h",
            f"  Pakiranje : {r['normativ_pak']:>8,} et/h",
            f"  Broj kutija: {r['broj_kutija']:>7,}",
            f"  Broj paleta: {r['broj_paleta']:>7}",
            f"  Otpad     : {r['ukupno_ot']:>8.1f} kg",
            "",
        ]
    pt(px3, TOP, lines3)

    # ══ Panel 4: Tisak ════════════════════════════════════════════════════════
    px4 = panel_x[3]
    ph(px4, TOP, "TISAK")
    lines4 = []
    for name, r in tisak_results:
        lines4 += [
            name,
            f"  Normativ  : {r['normativ_tisk']:>8,} ar/h",
            f"  Priprema  : {r['priprema_h']:>8.2f} h",
            f"  Pranje    : {r['pranje_h']:>8.2f} h",
            f"  Netto     : {r['netto_araka']:>8,}",
            f"  Brutto    : {r['brutto_izdati']:>8,}",
            f"  Škart     : {r['skart']:>8,}",
            f"  Paleta ul.: {r['paleta_ulaz']:>8}",
            f"  Paleta izl: {r['paleta_izlag']:>8}",
            "",
        ]
    pt(px4, TOP, lines4)

    # ── Footer ────────────────────────────────────────────────────────────────
    fig.text(0.03, 0.05, "Normativ rada na rezačim strojevima 2025",
             ha='left', va='top', fontsize=7, color='#999999', fontfamily='monospace')
    fig.text(0.97, 0.05, f"Ispisano: {today}",
             ha='right', va='top', fontsize=7, color='#999999', fontfamily='monospace')

    buf = io.BytesIO()
    fig.savefig(buf, format='pdf', facecolor='white', bbox_inches=None)
    plt.close(fig)
    buf.seek(0)
    return buf
