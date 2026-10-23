"""City events feeds: global ticketing aggregator (JSON, English) + Asia aggregator (CSV, local languages)."""
import csv
import datetime as dt
import json

import numpy as np
import pandas as pd

from common import CITIES, OUT, d, drange, mkdir, rng_for, write_json

E = mkdir(OUT / "events" / "city_events")
TD = dt.timedelta

# (city_key, title, category, venue, start, end, attendance, extra)
MAJOR = [
    # Milano / Cortina / Roma / Venezia
    ("MILANO", "Milano Fashion Week Women SS26", "fashion", "various", "2025-09-23", "2025-09-29", 120000, {}),
    ("MILANO", "Milano Fashion Week Women SS27", "fashion", "various", "2026-09-22", "2026-09-28", 125000, {}),
    ("MILANO", "Milano Fashion Week Women FW26", "fashion", "various", "2026-02-24", "2026-03-02", 110000, {}),
    ("MILANO", "Salone del Mobile.Milano 2025", "fair", "Fiera Milano Rho", "2025-04-08", "2025-04-13", 370000, {}),
    ("MILANO", "Salone del Mobile.Milano 2026", "fair", "Fiera Milano Rho", "2026-04-21", "2026-04-26", 360000, {}),
    ("MILANO", "Olympic Winter Games Milano Cortina 2026 - Milano venues", "sports", "San Siro / Santa Giulia / Rho", "2026-02-06", "2026-02-22", 1200000, {}),
    ("CORTINA", "Olympic Winter Games Milano Cortina 2026 - Cortina cluster", "sports", "Olympia delle Tofane / Sliding Centre", "2026-02-06", "2026-02-22", 450000, {}),
    ("CORTINA", "Paralympic Winter Games 2026 - Cortina", "sports", "Cortina d'Ampezzo", "2026-03-06", "2026-03-15", 120000, {}),
    ("MILANO", "EICMA 2025", "fair", "Fiera Milano Rho", "2025-11-04", "2025-11-09", 560000, {}),
    ("MILANO", "EICMA 2026", "fair", "Fiera Milano Rho", "2026-11-05", "2026-11-08", 550000, {}),
    ("MILANO", "Milano Marathon 2026", "marathon", "city centre", "2026-04-12", "2026-04-12", 30000, {}),
    ("MILANO", "Derby della Madonnina (Serie A)", "sports", "Stadio San Siro", "2026-10-25", "2026-10-25", 75000, {}),
    ("ROMA", "Giubileo 2025 - Anno Santo", "religious", "Basilica di San Pietro / città", "2024-12-24", "2026-01-06", 32000000, {"note": "pilgrims over the whole year"}),
    ("ROMA", "Festa del Cinema di Roma 2025", "film", "Auditorium Parco della Musica", "2025-10-15", "2025-10-26", 120000, {}),
    ("ROMA", "Festa del Cinema di Roma 2026", "film", "Auditorium Parco della Musica", "2026-10-15", "2026-10-25", 120000, {}),
    ("ROMA", "Internazionali BNL d'Italia 2026", "sports", "Foro Italico", "2026-05-04", "2026-05-17", 370000, {}),
    ("VENEZIA", "Biennale Arte 2026", "exhibition", "Giardini / Arsenale", "2026-05-09", "2026-11-22", 800000, {}),
    ("VENEZIA", "Biennale Architettura 2025", "exhibition", "Giardini / Arsenale", "2025-05-10", "2025-11-23", 600000, {}),
    ("VENEZIA", "Mostra Internazionale d'Arte Cinematografica 2025", "film", "Lido", "2025-08-27", "2025-09-06", 90000, {}),
    ("VENEZIA", "Mostra Internazionale d'Arte Cinematografica 2026", "film", "Lido", "2026-09-02", "2026-09-12", 90000, {}),
    ("VENEZIA", "Carnevale di Venezia 2026", "festival", "Piazza San Marco", "2026-01-31", "2026-02-17", 1500000, {}),
    ("VENEZIA", "Venicemarathon 2026", "marathon", "Stra - Riva Sette Martiri", "2026-10-25", "2026-10-25", 8000, {}),
    ("VENEZIA", "Regata Storica 2026", "festival", "Canal Grande", "2026-09-06", "2026-09-06", 50000, {}),
    # Paris / Cannes
    ("PARIS", "Paris Fashion Week Women SS27", "fashion", "various", "2026-09-29", "2026-10-07", 140000, {}),
    ("PARIS", "Paris Fashion Week Women SS26", "fashion", "various", "2025-09-29", "2025-10-07", 135000, {}),
    ("PARIS", "Art Basel Paris 2025", "art_fair", "Grand Palais", "2025-10-22", "2025-10-26", 65000, {}),
    ("PARIS", "Art Basel Paris 2026", "art_fair", "Grand Palais", "2026-10-23", "2026-10-25", 68000, {"vip_days": "2026-10-21/22"}),
    ("PARIS", "Mondial de l'Auto 2026", "fair", "Paris Expo Porte de Versailles", "2026-10-13", "2026-10-18", 400000, {}),
    ("PARIS", "Nuit Blanche 2026", "cultural", "city-wide", "2026-10-03", "2026-10-03", 1000000, {}),
    ("PARIS", "Schneider Electric Marathon de Paris 2026", "marathon", "Champs-Élysées", "2026-04-12", "2026-04-12", 57000, {}),
    ("PARIS", "Roland-Garros 2026", "sports", "Stade Roland-Garros", "2026-05-24", "2026-06-07", 650000, {}),
    ("CANNES", "Festival de Cannes 2026", "film", "Palais des Festivals", "2026-05-12", "2026-05-23", 200000, {}),
    ("CANNES", "Cannes Yachting Festival 2026", "fair", "Vieux Port / Port Canto", "2026-09-08", "2026-09-13", 55000, {}),
    ("CANNES", "MIPCOM 2026", "conference", "Palais des Festivals", "2026-10-19", "2026-10-22", 11000, {}),
    # CH
    ("GENEVE", "Watches and Wonders Geneva 2026", "fair", "Palexpo", "2026-04-14", "2026-04-20", 55000, {}),
    ("GENEVE", "Fêtes de Genève 2026", "festival", "Rade", "2026-07-23", "2026-08-02", 1000000, {}),
    ("ZUERICH", "Zurich Film Festival 2026", "film", "Corso / Kino Kosmos", "2026-09-24", "2026-10-04", 135000, {}),
    ("ZUERICH", "Zurich Film Festival 2025", "film", "Corso / Kino Kosmos", "2025-09-25", "2025-10-05", 130000, {}),
    ("ZUERICH", "Street Parade 2026", "festival", "Seebecken", "2026-08-08", "2026-08-08", 900000, {}),
    ("STMORITZ", "Snow Jersey Polo World Cup St. Moritz 2026", "sports", "Frozen lake", "2026-01-23", "2026-01-25", 18000, {}),
    ("STMORITZ", "White Turf St. Moritz 2026", "sports", "Frozen lake", "2026-02-08", "2026-02-22", 35000, {}),
    ("STMORITZ", "St. Moritz Gourmet Festival 2026", "food", "various hotels", "2026-01-30", "2026-02-07", 6000, {}),
    # London
    ("LONDON", "London Fashion Week SS27", "fashion", "various", "2026-09-17", "2026-09-21", 80000, {}),
    ("LONDON", "Frieze London & Frieze Masters 2026", "art_fair", "Regent's Park", "2026-10-14", "2026-10-18", 90000, {}),
    ("LONDON", "Frieze London & Frieze Masters 2025", "art_fair", "Regent's Park", "2025-10-15", "2025-10-19", 88000, {}),
    ("LONDON", "BFI London Film Festival 2026", "film", "Southbank / Leicester Sq", "2026-10-07", "2026-10-18", 200000, {}),
    ("LONDON", "TCS London Marathon 2026", "marathon", "Greenwich - The Mall", "2026-04-26", "2026-04-26", 56000, {}),
    ("LONDON", "NFL London Games 2026 (Tottenham)", "sports", "Tottenham Hotspur Stadium", "2026-10-11", "2026-10-11", 61000, {}),
    ("LONDON", "Wimbledon Championships 2026", "sports", "AELTC", "2026-06-29", "2026-07-12", 530000, {}),
    ("LONDON", "Winter Wonderland 2026", "festival", "Hyde Park", "2026-11-20", "2027-01-03", 3000000, {}),
    # Germany
    ("MUENCHEN", "Oktoberfest 2026", "festival", "Theresienwiese", "2026-09-19", "2026-10-04", 6500000, {}),
    ("MUENCHEN", "Oktoberfest 2025", "festival", "Theresienwiese", "2025-09-20", "2025-10-05", 6500000, {}),
    ("MUENCHEN", "Oktoberfest 2024", "festival", "Theresienwiese", "2024-09-21", "2024-10-06", 6700000, {}),
    ("MUENCHEN", "Generali München Marathon 2026", "marathon", "Olympiapark", "2026-10-11", "2026-10-11", 22000, {}),
    ("MUENCHEN", "ISPO Munich 2026", "fair", "Messe München", "2026-11-29", "2026-12-01", 40000, {}),
    ("MUENCHEN", "Christkindlmarkt Marienplatz 2026", "festival", "Marienplatz", "2026-11-23", "2026-12-24", 3000000, {}),
    ("BERLIN", "BMW Berlin-Marathon 2026", "marathon", "Tiergarten", "2026-09-27", "2026-09-27", 55000, {}),
    ("BERLIN", "Festival of Lights 2026", "cultural", "city-wide", "2026-10-02", "2026-10-11", 2000000, {}),
    ("BERLIN", "IFA Berlin 2026", "fair", "Messe Berlin", "2026-09-04", "2026-09-08", 215000, {}),
    ("BERLIN", "Berlinale 2026", "film", "Potsdamer Platz", "2026-02-12", "2026-02-22", 330000, {}),
    # Spain / NL / DK
    ("MADRID", "Mercedes-Benz Fashion Week Madrid Sep 2026", "fashion", "IFEMA", "2026-09-16", "2026-09-20", 40000, {}),
    ("MADRID", "Desfile Fiesta Nacional (12 de Octubre)", "cultural", "Paseo de la Castellana", "2026-10-12", "2026-10-12", 150000, {}),
    ("MADRID", "Formula 1 Gran Premio de España - Madring 2026", "sports", "IFEMA Madring", "2026-09-11", "2026-09-13", 330000, {}),
    ("MADRID", "Mad Cool Festival 2026", "concert", "Iberdrola Music", "2026-07-08", "2026-07-11", 240000, {}),
    ("AMSTERDAM", "Amsterdam Dance Event 2026", "concert", "200+ venues", "2026-10-14", "2026-10-18", 450000, {}),
    ("AMSTERDAM", "TCS Amsterdam Marathon 2026", "marathon", "Olympisch Stadion", "2026-10-18", "2026-10-18", 45000, {}),
    ("AMSTERDAM", "Koningsdag 2026", "festival", "city-wide", "2026-04-27", "2026-04-27", 1000000, {}),
    ("KOBENHAVN", "Copenhagen Fashion Week SS27", "fashion", "various", "2026-08-04", "2026-08-07", 30000, {}),
    ("KOBENHAVN", "Copenhagen Marathon 2026", "marathon", "Islands Brygge", "2026-05-10", "2026-05-10", 25000, {}),
    ("KOBENHAVN", "Kulturnatten 2026", "cultural", "city-wide", "2026-10-09", "2026-10-09", 80000, {}),
    # Dubai
    ("DUBAI", "GITEX Global 2026", "fair", "Dubai World Trade Centre / Expo City", "2026-10-12", "2026-10-16", 200000, {}),
    ("DUBAI", "Dubai Shopping Festival 2026/27", "festival", "city-wide", "2026-12-04", "2027-01-17", 3500000, {}),
    ("DUBAI", "Dubai Airshow 2025", "fair", "Dubai World Central", "2025-11-17", "2025-11-21", 148000, {}),
    ("DUBAI", "Dubai Design Week 2026", "fair", "d3", "2026-11-10", "2026-11-15", 90000, {}),
    ("DUBAI", "Art Dubai 2026", "art_fair", "Madinat Jumeirah", "2026-04-17", "2026-04-19", 30000, {}),
    # North America
    ("NEWYORK", "UN General Assembly High-Level Week (UNGA 81)", "political", "UN HQ / Midtown East & Upper East Side frozen zones", "2026-09-21", "2026-09-26", 0,
     {"note": "motorcades, street closures 1st-2nd Ave, Madison & Park Ave intermittently; NYPD gridlock alert days"}),
    ("NEWYORK", "UN General Assembly High-Level Week (UNGA 80)", "political", "UN HQ", "2025-09-22", "2025-09-27", 0, {}),
    ("NEWYORK", "New York Fashion Week SS27", "fashion", "various", "2026-09-10", "2026-09-15", 100000, {}),
    ("NEWYORK", "US Open Tennis 2026", "sports", "USTA Billie Jean King NTC", "2026-08-31", "2026-09-13", 1000000, {}),
    ("NEWYORK", "TCS New York City Marathon 2026", "marathon", "Staten Island - Central Park", "2026-11-01", "2026-11-01", 55000, {}),
    ("NEWYORK", "New York Comic Con 2026", "fair", "Javits Center", "2026-10-08", "2026-10-11", 200000, {}),
    ("NEWYORK", "FIFA World Cup 2026 - Final (NY/NJ)", "sports", "MetLife Stadium", "2026-07-19", "2026-07-19", 82000, {}),
    ("NEWYORK", "FIFA World Cup 2026 - NY/NJ matches", "sports", "MetLife Stadium", "2026-06-13", "2026-07-19", 650000, {}),
    ("NEWYORK", "Macy's Thanksgiving Day Parade 2026", "cultural", "Central Park West - 34th St", "2026-11-26", "2026-11-26", 3500000, {}),
    ("MIAMI", "Art Basel Miami Beach 2026", "art_fair", "Miami Beach Convention Center", "2026-12-04", "2026-12-06", 80000, {}),
    ("MIAMI", "Art Basel Miami Beach 2025", "art_fair", "Miami Beach Convention Center", "2025-12-05", "2025-12-07", 80000, {}),
    ("MIAMI", "Formula 1 Miami Grand Prix 2026", "sports", "Hard Rock Stadium", "2026-05-01", "2026-05-03", 275000, {}),
    ("MIAMI", "FIFA World Cup 2026 - Miami matches", "sports", "Hard Rock Stadium", "2026-06-15", "2026-07-11", 400000, {}),
    ("MIAMI", "Design Miami 2026", "art_fair", "Miami Beach", "2026-12-02", "2026-12-06", 40000, {}),
    ("BEVERLYHILLS", "Academy Awards 2026", "film", "Dolby Theatre, Hollywood", "2026-03-15", "2026-03-15", 3400, {}),
    ("BEVERLYHILLS", "Emmy Awards 2026", "film", "Peacock Theater", "2026-09-14", "2026-09-14", 7000, {}),
    ("BEVERLYHILLS", "FIFA World Cup 2026 - Los Angeles matches", "sports", "SoFi Stadium", "2026-06-12", "2026-07-10", 560000, {}),
    ("BEVERLYHILLS", "Frieze Los Angeles 2026", "art_fair", "Santa Monica Airport", "2026-02-26", "2026-03-01", 35000, {}),
    ("ASPEN", "Aspen Snowmass opening day 2026/27", "sports", "Aspen Mountain / Snowmass", "2026-11-26", "2026-11-26", 8000, {}),
    ("ASPEN", "X Games Aspen 2026", "sports", "Buttermilk", "2026-01-23", "2026-01-25", 45000, {}),
    ("ASPEN", "Aspen Ideas Festival 2026", "conference", "Aspen Meadows", "2026-06-25", "2026-07-01", 4000, {}),
    ("ASPEN", "Food & Wine Classic in Aspen 2026", "food", "Wagner Park", "2026-06-19", "2026-06-21", 5000, {}),
    ("TORONTO", "Toronto International Film Festival 2026", "film", "TIFF Lightbox / King St", "2026-09-10", "2026-09-20", 450000, {}),
    ("TORONTO", "Toronto International Film Festival 2025", "film", "TIFF Lightbox / King St", "2025-09-04", "2025-09-14", 430000, {}),
    ("TORONTO", "TCS Toronto Waterfront Marathon 2026", "marathon", "Queen's Park", "2026-10-18", "2026-10-18", 27000, {}),
    ("TORONTO", "FIFA World Cup 2026 - Toronto matches", "sports", "BMO Field", "2026-06-12", "2026-07-02", 270000, {}),
    ("TORONTO", "Nuit Blanche Toronto 2026", "cultural", "city-wide", "2026-10-03", "2026-10-04", 800000, {}),
    # Asia (also listed by the Asia aggregator in local language)
    ("TOKYO", "Tokyo International Film Festival 2026", "film", "Hibiya / Ginza", "2026-10-26", "2026-11-04", 70000, {}),
    ("TOKYO", "Tokyo Game Show 2026", "fair", "Makuhari Messe", "2026-09-17", "2026-09-21", 260000, {}),
    ("TOKYO", "Tokyo Marathon 2026", "marathon", "Tokyo Metropolitan Govt", "2026-03-01", "2026-03-01", 38000, {}),
    ("TOKYO", "LUMIERE 1st World Tour 'PRISM' in Tokyo", "concert", "Tokyo Dome", "2026-11-28", "2026-11-29", 100000, {"announced": "2026-10-06"}),
    ("OSAKA", "Expo 2025 Osaka, Kansai", "exhibition", "Yumeshima", "2025-04-13", "2025-10-13", 25000000, {}),
    ("OSAKA", "Osaka Marathon 2026", "marathon", "Osaka Castle", "2026-02-22", "2026-02-22", 34000, {}),
    ("SEOUL", "Seoul Fashion Week SS27", "fashion", "DDP", "2026-09-01", "2026-09-05", 60000, {}),
    ("SEOUL", "Frieze Seoul / Kiaf 2026", "art_fair", "COEX", "2026-09-02", "2026-09-05", 80000, {}),
    ("SEOUL", "LUMIERE 1st World Tour 'PRISM' in Seoul", "concert", "KSPO Dome", "2026-11-14", "2026-11-15", 30000, {"announced": "2026-10-06"}),
    ("SEOUL", "JTBC Seoul Marathon 2026", "marathon", "Sangam - Jamsil", "2026-11-01", "2026-11-01", 37000, {}),
    ("SEOUL", "Seoul Lantern Festival 2026", "festival", "Cheonggyecheon", "2026-11-06", "2026-11-22", 2500000, {}),
    ("SEOUL", "Northpeak Cheongdam Pop-up", "popup", "Cheongdam-dong (Apgujeong-ro)", "2026-10-15", "2026-11-15", 0, {"note": "brand pop-up store, reservations via app"}),
    ("BUSAN", "Busan International Film Festival 2026", "film", "Busan Cinema Center, Haeundae", "2026-10-01", "2026-10-10", 160000, {}),
    ("BUSAN", "Busan International Film Festival 2025", "film", "Busan Cinema Center, Haeundae", "2025-09-17", "2025-09-26", 175000, {}),
    ("BUSAN", "Busan Fireworks Festival 2026", "festival", "Gwangalli Beach", "2026-11-07", "2026-11-07", 1000000, {}),
    ("BUSAN", "G-STAR 2026", "fair", "BEXCO", "2026-11-12", "2026-11-15", 200000, {}),
    ("SHANGHAI", "Shanghai Fashion Week SS27", "fashion", "Xintiandi", "2026-10-09", "2026-10-16", 70000, {}),
    ("SHANGHAI", "Rolex Shanghai Masters 2026", "sports", "Qizhong Stadium", "2026-10-01", "2026-10-12", 200000, {}),
    ("SHANGHAI", "China International Import Expo 2026", "fair", "NECC", "2026-11-05", "2026-11-10", 400000, {}),
    ("SHANGHAI", "Formula 1 Chinese Grand Prix 2026", "sports", "Shanghai International Circuit", "2026-03-13", "2026-03-15", 220000, {}),
    ("BEIJING", "China Open 2026", "sports", "National Tennis Center", "2026-09-23", "2026-10-05", 300000, {}),
    ("BEIJING", "Beijing Marathon 2026", "marathon", "Tiananmen - Olympic Park", "2026-10-25", "2026-10-25", 30000, {}),
    ("BEIJING", "Auto China 2026", "fair", "China International Exhibition Center", "2026-04-24", "2026-05-03", 850000, {}),
    ("CHENGDU", "The World Games 2025", "sports", "Chengdu", "2025-08-07", "2025-08-17", 500000, {}),
    ("CHENGDU", "Chengdu Marathon 2026", "marathon", "Jincheng Park", "2026-10-25", "2026-10-25", 35000, {}),
    ("HONGKONG", "Art Basel Hong Kong 2026", "art_fair", "HKCEC", "2026-03-27", "2026-03-29", 90000, {}),
    ("HONGKONG", "Hong Kong Sevens 2026", "sports", "Kai Tak Stadium", "2026-03-27", "2026-03-29", 120000, {}),
    ("HONGKONG", "Hong Kong Wine & Dine Festival 2026", "food", "Central Harbourfront", "2026-10-22", "2026-10-25", 150000, {}),
    ("HONGKONG", "Clockenflap 2026", "concert", "Central Harbourfront", "2026-12-04", "2026-12-06", 80000, {}),
    ("TAIPEI", "Taipei Marathon 2026", "marathon", "Taipei City Hall Plaza", "2026-12-20", "2026-12-20", 28000, {}),
    ("TAIPEI", "Computex 2026", "fair", "Nangang Exhibition Center", "2026-06-02", "2026-06-05", 85000, {}),
    ("SINGAPORE", "Formula 1 Singapore Airlines Singapore Grand Prix 2026", "sports", "Marina Bay Street Circuit", "2026-10-09", "2026-10-11", 300000,
     {"race_start_utc": "2026-10-11T12:00:00Z"}),
    ("SINGAPORE", "Formula 1 Singapore Grand Prix 2025", "sports", "Marina Bay Street Circuit", "2025-10-03", "2025-10-05", 300000, {}),
    ("SINGAPORE", "Singapore Art Week 2026", "art_fair", "various", "2026-01-15", "2026-01-24", 300000, {}),
    ("SINGAPORE", "Standard Chartered Singapore Marathon 2026", "marathon", "Marina Bay", "2026-12-05", "2026-12-06", 50000, {}),
    ("SYDNEY", "Vivid Sydney 2026", "festival", "Circular Quay / Darling Harbour", "2026-05-22", "2026-06-13", 3000000, {}),
    ("SYDNEY", "TCS Sydney Marathon 2026", "marathon", "North Sydney - Opera House", "2026-08-30", "2026-08-30", 35000, {}),
    ("SYDNEY", "Sculpture by the Sea, Bondi 2026", "exhibition", "Bondi - Tamarama", "2026-10-22", "2026-11-08", 450000, {}),
    ("SYDNEY", "Sydney Gay and Lesbian Mardi Gras 2026", "festival", "Oxford St", "2026-02-28", "2026-02-28", 300000, {}),
]

