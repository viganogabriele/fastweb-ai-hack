"""Venice tide bulletins (Centro Maree style) + hourly observed levels at Punta della Salute."""
import math
from pathlib import Path

HEAD = "COMUNE DI VENEZIA - Centro Previsioni e Segnalazioni Maree\nIstituzione Centro Previsioni e Segnalazioni Maree - San Marco 4090 - Venezia"
FOOT = ("Valori in cm riferiti allo Zero Mareografico di Punta della Salute (ZMPS, 1897). Le previsioni sono "
        "soggette a incertezza di +/- 5 cm a 24 ore e +/- 10 cm a 48-72 ore.\n"
        "Classi di marea: 'sostenuta' 80-109 cm; 'molto sostenuta' 110-139 cm; 'eccezionale' >= 140 cm.\n"
        "Segnali acustici: 110 cm 1 nota; 120 cm 2 note crescenti; 130 cm 3 note; 140 cm 4 note.\n"
        "Info: tel. 041 24X XXXX - Servizio SMS e app 'hi!tide Venice' - www.comune.venezia.example/maree")


def level(t):
    """t = hours since 2026-10-19 00:00 local time."""
    astro = 35 + 30 * math.cos(2 * math.pi * (t - 8.5) / 12.42) + 4 * math.cos(2 * math.pi * (t - 9) / 24.0)
    surge = 16 + 34.5 * math.exp(-(((t - 34.6) / 5.0) ** 2)) + (3 if 40 < t < 60 else 0)
    return astro + surge


def hourly_csv():
    rows = ["data;ora;stazione;livello_cm;note"]
    for h in range(72):
        day = 19 + h // 24
        hh = h % 24
        v = level(h)
        if day == 20 and hh == 7:
            rows.append(f"{day:02d}/10/2026;{hh:02d}:00;Punta della Salute;;dato mancante (manutenzione teletrasmissione)")
            continue
        note = ""
        if day == 20 and hh == 10:
            note = "massimo registrato 118 cm alle 09:40 (dato 10 min)"
        rows.append(f"{day:02d}/10/2026;{hh:02d}:00;Punta della Salute;{round(v)};{note}")
    return "\n".join(rows) + "\n"


B_1006 = f"""{HEAD}

PREVISIONE DI MAREA
Emessa il 06/10/2026 alle ore 17:00

Situazione meteorologica: una saccatura in approfondimento sul Mediterraneo occidentale determinerà nella notte un
rinforzo dei venti di scirocco sull'Adriatico centro-settentrionale, con raffiche fino a 50-55 km/h in mare aperto.
Pressione in calo a 1003 hPa.

Previsione a Punta della Salute:
  07/10/2026  ore 09:05  MASSIMO  110 cm
  07/10/2026  ore 15:20  minimo    30 cm
  07/10/2026  ore 21:10  massimo   75 cm
  08/10/2026  ore 09:50  massimo   85 cm

Livello di allerta: ARANCIONE - marea molto sostenuta prevista per la mattinata di mercoledì 07/10.
Percentuale di città pedonale interessata da allagamento: circa 12%.
Le sirene saranno attivate alle ore 06:00 di mercoledì se la previsione delle ore 04:00 sarà confermata.
L'eventuale sollevamento del sistema MOSE è di competenza del Commissario straordinario; consultare i canali ufficiali.

{FOOT}
"""

OBS_1007 = f"""{HEAD}

DATI OSSERVATI - mercoledì 07/10/2026

Aggiornamento previsione delle ore 04:00: massimo previsto ridotto a 100 cm (attenuazione del vento di scirocco
nelle ore notturne). Sirene NON attivate. Sistema MOSE non attivato.

Massimi osservati:
  Punta della Salute    92 cm   ore 08:50
  Diga Sud Lido         89 cm   ore 08:20
  Burano                95 cm   ore 09:15
  Chioggia Vigo         86 cm   ore 08:30

Scarto tra previsione delle 17:00 del giorno precedente (110 cm) e osservato (92 cm): -18 cm.
Piazza San Marco: allagamento parziale nell'area del nartece della Basilica tra le 08:20 e le 09:30.

{FOOT}
"""


def html_wrap(title, body):
    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>{title}</title>
