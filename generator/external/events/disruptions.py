"""Transport strike / disruption feeds: aggregator CSV, RATP notice, Italian ministry listing."""
import csv
import io
from pathlib import Path

SRC = {
    "sr": "https://strikeradar.example/e/{rid}",
    "mit": "https://scioperi.mit-trasporti.example/mit2/public/scioperi/dettaglio/{n}",
    "ratp": "https://www.ratp.example/actualites/trafic/{n}",
    "news": "https://newsdesk.example/transport/{n}",
    "uk": "https://www.tfl-status.example/strikes/{n}",
    "be": "https://www.belgianrail.example/fr/news/{n}",
    "es": "https://www.renfe-avisos.example/{n}",
}

# record_id, country, city, operator, sector, start_local, end_local, tz, scope, description, impact, status, src, updated_utc
ROWS = [
    ("SR-IT-26-0141", "IT", "", "Trenitalia; Italo; Trenord", "rail", "2026-08-07 21:00", "2026-08-08 21:00", "Europe/Rome", "national",
     "Sciopero nazionale personale ferroviario 24h, fasce garantite 6-9 e 18-21", "medium", "confirmed", "sr", "2026-08-05T10:12:00Z"),
    ("SR-ES-26-0088", "ES", "Madrid", "Renfe Cercanías", "rail", "2026-08-14 00:00", "2026-08-14 23:59", "Europe/Madrid", "regional",
     "Huelga parcial maquinistas Cercanías Madrid, servicios mínimos 75% en hora punta", "low", "confirmed", "es", "2026-08-11T08:40:00Z"),
    ("SR-IT-26-0150", "IT", "Milano", "Trenord", "rail", "2026-08-29 03:00", "2026-08-30 02:00", "Europe/Rome", "regional",
     "Sciopero Trenord 23h", "medium", "revoked", "sr", "2026-08-26T15:30:00Z"),
    ("SR-DE-26-0201", "DE", "München; Frankfurt am Main", "Lufthansa (ground staff, ver.di)", "aviation", "2026-09-03 04:00", "2026-09-03 23:59", "Europe/Berlin", "national",
     "Warnstreik Bodenpersonal Lufthansa, zahlreiche Flugausfälle in FRA und MUC", "high", "confirmed", "news", "2026-09-01T18:02:00Z"),
    ("SR-UK-26-0057", "GB", "London", "Elizabeth line (RMT)", "rail", "2026-09-08 00:01", "2026-09-09 23:59", "Europe/London", "local",
     "RMT action on Elizabeth line only, reduced timetable; Tube unaffected", "low", "confirmed", "uk", "2026-09-04T12:00:00Z"),
    ("SR-FR-26-0190", "FR", "", "SNCF Voyageurs (TGV, TER)", "rail", "2026-09-10 05:00", "2026-09-11 08:00", "Europe/Paris", "national",
     "Grève nationale contrôleurs et conducteurs, 2 TGV sur 3", "medium", "confirmed", "sr", "2026-09-08T17:45:00Z"),
    ("SR-IT-26-0158", "IT", "Milano", "ATM", "local_transport", "2026-09-11 18:00", "2026-09-11 22:00", "Europe/Rome", "local",
     "Sciopero 4 ore ATM, possibili interruzioni metro M1-M5", "low", "confirmed", "mit", "2026-09-07T09:00:00Z"),
    ("SR-GR-26-0033", "GR", "Athens", "GSEE (general strike); ferries; OASA", "general", "2026-09-16 00:00", "2026-09-16 23:59", "Europe/Athens", "national",
     "General strike, ferries docked, metro running reduced hours", "high", "confirmed", "news", "2026-09-14T07:00:00Z"),
    ("SR-NL-26-0040", "NL", "Noord-Holland", "NS (regional)", "rail", "2026-09-17 04:00", "2026-09-17 12:00", "Europe/Amsterdam", "regional",
     "Regionale estafettestaking NS, ochtend", "low", "confirmed", "sr", "2026-09-15T11:20:00Z"),
    ("SR-IT-26-0160", "IT", "", "ENAV; handling aeroportuale", "aviation", "2026-09-18 10:00", "2026-09-18 18:00", "Europe/Rome", "national",
     "Sciopero trasporto aereo, voli garantiti 7-10 e 18-21", "medium", "confirmed", "mit", "2026-09-15T08:10:00Z"),
    ("SR-FR-26-0198", "FR", "", "DGAC (contrôleurs aériens)", "aviation", "2026-09-23 06:00", "2026-09-24 06:00", "Europe/Paris", "national",
     "Préavis contrôleurs aériens, annulations attendues à Orly et Marseille", "high", "revoked", "news", "2026-09-21T19:33:00Z"),
    ("SR-PT-26-0019", "PT", "Lisboa; Porto", "CP Comboios de Portugal", "rail", "2026-09-24 00:00", "2026-09-24 23:59", "Europe/Lisbon", "national",
     "Greve CP 24h, serviços mínimos", "medium", "confirmed", "sr", "2026-09-21T10:00:00Z"),
    ("SR-IT-26-0163", "IT", "", "Trenitalia; Italo", "rail", "2026-09-24 21:00", "2026-09-25 21:00", "Europe/Rome", "national",
     "Sciopero nazionale ferrovieri 24h", "medium", "revoked", "mit", "2026-09-22T16:05:00Z"),
    ("SR-BE-26-0061", "BE", "Bruxelles; Antwerpen; Liège", "SNCB; STIB; De Lijn; TEC", "general", "2026-09-29 00:00", "2026-09-29 23:59", "Europe/Brussels", "national",
     "Journée d'action nationale, transports publics fortement perturbés", "high", "confirmed", "be", "2026-09-25T09:00:00Z"),
    ("SR-IT-26-0166", "IT", "Venezia", "ACTV", "local_transport", "2026-09-29 00:00", "2026-09-29 23:59", "Europe/Rome", "local",
     "Sciopero ACTV navigazione e automobilistico, garantite fasce 6:00-8:59 e 16:30-19:29", "low", "confirmed", "mit", "2026-09-24T13:00:00Z"),
    ("SR-UK-26-0062", "GB", "London", "Heathrow security (Unite)", "aviation", "2026-09-30 04:00", "2026-10-02 04:00", "Europe/London", "local",
     "Security staff walkout at T3/T5", "medium", "revoked", "uk", "2026-09-28T14:10:00Z"),
    ("SR-DE-26-0209", "DE", "Berlin", "BVG", "local_transport", "2026-10-01 03:00", "2026-10-01 12:00", "Europe/Berlin", "local",
     "Warnstreik BVG U-Bahn, Tram und Bus bis 12 Uhr", "medium", "confirmed", "news", "2026-09-29T15:00:00Z"),
    ("SR-ES-26-0101", "ES", "", "Renfe; Adif", "rail", "2026-10-02 00:00", "2026-10-02 23:59", "Europe/Madrid", "national",
     "Huelga Renfe/Adif 24h", "medium", "revoked", "es", "2026-09-30T18:00:00Z"),
    ("SR-FR-26-0205", "FR", "Paris", "RER B (RATP/SNCF)", "rail", "2026-10-02 05:30", "2026-10-02 20:00", "Europe/Paris", "local",
     "Mouvement social local RER B, 1 train sur 2 au nord de Gare du Nord", "low", "confirmed", "ratp", "2026-09-30T16:00:00Z"),
    ("SR-IT-26-0170", "IT", "Roma", "ATAC", "local_transport", "2026-10-06 20:00", "2026-10-07 00:00", "Europe/Rome", "local",
     "Sciopero aziendale ATAC 4 ore serali", "low", "confirmed", "mit", "2026-10-01T09:30:00Z"),
    ("SR-NL-26-0046", "NL", "Amsterdam", "GVB", "local_transport", "2026-10-09 00:00", "2026-10-09 23:59", "Europe/Amsterdam", "local",
     "Estafettestaking GVB nachtbussen en tram 26", "low", "confirmed", "sr", "2026-10-06T08:15:00Z"),
    ("SR-FR-26-0217", "FR", "Paris; Île-de-France", "RATP", "metro", "2026-10-13 05:30", "2026-10-15 05:30", "Europe/Paris", "regional",
     "Grève RATP: métro lignes 1, 8, 9 quasi interrompues, RER A 1 train sur 2", "high", "confirmed", "sr", "2026-10-08T09:14:00Z"),
    ("SR-FR-26-0217", "FR", "Paris; Île-de-France", "RATP", "metro", "2026-10-13 05:30", "2026-10-14 05:30", "Europe/Paris", "regional",
     "CORRECTION: préavis de 24h (et non 48h). Lignes 1, 8, 9 quasi interrompues, ligne 14 normale, RER A 1/2", "high", "corrected", "sr", "2026-10-10T16:02:00Z"),
    ("SR-FR-26-0218", "FR", "Paris; Île-de-France", "SNCF Transilien; RER B/C/D/E", "rail", "2026-10-12 20:00", "2026-10-14 08:00", "Europe/Paris", "regional",
     "Grève SNCF Île-de-France, RER B 1 train sur 3, interconnexion suspendue à Gare du Nord", "high", "confirmed", "ratp", "2026-10-12T15:00:00Z"),
    ("SR-DE-26-0215", "DE", "München", "MVG", "local_transport", "2026-10-14 03:00", "2026-10-14 23:59", "Europe/Berlin", "local",
     "Warnstreik MVG U-Bahn und Tram", "medium", "revoked", "news", "2026-10-12T17:40:00Z"),
    ("SR-BE-26-0066", "BE", "", "SNCB", "rail", "2026-10-14 22:00", "2026-10-16 22:00", "Europe/Brussels", "national",
     "Grève du rail 48h, service alternatif", "high", "confirmed", "be", "2026-10-09T10:00:00Z"),
    ("SR-CH-26-0004", "CH", "Uri; Graubünden", "SBB; RhB", "rail", "2026-10-14 05:00", "2026-10-14 14:00", "Europe/Zurich", "regional",
     "Not a strike: snow and fallen trees, Gotthard route and Oberalp interrupted", "medium", "incident", "news", "2026-10-14T13:05:00Z"),
    ("SR-IT-26-0176", "IT", "", "Trenitalia; Italo; Trenord; Ferrovie Nord", "rail", "2026-10-15 21:00", "2026-10-16 21:00", "Europe/Rome", "national",
     "Sciopero generale: treni a rischio, fasce garantite 6-9 e 18-21", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0177", "IT", "Milano", "ATM", "local_transport", "2026-10-16 08:45", "2026-10-16 15:00", "Europe/Rome", "local",
     "Sciopero generale: metro, tram e bus a rischio dopo le 8:45; garantito 15-18", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0177", "IT", "Milano", "ATM", "local_transport", "2026-10-16 18:00", "2026-10-17 01:30", "Europe/Rome", "local",
     "Sciopero generale ATM (seconda finestra, fino a fine servizio)", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0178", "IT", "Roma", "ATAC; Roma TPL", "local_transport", "2026-10-16 08:30", "2026-10-16 17:00", "Europe/Rome", "local",
     "Sciopero generale: metro A/B/C, bus e tram a rischio; garantito fino 8:30 e 17-20", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0178", "IT", "Roma", "ATAC; Roma TPL", "local_transport", "2026-10-16 20:00", "2026-10-17 00:30", "Europe/Rome", "local",
     "Sciopero generale ATAC (seconda finestra)", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0179", "IT", "Venezia", "ACTV", "local_transport", "2026-10-16 00:00", "2026-10-16 23:59", "Europe/Rome", "local",
     "Sciopero generale: vaporetti e bus, garantite 6:00-8:59 e 16:30-19:29", "medium", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0180", "IT", "Torino; Napoli; Firenze; Bologna", "GTT; ANM; Autolinee Toscane; TPER", "local_transport", "2026-10-16 00:00", "2026-10-16 23:59", "Europe/Rome", "national",
     "Sciopero generale TPL, fasce di garanzia locali", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-IT-26-0181", "IT", "", "ENAV; handling; Alitalia-ITA", "aviation", "2026-10-16 00:00", "2026-10-16 23:59", "Europe/Rome", "national",
     "Sciopero generale settore aereo, voli garantiti 7-10 e 18-21", "medium", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("MIT-55821", "IT", "", "Tutti i settori pubblici e privati", "general", "16/10/2026 00:00", "16/10/2026 23:59", "Europe/Rome", "national",
     "Sciopero generale nazionale (USB, CUB, SI Cobas, ADL Cobas) - trasporti con modalità specifiche", "high", "confermato", "mit", "2026-10-13T06:00:00Z"),
    ("MIT-55822", "IT", "", "Ferroviario", "rail", "15/10/2026 21:00", "16/10/2026 21:00", "Europe/Rome", "national",
     "Sciopero generale - settore ferroviario", "high", "confermato", "mit", "2026-10-13T06:00:00Z"),
    ("SR-ES-26-0109", "ES", "Madrid", "Metro de Madrid", "metro", "2026-10-21 06:00", "2026-10-21 09:00", "Europe/Madrid", "local",
     "Paros parciales maquinistas, servicios mínimos 70%", "low", "confirmed", "es", "2026-10-19T12:00:00Z"),
    ("SR-ES-26-0109", "ES", "Madrid", "Metro de Madrid", "metro", "2026-10-21 17:00", "2026-10-21 20:00", "Europe/Madrid", "local",
     "Paros parciales maquinistas (tarde)", "low", "confirmed", "es", "2026-10-19T12:00:00Z"),
    ("SR-FR-26-0224", "FR", "", "Air France PNC", "aviation", "2026-10-20 00:00", "2026-10-22 23:59", "Europe/Paris", "national",
     "Grève hôtesses et stewards Air France", "medium", "revoked", "news", "2026-10-16T18:20:00Z"),
    ("SR-IT-26-0185", "IT", "Roma", "Taxi (sigle sindacali tassisti)", "taxi", "2026-10-23 08:00", "2026-10-23 22:00", "Europe/Rome", "local",
     "Fermo taxi Roma contro nuove licenze NCC", "low", "confirmed", "news", "2026-10-20T10:00:00Z"),
    ("SR-UK-26-0071", "GB", "London; Brighton", "Govia Thameslink (ASLEF)", "rail", "2026-10-27 00:01", "2026-10-27 23:59", "Europe/London", "regional",
     "Drivers strike Southern/Thameslink", "medium", "announced", "uk", "2026-10-15T09:00:00Z"),
    ("SR-PT-26-0024", "PT", "Lisboa", "Metropolitano de Lisboa", "metro", "2026-10-30 06:30", "2026-10-30 10:00", "Europe/Lisbon", "local",
     "Greve parcial, abertura das estações às 10h", "low", "announced", "sr", "2026-10-19T08:00:00Z"),
    ("SR-IT-26-0172", "IT", "", "Trasporto aereo (handling, ENAV)", "aviation", "2026-10-30 10:00", "2026-10-30 18:00", "Europe/Rome", "national",
     "Sciopero trasporto aereo - DIFFERITO al 13/11/2026 su indicazione della Commissione di Garanzia", "medium", "postponed", "mit", "2026-10-14T11:00:00Z"),
    ("SR-IT-26-0172b", "IT", "", "Trasporto aereo (handling, ENAV)", "aviation", "2026-11-13 10:00", "2026-11-13 18:00", "Europe/Rome", "national",
     "Sciopero trasporto aereo (nuova data)", "medium", "rescheduled", "mit", "2026-10-14T11:00:00Z"),
    ("SR-ES-26-0112", "ES", "", "Azul Handling", "aviation", "2026-11-02 00:00", "2026-11-30 23:59", "Europe/Madrid", "national",
     "Huelga indefinida lunes, miércoles y viernes en aeropuertos españoles", "low", "announced", "es", "2026-10-18T09:30:00Z"),
    ("SR-FR-26-0230", "FR", "", "Intersyndicale (CGT, FO, SUD)", "general", "2026-11-05 00:00", "2026-11-05 23:59", "Europe/Paris", "national",
     "Journée de mobilisation interprofessionnelle", "medium", "announced", "news", "2026-10-21T07:00:00Z"),
    ("SR-IT-26-0188", "IT", "", "Trenitalia; Italo", "rail", "2026-11-06 21:00", "2026-11-07 21:00", "Europe/Rome", "national",
     "Sciopero ferrovieri 24h", "medium", "confirmed", "mit", "2026-10-21T08:00:00Z"),
    ("SR-BE-26-0070", "BE", "Bruxelles", "STIB", "local_transport", "2026-11-12 00:00", "2026-11-12 23:59", "Europe/Brussels", "local",
     "Action syndicale STIB", "medium", "announced", "be", "2026-10-20T10:00:00Z"),
    ("SR-IT-26-0190", "IT", "", "Sindacati di base (sciopero generale)", "general", "2026-11-20 00:00", "2026-11-20 23:59", "Europe/Rome", "national",
     "Proclamazione sciopero generale contro legge di bilancio", "high", "announced", "news", "2026-10-21T15:00:00Z"),
    ("SR-DE-26-0221", "DE", "Hamburg", "Hamburger Hochbahn", "local_transport", "2026-11-04 03:00", "2026-11-04 14:00", "Europe/Berlin", "local",
     "Warnstreik Hochbahn (angekündigt)", "low", "announced", "news", "2026-10-21T12:00:00Z"),
    ("SR-DK-26-0007", "DK", "København", "Metroselskabet", "metro", "2026-09-28 10:00", "2026-09-28 14:00", "Europe/Copenhagen", "local",
     "Short work stoppage, M3 Cityringen", "low", "confirmed", "sr", "2026-09-28T08:30:00Z"),
    ("SR-IT-26-0177", "IT", "Milano", "ATM", "local_transport", "2026-10-16 08:45", "2026-10-16 15:00", "Europe/Rome", "local",
     "Sciopero generale: metro, tram e bus a rischio dopo le 8:45; garantito 15-18", "high", "confirmed", "sr", "2026-10-12T08:00:00Z"),
    ("SR-GR-26-0038", "GR", "Piraeus", "PNO (seamen)", "ferry", "2026-10-08 06:00", "2026-10-09 06:00", "Europe/Athens", "national",
     "24-hour ferry strike", "medium", "confirmed", "news", "2026-10-06T07:00:00Z"),
    ("SR-UK-26-0068", "GB", "London", "London Underground (RMT)", "metro", "2026-10-06 00:01", "2026-10-07 23:59", "Europe/London", "local",
     "Tube strike - SUSPENDED after new pay offer", "high", "revoked", "uk", "2026-10-02T21:45:00Z"),
]


def strikes_csv():
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["record_id", "country", "city", "operator", "sector", "start_local", "end_local", "tz", "scope",
                "description", "expected_impact", "status", "source_url", "last_updated_utc"])
    for i, r in enumerate(ROWS):
        rid, src = r[0], r[12]
        url = SRC[src].format(rid=rid.lower(), n=40000 + i * 37)
        w.writerow(list(r[:12]) + [url, r[13]])
    return buf.getvalue()