VENUES = {
    "MILANO": ["Unipol Forum", "Ippodromo SNAI San Siro", "Fabrique", "Teatro alla Scala", "Alcatraz"], "ROMA": ["Palazzo dello Sport", "Stadio Olimpico", "Auditorium Parco della Musica"],
    "VENEZIA": ["Teatro La Fenice", "Palazzo Grassi"], "COURMAYEUR": ["Skyway Monte Bianco"], "CORTINA": ["Stadio Olimpico del Ghiaccio"],
    "PARIS": ["Accor Arena", "Stade de France", "Olympia", "Zénith Paris", "Parc des Princes", "Philharmonie"], "CANNES": ["Palais des Festivals"],
    "GENEVE": ["Arena de Genève", "Victoria Hall", "Stade de Genève"], "LONDON": ["The O2", "Wembley Stadium", "Royal Albert Hall", "OVO Arena Wembley", "Emirates Stadium", "Stamford Bridge"],
    "MUENCHEN": ["Olympiahalle", "Allianz Arena", "Zenith", "Isarphilharmonie"], "BERLIN": ["Uber Arena", "Olympiastadion", "Columbiahalle", "Philharmonie Berlin"],
    "ZUERICH": ["Hallenstadion", "Letzigrund", "Tonhalle"], "STMORITZ": ["Kulm Hotel"], "MADRID": ["Movistar Arena", "Santiago Bernabéu", "WiZink Center", "Riyadh Air Metropolitano"],
    "AMSTERDAM": ["Ziggo Dome", "Johan Cruijff ArenA", "AFAS Live", "Concertgebouw"], "KOBENHAVN": ["Royal Arena", "Parken", "K.B. Hallen"],
    "DUBAI": ["Coca-Cola Arena", "Dubai Opera", "Expo City"], "NEWYORK": ["Madison Square Garden", "Barclays Center", "Yankee Stadium", "Radio City Music Hall", "Carnegie Hall"],
    "MIAMI": ["Kaseya Center", "loanDepot park", "Fillmore Miami Beach"], "BEVERLYHILLS": ["Hollywood Bowl", "Crypto.com Arena", "The Wallis", "Kia Forum"],
    "ASPEN": ["Belly Up Aspen", "Wheeler Opera House"], "TORONTO": ["Scotiabank Arena", "Rogers Centre", "Massey Hall", "Budweiser Stage"],
    "TOKYO": ["Tokyo Dome", "Nippon Budokan", "Ariake Arena", "Saitama Super Arena", "Zepp Haneda"], "OSAKA": ["Kyocera Dome Osaka", "Osaka-jo Hall", "Zepp Osaka Bayside"],
    "SEOUL": ["KSPO Dome", "Gocheok Sky Dome", "Jamsil Arena", "Blue Square", "Seoul World Cup Stadium"], "BUSAN": ["BEXCO Auditorium", "Busan Asiad Stadium"],
    "SHANGHAI": ["Mercedes-Benz Arena", "Shanghai Stadium", "Shanghai Grand Theatre"], "BEIJING": ["Cadillac Arena", "Workers' Stadium", "National Centre for the Performing Arts"],
    "CHENGDU": ["Phoenix Hill Sports Park", "Chengdu Financial City Performing Arts Centre"], "HONGKONG": ["AsiaWorld-Arena", "Hong Kong Coliseum", "Kai Tak Stadium"],
    "TAIPEI": ["Taipei Arena", "Taipei Dome", "Taipei Music Center"], "SINGAPORE": ["Singapore Indoor Stadium", "National Stadium", "Esplanade"],
    "SYDNEY": ["Qudos Bank Arena", "Sydney Opera House", "Accor Stadium", "ICC Sydney"]}