<style>table{{border-collapse:collapse}}td,th{{border:1px solid #888;padding:2px 6px}}.allerta{{font-weight:bold}}</style></head>
<body>
<div class="testata">Comune di Venezia &gt; Centro Previsioni e Segnalazioni Maree &gt; Previsioni</div>
{body}
<p class="piede"><small>{FOOT.replace(chr(10), '<br>')}</small></p>
<div class="cookie">Questo sito utilizza solo cookie tecnici. [Ho capito]</div>
</body></html>
"""


def table(rows):
    tr = "\n".join(f"<tr><td>{d}</td><td>{o}</td><td>{t}</td><td>{v}</td></tr>" for d, o, t, v in rows)
    return f"<table><tr><th>data</th><th>ora</th><th>tipo</th><th>cm ZMPS</th></tr>\n{tr}\n</table>"


B_1018 = html_wrap("Previsione di marea 18/10/2026 ore 12:00", f"""
<h2>PREVISIONE DI MAREA</h2>
<p>Emessa il <b>18/10/2026</b> alle ore <b>12:00</b></p>
<p>Situazione meteorologica: dopo l'irruzione di aria fredda dei giorni scorsi sull'Europa centrale, un minimo depressionario
in formazione sul golfo di Genova tenderà a muoversi verso est tra lunedì e martedì. Previsto un rinforzo dello scirocco
sull'Adriatico da lunedì sera.</p>
{table([("19/10/2026", "08:35", "max", "85"), ("19/10/2026", "14:55", "min", "25"), ("19/10/2026", "20:50", "max", "70"),
        ("20/10/2026", "09:15", "max", "100"), ("20/10/2026", "15:40", "min", "35"), ("21/10/2026", "10:05", "max", "85")])}
<p class="allerta">Livello di allerta per il 20/10: GIALLA - marea sostenuta. Tendenza: in aumento, previsione da confermare.</p>
""")

B_1019_AM = f"""{HEAD}

PREVISIONE DI MAREA
Emessa il 19/10/2026 alle ore 09:00

Massimo di stamattina in linea con la previsione (osservato 84 cm alle 08:30).
La depressione sul golfo di Genova si sta approfondendo. Per la mattinata di domani, martedì 20/10, si prevede un
massimo di marea sostenuta in prossimità della soglia dei 110 cm.

Previsione a Punta della Salute:
  19/10/2026  ore 20:55  massimo   70 cm
  20/10/2026  ore 03:10  minimo    40 cm
  20/10/2026  ore 09:30  MASSIMO  105 cm
  20/10/2026  ore 15:45  minimo    40 cm
  20/10/2026  ore 21:35  massimo   80 cm

Livello di allerta per martedì 20/10: GIALLA (marea sostenuta), possibile passaggio ad ARANCIONE.
Prossimo aggiornamento: ore 17:00.

{FOOT}
"""

B_1019_PM = html_wrap("Previsione di marea 19/10/2026 ore 17:00", f"""
<h2>PREVISIONE DI MAREA</h2>
<p>Emessa il <b>19/10/2026</b> alle ore <b>17:00</b></p>
<p>Situazione meteorologica: scirocco in rinforzo nella notte sull'Adriatico centro-settentrionale (raffiche 45-55 km/h al largo),
pressione in diminuzione a 1001 hPa su Venezia nelle prime ore di domani. La previsione per il colmo di martedì mattina è
compresa tra 105 e 110 cm, con incertezza legata all'intensità e alla rotazione del vento.</p>
{table([("20/10/2026", "03:15", "min", "40"), ("20/10/2026", "09:35", "max", "105-110"), ("20/10/2026", "15:50", "min", "40"),
        ("20/10/2026", "21:40", "max", "80"), ("21/10/2026", "10:10", "max", "85")])}
<p class="allerta">Livello di allerta per martedì 20/10: GIALLA/ARANCIONE - marea sostenuta, al limite della soglia di marea molto sostenuta.</p>
<p>Sistema MOSE: l'attivazione delle barriere viene disposta dal Commissario straordinario / Provveditorato per le Opere
Pubbliche sulla base delle previsioni pari o superiori a 110 cm. Allo stato attuale, con previsione al limite della soglia,
l'attivazione per la marea di domani mattina NON è programmata; la situazione è in monitoraggio e sarà rivalutata con
l'aggiornamento notturno.</p>
<p>Sirene: in caso di conferma di valori &gt;= 110 cm, attivazione alle ore 06:30-07:00.</p>
""")

B_1020 = html_wrap("AGGIORNAMENTO previsione di marea 20/10/2026 ore 06:30", f"""
<h2 style="color:#c60">AGGIORNAMENTO - PREVISIONE DI MAREA</h2>
<p>Emesso il <b>20/10/2026</b> alle ore <b>06:30</b> (sostituisce la previsione delle 17:00 del 19/10)</p>
<p>Lo scirocco si è rinforzato oltre le attese nella notte (raffiche fino a 62 km/h alla piattaforma oceanografica) con
contemporanea sessa in fase. La previsione del colmo di stamattina è rivista al rialzo.</p>
{table([("20/10/2026", "09:40", "MAX", "118"), ("20/10/2026", "15:55", "min", "45"), ("20/10/2026", "21:45", "max", "85"),
        ("21/10/2026", "10:10", "max", "85")])}
<p class="allerta" style="color:#c60">Livello di allerta: ARANCIONE - marea molto sostenuta (110-139 cm).</p>
<p>Percentuale di città pedonale interessata da allagamento al colmo: circa 20-25%. Piazza San Marco allagata a partire dalle ore 08:00 circa.</p>
<p>Sirene: attivazione alle ore 06:45 con segnale a 2 note.</p>
<p>Sistema MOSE: la richiesta di attivazione è stata trasmessa alle ore 06:35. Considerati i tempi tecnici di preavviso e di
sollevamento, la chiusura completa delle bocche di porto potrebbe non essere raggiunta prima del colmo.</p>
<p>Percorsi pedonali sopraelevati (passerelle) in allestimento sui percorsi principali. Si raccomanda l'uso di stivali.</p>
""")

OBS_1020 = f"""{HEAD}

DATI OSSERVATI - martedì 20/10/2026 (aggiornamento ore 15:00)

Massimi osservati (dati a 10 minuti):
  Punta della Salute   118 cm   ore 09:40
  Diga Sud Lido        116 cm   ore 09:20
  Burano               121 cm   ore 10:05
  Chioggia Vigo        112 cm   ore 09:10
  Piattaforma CNR      108 cm   ore 08:55

Sistema MOSE: sollevamento delle barriere avviato alle ore 08:40 alle bocche di Lido, Malamocco e Chioggia;
chiusura completa raggiunta alle ore 09:55, successivamente al colmo registrato in città. L'effetto sul massimo è
stato pertanto limitato.

Sirene attivate alle 06:45 (2 note). Allagamento della Piazza San Marco dalle 08:00 circa alle 11:15 circa;
massima estensione allagata stimata 22% della città pedonale.

Previsione per mercoledì 21/10: massimo 85 cm alle 10:10. Livello di allerta: VERDE/GIALLA.

{FOOT}
"""


def build(out_dir: Path):
    d = out_dir / "venice"
    d.mkdir(parents=True, exist_ok=True)
    (d / "previsione_marea_2026-10-06_h1700.txt").write_text(B_1006, encoding="utf-8")
    (d / "dati_osservati_2026-10-07.txt").write_text(OBS_1007, encoding="utf-8")
    (d / "previsione_marea_2026-10-18_h1200.html").write_text(B_1018, encoding="utf-8")
    (d / "previsione_marea_2026-10-19_h0900.txt").write_text(B_1019_AM, encoding="utf-8")
    (d / "previsione_marea_2026-10-19_h1700.html").write_text(B_1019_PM, encoding="utf-8")
    (d / "AGGIORNAMENTO_previsione_marea_2026-10-20_h0630.html").write_text(B_1020, encoding="utf-8")
    (d / "dati_osservati_2026-10-20.txt").write_text(OBS_1020, encoding="utf-8")
    (d / "livelli_orari_PuntaSalute_2026-10-19_21.csv").write_text(hourly_csv(), encoding="utf-8")


if __name__ == "__main__":
    for h in range(72):
        print(19 + h // 24, h % 24, round(level(h)))
