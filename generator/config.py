"""Static master data for the synthetic Moncler-like retail world.

Everything here is fictional/synthetic, loosely inspired by public info about the brand.
"""
import datetime as dt

START = dt.date(2024, 9, 1)
END = dt.date(2026, 10, 21)          # last closed business day ("today" is 2026-10-22)
WINDOW_START = dt.date(2026, 8, 1)   # size-level / inventory / POS-line window
EMAIL_START = dt.date(2026, 8, 31)   # store closing emails window

# ---------------------------------------------------------------------------
# Stores
# scale = avg units/day when season index == 1
# hemi: N / S / T (tropical)
# closed_dow: weekdays (0=Mon) the store is normally closed
# ---------------------------------------------------------------------------
STORES = [
    # id, name, type, city, cc, country, region, subregion, lang, tz, ccy, lat, lon, sqm, opened, scale, hemi, closed_dow, manager, deputy
    ("MIL01", "Milano Montenapoleone", "Flagship", "Milano", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 45.4685, 9.1955, 820, "2008-03-14", 70, "N", [], "Giulia Ferrandi", "Marco Pellizzari"),
    ("MIL02", "Milano Rinascente Duomo", "Shop-in-shop", "Milano", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 45.4655, 9.1912, 140, "2015-09-01", 26, "N", [], "Stefano Rocchi", "Ilaria Mancuso"),
    ("ROM01", "Roma Via Condotti", "Boutique", "Roma", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 41.9055, 12.4800, 390, "2011-11-18", 38, "N", [], "Alessandra De Santis", "Fabio Cardarelli"),
    ("VEN01", "Venezia San Marco", "Boutique", "Venezia", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 45.4337, 12.3363, 210, "2013-04-05", 24, "N", [], "Chiara Zennaro", "Luca Boscolo"),
    ("COU01", "Courmayeur", "Resort", "Courmayeur", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 45.7969, 6.9690, 160, "2010-12-03", 22, "N", [], "Paolo Bertholin", "Elisa Vuillermoz"),
    ("CRT01", "Cortina d'Ampezzo", "Resort", "Cortina d'Ampezzo", "IT", "Italy", "EMEA", "Italy", "it", "Europe/Rome", "EUR", 46.5405, 12.1357, 180, "2012-12-07", 20, "N", [], "Martina Menardi", "Davide Dibona"),
    ("PAR01", "Paris Saint-Honoré", "Flagship", "Paris", "FR", "France", "EMEA", "France", "fr", "Europe/Paris", "EUR", 48.8686, 2.3224, 760, "2009-10-01", 64, "N", [6], "Camille Lefèvre", "Thomas Nguyen"),
    ("PAR02", "Paris Galeries Lafayette Haussmann", "Shop-in-shop", "Paris", "FR", "France", "EMEA", "France", "fr", "Europe/Paris", "EUR", 48.8738, 2.3320, 180, "2014-03-20", 42, "N", [], "Sophie Marchand", "Karim Benali"),
    ("CAN01", "Cannes La Croisette", "Boutique", "Cannes", "FR", "France", "EMEA", "France", "fr", "Europe/Paris", "EUR", 43.5503, 7.0225, 230, "2016-06-10", 12, "N", [6], "Laetitia Rossi", "Julien Pastor"),
    ("GVA01", "Genève Rue du Rhône", "Boutique", "Genève", "CH", "Switzerland", "EMEA", "Switzerland", "fr", "Europe/Zurich", "CHF", 46.2033, 6.1478, 260, "2013-09-14", 20, "N", [6], "Nathalie Favre", "Bruno Monnier"),
    ("LON01", "London New Bond Street", "Flagship", "London", "GB", "United Kingdom", "EMEA", "UK", "en", "Europe/London", "GBP", 51.5122, -0.1450, 700, "2010-05-21", 55, "N", [], "Olivia Hartley", "Daniel Okafor"),
    ("LON02", "London Harrods", "Shop-in-shop", "London", "GB", "United Kingdom", "EMEA", "UK", "en", "Europe/London", "GBP", 51.4994, -0.1632, 160, "2012-10-01", 38, "N", [], "Priya Raman", "James Whitcombe"),
    ("MUN01", "München Maximilianstraße", "Boutique", "München", "DE", "Germany", "EMEA", "Germany", "de", "Europe/Berlin", "EUR", 48.1394, 11.5823, 340, "2012-09-28", 30, "N", [6], "Katharina Huber", "Florian Brandl"),
    ("BER01", "Berlin KaDeWe", "Shop-in-shop", "Berlin", "DE", "Germany", "EMEA", "Germany", "de", "Europe/Berlin", "EUR", 52.5016, 13.3411, 130, "2016-10-14", 20, "N", [6], "Jana Schulte", "Mehmet Aydın"),
    ("ZRH01", "Zürich Bahnhofstrasse", "Boutique", "Zürich", "CH", "Switzerland", "EMEA", "Switzerland", "de", "Europe/Zurich", "CHF", 47.3700, 8.5390, 300, "2014-11-07", 24, "N", [6], "Reto Ammann", "Lea Baumgartner"),
    ("STM01", "St. Moritz Via Serlas", "Resort", "St. Moritz", "CH", "Switzerland", "EMEA", "Switzerland", "de", "Europe/Zurich", "CHF", 46.4983, 9.8390, 190, "2011-12-16", 16, "N", [], "Gian-Andrea Caviezel", "Sabrina Gredig"),
    ("MAD01", "Madrid Calle Serrano", "Boutique", "Madrid", "ES", "Spain", "EMEA", "Spain", "es", "Europe/Madrid", "EUR", 40.4260, -3.6870, 310, "2015-11-12", 24, "N", [], "Lucía Fernández Ortega", "Javier Molina"),
    ("AMS01", "Amsterdam P.C. Hooftstraat", "Boutique", "Amsterdam", "NL", "Netherlands", "EMEA", "Benelux", "en", "Europe/Amsterdam", "EUR", 52.3590, 4.8780, 240, "2017-03-03", 18, "N", [], "Sanne de Vries", "Ruben Bakker"),
    ("CPH01", "København Østergade", "Boutique", "København", "DK", "Denmark", "EMEA", "Nordics", "en", "Europe/Copenhagen", "DKK", 55.6790, 12.5800, 220, "2018-09-21", 15, "N", [6], "Mette Kjær", "Anders Holm"),
    ("DXB01", "Dubai Mall Fashion Avenue", "Boutique", "Dubai", "AE", "United Arab Emirates", "EMEA", "Middle East", "en", "Asia/Dubai", "AED", 25.1985, 55.2796, 330, "2014-12-10", 28, "T", [], "Rania Khoury", "Joel Santos"),
    ("NYC01", "New York Madison Avenue", "Flagship", "New York", "US", "United States", "AMERICAS", "USA", "en", "America/New_York", "USD", 40.7680, -73.9660, 650, "2011-09-15", 45, "N", [], "Rebecca Stein", "Marcus Bell"),
    ("NYC02", "New York SoHo", "Boutique", "New York", "US", "United States", "AMERICAS", "USA", "en", "America/New_York", "USD", 40.7240, -74.0010, 420, "2016-11-04", 34, "N", [], "Tyler Brooks", "Ana Gutierrez"),
    ("MIA01", "Miami Design District", "Boutique", "Miami", "US", "United States", "AMERICAS", "USA", "en", "America/New_York", "USD", 25.8130, -80.1930, 280, "2017-12-01", 14, "T", [], "Daniela Restrepo", "Kevin Hall"),
    ("BHS01", "Beverly Hills Rodeo Drive", "Boutique", "Beverly Hills", "US", "United States", "AMERICAS", "USA", "en", "America/Los_Angeles", "USD", 34.0680, -118.4010, 360, "2013-06-14", 22, "N", [], "Jennifer Kim", "Luis Ortega"),
    ("ASP01", "Aspen", "Resort", "Aspen", "US", "United States", "AMERICAS", "USA", "en", "America/Denver", "USD", 39.1890, -106.8180, 210, "2014-12-12", 14, "N", [], "Hannah Novak", "Chris Delgado"),
    ("TOR01", "Toronto Yorkville", "Boutique", "Toronto", "CA", "Canada", "AMERICAS", "Canada", "en", "America/Toronto", "CAD", 43.6710, -79.3930, 300, "2016-10-20", 22, "N", [], "Émilie Gagnon", "Ryan Chen"),
    ("TYO01", "Tokyo Ginza", "Flagship", "Tokyo", "JP", "Japan", "APAC", "Japan", "ja", "Asia/Tokyo", "JPY", 35.6717, 139.7650, 720, "2010-09-10", 58, "N", [], "佐藤 美咲", "田中 健一"),
    ("TYO02", "Tokyo Omotesando", "Boutique", "Tokyo", "JP", "Japan", "APAC", "Japan", "ja", "Asia/Tokyo", "JPY", 35.6655, 139.7120, 380, "2013-03-22", 36, "N", [], "高橋 由香", "伊藤 翔"),
    ("OSA01", "Osaka Shinsaibashi", "Boutique", "Osaka", "JP", "Japan", "APAC", "Japan", "ja", "Asia/Tokyo", "JPY", 34.6740, 135.5010, 340, "2015-04-17", 32, "N", [], "山本 恵", "中村 大輔"),
    ("SEL01", "Seoul Cheongdam Flagship", "Flagship", "Seoul", "KR", "South Korea", "APAC", "Korea", "ko", "Asia/Seoul", "KRW", 37.5245, 127.0470, 690, "2014-08-29", 62, "N", [], "김지현", "박민수"),
    ("SEL02", "Seoul Hyundai Apgujeong", "Shop-in-shop", "Seoul", "KR", "South Korea", "APAC", "Korea", "ko", "Asia/Seoul", "KRW", 37.5272, 127.0280, 170, "2012-02-17", 40, "N", [], "이수진", "최동욱"),
    ("BUS01", "Busan Shinsegae Centum City", "Shop-in-shop", "Busan", "KR", "South Korea", "APAC", "Korea", "ko", "Asia/Seoul", "KRW", 35.1690, 129.1290, 150, "2016-03-11", 26, "N", [], "정은비", "한승우"),
    ("SHA01", "Shanghai Plaza 66", "Flagship", "Shanghai", "CN", "China", "APAC", "Mainland China", "zh-CN", "Asia/Shanghai", "CNY", 31.2290, 121.4550, 610, "2012-11-23", 55, "N", [], "王静", "陈浩"),
    ("BJS01", "Beijing SKP", "Boutique", "Beijing", "CN", "China", "APAC", "Mainland China", "zh-CN", "Asia/Shanghai", "CNY", 39.9090, 116.4810, 420, "2014-09-26", 48, "N", [], "刘洋", "张敏"),
    ("CDU01", "Chengdu Taikoo Li", "Boutique", "Chengdu", "CN", "China", "APAC", "Mainland China", "zh-CN", "Asia/Shanghai", "CNY", 30.6530, 104.0820, 360, "2017-09-15", 34, "N", [], "李娜", "杨帆"),
    ("HKG01", "Hong Kong Canton Road", "Boutique", "Hong Kong", "HK", "Hong Kong SAR", "APAC", "HK/Macau/TW", "zh-HK", "Asia/Hong_Kong", "HKD", 22.2960, 114.1690, 450, "2011-12-02", 36, "T", [], "陳嘉欣 Karen Chan", "黃志明 Ming Wong"),
    ("TPE01", "Taipei 101", "Boutique", "Taipei", "TW", "Taiwan", "APAC", "HK/Macau/TW", "zh-TW", "Asia/Taipei", "TWD", 25.0340, 121.5645, 280, "2015-10-16", 22, "T", [], "林怡君", "吳承恩"),
    ("SIN01", "Singapore Marina Bay Sands", "Boutique", "Singapore", "SG", "Singapore", "APAC", "South-East Asia", "en", "Asia/Singapore", "SGD", 1.2834, 103.8607, 300, "2013-07-26", 24, "T", [], "Grace Tan", "Muhammad Hafiz"),
    ("SYD01", "Sydney Castlereagh Street", "Boutique", "Sydney", "AU", "Australia", "APAC", "Oceania", "en", "Australia/Sydney", "AUD", -33.8690, 151.2080, 260, "2018-04-12", 14, "S", [], "Chloe Mitchell", "Arjun Patel"),
]
STORE_COLS = ["store_id", "store_name", "store_type", "city", "country_code", "country", "region", "subregion",
              "language", "timezone", "currency", "lat", "lon", "sqm", "opening_date", "scale", "hemi",
              "closed_dow", "store_manager", "assistant_manager"]