SIZE = {"MILANO": 6, "ROMA": 5, "VENEZIA": 2, "COURMAYEUR": 0.3, "CORTINA": 0.4, "PARIS": 9, "CANNES": 1.5, "GENEVE": 2, "LONDON": 10, "MUENCHEN": 5,
        "BERLIN": 7, "ZUERICH": 3, "STMORITZ": 0.4, "MADRID": 6, "AMSTERDAM": 4, "KOBENHAVN": 3, "DUBAI": 5, "NEWYORK": 10, "MIAMI": 4, "BEVERLYHILLS": 6,
        "ASPEN": 0.6, "TORONTO": 5, "TOKYO": 10, "OSAKA": 5, "SEOUL": 8, "BUSAN": 3, "SHANGHAI": 7, "BEIJING": 6, "CHENGDU": 4, "HONGKONG": 5,
        "TAIPEI": 4, "SINGAPORE": 5, "SYDNEY": 5}
SYL = ["Nova", "Lune", "Velvet", "Ember", "Kite", "Arlo", "Mira", "Juno", "Sable", "Orion", "Cass", "Rumi", "Tove", "Echo", "Pax", "Indigo", "Saffi", "Vale"]
SUF = ["& The Static", "Collective", "Quartet", "", "", "", " Live", " Trio", " (DJ set)", " Orchestra"]
SPORT = {"MILANO": ["Inter vs {}", "AC Milan vs {}"], "ROMA": ["AS Roma vs {}", "SS Lazio vs {}"], "PARIS": ["Paris SG vs {}"], "LONDON": ["Arsenal vs {}", "Chelsea vs {}"],
         "MUENCHEN": ["FC Bayern vs {}"], "BERLIN": ["Hertha BSC vs {}", "Union Berlin vs {}"], "MADRID": ["Real Madrid vs {}", "Atlético vs {}"],
         "AMSTERDAM": ["Ajax vs {}"], "NEWYORK": ["Knicks vs {}", "Yankees vs {}", "Rangers vs {}"], "MIAMI": ["Heat vs {}", "Inter Miami vs {}"],
         "BEVERLYHILLS": ["Lakers vs {}", "Dodgers vs {}"], "TORONTO": ["Maple Leafs vs {}", "Raptors vs {}", "Blue Jays vs {}"], "TOKYO": ["Yomiuri Giants vs {}"],
         "SEOUL": ["FC Seoul vs {}", "LG Twins vs {}"], "SHANGHAI": ["Shanghai Port vs {}"], "BEIJING": ["Beijing Guoan vs {}"], "SYDNEY": ["Sydney Swans vs {}"],
         "GENEVE": ["Servette FC vs {}", "Genève-Servette HC vs {}"], "ZUERICH": ["FC Zürich vs {}", "ZSC Lions vs {}"], "KOBENHAVN": ["FC København vs {}"],
         "OSAKA": ["Hanshin Tigers vs {}"], "HONGKONG": ["Kitchee vs {}"], "DUBAI": ["Al Wasl vs {}"]}
