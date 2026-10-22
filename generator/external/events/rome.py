"""Roma Capitale ordinances (Via dei Condotti works) as scanned-looking PDFs + OCR text extractions."""
import random
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_DIR = Path("/usr/share/fonts/liberation")
pdfmetrics.registerFont(TTFont("Serif", str(FONT_DIR / "LiberationSerif-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Serif-B", str(FONT_DIR / "LiberationSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Serif-I", str(FONT_DIR / "LiberationSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("Mono", str(FONT_DIR / "LiberationMono-Regular.ttf")))

HEADER = ["ROMA CAPITALE", "Dipartimento Mobilità Sostenibile e Trasporti",
          "Direzione Programmazione e Attuazione dei Piani di Mobilità",
          "U.O. Regolamentazione della Mobilità - Centro Storico"]

# (style, text) ; style: T=title bold centered, B=bold, P=paragraph, I=italic, S=signature, C=centered
ORD1 = [
    ("M", "Prot. QG/2026/0187345 del 08/09/2026"),
    ("M", "Rep. n. QG/1452/2026"),
    ("M", "Classifica: 6.4.2 - Fascicolo 2026/CS/0331"),
    ("T", "DETERMINAZIONE DIRIGENZIALE"),
    ("T", "(Ordinanza di traffico temporanea)"),
    ("B", "OGGETTO: Via dei Condotti, tratto compreso tra Piazza di Spagna e Via Bocca di Leone (fase 1) e tratto "
          "compreso tra Via Bocca di Leone e Via del Corso (fase 2). Lavori di rifacimento della pavimentazione in "
          "lastre di peperino e selci nell'ambito dell'intervento \"Manutenzione straordinaria pavimentazioni storiche - "
          "Tridente - Lotto 3\" e installazione di ponteggio a servizio del restauro della facciata dell'edificio ai "
          "civici 16-26. Provvedimenti temporanei di disciplina della circolazione e occupazione di suolo pubblico. "
          "Periodo: dal 14/09/2026 al 06/11/2026."),
    ("C", "IL DIRETTORE DELLA DIREZIONE PROGRAMMAZIONE E ATTUAZIONE DEI PIANI DI MOBILITÀ"),
    ("P", "VISTO il D.Lgs. 30 aprile 1992, n. 285 \"Nuovo Codice della Strada\" e successive modificazioni e "
          "integrazioni, ed in particolare gli artt. 5, 6, 7 e 21;"),
    ("P", "VISTO il D.P.R. 16 dicembre 1992, n. 495 \"Regolamento di esecuzione e di attuazione del Nuovo Codice "
          "della Strada\", ed in particolare gli artt. da 30 a 43;"),
    ("P", "VISTO il D.Lgs. 18 agosto 2000, n. 267 \"Testo Unico delle leggi sull'ordinamento degli Enti Locali\", ed in "
          "particolare l'art. 107;"),
    ("P", "VISTO lo Statuto di Roma Capitale approvato con Deliberazione dell'Assemblea Capitolina n. 8 del 7 marzo 2013 "
          "e s.m.i.;"),
    ("P", "VISTO il Regolamento per l'applicazione del canone patrimoniale di concessione, autorizzazione o esposizione "
          "pubblicitaria e del canone mercatale, approvato con Deliberazione dell'Assemblea Capitolina n. 21/2021 e s.m.i.;"),
    ("P", "VISTA la nota del Municipio Roma I Centro - Direzione Tecnica, prot. CA/2026/0098812 del 21/07/2026, con la "
          "quale si richiede l'adozione dei provvedimenti di traffico necessari all'esecuzione dei lavori in oggetto;"),
    ("P", "VISTA l'istanza presentata in data 28/07/2026 dalla ditta EDIL RESTAURI TIBERINA S.r.l., con sede in Roma, "
          "Via Prenestina n. 1184, P.IVA 0XXXXXXXXXX, esecutrice dei lavori, acquisita al prot. QG/2026/0161127, per "
          "l'occupazione di suolo pubblico con ponteggio a servizio del restauro conservativo della facciata "
          "dell'edificio sito in Via dei Condotti civv. 16-26, autorizzato dalla competente Soprintendenza Speciale "
          "con nota prot. n. 23876 del 30/06/2026;"),
    ("P", "VISTO il parere favorevole, con prescrizioni, espresso dalla Polizia Locale di Roma Capitale - I Gruppo "
          "Centro \"Trevi\", prot. GC/2026/0054419 del 03/09/2026;"),
    ("P", "CONSIDERATO che la Via dei Condotti ricade all'interno dell'Area Pedonale \"Tridente\" e della Zona a "
          "Traffico Limitato \"Centro Storico\", con accesso consentito ai soli veicoli autorizzati;"),
    ("P", "CONSIDERATO che la pavimentazione esistente presenta diffusi avvallamenti, lastre sconnesse e fessurate, "
          "tali da costituire pericolo per la pubblica incolumità, come rilevato nel verbale di sopralluogo del "
          "15/05/2026;"),
    ("P", "CONSIDERATO che, al fine di garantire la sicurezza della circolazione pedonale e dei lavoratori, si rende "
          "necessario adottare i provvedimenti temporanei di cui al dispositivo, per tutta la durata dei lavori;"),
    ("P", "RITENUTO di dover assicurare, compatibilmente con le esigenze di cantiere, l'accessibilità pedonale agli "
          "esercizi commerciali e alle abitazioni prospicienti il tratto interessato;"),
    ("P", "ATTESA la propria competenza ai sensi dell'art. 107 del D.Lgs. 267/2000;"),
    ("T", "ORDINA"),
    ("P", "dal giorno 14/09/2026 al giorno 06/11/2026, e comunque fino al termine dei lavori, l'istituzione dei seguenti "
          "provvedimenti di traffico temporanei:"),
    ("P", "1) VIA DEI CONDOTTI, tratto Piazza di Spagna - Via Bocca di Leone (FASE 1, indicativamente dal 14/09/2026 "
          "al 16/10/2026): delimitazione dell'area di cantiere sulla sede stradale mediante recinzione modulare di "
          "altezza non inferiore a m 2,00, con mantenimento di un percorso pedonale protetto di larghezza non inferiore "
          "a m 1,50 lungo i fronti degli edifici, su entrambi i lati della strada, ove la recinzione è posta in "
          "aderenza alle vetrine degli esercizi commerciali;"),
    ("P", "2) VIA DEI CONDOTTI, tratto Via Bocca di Leone - Via del Corso (FASE 2, indicativamente dal 12/10/2026 al "
          "06/11/2026): medesime prescrizioni di cui al punto 1). Le due fasi potranno sovrapporsi per un periodo "
          "massimo di cinque giorni lavorativi;"),
    ("P", "3) VIA DEI CONDOTTI civv. 16-26: occupazione di suolo pubblico con ponteggio per una superficie di mq 96 "
          "(m 32,00 x m 3,00), dotato di mantovana parasassi, tunnel pedonale illuminato di altezza libera non "
          "inferiore a m 2,50 e schermatura con teli di protezione, dal 14/09/2026 al 06/11/2026;"),
    ("P", "4) divieto di transito e di sosta con rimozione forzata, per tutti i veicoli, compresi quelli autorizzati, "
          "nei tratti interessati, eccetto i mezzi d'opera della ditta esecutrice, i mezzi di soccorso e di Polizia;"),
    ("P", "5) le operazioni di carico e scarico merci a servizio degli esercizi commerciali sono consentite "
          "esclusivamente dalle ore 6:00 alle ore 10:30, con veicoli di massa complessiva a pieno carico non superiore "
          "a 3,5 t, con accesso e uscita da Via Bocca di Leone; negli altri orari la consegna dovrà avvenire a mano "
          "lungo il percorso pedonale protetto;"),
    ("P", "6) le lavorazioni sono consentite dal lunedì al sabato, dalle ore 7:30 alle ore 17:00; le lavorazioni "
          "rumorose sono sospese tra le ore 13:00 e le ore 14:30. Sono escluse lavorazioni nei giorni festivi;"),
    ("P", "7) sospensione, nel tratto interessato e per l'intera durata dei lavori, delle concessioni di occupazione "
          "di suolo pubblico per tavolini, sedie, espositori e pedane (dehors);"),
    ("P", "8) la ditta esecutrice dovrà provvedere all'installazione della prescritta segnaletica stradale "
          "temporanea, conforme al D.M. 10 luglio 2002, almeno 48 ore prima dell'inizio dei lavori, nonché "
          "all'illuminazione notturna delle recinzioni e all'esposizione del cartello di cantiere recante gli estremi "
          "del presente provvedimento e la durata dei lavori;"),
    ("P", "9) la ditta esecutrice è responsabile della corretta installazione e manutenzione della segnaletica e "
          "delle recinzioni, nonché di ogni danno a persone o cose derivante dall'esecuzione dei lavori, sollevando "
          "Roma Capitale da qualsiasi responsabilità."),
    ("T", "DISPONE"),
    ("P", "che la Polizia Locale di Roma Capitale e gli altri organi di cui all'art. 12 del D.Lgs. 285/1992 siano "
          "incaricati di far rispettare il presente provvedimento; che il presente provvedimento sia pubblicato "
          "all'Albo Pretorio on line di Roma Capitale e reso noto mediante l'apposizione della prescritta segnaletica."),
    ("P", "Responsabile Unico del Procedimento: Ing. Paolo Ceccarelli (Municipio Roma I Centro - Direzione Tecnica). "
          "Direttore dei Lavori: Arch. Silvia Brancaleoni. Ditta esecutrice: EDIL RESTAURI TIBERINA S.r.l., referente "
          "di cantiere geom. Daniele Fiorucci, reperibilità h24 tel. 06 XXX XX 41."),
    ("I", "Avverso il presente provvedimento è ammesso ricorso al Tribunale Amministrativo Regionale del Lazio entro "
          "60 giorni dalla data di pubblicazione, ovvero ricorso straordinario al Presidente della Repubblica entro 120 "
          "giorni. Ai sensi dell'art. 37, comma 3, del D.Lgs. 285/1992, avverso il presente provvedimento, relativamente "
          "alla segnaletica, è ammesso ricorso al Ministero delle Infrastrutture e dei Trasporti entro 60 giorni, con "
          "le formalità stabilite dall'art. 74 del D.P.R. 495/1992."),
    ("S", "IL DIRETTORE"),
    ("S", "Ing. Roberto F. Malatesta"),
    ("I", "Documento firmato digitalmente ai sensi del D.Lgs. 82/2005 (Codice dell'Amministrazione Digitale) e norme "
          "collegate, il quale sostituisce il documento cartaceo e la firma autografa."),
]

ORD2 = [
    ("M", "Prot. QG/2026/0209981 del 08/10/2026"),
    ("M", "Rif. prot. QG/2026/0187345 del 08/09/2026"),
    ("T", "DETERMINAZIONE DIRIGENZIALE INTEGRATIVA"),
    ("B", "OGGETTO: Via dei Condotti - lavori di rifacimento della pavimentazione (Tridente - Lotto 3) e ponteggio "
          "civv. 16-26. Integrazione del provvedimento prot. QG/2026/0187345 dell'08/09/2026: autorizzazione di "
          "lavorazioni in orario notturno e rimodulazione dell'orario diurno."),
    ("C", "IL DIRETTORE DELLA DIREZIONE PROGRAMMAZIONE E ATTUAZIONE DEI PIANI DI MOBILITÀ"),
    ("P", "VISTO il proprio provvedimento prot. QG/2026/0187345 dell'08/09/2026;"),
    ("P", "VISTA la nota del Municipio Roma I Centro - Direzione Tecnica prot. CA/2026/0127730 del 01/10/2026, con la "
          "quale, a seguito degli incontri con le associazioni di categoria degli esercenti, si chiede di ridurre "
          "l'interferenza delle lavorazioni con le attività commerciali nelle ore di apertura;"),
    ("P", "VISTA l'autorizzazione in deroga ai limiti acustici rilasciata dal Dipartimento Tutela Ambientale, prot. "
          "QL/2026/0071204 del 06/10/2026, ai sensi del Regolamento per la disciplina delle attività rumorose;"),
    ("P", "RITENUTO di poter accogliere la richiesta;"),
    ("T", "ORDINA"),
    ("P", "a parziale modifica del punto 6) del provvedimento richiamato:"),
    ("P", "a) nelle notti 12-13, 13-14, 19-20, 20-21, 26-27 ottobre 2026 e 2-3 novembre 2026 sono consentite, dalle ore "
          "21:00 alle ore 05:00 del giorno successivo, le lavorazioni di posa delle lastre e di sigillatura dei giunti "
          "nel tratto Via Bocca di Leone - Via del Corso e nel tratto terminale lato Piazza di Spagna (civv. 2-10);"),
    ("P", "b) a decorrere dal 12/10/2026 le lavorazioni diurne sono consentite dal lunedì al venerdì dalle ore 8:00 "
          "alle ore 16:00; il sabato sono consentite esclusivamente lavorazioni non rumorose dalle ore 8:00 alle ore "
          "12:00;"),
    ("P", "c) nelle notti di cui al punto a) il percorso pedonale protetto dovrà essere mantenuto illuminato e "
          "presidiato; è vietato l'uso di martelli demolitori dopo le ore 23:00."),
    ("P", "Restano ferme tutte le altre prescrizioni del provvedimento prot. QG/2026/0187345, ivi compresa la fascia "
          "oraria per il carico e scarico merci (6:00-10:30). Resta invariato il termine dei lavori, fissato al "
          "06/11/2026."),
    ("I", "Avverso il presente provvedimento è ammesso ricorso al TAR Lazio entro 60 giorni dalla pubblicazione."),
    ("S", "IL DIRETTORE"),
    ("S", "Ing. Roberto F. Malatesta"),
    ("I", "Documento firmato digitalmente ai sensi del D.Lgs. 82/2005 e norme collegate."),
]


def _wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_pdf(path, blocks, seed, stamp_lines, n_hint=None):
    rnd = random.Random(seed)
    W, H = A4
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("")
    c.setAuthor("")
    c.setCreator("Canon iR-ADV C5840 ScanToPDF")
    c.setProducer("Canon iR-ADV C5840")
    margin_l, margin_r, top, bottom = 62, 58, 70, 70
    width = W - margin_l - margin_r
    # pre-layout into pages
    layout, y, page = [], H - top - 165, 0
    pages = [[]]
    for style, text in blocks:
        font = {"T": "Serif-B", "B": "Serif-B", "I": "Serif-I", "M": "Mono"}.get(style, "Serif")
        size = {"T": 11, "M": 8.2, "I": 8.8}.get(style, 9.4)
        lines = _wrap(text, font, size, width) if style not in ("S",) else [text]
        need = len(lines) * (size + 2.6) + 6
        if y - need < bottom:
            pages.append([])
            y = H - top - 40
        for ln in lines:
            pages[-1].append((style, font, size, ln, y))
            y -= size + 2.6
        y -= 6 if style != "M" else 1
    n = len(pages)
    for pi, items in enumerate(pages):
        # paper tone + scan skew
        c.setFillColorRGB(0.965, 0.962, 0.95)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.saveState()
        c.translate(W / 2, H / 2)
        c.rotate(rnd.uniform(-0.45, 0.45))
        c.translate(-W / 2, -H / 2)
        # specks
        for _ in range(rnd.randint(60, 140)):
            g = rnd.uniform(0.55, 0.85)
            c.setFillColorRGB(g, g, g)
            c.circle(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.2, 0.7), fill=1, stroke=0)
        c.setFillColorRGB(0.12, 0.12, 0.12)
        if pi == 0:
            c.setFont("Serif-B", 9)
            c.drawCentredString(W / 2, H - 52, "S.P.Q.R.")
            c.setFont("Serif-B", 12.5)
            c.drawCentredString(W / 2, H - 68, HEADER[0])
            c.setFont("Serif", 9.4)
            for i, h in enumerate(HEADER[1:]):
                c.drawCentredString(W / 2, H - 82 - i * 11.5, h)
            c.setLineWidth(0.6)
            c.line(margin_l, H - 122, W - margin_r, H - 122)
            # protocol stamp box (top right)
            c.saveState()
            c.setStrokeColorRGB(0.25, 0.3, 0.55)
            c.setFillColorRGB(0.25, 0.3, 0.55)
            c.translate(W - 190, H - 182)
            c.rotate(rnd.uniform(-3, 3))
            c.rect(0, 0, 140, 46, fill=0, stroke=1)
            c.setFont("Mono", 6.6)
            for k, s in enumerate(stamp_lines):
                c.drawString(5, 36 - k * 9, s)
            c.restoreState()
        else:
            c.setFont("Serif", 8)
            c.drawString(margin_l, H - 40, "Roma Capitale - Dipartimento Mobilità Sostenibile e Trasporti")
            c.drawRightString(W - margin_r, H - 40, stamp_lines[1].replace("PROT. ", ""))
        y_off = 0
        for style, font, size, ln, y in items:
            c.setFont(font, size)
            yy = y + y_off
            if style in ("T", "C"):
                c.drawCentredString(W / 2, yy, ln)
            elif style == "S":
                c.drawString(W - margin_r - 190, yy, ln)
            else:
                c.drawString(margin_l, yy, ln)
        # round rubber stamp on last page
        if pi == n - 1:
            c.saveState()
            c.setStrokeColorRGB(0.45, 0.45, 0.6)
            c.setFillColorRGB(0.45, 0.45, 0.6)
            c.translate(margin_l + 95, bottom + 70)
            c.rotate(rnd.uniform(-14, 14))
            c.circle(0, 0, 38, stroke=1, fill=0)
            c.circle(0, 0, 30, stroke=1, fill=0)
            c.setFont("Serif-B", 6.5)
            c.drawCentredString(0, 8, "ROMA CAPITALE")
            c.drawCentredString(0, -2, "DIP. MOBILITÀ")
            c.drawCentredString(0, -12, "E TRASPORTI")
            c.restoreState()
        c.restoreState()
        c.setFont("Serif", 7.5)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(W / 2, 36, f"Pag. {pi + 1} di {n}")
        c.drawString(margin_l, 24, "Via di Settebagni 384 - 00139 Roma - PEC: protocollo.mobilitatrasporti@pec.comune.roma.example")
        c.showPage()
    c.save()
    return pages


OCR_SUBS = [  # (pattern, replacement, max count)
    (r"Condotti", "Condottì", 1),
    (r"ORDINA\b", "0RDINA", 1),
    (r"dal giorno 14/09/2026", "dal giorno l4/09/2026", 1),
    (r"Programmazione", "Prograrnmazione", 1),
    (r"marnmazione", "marnmazione", 0),
    (r"modificazioni", "modifìcazioni", 1),
    (r"illuminazione", "illurninazione", 1),
    (r"Spagna", "Spagna", 0),
    (r"pedonale", "pedona1e", 1),
    (r"carico e scarico", "carico e scar ico", 1),
    (r"Tridente", "Trìdente", 1),
]


def ocr_text(pages, header_lines, glitch_date=True, heavy=True, seed=0):
    rnd = random.Random(seed)
    out = []
    n = len(pages)
    for pi, items in enumerate(pages):
        if pi == 0:
            out += ["S.P.Q.R.", header_lines[0]] + header_lines[1:] + ["_" * 58, ""]
        else:
            out += ["Roma Capitale - Dipartirnento Mobilità Sostenibile e Trasporti" if heavy else
                    "Roma Capitale - Dipartimento Mobilità Sostenibile e Trasporti", ""]
        prev_style = None
        for style, font, size, ln, y in items:
            if prev_style and style != prev_style:
                out.append("")
            out.append(ln)
            prev_style = style
        out += ["", f"Pag. {pi + 1} di {n}" if pi % 2 == 0 or not heavy else f"Pag. {pi + 1} dl {n}", "\f"]
    text = "\n".join(out)
    if heavy:
        for pat, rep, k in OCR_SUBS:
            if k:
                text = re.sub(pat, rep, text, count=k)
        # broken hyphenation on a couple of long words
        text = text.replace("pavimentazione in\nlastre", "pavimen-\ntazione in\nlastre", 1)
        text = text.replace("Polizia Locale di Roma Capitale - I Gruppo", "Polizia Locale di Roma Capitale - l Gruppo", 1)
        if glitch_date:
            # third occurrence of the end date misread
            parts = text.split("06/11/2026")
            if len(parts) > 4:
                seps = ["06/11/2026"] * (len(parts) - 1)
                seps[2] = "06/1l/2026"   # fase 2 end date
                seps[3] = "08/11/2026"   # scaffolding end date misread
                text = parts[0] + "".join(sep + part for sep, part in zip(seps, parts[1:]))
        # stray specks read as characters
        lines = text.split("\n")
        for _ in range(7):
            i = rnd.randrange(len(lines))
            if lines[i] and lines[i] != "\f":
                lines[i] = lines[i] + rnd.choice([" ~", " .", " '", " |", " ,"])
        text = "\n".join(lines)
        text = text.replace("’", "'")
    else:
        text = text.replace("Direttore", "Direttore", 1).replace("ORDINA", "ORD INA", 1)
    return text


def build(out_dir: Path):
    d = out_dir / "municipal"
    d.mkdir(parents=True, exist_ok=True)
    p1 = d / "RomaCapitale_DD_QG-2026-0187345_ViaCondotti_pavimentazione_ponteggio.pdf"
    pages1 = make_pdf(p1, ORD1, 11, ["ROMA CAPITALE - QG", "PROT. QG/2026/0187345", "DEL 08/09/2026  ORE 12:41",
                                     "CLASS. 6.4.2"])
    (d / "RomaCapitale_DD_QG-2026-0187345_ViaCondotti_pavimentazione_ponteggio_OCR.txt").write_text(
        ocr_text(pages1, HEADER, glitch_date=True, heavy=True, seed=3), encoding="utf-8")
    p2 = d / "RomaCapitale_DD_QG-2026-0209981_integrazione_orari_notturni.pdf"
    pages2 = make_pdf(p2, ORD2, 23, ["ROMA CAPITALE - QG", "PROT. QG/2026/0209981", "DEL 08/10/2026  ORE 16:05",
                                     "CLASS. 6.4.2"])
    (d / "RomaCapitale_DD_QG-2026-0209981_integrazione_orari_notturni_OCR.txt").write_text(
        ocr_text(pages2, HEADER, glitch_date=False, heavy=False, seed=5), encoding="utf-8")
    (d / "municipio1_avviso_web_2026-09-11.html").write_text(WEB_NOTICE, encoding="utf-8")
    return [p1, p2]


WEB_NOTICE = """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Via Condotti, dal 14 settembre al via i lavori di rifacimento della pavimentazione | Municipio Roma I Centro</title></head>
<body>
<div class="cookie">Questo sito utilizza cookie tecnici e, previo consenso, cookie analitici. <a href="#">Informativa</a> [OK]</div>
<div class="breadcrumb">Home &gt; Municipio I &gt; Notizie &gt; Lavori pubblici</div>
<h1>Via Condotti, dal 14 settembre al via i lavori di rifacimento della pavimentazione</h1>
<p class="data">Pubblicato: 11 settembre 2026 - Ultimo aggiornamento: 11 settembre 2026</p>
<p>Partiranno lunedì 14 settembre i lavori di manutenzione straordinaria della pavimentazione storica di via dei Condotti, nell'ambito del programma di riqualificazione del Tridente (lotto 3). L'intervento prevede la rimozione e la ricollocazione delle lastre di peperino e dei sampietrini, con sostituzione degli elementi danneggiati.</p>
<p>I lavori si svolgeranno in due fasi: la prima interesserà il tratto tra piazza di Spagna e via Bocca di Leone, la seconda il tratto fino a via del Corso. La conclusione è prevista per il 6 novembre.</p>
<p>Durante il cantiere sarà sempre garantito il passaggio pedonale lungo i negozi e l'accesso alle abitazioni. Le consegne merci saranno consentite dalle 6 alle 10:30 con accesso da via Bocca di Leone.</p>
<p>"Un intervento atteso da anni, che restituirà sicurezza e decoro a una delle strade più conosciute al mondo", ha dichiarato l'assessora ai Lavori pubblici del Municipio.</p>
<p>Contemporaneamente, a cura di un soggetto privato, sarà installato un ponteggio per il restauro della facciata di un edificio storico.</p>
<p>Per informazioni: Ufficio Relazioni con il Pubblico del Municipio I, tel. 06 XXXX 6000.</p>
<div class="share">Condividi: Facebook | X | WhatsApp</div>
<footer>Roma Capitale - Municipio Roma I Centro - Via della Greca 5</footer>
</body></html>
"""