# Seasonal closures (resort stores): list of (start, end) inclusive periods where closed
SEASONAL_CLOSURES = {
    "COU01": [("2025-04-21", "2025-06-26"), ("2025-09-14", "2025-11-27"), ("2026-04-13", "2026-06-25"), ("2026-09-13", "2026-11-26"), ("2024-09-15", "2024-11-28")],
    "CRT01": [("2025-04-22", "2025-06-12"), ("2025-10-06", "2025-11-27"), ("2026-04-14", "2026-06-11")],  # Oct 2026: weekends only (handled in world.py)
    "STM01": [("2025-04-14", "2025-06-19"), ("2025-10-20", "2025-12-04"), ("2026-04-13", "2026-06-18"), ("2026-10-19", "2026-12-03"), ("2024-10-21", "2024-12-05")],
    "CAN01": [("2025-01-06", "2025-02-28"), ("2026-01-07", "2026-02-27")],
    "ASP01": [("2025-04-14", "2025-05-22"), ("2026-04-13", "2026-05-21")],
}

FX_EUR = {  # local currency per 1 EUR (avg, used for list prices); daily FX is in external data
    "EUR": 1.0, "CHF": 0.94, "GBP": 0.86, "DKK": 7.46, "AED": 4.05, "USD": 1.10, "CAD": 1.51,
    "JPY": 168.0, "KRW": 1530.0, "CNY": 7.95, "HKD": 8.60, "TWD": 35.4, "SGD": 1.47, "AUD": 1.68,
}
PRICE_PREMIUM = {  # retail price list premium vs Italy
    "EUR": 1.0, "CHF": 1.06, "GBP": 1.0, "DKK": 1.05, "AED": 1.08, "USD": 1.06, "CAD": 1.10,
    "JPY": 1.17, "KRW": 1.12, "CNY": 1.20, "HKD": 1.08, "TWD": 1.12, "SGD": 1.08, "AUD": 1.12,
}
ROUNDING = {"EUR": 10, "CHF": 10, "GBP": 10, "DKK": 100, "AED": 50, "USD": 25, "CAD": 25, "JPY": 1000,
            "KRW": 10000, "CNY": 100, "HKD": 100, "TWD": 100, "SGD": 50, "AUD": 50}