OPP = ["Juventus", "Napoli", "Marseille", "Lyon", "Liverpool", "Dortmund", "Leipzig", "Sevilla", "Valencia", "PSV", "Celtics", "Bulls", "Red Sox", "Canadiens",
       "Hanshin Tigers", "Ulsan HD", "Shandong Taishan", "Collingwood", "Basel", "Young Boys", "Brøndby", "Al Ain", "Tokyo Verdy", "Eastern"]

rng = rng_for("events-feed")
rows = []
eid = 100000


def att_fmt(a, r):
    if a == 0:
        return None
    k = r.random()
    if k < 0.65:
        return a
    if k < 0.8:
        return f"{a:,}"
    if k < 0.9:
        return f"~{round(a / 1000)}k"
    return f"{a / 1e6:.1f}M" if a >= 1e6 else f"{round(a, -3):.0f}+"


for ck, title, cat, venue, a, b, att, extra in MAJOR:
    c = CITIES[ck]
    eid += 1
    status = "completed" if d(b) < d("2026-10-22") else ("ongoing" if d(a) <= d("2026-10-22") else "scheduled")
    rows.append(dict(event_id=f"EVH-{eid}", title=title, category=cat, city=c["name"], country=c["cc"], venue=venue,
                     start_local=f"{a}T{'10:00:00' if cat != 'concert' else '20:00:00'}", end_local=f"{b}T22:00:00", timezone=c["tz"],
                     expected_attendance=att_fmt(att, rng), attendance_basis="organiser estimate (multi-day, cumulative)" if d(b) > d(a) else "organiser estimate",
                     status=status, tier="major", **({"extra": extra} if extra else {})))

