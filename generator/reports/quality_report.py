"""Customer Care & Quality monthly report (DOCX + PDF export) - September 2026 with early warning to 11/10.

Author: Quality Assurance & Customer Care (Milano), mixed Italian/English.
Definitions planted:
- TIB 'tasso di difettosità' = DEF returns in window / TIB units SOLD IN THE SAME WINDOW (28/09-11/10) -> ~42%
  (correct reading: DEF returns / units sold since 15/08 from the affected batch ~13% so far, heading to ~15-16%)
- ARNEB 'exchange rate' on receipts containing ARNEB in September only
- contact-centre volumes are synthetic (no other source)
"""
import datetime as dt
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from common import D, Facts, outdir, pos, shipments, skus
from pdfkit import savefig

OUTD = outdir("customer_care_quality")
TMP = Path(__file__).parent / "_tmp"
facts = Facts("quality")


def main():
    p = pos()
    tib = p[p.style_name == "TIB"]
    s, r = tib[tib.line_type == "SALE"], tib[tib.line_type == "RETURN"]
    a, b = D(2026, 9, 28), D(2026, 10, 11)
    sold_win = int(s[(s.date >= a) & (s.date <= b)].qty.sum())
    def_win = int(((r.return_reason == "DEF") & (r.date >= a) & (r.date <= b)).sum())
    sold_since = int(s[(s.date >= D(2026, 8, 15)) & (s.date <= b)].qty.sum())
    rate_shown = def_win / sold_win * 100
    rate_since = def_win / sold_since * 100
    sh = shipments().merge(skus()[["sku", "style_name"]])
    deliv = int(sh[(sh.style_name == "TIB") & (sh.arrival >= "2026-08-15") & (sh.arrival <= b.isoformat())].qty.sum())
    defr = r[(r.return_reason == "DEF") & (r.date <= b)]
    by_reg = defr.groupby("region").size()
    defr = defr.assign(wk=defr.date.map(lambda d: d - dt.timedelta(days=d.weekday())))
    by_wk = defr.groupby("wk").size()

    ar = p[p.style_name == "ARNEB"]
    sep = (ar.date >= D(2026, 9, 1)) & (ar.date <= D(2026, 9, 30))
    ar_sep_ret = ar[sep & ar.return_reason.isin(["SIZE", "EXCHANGE_SIZE"])]
    ar_sep_rcpt = ar[sep & (ar.line_type == "SALE")].receipt_id.nunique()
    arneb_rate_shown = len(ar_sep_ret) / ar_sep_rcpt * 100
    ar_all_ret = ar[(ar.date <= b) & ar.return_reason.isin(["SIZE", "EXCHANGE_SIZE"])]
    arneb_rate_true = len(ar_all_ret) / ar[(ar.date <= b) & (ar.line_type == "SALE")].qty.sum() * 100
    ar_exch = (ar_all_ret.return_reason == "EXCHANGE_SIZE").mean() * 100

    # overall return rate by region Sep (units)
    rr = p[(p.date >= D(2026, 9, 1)) & (p.date <= D(2026, 9, 30))]
    reg = rr.groupby(["region", "line_type"]).qty.sum().abs().unstack()
    reg["rate"] = reg.RETURN / reg.SALE * 100
    reasons = rr[rr.line_type == "RETURN"].return_reason.value_counts()

    fig, ax = plt.subplots(figsize=(5.5, 2.4))
    ax.bar([d.strftime("%d/%m") for d in by_wk.index], by_wk.values, color="#B03A2E")
    for i, v in enumerate(by_wk.values):
        ax.text(i, v + 2, str(v), ha="center", fontsize=7)
    ax.set_title("TIB - resi motivo DEF per settimana (lun)", fontsize=8, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=7)
    f1 = savefig(fig, TMP / "q_tib.png")

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10)
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.2)
        hdr = sec.header.paragraphs[0]
        hdr.text = "Moncler S.p.A. - Quality Assurance & Customer Care          Rev. 1.2 - 13/10/2026"
        hdr.runs[0].font.size = Pt(8)
        hdr.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        ft = sec.footer.paragraphs[0]
        ft.text = "Confidential - Internal use only. Distribuzione: Quality, Retail Ops, Merchandising, Customer Care, Regional MDs."
        ft.runs[0].font.size = Pt(7)

    t = doc.add_paragraph()
    run = t.add_run("CUSTOMER CARE & QUALITY\nMonthly Report - Settembre 2026")
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x1F, 0x2A, 0x44)
    doc.add_paragraph("Include early warning aggiornato all'11/10/2026. Redatto da: L. Moretti (Product Integrity), C. Rinaldi (Customer Care Manager EMEA).")

    doc.add_heading("1. Executive summary", level=1)
    for x in [
        f"TIB (gilet uomo, piumino laqué): difetto sul cursore della zip (slider) sulle consegne da metà agosto, lotto di produzione 2026-07. "
        f"Tasso di difettosità {rate_shown:.0f}% nel periodo 28/09-11/10 ({def_win} resi DEF su {sold_win} capi venduti nello stesso periodo). "
        "Proposta: STOP-SALE immediato del lotto 2026-07 e richiamo in negozio.",
        f"ARNEB (parka uomo FW26): vestibilità abbondante, exchange rate {arneb_rate_shown:.0f}% a settembre. Indicazione ai negozi: consigliare una taglia in meno.",
        f"Resi totali settembre: tasso medio {reg.RETURN.sum() / reg.SALE.sum() * 100:.1f}% (unità), in linea con la stagione salvo TIB.",
        "Contatti customer care in aumento (+38% vs agosto), trainati da richieste di disponibilità (ILVARO rosa, MAIRE nero) e reclami TIB.",
    ]:
        doc.add_paragraph(x, style="List Bullet")

    doc.add_heading("2. TIB - zipper slider defect", level=1)
    doc.add_paragraph(
        "Dal 28/09 i negozi registrano resi con codice motivo DEF (difetto) sul TIB: il cursore si apre/si sfila dopo pochi utilizzi. "
        "I capi coinvolti appartengono alle consegne DC -> negozi dal 15/08 (lotto 2026-07, fornitore accessori metallici 'Officine Cursori S.r.l.'). "
        "Analisi di laboratorio su 24 capi resi: 21 con lega del cursore fuori specifica (durezza).")
    doc.add_picture(f1, width=Cm(14))
    tb = doc.add_table(rows=1, cols=2)
    tb.style = "Light Grid Accent 1"
    tb.rows[0].cells[0].text = "Region"
    tb.rows[0].cells[1].text = "Resi DEF (al 11/10)"
    for k_, v in by_reg.items():
        c = tb.add_row().cells
        c[0].text, c[1].text = k_, str(v)
    doc.add_paragraph()
    tb = doc.add_table(rows=1, cols=2)
    tb.style = "Light Grid Accent 1"
    tb.rows[0].cells[0].text = "KPI"
    tb.rows[0].cells[1].text = "Valore"
    for k_, v in [("Capi TIB venduti 28/09-11/10", sold_win), ("Resi DEF 28/09-11/10", def_win),
                  ("Tasso di difettosità (resi/venduto periodo)", f"{rate_shown:.1f}%"),
                  ("Capi TIB consegnati ai negozi dal 15/08", deliv),
                  ("Resi DEF / consegnato", f"{def_win / deliv * 100:.1f}%")]:
        c = tb.add_row().cells
        c[0].text, c[1].text = k_, str(v)
    doc.add_paragraph()
    doc.add_paragraph("Azioni in corso: (1) controllo cursore alla cassa prima della vendita; (2) cambio merce o rimborso senza scontrino "
                      "per clienti con capo difettoso; (3) richiesta al fornitore di nuovo lotto cursori, ETA sostituzione 3 settimane; "
                      "(4) valutazione stop-sale in comitato qualità del 15/10.")
    doc.add_paragraph("Customer care: 212 contatti su TIB in 2 settimane (email 118, telefono 61, chat 19, social 14). "
                      "Post Instagram/小红书 con foto della zip rotta, sentiment negativo limitato.")

    doc.add_heading("3. ARNEB - size & fit", level=1)
    doc.add_paragraph(
        f"Settembre: {len(ar_sep_ret)} resi/cambi per taglia su {ar_sep_rcpt} scontrini con ARNEB = {arneb_rate_shown:.1f}% (exchange rate). "
        f"Il {ar_exch:.0f}% dei casi si chiude con cambio taglia (non perdita di vendita). Feedback: maniche lunghe, spalle larghe; "
        "i negozi consigliano una taglia in meno. Richiesta al prodotto di rivedere la tabella taglie online.")

    doc.add_heading("4. Resi per regione e motivo (settembre)", level=1)
    tb = doc.add_table(rows=1, cols=4)
    tb.style = "Light Grid Accent 1"
    for i, h in enumerate(["Region", "Unità vendute", "Unità rese", "Tasso"]):
        tb.rows[0].cells[i].text = h
    for k_, x in reg.iterrows():
        c = tb.add_row().cells
        c[0].text, c[1].text, c[2].text, c[3].text = k_, f"{int(x.SALE):,}", f"{int(x.RETURN):,}", f"{x.rate:.1f}%"
    doc.add_paragraph()
    doc.add_paragraph("Motivi di reso settembre: " + ", ".join(f"{k_} {v}" for k_, v in reasons.items()) + ".")

    doc.add_heading("5. Customer care - contatti", level=1)
    tb = doc.add_table(rows=1, cols=4)
    tb.style = "Light Grid Accent 1"
    for i, h in enumerate(["Topic", "Agosto", "Settembre", "1-11 ottobre"]):
        tb.rows[0].cells[i].text = h
    for row in [("Disponibilità prodotto / taglie", 1420, 1980, 1610), ("Stato ordine online", 2210, 2390, 980),
                ("Reclami qualità (tot.)", 160, 310, 402), ("  di cui TIB zip", 0, 41, 171), ("Resi e rimborsi", 980, 1160, 640),
                ("Info prodotto / vestibilità", 760, 1050, 520), ("Altro", 640, 720, 310)]:
        c = tb.add_row().cells
        for i, v in enumerate(row):
            c[i].text = f"{v:,}" if isinstance(v, int) else v
    doc.add_paragraph()
    doc.add_paragraph("Picco di richieste di disponibilità dal 02/10: ILVARO powder pink (Asia, ma anche clienti europei che hanno visto le foto "
                      "della sfilata) e MAIRE nero (clienti coreani in Francia e Italia).")

    doc.add_heading("Appendice - definizioni", level=1)
    for x in ["Tasso di difettosità = resi con motivo DEF nel periodo / unità vendute nel medesimo periodo.",
              "Exchange rate ARNEB = resi motivo SIZE o EXCHANGE_SIZE / numero di scontrini contenenti ARNEB nel mese.",
              "Tasso di reso regione = unità rese nel mese / unità vendute nel mese (fonte POS line-level).",
              "Contatti = ticket unici Salesforce Service Cloud, tutti i canali."]:
        doc.add_paragraph(x, style="List Bullet")

    path = OUTD / "CCQ_Monthly_Report_2026-09_rev1.2.docx"
    doc.save(path)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUTD), str(path)], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    facts.update(dict(tib_rate_shown=round(rate_shown, 1), tib_def_win=def_win, tib_sold_win=sold_win,
                      tib_sold_since_aug15=sold_since, tib_rate_since=round(rate_since, 1), tib_delivered=deliv,
                      tib_def_by_region=by_reg.to_dict(), arneb_rate_shown=round(arneb_rate_shown, 1),
                      arneb_rate_units=round(arneb_rate_true, 1), arneb_exchange_share=round(ar_exch, 1),
                      return_rate_by_region=reg.rate.round(1).to_dict()))
    facts.save()


if __name__ == "__main__":
    main()