# ---------------------------------------------------------------------------
# Colours: code -> (it, en, fr, de, es, ja, ko, zh)
# ---------------------------------------------------------------------------
COLORS = {
    "999": ("nero", "black", "noir", "schwarz", "negro", "ブラック", "블랙", "黑色"),
    "742": ("blu notte", "navy", "bleu marine", "navy", "azul marino", "ネイビー", "네이비", "藏青色"),
    "20D": ("bianco latte", "off-white", "blanc cassé", "offwhite", "blanco roto", "オフホワイト", "오프화이트", "米白色"),
    "034": ("beige", "beige", "beige", "beige", "beige", "ベージュ", "베이지", "米色"),
    "510": ("rosa cipria", "powder pink", "rose poudré", "puderrosa", "rosa empolvado", "パウダーピンク", "인디 핑크", "粉色"),
    "82D": ("verde oliva", "olive", "olive", "oliv", "verde oliva", "オリーブ", "올리브", "橄榄绿"),
    "90X": ("grigio melange", "grey melange", "gris chiné", "grau meliert", "gris jaspeado", "グレー", "그레이", "灰色"),
    "23R": ("marrone cioccolato", "chocolate brown", "marron chocolat", "schokobraun", "marrón chocolate", "ブラウン", "브라운", "巧克力色"),
    "41F": ("rosso", "red", "rouge", "rot", "rojo", "レッド", "레드", "红色"),
    "73A": ("azzurro", "light blue", "bleu ciel", "hellblau", "azul claro", "ライトブルー", "라이트블루", "浅蓝色"),
    "001": ("bianco", "white", "blanc", "weiß", "blanco", "ホワイト", "화이트", "白色"),
}