# background events
for ck, c in CITIES.items():
    lam = SIZE[ck] * 1.5
    for m in pd.date_range("2024-09-01", "2026-12-01", freq="MS"):
        n = rng.poisson(lam)
        for _ in range(n):
            day = m.date() + TD(int(rng.integers(0, 28)))
            eid += 1
            if ck in SPORT and rng.random() < 0.35:
                title = rng.choice(SPORT[ck]).format(rng.choice(OPP))
                cat, att = "sports", int(rng.integers(12000, 70000))
                venue = rng.choice(VENUES[ck])
            else:
                kind = rng.random()
                if kind < 0.6:
                    title = f"{rng.choice(SYL)}{rng.choice(SYL).lower()}{rng.choice(SUF)} - {rng.choice(['World Tour', 'Live', 'in concert', 'Tour 2026', 'Europe Tour', 'Asia Tour'])}"
                    cat, att = "concert", int(rng.lognormal(8.6, 0.8))
                elif kind < 0.8:
                    title = f"{rng.choice(['Comedy night', 'Musical', 'Ballet', 'Opera', 'Theatre'])}: {rng.choice(SYL)} {rng.choice(['Rising', 'Nights', 'Dreams', 'Story', 'Reloaded'])}"
                    cat, att = "performing_arts", int(rng.lognormal(7.4, 0.6))
                else:
                    title = f"{rng.choice(['Expo', 'Salon', 'Fair', 'Summit', 'Week'])} {rng.choice(['Food', 'Design', 'Wedding', 'Tech', 'Wine', 'Boat', 'Watch', 'Vintage'])} {day.year}"
                    cat, att = "fair", int(rng.lognormal(9.0, 0.9))
                venue = rng.choice(VENUES[ck])
            length = 1 if cat != "fair" else int(rng.integers(2, 5))
            st = "completed" if day < d("2026-10-22") else "scheduled"
            if rng.random() < 0.02:
                st = "cancelled"
            rows.append(dict(event_id=f"EVH-{eid}", title=title, category=cat, city=c["name"], country=c["cc"], venue=venue,
                             start_local=f"{day.isoformat()}T{int(rng.integers(18, 21))}:{rng.choice(['00', '30'])}:00",
                             end_local=f"{(day + TD(length - 1)).isoformat()}T23:00:00", timezone=c["tz"],
                             expected_attendance=att_fmt(att, rng), attendance_basis="venue capacity" if rng.random() < 0.5 else "tickets sold",
                             status=st, tier="regular"))