RATP = """RATP - INFO TRAFIC
Prévisions de trafic pour le mardi 13 octobre 2026
Publié le lundi 12 octobre 2026 à 17h00

En raison d'un mouvement social interprofessionnel, le trafic sera très perturbé sur l'ensemble des réseaux RATP le mardi 13 octobre 2026.
Nous vous invitons à limiter vos déplacements et à privilégier le télétravail lorsque cela est possible.

MÉTRO
Ligne 1 : trafic quasi nul. 1 train sur 4 de 7h30 à 9h30 et de 17h00 à 19h00 uniquement. Fermeture des stations Concorde, Champs-Élysées - Clemenceau et Franklin D. Roosevelt toute la journée.
Ligne 2 : 1 train sur 2 aux heures de pointe.
Ligne 3 : 1 train sur 3 aux heures de pointe.
Ligne 4 : 1 train sur 2.
Ligne 5 : 1 train sur 3 aux heures de pointe.
Ligne 6 : 1 train sur 3 aux heures de pointe.
Ligne 7 : 1 train sur 2 aux heures de pointe uniquement, entre La Courneuve et Place d'Italie.
Ligne 8 : service interrompu toute la journée.
Ligne 9 : quelques trains aux heures de pointe entre Pont de Sèvres et Havre - Caumartin. Pas de desserte entre Havre - Caumartin et Mairie de Montreuil. Stations Saint-Augustin et Miromesnil fermées.
Ligne 10 : 1 train sur 3.
Ligne 11 : 1 train sur 2.
Ligne 12 : 1 train sur 2 aux heures de pointe.
Ligne 13 : 1 train sur 3 aux heures de pointe.
Ligne 14 : trafic normal. Forte affluence attendue, régulation des accès en station possible.
Lignes 3bis et 7bis : service interrompu.

RER
RER A : 1 train sur 2 aux heures de pointe, 1 train sur 3 en heures creuses. Interconnexion maintenue à Nanterre-Préfecture.
RER B : 1 train sur 3. Interconnexion suspendue à Gare du Nord, changement de train obligatoire.

BUS ET TRAMWAY
Bus : 2 bus sur 3 en moyenne. Noctilien : 1 bus sur 2 dans la nuit de mardi à mercredi.
Tramway : T1, T2, T3a, T3b : 2 trams sur 3. Autres lignes : trafic normal.

Pour les lignes SNCF (RER C, D, E et Transilien), consultez les prévisions de SNCF Voyageurs.
Retour à un trafic normal prévu le mercredi 14 octobre en début de service, sauf exceptions locales.

Ces prévisions sont susceptibles d'évoluer. Retrouvez l'information en temps réel sur l'appli et sur ratp.example.
"""