SIZE_RUNS = {
    "W_OUT": ["00", "0", "1", "2", "3", "4"],
    "M_OUT": ["1", "2", "3", "4", "5", "6", "7"],
    "ALPHA": ["XS", "S", "M", "L", "XL", "XXL"],
    "W_SHOE": ["35", "36", "37", "38", "39", "40", "41"],
    "M_SHOE": ["39", "40", "41", "42", "43", "44", "45", "46"],
    "TU": ["TU"],
}
# base size curves (will be skewed per region)
SIZE_CURVES = {
    "W_OUT": [0.07, 0.22, 0.30, 0.23, 0.12, 0.06],
    "M_OUT": [0.04, 0.14, 0.26, 0.26, 0.17, 0.09, 0.04],
    "ALPHA": [0.05, 0.20, 0.31, 0.25, 0.13, 0.06],
    "W_SHOE": [0.05, 0.13, 0.22, 0.25, 0.20, 0.10, 0.05],
    "M_SHOE": [0.04, 0.09, 0.16, 0.21, 0.21, 0.15, 0.09, 0.05],
    "TU": [1.0],
}

# season groups for seasonality: HEAVY (down/ski/winter acc), MID (knit/vest/sneakers), LIGHT (SS)
# ---------------------------------------------------------------------------
# Styles
# code, name, line, category, subcategory, gender, season, launch, end, price_eur, colors, size_run, pop, sgroup, desc
# season: CO = continuative/carry-over
# ---------------------------------------------------------------------------
STYLES = [
    # --- women outerwear
    ("J20931A00012", "MAIRE", "Collection", "Outerwear", "Short down jacket", "W", "CO", None, None, 1450, ["999", "034", "20D", "742"], "W_OUT", 1.6, "HEAVY", "Giubbotto corto in piumino laqué con cappuccio"),
    ("J20931A00087", "HERMINE", "Collection", "Outerwear", "Long down jacket", "W", "CO", None, None, 2050, ["999", "742", "20D"], "W_OUT", 1.0, "HEAVY", "Piumino lungo sciancrato con cappuccio staccabile"),
    ("J20931A00144", "BADY", "Collection", "Outerwear", "Short down jacket", "W", "CO", None, None, 1350, ["999", "20D", "510"], "W_OUT", 1.3, "HEAVY", "Piumino corto trapuntato a collo alto"),
    ("J20931A00203", "FLAMMETTE", "Collection", "Outerwear", "Long down jacket", "W", "CO", None, None, 1890, ["999", "742"], "W_OUT", 0.8, "HEAVY", "Piumino lungo a trapuntature larghe"),
    ("J20931A00618", "ILVARO", "Collection", "Outerwear", "Cropped down jacket", "W", "FW26", "2026-09-03", None, 1590, ["999", "510", "20D"], "W_OUT", 0.9, "HEAVY", "Piumino cropped boxy, nylon opaco, collo a imbuto"),
    ("J20931A00622", "AMBRINE", "Collection", "Outerwear", "Long down coat", "W", "FW26", "2026-09-03", None, 2290, ["999", "23R"], "W_OUT", 0.7, "HEAVY", "Cappotto lungo in piumino con cintura"),
    ("J20931A00655", "VALLENTE", "Collection", "Outerwear", "Short down jacket", "W", "FW25", "2025-08-28", "2026-03-15", 1490, ["999", "034", "82D"], "W_OUT", 0.9, "HEAVY", "Piumino corto con dettaglio in maglia"),
    ("J20931A00410", "BOUREY", "Collection", "Outerwear", "Short down jacket", "W", "FW24", "2024-08-29", "2025-03-16", 1390, ["999", "742", "41F"], "W_OUT", 0.9, "HEAVY", "Piumino corto lucido"),
    ("J20931A00711", "LAIS", "Collection", "Outerwear", "Rain jacket", "W", "SS25", "2025-01-16", "2025-08-31", 990, ["999", "73A", "034"], "W_OUT", 0.7, "LIGHT", "Giacca antipioggia leggera con cappuccio"),
    ("J20931A00733", "ALBENGA", "Collection", "Outerwear", "Rain jacket", "W", "SS26", "2026-01-15", "2026-08-31", 1050, ["999", "034", "73A"], "W_OUT", 0.7, "LIGHT", "Trench antipioggia in tessuto tecnico"),
    ("J20931A00560", "CHAMBRE", "Collection", "Outerwear", "Down vest", "W", "CO", None, None, 890, ["999", "20D"], "W_OUT", 0.6, "MID", "Gilet in piumino con collo alto"),
    # --- men outerwear
    ("J10911A00034", "MAYA", "Collection", "Outerwear", "Short down jacket", "M", "CO", None, None, 1550, ["999", "742", "82D"], "M_OUT", 1.8, "HEAVY", "Piumino laqué con cappuccio, l'iconico"),
    ("J10911A00088", "MONTCLA", "Collection", "Outerwear", "Short down jacket", "M", "CO", None, None, 1650, ["999", "742"], "M_OUT", 1.1, "HEAVY", "Piumino con cappuccio in nylon opaco"),
    ("J10911A00142", "KARAKORUM", "Collection", "Outerwear", "Short down jacket", "M", "CO", None, None, 1450, ["999", "742", "90X"], "M_OUT", 1.0, "HEAVY", "Piumino in ripstop con cappuccio"),
    ("J10911A00190", "ECRINS", "Collection", "Outerwear", "Short down jacket", "M", "CO", None, None, 1490, ["999"], "M_OUT", 0.7, "HEAVY", "Piumino con collo alto e tasche a toppa"),
    ("J10911A00213", "MONTGENEVRE", "Collection", "Outerwear", "Wool down jacket", "M", "CO", None, None, 1750, ["999", "742", "90X"], "M_OUT", 0.8, "HEAVY", "Piumino in lana con cappuccio"),
    ("J10911A00305", "TIB", "Collection", "Outerwear", "Down vest", "M", "CO", None, None, 990, ["999", "742", "20D"], "M_OUT", 1.0, "MID", "Gilet in piumino laqué"),
    ("J10911A00577", "ARNEB", "Collection", "Outerwear", "Long parka", "M", "FW26", "2026-09-03", None, 2190, ["999", "742"], "M_OUT", 0.7, "HEAVY", "Parka lungo in piumino con cappuccio in pelliccia sintetica"),
    ("J10911A00581", "ROSIERE", "Collection", "Outerwear", "Short down jacket", "M", "FW26", "2026-09-03", None, 1690, ["999", "82D"], "M_OUT", 0.8, "HEAVY", "Piumino corto con inserti in velluto a coste"),
    ("J10911A00499", "LANS", "Collection", "Outerwear", "Short down jacket", "M", "FW25", "2025-08-28", "2026-03-15", 1590, ["999", "742"], "M_OUT", 0.9, "HEAVY", "Piumino con cappuccio a scomparsa"),
    ("J10911A00402", "VEZERE", "Collection", "Outerwear", "Short down jacket", "M", "FW24", "2024-08-29", "2025-03-16", 1490, ["999", "82D"], "M_OUT", 0.9, "HEAVY", "Piumino imbottito con patch logo"),
    ("J10911A00720", "ETIACHE", "Collection", "Outerwear", "Windbreaker", "M", "SS25", "2025-01-16", "2025-08-31", 950, ["999", "742", "73A"], "M_OUT", 0.8, "LIGHT", "Giacca a vento con cappuccio"),
    ("J10911A00745", "MARIN", "Collection", "Outerwear", "Windbreaker", "M", "SS26", "2026-01-15", "2026-08-31", 990, ["999", "742", "001"], "M_OUT", 0.8, "LIGHT", "Giacca leggera idrorepellente"),
    # --- Grenoble (ski)
    ("H20971A00010", "PEYRE", "Grenoble", "Outerwear", "Ski jacket", "M", "CO", None, None, 2250, ["999", "41F"], "M_OUT", 0.5, "HEAVY", "Giacca da sci in GORE-TEX"),
    ("H20981A00020", "VALBOURG", "Grenoble", "Outerwear", "Ski jacket", "W", "CO", None, None, 2150, ["999", "20D"], "W_OUT", 0.5, "HEAVY", "Giacca da sci sciancrata"),
    ("H20971A00055", "CHAMONIX", "Grenoble", "Bottoms", "Ski trousers", "U", "CO", None, None, 990, ["999"], "ALPHA", 0.4, "HEAVY", "Pantaloni da sci imbottiti"),
    # --- Genius capsule FW26 (fictional "Polaris")
    ("G20921A00901", "POLARIS CAPE", "Genius", "Outerwear", "Down cape", "U", "FW26", "2026-09-24", None, 2900, ["999", "001"], "ALPHA", 0.45, "HEAVY", "Moncler Genius Polaris: mantella in piumino oversize"),
    ("G20921A00902", "POLARIS OVERSIZED", "Genius", "Outerwear", "Oversized down jacket", "U", "FW26", "2026-09-24", None, 2400, ["999", "73A"], "ALPHA", 0.5, "HEAVY", "Moncler Genius Polaris: piumino oversize"),
    ("G20921A00903", "POLARIS BALACLAVA", "Genius", "Accessories", "Knit balaclava", "U", "FW26", "2026-09-24", None, 450, ["999", "001"], "TU", 0.5, "HEAVY", "Moncler Genius Polaris: passamontagna in maglia"),
    # --- Knitwear / jersey
    ("I10919B00011", "LOGO CARDIGAN", "Collection", "Knitwear", "Cardigan", "M", "CO", None, None, 790, ["999", "742"], "ALPHA", 1.2, "MID", "Cardigan in lana con patch logo"),
    ("I10919B00042", "TRICOT PADDED CARDIGAN", "Collection", "Knitwear", "Padded cardigan", "M", "CO", None, None, 1150, ["999", "742", "90X"], "ALPHA", 1.0, "MID", "Cardigan in maglia con fronte in piumino"),
    ("I20939C00008", "CABLE KNIT SWEATER", "Collection", "Knitwear", "Sweater", "W", "CO", None, None, 750, ["20D", "999", "034"], "ALPHA", 0.8, "MID", "Maglione a trecce in lana e cashmere"),
    ("I10919C00067", "WOOL TURTLENECK", "Collection", "Knitwear", "Turtleneck", "M", "FW26", "2026-09-03", None, 650, ["999", "742", "23R"], "ALPHA", 0.7, "MID", "Dolcevita in lana vergine"),
    ("I10918G00031", "LOGO HOODIE", "Collection", "Jersey", "Hoodie", "U", "CO", None, None, 590, ["999", "742", "90X"], "ALPHA", 1.3, "MID", "Felpa con cappuccio e logo"),
    ("I10918G00045", "CREWNECK SWEATSHIRT", "Collection", "Jersey", "Sweatshirt", "U", "CO", None, None, 490, ["999", "90X", "001"], "ALPHA", 1.0, "MID", "Felpa girocollo"),
    ("I10918C00012", "LOGO T-SHIRT", "Collection", "Jersey", "T-shirt", "U", "CO", None, None, 350, ["999", "001", "742"], "ALPHA", 1.3, "LIGHT", "T-shirt con patch logo"),
    ("I10918A00034", "POLO", "Collection", "Jersey", "Polo", "M", "CO", None, None, 450, ["999", "742", "001"], "ALPHA", 0.9, "LIGHT", "Polo in piquet con logo tricolore"),
    # --- Footwear
    ("I10914M00061", "TRAILGRIP GTX", "Collection", "Footwear", "Sneakers", "M", "CO", None, None, 690, ["999", "90X"], "M_SHOE", 1.0, "MID", "Sneakers da trail in GORE-TEX"),
    ("I20924M00062", "TRAILGRIP W", "Collection", "Footwear", "Sneakers", "W", "CO", None, None, 690, ["999", "20D"], "W_SHOE", 0.8, "MID", "Sneakers da trail"),
    ("I20924H00080", "INSOLUX", "Collection", "Footwear", "Après-ski boots", "W", "CO", None, None, 890, ["999", "20D"], "W_SHOE", 0.7, "HEAVY", "Doposci imbottiti"),
    # --- Accessories
    ("I10913B00001", "LOGO BEANIE", "Collection", "Accessories", "Beanie", "U", "CO", None, None, 290, ["999", "742", "001", "510"], "TU", 1.4, "HEAVY", "Berretto in lana con patch logo"),
    ("I10913A00004", "CASHMERE SCARF", "Collection", "Accessories", "Scarf", "U", "CO", None, None, 450, ["999", "90X", "034"], "TU", 0.8, "HEAVY", "Sciarpa in cashmere"),
    ("I10913E00007", "TECH GLOVES", "Collection", "Accessories", "Gloves", "U", "CO", None, None, 390, ["999"], "TU", 0.6, "HEAVY", "Guanti imbottiti touch"),
    ("I10913D00012", "LOGO CAP", "Collection", "Accessories", "Baseball cap", "U", "CO", None, None, 270, ["999", "742", "001"], "TU", 0.9, "LIGHT", "Cappellino con logo"),
    ("I10915C00021", "LEGERE BELT BAG", "Collection", "Accessories", "Belt bag", "U", "CO", None, None, 450, ["999"], "TU", 0.7, "MID", "Marsupio in nylon"),
    ("I10915D00030", "MAKAIO BACKPACK", "Collection", "Accessories", "Backpack", "U", "CO", None, None, 690, ["999", "742"], "TU", 0.5, "MID", "Zaino in nylon tecnico"),
]
STYLE_COLS = ["style_code", "style_name", "line", "category", "subcategory", "gender", "season", "launch_date", "end_date",
              "price_eur", "colors", "size_run", "popularity", "season_group", "description_it"]