# scenario-specific edits / quirks
rows.append(dict(event_id="EVH-990017", title="Harbourfront Mid-Autumn Lantern Carnival - DAY 1", category="festival", city="Hong Kong", country="HK",
                 venue="Central Harbourfront Event Space", start_local="2026-09-17T18:00:00", end_local="2026-09-17T23:00:00", timezone="Asia/Hong_Kong",
                 expected_attendance=40000, attendance_basis="organiser estimate", status="cancelled",
                 extra={"status_reason": "Tropical cyclone warning signal No. 8", "status_updated": "2026-09-16T21:05:00+08:00"}))
rows.append(dict(event_id="EVH-990018", title="Konzert im Englischen Garten (Open Air)", category="concert", city="München", country="DE",
                 venue="Englischer Garten", start_local="2026-10-14T19:00:00", end_local="2026-10-14T22:00:00", timezone="Europe/Berlin",
                 expected_attendance=6000, attendance_basis="tickets sold", status="postponed",
                 extra={"status_reason": "Wetter / Schneefall", "new_date": "2027-05-15"}))
# duplicate of TIFF from a partner sync with different id and UTC timestamps
rows.append(dict(event_id="EVH-P-55120", title="TIFF 2026 (Toronto Int'l Film Fest)", category="film", city="Toronto", country="CA", venue="Various",
                 start_local="2026-09-10T13:00:00Z", end_local="2026-09-21T03:59:00Z", timezone="UTC", expected_attendance="450k",
                 attendance_basis="partner feed", status="completed", tier="major"))