MIT_HEADER = ["Stato", "Settore", "Data inizio", "Data fine", "Sindacati", "Categoria interessata", "Modalità",
              "Rilevanza", "Regione", "Provincia", "Data proclamazione", "Data ricezione", "Note"]
MIT_ROWS = [
    ("Effettuato", "Ferroviario", "07/09/2026", "08/09/2026", "CUB Trasporti", "Personale mobile", "Dalle 21:00 del 7 alle 21:00 dell'8", "Regionale", "Lombardia", "", "18/08/2026", "19/08/2026", "Trenord"),
    ("Effettuato", "Trasporto pubblico locale", "11/09/2026", "11/09/2026", "Al Cobas; Orsa TPL", "Personale ATM", "4 ore: 18:00-22:00", "Locale", "Lombardia", "Milano", "21/08/2026", "21/08/2026", ""),
    ("Effettuato", "Aereo", "18/09/2026", "18/09/2026", "Cub Trasporti; USB Lavoro Privato", "Personale ENAV e handling", "Dalle 10:00 alle 18:00", "Nazionale", "", "", "25/08/2026", "26/08/2026", "Voli garantiti 7-10 e 18-21"),
    ("Revocato", "Ferroviario", "24/09/2026", "25/09/2026", "USB Lavoro Privato; Orsa Ferrovie", "Personale Gruppo FS e Italo", "Dalle 21:00 del 24 alle 21:00 del 25", "Nazionale", "", "", "02/09/2026", "03/09/2026", "Revocato il 22/09/2026"),
    ("Effettuato", "Trasporto pubblico locale", "29/09/2026", "29/09/2026", "Filt Cgil; Uiltrasporti", "Personale ACTV", "Intera giornata con fasce 6:00-8:59 e 16:30-19:29", "Locale", "Veneto", "Venezia", "08/09/2026", "09/09/2026", "Navigazione e automobilistico"),
    ("Effettuato", "Trasporto pubblico locale", "06/10/2026", "06/10/2026", "Faisa Confail; Cobas Lavoro Privato", "Personale ATAC", "4 ore: 20:00-24:00", "Locale", "Lazio", "Roma", "15/09/2026", "16/09/2026", ""),
    ("Effettuato", "Generale", "16/10/2026", "16/10/2026", "USB; CUB; SI Cobas; ADL Cobas; Cobas Scuola", "Tutti i settori pubblici e privati", "Intera giornata; trasporti secondo le modalità di settore", "Nazionale", "", "", "18/09/2026", "19/09/2026", "Sciopero generale"),
    ("Effettuato", "Ferroviario", "15/10/2026", "16/10/2026", "USB; CUB Trasporti; SI Cobas", "Personale Gruppo FS, Italo, Trenord", "Dalle 21:00 del 15 alle 21:00 del 16", "Nazionale", "", "", "18/09/2026", "19/09/2026", "Adesione allo sciopero generale"),
    ("Effettuato", "Trasporto pubblico locale", "16/10/2026", "16/10/2026", "USB; CUB Trasporti", "Personale ATM Milano", "Dalle 8:45 alle 15:00 e dalle 18:00 a fine servizio", "Locale", "Lombardia", "Milano", "18/09/2026", "19/09/2026", "Adesione allo sciopero generale"),
    ("Effettuato", "Trasporto pubblico locale", "16/10/2026", "16/10/2026", "USB; CUB Trasporti; Cobas", "Personale ATAC e Roma TPL", "Dalle 8:30 alle 17:00 e dalle 20:00 a fine servizio", "Locale", "Lazio", "Roma", "18/09/2026", "19/09/2026", "Adesione allo sciopero generale"),
    ("Effettuato", "Trasporto pubblico locale", "16/10/2026", "16/10/2026", "USB", "Personale ACTV", "Intera giornata con fasce 6:00-8:59 e 16:30-19:29", "Locale", "Veneto", "Venezia", "18/09/2026", "19/09/2026", "Adesione allo sciopero generale"),
    ("Effettuato", "Aereo", "16/10/2026", "16/10/2026", "USB; CUB Trasporti", "Personale aeroportuale", "Intera giornata, voli garantiti 7-10 e 18-21", "Nazionale", "", "", "18/09/2026", "19/09/2026", "Adesione allo sciopero generale"),
    ("Effettuato", "Marittimo", "16/10/2026", "16/10/2026", "USB", "Personale imprese portuali", "Intera giornata", "Locale", "Liguria", "Genova", "20/09/2026", "21/09/2026", ""),
    ("Proclamato", "Taxi", "23/10/2026", "23/10/2026", "Unica Taxi; Uritaxi; Ugl Taxi", "Tassisti", "Dalle 8:00 alle 22:00", "Locale", "Lazio", "Roma", "08/10/2026", "08/10/2026", ""),
    ("Differito", "Aereo", "30/10/2026", "30/10/2026", "Cub Trasporti; Usb", "Personale ENAV e handling", "Dalle 10:00 alle 18:00", "Nazionale", "", "", "29/09/2026", "30/09/2026", "Differito al 13/11/2026 a seguito di indicazione immediata della Commissione di Garanzia"),
    ("Proclamato", "Ferroviario", "06/11/2026", "07/11/2026", "Orsa Ferrovie; Fast Confsal", "Personale mobile", "Dalle 21:00 del 6 alle 21:00 del 7", "Nazionale", "", "", "15/10/2026", "16/10/2026", ""),
    ("Proclamato", "Aereo", "13/11/2026", "13/11/2026", "Cub Trasporti; Usb", "Personale ENAV e handling", "Dalle 10:00 alle 18:00", "Nazionale", "", "", "14/10/2026", "14/10/2026", "Nuova data dopo differimento"),
    ("Proclamato", "Generale", "20/11/2026", "20/11/2026", "USB; CUB; SGB", "Tutti i settori pubblici e privati", "Intera giornata", "Nazionale", "", "", "20/10/2026", "21/10/2026", "In attesa di valutazione della Commissione"),
    ("Revocato", "Trasporto pubblico locale", "09/10/2026", "09/10/2026", "Orsa TPL", "Personale GTT", "4 ore: 17:30-21:30", "Locale", "Piemonte", "Torino", "18/09/2026", "18/09/2026", "Revocato il 07/10/2026"),
    ("Effettuato", "Trasporto pubblico locale", "02/10/2026", "02/10/2026", "Usb", "Personale ANM", "24 ore con fasce di garanzia", "Locale", "Campania", "Napoli", "11/09/2026", "12/09/2026", ""),
    ("Effettuato", "Autostrade", "26/09/2026", "27/09/2026", "Filt Cgil; Fit Cisl; Uiltrasporti", "Personale caselli", "Dalle 22:00 del 26 alle 22:00 del 27", "Nazionale", "", "", "28/08/2026", "29/08/2026", ""),
]


def mit_csv_bytes():
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    w.writerow(MIT_HEADER)
    for r in MIT_ROWS:
        w.writerow(r)
    return buf.getvalue().encode("cp1252")


def build(out_dir: Path):
    d = out_dir / "disruptions"
    d.mkdir(parents=True, exist_ok=True)
    (d / "strikes_feed.csv").write_text(strikes_csv(), encoding="utf-8")
    (d / "ratp_previsions_trafic_2026-10-13.txt").write_text(RATP, encoding="utf-8")
    (d / "mit_scioperi_export_2026-10-22.csv").write_bytes(mit_csv_bytes())