# Store-group affinities: multipliers on product popularity, keyed by (subregion or store_id) -> {style_name or 'cat:<category>' or 'line:<line>'}
AFFINITY = {
    "Korea": {"MAIRE": 1.4, "BADY": 1.5, "ILVARO": 1.5, "LOGO HOODIE": 1.3, "TIB": 0.8, "line:Grenoble": 0.6},
    "Japan": {"MAYA": 1.3, "MAIRE": 1.2, "LOGO CARDIGAN": 1.3, "TRICOT PADDED CARDIGAN": 1.3, "line:Grenoble": 0.4},
    "Mainland China": {"line:Genius": 2.0, "MAYA": 1.3, "HERMINE": 1.3, "AMBRINE": 1.4, "cat:Footwear": 1.2},
    "HK/Macau/TW": {"cat:Jersey": 1.3, "MAYA": 1.1, "line:Grenoble": 0.4},
    "USA": {"MONTCLA": 1.3, "MAYA": 1.2, "cat:Jersey": 1.2, "line:Genius": 0.7},
    "Canada": {"ARNEB": 1.4, "MONTGENEVRE": 1.3, "line:Grenoble": 1.2},
    "UK": {"MONTCLA": 1.2, "line:Genius": 1.1, "cat:Knitwear": 1.2},
    "Italy": {"MAYA": 1.2, "HERMINE": 1.2, "TIB": 1.3, "CHAMBRE": 1.3},
    "France": {"MAIRE": 1.1, "FLAMMETTE": 1.2, "line:Genius": 0.8},
    "Germany": {"MONTGENEVRE": 1.3, "KARAKORUM": 1.2, "cat:Accessories": 1.2},
    "Switzerland": {"line:Grenoble": 1.6, "cat:Accessories": 1.2},
    "Spain": {"TIB": 1.2, "cat:Jersey": 1.2},
    "Benelux": {"KARAKORUM": 1.3, "cat:Jersey": 1.2},
    "Nordics": {"MONTGENEVRE": 1.3, "ARNEB": 1.3, "cat:Accessories": 1.2},
    "Middle East": {"cat:Jersey": 1.6, "cat:Footwear": 1.4, "LOGO CAP": 1.5, "cat:Knitwear": 0.7},
    "South-East Asia": {"cat:Jersey": 1.5, "cat:Footwear": 1.3, "LOGO CAP": 1.4, "line:Grenoble": 0.2},
    "Oceania": {"cat:Jersey": 1.3, "line:Grenoble": 0.6},
}
RESORT_AFFINITY = {"line:Grenoble": 2.8, "INSOLUX": 2.5, "cat:Accessories": 1.5, "cat:Jersey": 0.7, "line:Genius": 0.5}