rng.shuffle(rows)
write_json(E / "eventhub_global_feed.json", {"source": "EventHub aggregator API v3", "generated_at": "2026-10-22T05:00:12Z", "page": 1, "pages": 1,
                                            "count": len(rows), "events": rows}, indent=None)

# ---------------------------------------------------------------------------------------------- Asia aggregator (CSV, local language)
ASIA = [
    ("서울", "KR", "서울패션위크 2027 S/S", "패션", "DDP 동대문디자인플라자", "2026.09.01", "2026.09.05", "6만"),
    ("서울", "KR", "프리즈 서울 & 키아프 2026", "전시", "코엑스", "2026.09.02", "2026.09.05", "8만"),
    ("서울", "KR", "노스피크(Northpeak) 청담 팝업스토어", "팝업", "서울 강남구 청담동", "2026.10.15", "2026.11.15", ""),
    ("서울", "KR", "루미에르(LUMIERE) 1st WORLD TOUR [PRISM] IN SEOUL", "콘서트", "KSPO DOME", "2026.11.14", "2026.11.15", "3만"),
    ("서울", "KR", "2026 JTBC 서울마라톤", "마라톤", "상암 월드컵공원", "2026.11.01", "2026.11.01", "37,000"),
    ("서울", "KR", "2026 서울빛초롱축제", "축제", "청계천", "2026.11.06", "2026.11.22", "250만"),
    ("부산", "KR", "제31회 부산국제영화제", "영화제", "영화의전당", "2026.10.02", "2026.10.11", "16만"),
    ("부산", "KR", "제21회 부산불꽃축제", "축제", "광안리해수욕장", "2026.11.07", "2026.11.07", "100만"),
    ("부산", "KR", "지스타 2026", "전시", "벡스코", "2026.11.12", "2026.11.15", "20만"),
    ("東京", "JP", "第39回東京国際映画祭", "映画祭", "日比谷・銀座エリア", "2026/10/26", "2026/11/4", "7万人"),
    ("東京", "JP", "東京ゲームショウ2026", "展示会", "幕張メッセ", "2026/9/17", "2026/9/21", "26万人"),
    ("東京", "JP", "LUMIERE 1st WORLD TOUR 'PRISM' in JAPAN", "コンサート", "東京ドーム", "2026/11/28", "2026/11/29", "10万人"),
    ("東京", "JP", "楽天 Fashion Week TOKYO 2027 S/S", "ファッション", "渋谷ヒカリエ ほか", "2026/8/31", "2026/9/5", ""),
    ("大阪", "JP", "御堂筋ランウェイ2026", "イベント", "御堂筋", "2026/10/25", "2026/10/25", "30万人"),
    ("上海", "CN", "上海时装周 2027春夏", "时装周", "新天地", "2026-10-09", "2026-10-16", "7万"),
    ("上海", "CN", "2026劳力士上海大师赛", "体育", "旗忠网球中心", "2026-10-01", "2026-10-12", "20万"),
    ("上海", "CN", "第九届中国国际进口博览会", "展会", "国家会展中心(上海)", "2026-11-05", "2026-11-10", "40万"),
    ("上海", "CN", "天猫双11全球狂欢季 预售启动", "电商", "线上", "2026-10-20", "2026-11-11", ""),
    ("北京", "CN", "2026中国网球公开赛", "体育", "国家网球中心", "2026-09-23", "2026-10-05", "30万"),
    ("北京", "CN", "2026北京马拉松", "马拉松", "天安门广场", "2026-10-25", "2026-10-25", "3万"),
    ("成都", "CN", "2026成都马拉松", "马拉松", "金城公园", "2026-10-25", "2026-10-25", "3.5万"),
    ("成都", "CN", "成都国际车展 2026", "展会", "西部国际博览城", "2026-08-28", "2026-09-06", "90万"),
    ("香港", "HK", "香港美酒佳餚巡禮 2026", "美食", "中環海濱活動空間", "2026-10-22", "2026-10-25", "15萬"),
    ("香港", "HK", "中秋綵燈會（中環海濱）", "節慶", "中環海濱", "2026-09-17", "2026-09-27", "4萬/日"),
    ("台北", "TW", "2026臺北馬拉松", "馬拉松", "臺北市政府市民廣場", "2026-12-20", "2026-12-20", "2.8萬"),
    ("台北", "TW", "國慶焰火（臺北場）", "節慶", "大佳河濱公園", "2026-10-10", "2026-10-10", "30萬"),
    ("Singapore", "SG", "Formula 1 Singapore Grand Prix 2026", "Sports", "Marina Bay Street Circuit", "09/10/2026", "11/10/2026", "300,000"),
    ("Singapore", "SG", "Deepavali Light-Up 2026 (Little India)", "Festival", "Serangoon Road", "26/09/2026", "15/11/2026", ""),
    ("Singapore", "SG", "Singapore Fashion Week 2026", "Fashion", "Raffles City", "22/10/2026", "25/10/2026", "15,000"),
]
with open(E / "asia_ticketing_feed_export.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["no", "city", "country", "title", "genre", "venue", "date_from", "date_to", "expected_visitors", "crawl_ts"])
    for i, r in enumerate(ASIA):
        w.writerow([i + 1, *r, f"2026-10-21 23:{10 + i:02d}:00"])
(E / "README.txt").write_text(
    "eventhub_global_feed.json: global ticketing/listings aggregator. start_local/end_local are local wall-clock time of the venue\n"
    "unless the value ends with 'Z' (UTC; partner-synced records). expected_attendance is free-form (int, '12,000', '~120k', '1.5M').\n"
    "Multi-day attendance is cumulative over the whole event.\n"
    "asia_ticketing_feed_export.csv: crawl of an Asian ticketing/listing portal; dates in the format used by each country site\n"
    "(KR yyyy.mm.dd, JP yyyy/m/d, CN/HK/TW yyyy-mm-dd, SG dd/mm/yyyy); visitor counts in local notation (만 = 10,000, 万/萬 = 10,000).\n",
    encoding="utf-8")
print("events feed done", len(rows))
