"""Calendars: public holidays (ICS per country 2024-2027, JP as CSV cp932, CN with make-up working days),
school holidays, retail/cultural calendar, fashion weeks."""
import csv
import datetime as dt
import io
import json
import uuid

from dateutil.easter import easter

from common import OUT, d, drange, mkdir, rng_for, write_json

C = mkdir(OUT / "calendars")
YEARS = [2024, 2025, 2026, 2027]
D = dt.date
TD = dt.timedelta


def nth_wd(y, m, wd, n):
    x = D(y, m, 1)
    x += TD(days=(wd - x.weekday()) % 7)
    return x + TD(weeks=n - 1)


def last_wd(y, m, wd):
    x = D(y, m + 1, 1) - TD(days=1) if m < 12 else D(y, 12, 31)
    return x - TD(days=(x.weekday() - wd) % 7)


# --------------------------------------------------------------------------------------- holiday definitions
def h_it(y):
    e = easter(y)
    out = [(D(y, 1, 1), "Capodanno", ""), (D(y, 1, 6), "Epifania", ""), (e, "Pasqua", ""), (e + TD(1), "Lunedì dell'Angelo (Pasquetta)", ""),
           (D(y, 4, 25), "Festa della Liberazione", ""), (D(y, 5, 1), "Festa del Lavoro", ""), (D(y, 6, 2), "Festa della Repubblica", ""),
           (D(y, 8, 15), "Ferragosto / Assunzione", ""), (D(y, 11, 1), "Ognissanti", ""), (D(y, 12, 8), "Immacolata Concezione", ""),
           (D(y, 12, 25), "Natale", ""), (D(y, 12, 26), "Santo Stefano", ""),
           (D(y, 12, 7), "Sant'Ambrogio (patrono Milano)", "IT-MI"), (D(y, 6, 29), "Santi Pietro e Paolo (patroni Roma)", "IT-RM"),
           (D(y, 4, 25), "San Marco (patrono Venezia)", "IT-VE"), (D(y, 11, 21), "Madonna della Salute (festa cittadina, non festivo)", "IT-VE")]
    if y >= 2026:
        out.append((D(y, 10, 4), "San Francesco d'Assisi (festa nazionale dal 2026)", ""))
    return out


def h_fr(y):
    e = easter(y)
    return [(D(y, 1, 1), "Jour de l'an", ""), (e + TD(1), "Lundi de Pâques", ""), (D(y, 5, 1), "Fête du Travail", ""),
            (D(y, 5, 8), "Victoire 1945", ""), (e + TD(39), "Ascension", ""), (e + TD(50), "Lundi de Pentecôte", ""),
            (D(y, 7, 14), "Fête nationale", ""), (D(y, 8, 15), "Assomption", ""), (D(y, 11, 1), "Toussaint", ""),
            (D(y, 11, 11), "Armistice 1918", ""), (D(y, 12, 25), "Noël", "")]


def h_ch(y):
    e = easter(y)
    sep1 = D(y, 9, 1) + TD(days=(6 - D(y, 9, 1).weekday()) % 7)
    return [(D(y, 1, 1), "Neujahr / Nouvel An", ""), (D(y, 1, 2), "Berchtoldstag", "CH-ZH,CH-GR"), (e - TD(2), "Karfreitag / Vendredi saint", ""),
            (e + TD(1), "Ostermontag / Lundi de Pâques", ""), (D(y, 5, 1), "Tag der Arbeit", "CH-ZH"), (e + TD(39), "Auffahrt / Ascension", ""),
            (e + TD(50), "Pfingstmontag / Lundi de Pentecôte", ""), (D(y, 8, 1), "Bundesfeier / Fête nationale", ""),
            (sep1 + TD(4), "Jeûne genevois", "CH-GE"), (D(y, 12, 25), "Weihnachten / Noël", ""), (D(y, 12, 26), "Stephanstag", "CH-ZH,CH-GR"),
            (D(y, 12, 31), "Restauration de la République", "CH-GE")]


def sub_weekend(x):
    return x + TD(days=2) if x.weekday() == 5 else x + TD(days=1) if x.weekday() == 6 else x


def h_gb(y):
    e = easter(y)
    xm, bx = D(y, 12, 25), D(y, 12, 26)
    if xm.weekday() == 5:
        xm_o, bx_o = D(y, 12, 27), D(y, 12, 28)
    elif xm.weekday() == 4:
        xm_o, bx_o = xm, D(y, 12, 28)
    elif xm.weekday() == 6:
        xm_o, bx_o = D(y, 12, 27), D(y, 12, 26)
    else:
        xm_o, bx_o = xm, bx
    return [(sub_weekend(D(y, 1, 1)), "New Year's Day" + (" (substitute day)" if D(y, 1, 1).weekday() >= 5 else ""), ""),
            (e - TD(2), "Good Friday", ""), (e + TD(1), "Easter Monday", ""), (nth_wd(y, 5, 0, 1), "Early May bank holiday", ""),
            (last_wd(y, 5, 0), "Spring bank holiday", ""), (last_wd(y, 8, 0), "Summer bank holiday", ""),
            (xm_o, "Christmas Day" + (" (substitute day)" if xm_o != xm else ""), ""), (bx_o, "Boxing Day" + (" (substitute day)" if bx_o != bx else ""), "")]


def h_de(y):
    e = easter(y)
    return [(D(y, 1, 1), "Neujahr", ""), (D(y, 1, 6), "Heilige Drei Könige", "DE-BY"), (D(y, 3, 8), "Internationaler Frauentag", "DE-BE"),
            (e - TD(2), "Karfreitag", ""), (e + TD(1), "Ostermontag", ""), (D(y, 5, 1), "Tag der Arbeit", ""), (e + TD(39), "Christi Himmelfahrt", ""),
            (e + TD(50), "Pfingstmontag", ""), (e + TD(60), "Fronleichnam", "DE-BY"), (D(y, 8, 15), "Mariä Himmelfahrt", "DE-BY"),
            (D(y, 10, 3), "Tag der Deutschen Einheit", ""), (D(y, 11, 1), "Allerheiligen", "DE-BY"), (D(y, 12, 25), "1. Weihnachtsfeiertag", ""),
            (D(y, 12, 26), "2. Weihnachtsfeiertag", "")]


def h_es(y):
    e = easter(y)
    out = [(D(y, 1, 1), "Año Nuevo", ""), (D(y, 1, 6), "Epifanía del Señor", ""), (e - TD(3), "Jueves Santo", "ES-MD"), (e - TD(2), "Viernes Santo", ""),
           (D(y, 5, 1), "Fiesta del Trabajo", ""), (D(y, 5, 2), "Fiesta de la Comunidad de Madrid", "ES-MD"), (D(y, 5, 15), "San Isidro (Madrid capital)", "ES-MD-MAD"),
           (D(y, 8, 15), "Asunción de la Virgen", ""), (D(y, 10, 12), "Fiesta Nacional de España", ""), (D(y, 11, 1), "Todos los Santos", ""),
           (D(y, 11, 9), "Nuestra Señora de la Almudena (Madrid capital)", "ES-MD-MAD"), (D(y, 12, 6), "Día de la Constitución", ""),
           (D(y, 12, 8), "Inmaculada Concepción", ""), (D(y, 12, 25), "Natividad del Señor", "")]
    if D(y, 11, 1).weekday() == 6:
        out.append((D(y, 11, 2), "Lunes siguiente a Todos los Santos", "ES-MD"))
    return out


def h_nl(y):
    e = easter(y)
    kd = D(y, 4, 27) if D(y, 4, 27).weekday() != 6 else D(y, 4, 26)
    return [(D(y, 1, 1), "Nieuwjaarsdag", ""), (e - TD(2), "Goede Vrijdag", ""), (e, "Eerste Paasdag", ""), (e + TD(1), "Tweede Paasdag", ""),
            (kd, "Koningsdag", ""), (D(y, 5, 5), "Bevrijdingsdag", ""), (e + TD(39), "Hemelvaartsdag", ""), (e + TD(49), "Eerste Pinksterdag", ""),
            (e + TD(50), "Tweede Pinksterdag", ""), (D(y, 12, 25), "Eerste Kerstdag", ""), (D(y, 12, 26), "Tweede Kerstdag", "")]


def h_dk(y):
    e = easter(y)
    return [(D(y, 1, 1), "Nytårsdag", ""), (e - TD(3), "Skærtorsdag", ""), (e - TD(2), "Langfredag", ""), (e, "Påskedag", ""),
            (e + TD(1), "2. påskedag", ""), (e + TD(39), "Kristi himmelfartsdag", ""), (e + TD(49), "Pinsedag", ""), (e + TD(50), "2. pinsedag", ""),
            (D(y, 6, 5), "Grundlovsdag", ""), (D(y, 12, 24), "Juleaftensdag", ""), (D(y, 12, 25), "Juledag", ""), (D(y, 12, 26), "2. juledag", "")]


AE_LUNAR = {2024: dict(fitr=[D(2024, 4, 8), D(2024, 4, 9), D(2024, 4, 10), D(2024, 4, 11), D(2024, 4, 12)], arafat=D(2024, 6, 15),
                       adha=[D(2024, 6, 16), D(2024, 6, 17), D(2024, 6, 18)], hijri=D(2024, 7, 7), mawlid=D(2024, 9, 15)),
            2025: dict(fitr=[D(2025, 3, 30), D(2025, 3, 31), D(2025, 4, 1)], arafat=D(2025, 6, 5), adha=[D(2025, 6, 6), D(2025, 6, 7), D(2025, 6, 8)],
                       hijri=D(2025, 6, 27), mawlid=D(2025, 9, 5)),
            2026: dict(fitr=[D(2026, 3, 20), D(2026, 3, 21), D(2026, 3, 22)], arafat=D(2026, 5, 26), adha=[D(2026, 5, 27), D(2026, 5, 28), D(2026, 5, 29)],
                       hijri=D(2026, 6, 16), mawlid=D(2026, 8, 25)),
            2027: dict(fitr=[D(2027, 3, 9), D(2027, 3, 10), D(2027, 3, 11)], arafat=D(2027, 5, 15), adha=[D(2027, 5, 16), D(2027, 5, 17), D(2027, 5, 18)],
                       hijri=D(2027, 6, 6), mawlid=D(2027, 8, 14))}


def h_ae(y):
    L = AE_LUNAR[y]
    t = " (tentative, subject to moon sighting)" if y == 2027 else ""
    out = [(D(y, 1, 1), "New Year's Day", "")]
    out += [(x, "Eid Al Fitr holiday" + t, "") for x in L["fitr"]]
    out += [(L["arafat"], "Arafat Day" + t, "")] + [(x, "Eid Al Adha holiday" + t, "") for x in L["adha"]]
    out += [(L["hijri"], "Hijri New Year" + t, ""), (L["mawlid"], "Prophet Muhammad's Birthday" + t, ""),
            (D(y, 12, 1), "Commemoration Day", ""), (D(y, 12, 2), "National Day", ""), (D(y, 12, 3), "National Day holiday", "")]
    return out


def obs_us(x):
    return x - TD(1) if x.weekday() == 5 else x + TD(1) if x.weekday() == 6 else x


def h_us(y):
    out = [(obs_us(D(y, 1, 1)), "New Year's Day", ""), (nth_wd(y, 1, 0, 3), "Martin Luther King Jr. Day", ""),
           (nth_wd(y, 2, 0, 3), "Washington's Birthday", ""), (last_wd(y, 5, 0), "Memorial Day", ""), (obs_us(D(y, 6, 19)), "Juneteenth National Independence Day", ""),
           (obs_us(D(y, 7, 4)), "Independence Day" + (" (observed)" if D(y, 7, 4).weekday() >= 5 else ""), ""), (nth_wd(y, 9, 0, 1), "Labor Day", ""),
           (nth_wd(y, 10, 0, 2), "Columbus Day", ""), (obs_us(D(y, 11, 11)), "Veterans Day", ""), (nth_wd(y, 11, 3, 4), "Thanksgiving Day", ""),
           (obs_us(D(y, 12, 25)), "Christmas Day", "")]
    # non-holiday observances included by the vendor feed
    out += [(D(y, 10, 31), "Halloween [observance]", ""), (nth_wd(y, 11, 3, 4) + TD(1), "Black Friday [observance]", ""),
            (D(y, 2, 14), "Valentine's Day [observance]", ""), (nth_wd(y, 5, 6, 2), "Mother's Day [observance]", "")]
    return out


def h_ca(y):
    e = easter(y)
    vic = D(y, 5, 24) - TD(days=D(y, 5, 24).weekday())
    return [(D(y, 1, 1), "New Year's Day", ""), (nth_wd(y, 2, 0, 3), "Family Day", "CA-ON"), (e - TD(2), "Good Friday", ""),
            (vic, "Victoria Day", ""), (D(y, 7, 1), "Canada Day", ""), (nth_wd(y, 8, 0, 1), "Civic Holiday", "CA-ON"),
            (nth_wd(y, 9, 0, 1), "Labour Day", ""), (D(y, 9, 30), "National Day for Truth and Reconciliation", "federal"),
            (nth_wd(y, 10, 0, 2), "Thanksgiving", ""), (D(y, 11, 11), "Remembrance Day", "federal"), (D(y, 12, 25), "Christmas Day", ""),
            (D(y, 12, 26), "Boxing Day", "")]


def h_jp(y):
    eq_spring = {2024: 20, 2025: 20, 2026: 20, 2027: 21}[y]
    eq_aut = {2024: 22, 2025: 23, 2026: 23, 2027: 23}[y]
    base = [(D(y, 1, 1), "元日"), (nth_wd(y, 1, 0, 2), "成人の日"), (D(y, 2, 11), "建国記念の日"), (D(y, 2, 23), "天皇誕生日"),
            (D(y, 3, eq_spring), "春分の日"), (D(y, 4, 29), "昭和の日"), (D(y, 5, 3), "憲法記念日"), (D(y, 5, 4), "みどりの日"),
            (D(y, 5, 5), "こどもの日"), (nth_wd(y, 7, 0, 3), "海の日"), (D(y, 8, 11), "山の日"), (nth_wd(y, 9, 0, 3), "敬老の日"),
            (D(y, 9, eq_aut), "秋分の日"), (nth_wd(y, 10, 0, 2), "スポーツの日"), (D(y, 11, 3), "文化の日"), (D(y, 11, 23), "勤労感謝の日")]
    days = {x: n for x, n in base}
    for x, n in sorted(base):
        if x.weekday() == 6:
            s = x + TD(1)
            while s in days:
                s += TD(1)
            days[s] = "休日"
    for x in sorted(list(days)):
        mid = x + TD(1)
        if mid not in days and (x + TD(2)) in days and mid.weekday() != 6:
            days[mid] = "休日"
    return [(x, n, "") for x, n in sorted(days.items())]


KR_LUNAR = {2024: dict(seol=[D(2024, 2, 9), D(2024, 2, 10), D(2024, 2, 11)], buddha=D(2024, 5, 15), chu=[D(2024, 9, 16), D(2024, 9, 17), D(2024, 9, 18)]),
            2025: dict(seol=[D(2025, 1, 28), D(2025, 1, 29), D(2025, 1, 30)], buddha=D(2025, 5, 5), chu=[D(2025, 10, 5), D(2025, 10, 6), D(2025, 10, 7)]),
            2026: dict(seol=[D(2026, 2, 16), D(2026, 2, 17), D(2026, 2, 18)], buddha=D(2026, 5, 24), chu=[D(2026, 9, 24), D(2026, 9, 25), D(2026, 9, 26)]),
            2027: dict(seol=[D(2027, 2, 6), D(2027, 2, 7), D(2027, 2, 8)], buddha=D(2027, 5, 13), chu=[D(2027, 9, 14), D(2027, 9, 15), D(2027, 9, 16)])}
KR_EXTRA = {2024: [(D(2024, 2, 12), "대체공휴일(설날)"), (D(2024, 5, 6), "대체공휴일(어린이날)"), (D(2024, 4, 10), "제22대 국회의원선거일"), (D(2024, 10, 1), "국군의 날 (임시공휴일)")],
            2025: [(D(2025, 1, 27), "임시공휴일"), (D(2025, 3, 3), "대체공휴일(삼일절)"), (D(2025, 5, 6), "대체공휴일(어린이날·부처님오신날)"),
                   (D(2025, 6, 3), "제21대 대통령선거일"), (D(2025, 10, 8), "대체공휴일(추석)")],
            2026: [(D(2026, 3, 2), "대체공휴일(삼일절)"), (D(2026, 5, 25), "대체공휴일(부처님오신날)"), (D(2026, 6, 3), "제9회 전국동시지방선거일"),
                   (D(2026, 8, 17), "대체공휴일(광복절)"), (D(2026, 10, 5), "대체공휴일(개천절)")],
            2027: [(D(2027, 2, 9), "대체공휴일(설날)"), (D(2027, 8, 16), "대체공휴일(광복절)"), (D(2027, 10, 4), "대체공휴일(개천절)"),
                   (D(2027, 10, 11), "대체공휴일(한글날)"), (D(2027, 12, 27), "대체공휴일(기독탄신일)")]}


def h_kr(y):
    L = KR_LUNAR[y]
    out = [(D(y, 1, 1), "1월1일", "")] + [(x, "설날", "") for x in L["seol"]] + [(D(y, 3, 1), "삼일절", ""), (D(y, 5, 5), "어린이날", ""),
                                                                             (L["buddha"], "부처님오신날", ""), (D(y, 6, 6), "현충일", ""), (D(y, 8, 15), "광복절", "")]
    out += [(x, "추석", "") for x in L["chu"]] + [(D(y, 10, 3), "개천절", ""), (D(y, 10, 9), "한글날", ""), (D(y, 12, 25), "기독탄신일", "")]
    out += [(x, n, "") for x, n in KR_EXTRA[y]]
    return out


CN = {2024: dict(hol=[("元旦", [D(2024, 1, 1)]), ("春节", drange("2024-02-10", "2024-02-17")), ("清明节", drange("2024-04-04", "2024-04-06")),
                      ("劳动节", drange("2024-05-01", "2024-05-05")), ("端午节", [D(2024, 6, 10)]), ("中秋节", drange("2024-09-15", "2024-09-17")),
                      ("国庆节", drange("2024-10-01", "2024-10-07"))],
                 work=[D(2024, 2, 4), D(2024, 2, 18), D(2024, 4, 7), D(2024, 4, 28), D(2024, 5, 11), D(2024, 9, 14), D(2024, 9, 29), D(2024, 10, 12)]),
      2025: dict(hol=[("元旦", [D(2025, 1, 1)]), ("春节", drange("2025-01-28", "2025-02-04")), ("清明节", drange("2025-04-04", "2025-04-06")),
                      ("劳动节", drange("2025-05-01", "2025-05-05")), ("端午节", drange("2025-05-31", "2025-06-02")), ("国庆节、中秋节", drange("2025-10-01", "2025-10-08"))],
                 work=[D(2025, 1, 26), D(2025, 2, 8), D(2025, 4, 27), D(2025, 9, 28), D(2025, 10, 11)]),
      2026: dict(hol=[("元旦", drange("2026-01-01", "2026-01-03")), ("春节", drange("2026-02-15", "2026-02-23")), ("清明节", drange("2026-04-04", "2026-04-06")),
                      ("劳动节", drange("2026-05-01", "2026-05-05")), ("端午节", drange("2026-06-19", "2026-06-21")), ("中秋节", drange("2026-09-25", "2026-09-27")),
                      ("国庆节", drange("2026-10-01", "2026-10-07"))],
                 work=[D(2026, 1, 4), D(2026, 2, 14), D(2026, 2, 28), D(2026, 5, 9), D(2026, 9, 20), D(2026, 10, 10)]),
      2027: dict(hol=[("元旦", [D(2027, 1, 1)]), ("春节", drange("2027-02-06", "2027-02-12")), ("清明节", [D(2027, 4, 5)]), ("劳动节", drange("2027-05-01", "2027-05-05")),
                      ("端午节", [D(2027, 6, 9)]), ("中秋节", [D(2027, 9, 15)]), ("国庆节", drange("2027-10-01", "2027-10-07"))], work=[])}

HK = {2024: [("2024-01-01", "The first day of January"), ("2024-02-10", "Lunar New Year's Day"), ("2024-02-12", "The third day of Lunar New Year"),
             ("2024-02-13", "The fourth day of Lunar New Year"), ("2024-03-29", "Good Friday"), ("2024-03-30", "The day following Good Friday"),
             ("2024-04-01", "Easter Monday"), ("2024-04-04", "Ching Ming Festival"), ("2024-05-01", "Labour Day"), ("2024-05-15", "The Birthday of the Buddha"),
             ("2024-06-10", "Tuen Ng Festival"), ("2024-07-01", "HKSAR Establishment Day"), ("2024-09-18", "The day following the Chinese Mid-Autumn Festival"),
             ("2024-10-01", "National Day"), ("2024-10-11", "Chung Yeung Festival"), ("2024-12-25", "Christmas Day"), ("2024-12-26", "The first weekday after Christmas Day")],
      2025: [("2025-01-01", "The first day of January"), ("2025-01-29", "Lunar New Year's Day"), ("2025-01-30", "The second day of Lunar New Year"),
             ("2025-01-31", "The third day of Lunar New Year"), ("2025-04-04", "Ching Ming Festival"), ("2025-04-18", "Good Friday"),
             ("2025-04-19", "The day following Good Friday"), ("2025-04-21", "Easter Monday"), ("2025-05-01", "Labour Day"), ("2025-05-05", "The Birthday of the Buddha"),
             ("2025-05-31", "Tuen Ng Festival"), ("2025-07-01", "HKSAR Establishment Day"), ("2025-10-01", "National Day"),
             ("2025-10-07", "The day following the Chinese Mid-Autumn Festival"), ("2025-10-29", "Chung Yeung Festival"), ("2025-12-25", "Christmas Day"),
             ("2025-12-26", "The first weekday after Christmas Day")],
      2026: [("2026-01-01", "The first day of January"), ("2026-02-17", "Lunar New Year's Day"), ("2026-02-18", "The second day of Lunar New Year"),
             ("2026-02-19", "The third day of Lunar New Year"), ("2026-04-03", "Good Friday"), ("2026-04-04", "The day following Good Friday"),
             ("2026-04-06", "Easter Monday"), ("2026-04-07", "The day following Ching Ming Festival"), ("2026-05-01", "Labour Day"),
             ("2026-05-25", "The day following the Birthday of the Buddha"), ("2026-06-19", "Tuen Ng Festival"), ("2026-07-01", "HKSAR Establishment Day"),
             ("2026-09-26", "The day following the Chinese Mid-Autumn Festival"), ("2026-10-01", "National Day"),
             ("2026-10-19", "The day following Chung Yeung Festival"), ("2026-12-25", "Christmas Day"), ("2026-12-26", "The first weekday after Christmas Day")],
      2027: [("2027-01-01", "The first day of January"), ("2027-02-06", "Lunar New Year's Day"), ("2027-02-08", "The third day of Lunar New Year"),
             ("2027-02-09", "The fourth day of Lunar New Year"), ("2027-03-26", "Good Friday"), ("2027-03-27", "The day following Good Friday"),
             ("2027-03-29", "Easter Monday"), ("2027-04-05", "Ching Ming Festival"), ("2027-05-01", "Labour Day"), ("2027-05-13", "The Birthday of the Buddha"),
             ("2027-06-09", "Tuen Ng Festival"), ("2027-07-01", "HKSAR Establishment Day"), ("2027-09-16", "The day following the Chinese Mid-Autumn Festival"),
             ("2027-10-01", "National Day"), ("2027-10-08", "Chung Yeung Festival"), ("2027-12-25", "Christmas Day"), ("2027-12-27", "The first weekday after Christmas Day")]}

TW = {2024: [("2024-01-01", "中華民國開國紀念日"), *[(x.isoformat(), "農曆春節") for x in drange("2024-02-08", "2024-02-14")], ("2024-02-28", "和平紀念日"),
             ("2024-04-04", "兒童節及民族掃墓節"), ("2024-04-05", "民族掃墓節"), ("2024-06-10", "端午節"), ("2024-09-17", "中秋節"), ("2024-10-10", "國慶日")],
      2025: [("2025-01-01", "中華民國開國紀念日"), *[(x.isoformat(), "農曆春節") for x in drange("2025-01-25", "2025-02-02")], ("2025-02-28", "和平紀念日"),
             ("2025-04-03", "兒童節補假"), ("2025-04-04", "兒童節及民族掃墓節"), ("2025-05-01", "勞動節"), ("2025-05-30", "端午節補假"), ("2025-05-31", "端午節"),
             ("2025-09-29", "教師節補假"), ("2025-10-06", "中秋節"), ("2025-10-10", "國慶日"), ("2025-10-24", "臺灣光復暨金門古寧頭大捷紀念日補假"),
             ("2025-12-25", "行憲紀念日")],
      2026: [("2026-01-01", "中華民國開國紀念日"), *[(x.isoformat(), "農曆春節") for x in drange("2026-02-14", "2026-02-22")], ("2026-02-27", "和平紀念日補假"),
             ("2026-04-03", "兒童節補假"), ("2026-04-04", "兒童節"), ("2026-04-05", "民族掃墓節"), ("2026-04-06", "民族掃墓節補假"), ("2026-05-01", "勞動節"),
             ("2026-06-19", "端午節"), ("2026-09-25", "中秋節"), ("2026-09-28", "教師節"), ("2026-10-09", "國慶日補假"), ("2026-10-10", "國慶日"),
             ("2026-10-25", "臺灣光復暨金門古寧頭大捷紀念日"), ("2026-10-26", "臺灣光復暨金門古寧頭大捷紀念日補假"), ("2026-12-25", "行憲紀念日")],
      2027: [("2027-01-01", "中華民國開國紀念日"), *[(x.isoformat(), "農曆春節") for x in drange("2027-02-05", "2027-02-10")], ("2027-03-01", "和平紀念日補假"),
             ("2027-04-05", "兒童節及民族掃墓節"), ("2027-05-01", "勞動節"), ("2027-06-09", "端午節"), ("2027-09-15", "中秋節"), ("2027-09-28", "教師節"),
             ("2027-10-10", "國慶日"), ("2027-10-11", "國慶日補假"), ("2027-10-25", "臺灣光復暨金門古寧頭大捷紀念日"), ("2027-12-24", "行憲紀念日補假")]}

SG = {2024: [("2024-01-01", "New Year's Day"), ("2024-02-10", "Chinese New Year"), ("2024-02-11", "Chinese New Year"), ("2024-02-12", "Chinese New Year (observed)"),
             ("2024-03-29", "Good Friday"), ("2024-04-10", "Hari Raya Puasa"), ("2024-05-01", "Labour Day"), ("2024-05-22", "Vesak Day"),
             ("2024-06-17", "Hari Raya Haji"), ("2024-08-09", "National Day"), ("2024-10-31", "Deepavali"), ("2024-12-25", "Christmas Day")],
      2025: [("2025-01-01", "New Year's Day"), ("2025-01-29", "Chinese New Year"), ("2025-01-30", "Chinese New Year"), ("2025-03-31", "Hari Raya Puasa"),
             ("2025-04-18", "Good Friday"), ("2025-05-01", "Labour Day"), ("2025-05-03", "Polling Day"), ("2025-05-12", "Vesak Day"),
             ("2025-06-07", "Hari Raya Haji"), ("2025-08-09", "National Day"), ("2025-10-20", "Deepavali"), ("2025-12-25", "Christmas Day")],
      2026: [("2026-01-01", "New Year's Day"), ("2026-02-17", "Chinese New Year"), ("2026-02-18", "Chinese New Year"), ("2026-03-21", "Hari Raya Puasa"),
             ("2026-04-03", "Good Friday"), ("2026-05-01", "Labour Day"), ("2026-05-27", "Hari Raya Haji"), ("2026-05-31", "Vesak Day"),
             ("2026-06-01", "Vesak Day (observed)"), ("2026-08-09", "National Day"), ("2026-08-10", "National Day (observed)"),
             ("2026-11-08", "Deepavali"), ("2026-11-09", "Deepavali (observed)"), ("2026-12-25", "Christmas Day")],
      2027: [("2027-01-01", "New Year's Day"), ("2027-02-06", "Chinese New Year"), ("2027-02-07", "Chinese New Year"), ("2027-02-08", "Chinese New Year (observed)"),
             ("2027-03-10", "Hari Raya Puasa"), ("2027-03-26", "Good Friday"), ("2027-05-01", "Labour Day"), ("2027-05-17", "Hari Raya Haji"),
             ("2027-05-20", "Vesak Day"), ("2027-08-09", "National Day"), ("2027-10-28", "Deepavali"), ("2027-12-25", "Christmas Day")]}


def h_au(y):
    e = easter(y)
    out = [(sub_weekend(D(y, 1, 1)), "New Year's Day", ""), (sub_weekend(D(y, 1, 26)) if D(y, 1, 26).weekday() >= 5 else D(y, 1, 26), "Australia Day", ""),
           (e - TD(2), "Good Friday", ""), (e - TD(1), "Easter Saturday", ""), (e, "Easter Sunday", ""), (e + TD(1), "Easter Monday", ""),
           (D(y, 4, 25), "Anzac Day", ""), (nth_wd(y, 6, 0, 2), "King's Birthday", ""), (nth_wd(y, 8, 0, 1), "Bank Holiday (banks and some financial institutions)", "AU-NSW"),
           (nth_wd(y, 10, 0, 1), "Labour Day", "AU-NSW")]
    xm, bx = D(y, 12, 25), D(y, 12, 26)
    out.append((xm if xm.weekday() < 5 else xm + TD(2), "Christmas Day" + ("" if xm.weekday() < 5 else " (additional day)"), ""))
    out.append((bx if bx.weekday() < 5 else bx + TD(2), "Boxing Day" + ("" if bx.weekday() < 5 else " (additional day)"), ""))
    return out


FUN = {"IT": h_it, "FR": h_fr, "CH": h_ch, "GB": h_gb, "DE": h_de, "ES": h_es, "NL": h_nl, "DK": h_dk, "AE": h_ae, "US": h_us, "CA": h_ca,
       "KR": h_kr, "AU": h_au}


def all_holidays(cc):
    out = []
    for y in YEARS:
        if cc in FUN:
            out += FUN[cc](y)
        elif cc == "HK":
            out += [(d(a), n, "") for a, n in HK[y]]
        elif cc == "TW":
            out += [(d(a), n, "") for a, n in TW[y]]
        elif cc == "SG":
            out += [(d(a), n, "") for a, n in SG[y]]
        elif cc == "JP":
            out += h_jp(y)
    return sorted(out, key=lambda r: r[0])


def ics(cc, events, calname, prodid, multi=None, tz_hint=None, crlf=True):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{prodid}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{calname}"]
    if tz_hint:
        L.append(f"X-WR-TIMEZONE:{tz_hint}")
    for x, name, sub in events:
        L += ["BEGIN:VEVENT", f"DTSTART;VALUE=DATE:{x.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{(x + TD(1)).strftime('%Y%m%d')}",
              f"DTSTAMP:20261001T060000Z", f"UID:{uuid.uuid5(uuid.NAMESPACE_DNS, cc + x.isoformat() + name)}@holidays.example",
              f"SUMMARY:{name}"]
        if sub:
            L.append(f"DESCRIPTION:Regional holiday ({sub})")
            L.append(f"X-SUBDIVISION:{sub}")
        cat = "Observance" if "[observance]" in name or "non festivo" in name else "Public holiday"
        L += [f"CATEGORIES:{cat}", "TRANSP:TRANSPARENT", "END:VEVENT"]
    for x0, x1, name, cat in (multi or []):
        L += ["BEGIN:VEVENT", f"DTSTART;VALUE=DATE:{x0.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{(x1 + TD(1)).strftime('%Y%m%d')}",
              "DTSTAMP:20261001T060000Z", f"UID:{uuid.uuid5(uuid.NAMESPACE_DNS, cc + x0.isoformat() + name)}@holidays.example", f"SUMMARY:{name}",
              f"CATEGORIES:{cat}", "END:VEVENT"]
    L.append("END:VCALENDAR")
    sep = "\r\n" if crlf else "\n"
    return sep.join(L) + sep


H = mkdir(C / "public_holidays")
NAMES = {"IT": "Italia - Festività", "FR": "Jours fériés France", "CH": "Feiertage Schweiz (ZH/GE/GR)", "GB": "UK bank holidays (England and Wales)",
         "DE": "Feiertage Deutschland (BY/BE)", "ES": "Festivos Madrid", "NL": "Nederlandse feestdagen", "DK": "Helligdage Danmark", "AE": "UAE Public Holidays",
         "US": "US Holidays", "CA": "Canada/Ontario Holidays", "KR": "대한민국 공휴일", "AU": "NSW Public Holidays", "HK": "Hong Kong General Holidays",
         "TW": "中華民國政府行政機關辦公日曆", "SG": "Singapore Public Holidays"}
for cc in ["IT", "FR", "CH", "GB", "DE", "ES", "NL", "DK", "AE", "US", "CA", "KR", "AU", "HK", "TW", "SG"]:
    ev = all_holidays(cc)
    (H / f"{cc}_public_holidays_2024-2027.ics").write_text(ics(cc, ev, NAMES[cc], "-//HolidayFeed//Public Holidays 3.2//EN", crlf=cc != "TW"),
                                                            encoding="utf-8")
# China: ICS with make-up working days (班) as separate events + 2027 tentative
cn_ev, cn_multi = [], []
for y in YEARS:
    for name, days in CN[y]["hol"]:
        tag = "（2027年安排尚未公布，按惯例推算）" if y == 2027 else ""
        cn_multi.append((days[0], days[-1], f"{name} 放假{tag}", "休"))
    for x in CN[y]["work"]:
        cn_multi.append((x, x, "调休上班", "班"))
(H / "CN_public_holidays_2024-2027.ics").write_text(ics("CN", [], "中国法定节假日", "-//cal.example.cn//CN Holidays//ZH", multi=cn_multi,
                                                         tz_hint="Asia/Shanghai"), encoding="utf-8")
# Japan: Cabinet-Office-like CSV, Shift_JIS
lines = ["国民の祝日・休日月日,国民の祝日・休日名称"] + [f"{x.year}/{x.month}/{x.day},{n}" for x, n, _ in all_holidays("JP")]
(H / "syukujitsu_JP.csv").write_bytes(("\r\n".join(lines) + "\r\n").encode("cp932"))
(H / "README.txt").write_text(
    "Public holiday calendars. ICS files: one VEVENT per holiday day (DTEND exclusive), regional holidays flagged with X-SUBDIVISION.\n"
    "CN: multi-day blocks (DTEND exclusive) + '调休上班' make-up working days (CATEGORIES:班 = working day on a weekend).\n"
    "JP: government CSV (Shift_JIS), '休日' = substitute/bridge holiday.\n"
    "Lunar/Islamic dates for 2027 are provisional.\n", encoding="utf-8")

# --------------------------------------------------------------------------------------- school holidays
S = [
    # country, subdivision, name, start, end, school_year, note
    ("IT", "Lombardia", "Vacanze di Natale", "2024-12-23", "2025-01-06", "2024/25", ""), ("IT", "Lombardia", "Carnevale ambrosiano", "2025-03-06", "2025-03-08", "2024/25", ""),
    ("IT", "Lombardia", "Vacanze di Pasqua", "2025-04-17", "2025-04-22", "2024/25", ""), ("IT", "Lombardia", "Vacanze estive", "2025-06-07", "2025-09-11", "2024/25", ""),
    ("IT", "Lombardia", "Vacanze di Natale", "2025-12-22", "2026-01-06", "2025/26", ""), ("IT", "Lombardia", "Carnevale ambrosiano", "2026-02-19", "2026-02-21", "2025/26", ""),
    ("IT", "Lombardia", "Vacanze di Pasqua", "2026-04-02", "2026-04-07", "2025/26", ""), ("IT", "Lombardia", "Vacanze estive", "2026-06-06", "2026-09-13", "2025/26", ""),
    ("IT", "Lombardia", "Vacanze di Natale", "2026-12-23", "2027-01-06", "2026/27", "calendario regionale"),
    ("IT", "Lazio", "Vacanze di Natale", "2024-12-23", "2025-01-06", "2024/25", ""), ("IT", "Lazio", "Vacanze estive", "2025-06-07", "2025-09-14", "2024/25", ""),
    ("IT", "Lazio", "Vacanze di Natale", "2025-12-23", "2026-01-06", "2025/26", ""), ("IT", "Lazio", "Vacanze di Pasqua", "2026-04-02", "2026-04-07", "2025/26", ""),
    ("IT", "Lazio", "Vacanze estive", "2026-06-06", "2026-09-13", "2025/26", ""), ("IT", "Veneto", "Ponte di Ognissanti", "2026-11-01", "2026-11-02", "2026/27", ""),
    ("IT", "Veneto", "Vacanze estive", "2026-06-06", "2026-09-13", "2025/26", ""),
    ("DE", "Bayern", "Herbstferien", "2024-10-28", "2024-10-31", "2024/25", ""), ("DE", "Bayern", "Weihnachtsferien", "2024-12-23", "2025-01-03", "2024/25", ""),
    ("DE", "Bayern", "Frühjahrsferien", "2025-03-03", "2025-03-07", "2024/25", ""), ("DE", "Bayern", "Osterferien", "2025-04-14", "2025-04-25", "2024/25", ""),
    ("DE", "Bayern", "Pfingstferien", "2025-06-10", "2025-06-20", "2024/25", ""), ("DE", "Bayern", "Sommerferien", "2025-08-01", "2025-09-15", "2024/25", ""),
    ("DE", "Bayern", "Herbstferien", "2025-11-03", "2025-11-07", "2025/26", ""), ("DE", "Bayern", "Weihnachtsferien", "2025-12-22", "2026-01-05", "2025/26", ""),
    ("DE", "Bayern", "Frühjahrsferien", "2026-02-16", "2026-02-20", "2025/26", ""), ("DE", "Bayern", "Osterferien", "2026-03-30", "2026-04-10", "2025/26", ""),
    ("DE", "Bayern", "Pfingstferien", "2026-05-26", "2026-06-05", "2025/26", ""), ("DE", "Bayern", "Sommerferien", "2026-08-03", "2026-09-14", "2025/26", ""),
    ("DE", "Bayern", "Herbstferien", "2026-11-02", "2026-11-06", "2026/27", ""), ("DE", "Bayern", "Weihnachtsferien", "2026-12-24", "2027-01-08", "2026/27", ""),
    ("DE", "Berlin", "Herbstferien", "2024-10-21", "2024-11-02", "2024/25", ""), ("DE", "Berlin", "Weihnachtsferien", "2024-12-23", "2024-12-31", "2024/25", ""),
    ("DE", "Berlin", "Winterferien", "2025-02-03", "2025-02-08", "2024/25", ""), ("DE", "Berlin", "Osterferien", "2025-04-14", "2025-04-25", "2024/25", ""),
    ("DE", "Berlin", "Sommerferien", "2025-07-24", "2025-09-06", "2024/25", ""), ("DE", "Berlin", "Herbstferien", "2025-10-20", "2025-11-01", "2025/26", ""),
    ("DE", "Berlin", "Weihnachtsferien", "2025-12-22", "2026-01-02", "2025/26", ""), ("DE", "Berlin", "Winterferien", "2026-02-02", "2026-02-07", "2025/26", ""),
    ("DE", "Berlin", "Osterferien", "2026-03-30", "2026-04-10", "2025/26", ""), ("DE", "Berlin", "Sommerferien", "2026-07-09", "2026-08-22", "2025/26", ""),
    ("DE", "Berlin", "Herbstferien", "2026-10-19", "2026-10-31", "2026/27", ""), ("DE", "Berlin", "Weihnachtsferien", "2026-12-23", "2027-01-02", "2026/27", ""),
    ("CH", "Zürich (Stadt)", "Herbstferien", "2024-10-07", "2024-10-18", "2024/25", ""), ("CH", "Zürich (Stadt)", "Weihnachtsferien", "2024-12-23", "2025-01-03", "2024/25", ""),
    ("CH", "Zürich (Stadt)", "Sportferien", "2025-02-10", "2025-02-21", "2024/25", ""), ("CH", "Zürich (Stadt)", "Frühlingsferien", "2025-04-22", "2025-05-02", "2024/25", ""),
    ("CH", "Zürich (Stadt)", "Sommerferien", "2025-07-14", "2025-08-15", "2024/25", ""), ("CH", "Zürich (Stadt)", "Herbstferien", "2025-10-06", "2025-10-17", "2025/26", ""),
    ("CH", "Zürich (Stadt)", "Weihnachtsferien", "2025-12-22", "2026-01-02", "2025/26", ""), ("CH", "Zürich (Stadt)", "Sportferien", "2026-02-09", "2026-02-20", "2025/26", ""),
    ("CH", "Zürich (Stadt)", "Frühlingsferien", "2026-04-20", "2026-05-01", "2025/26", ""), ("CH", "Zürich (Stadt)", "Sommerferien", "2026-07-13", "2026-08-14", "2025/26", ""),
    ("CH", "Zürich (Stadt)", "Herbstferien", "2026-10-05", "2026-10-16", "2026/27", ""), ("CH", "Zürich (Stadt)", "Weihnachtsferien", "2026-12-24", "2027-01-08", "2026/27", ""),
    ("CH", "Genève", "Vacances d'automne", "2024-10-21", "2024-10-25", "2024/25", ""), ("CH", "Genève", "Vacances de Noël", "2024-12-23", "2025-01-03", "2024/25", ""),
    ("CH", "Genève", "Vacances de février", "2025-02-17", "2025-02-21", "2024/25", ""), ("CH", "Genève", "Vacances de Pâques", "2025-04-14", "2025-04-25", "2024/25", ""),
    ("CH", "Genève", "Vacances d'été", "2025-06-30", "2025-08-22", "2024/25", ""), ("CH", "Genève", "Vacances d'automne", "2025-10-20", "2025-10-24", "2025/26", ""),
    ("CH", "Genève", "Vacances de Noël", "2025-12-22", "2026-01-02", "2025/26", ""), ("CH", "Genève", "Vacances de février", "2026-02-16", "2026-02-20", "2025/26", ""),
    ("CH", "Genève", "Vacances de Pâques", "2026-04-03", "2026-04-17", "2025/26", ""), ("CH", "Genève", "Vacances d'été", "2026-06-29", "2026-08-21", "2025/26", ""),
    ("CH", "Genève", "Vacances d'automne", "2026-10-19", "2026-10-23", "2026/27", ""),
    ("CH", "Graubünden (Oberengadin)", "Herbstferien", "2026-10-03", "2026-10-25", "2026/27", "Gemeindeschule St. Moritz"),
    ("CH", "Graubünden (Oberengadin)", "Herbstferien", "2025-10-04", "2025-10-26", "2025/26", "Gemeindeschule St. Moritz"),
    ("GB", "London", "October half term", "2024-10-28", "2024-11-01", "2024/25", ""), ("GB", "London", "Christmas holidays", "2024-12-23", "2025-01-03", "2024/25", ""),
    ("GB", "London", "February half term", "2025-02-17", "2025-02-21", "2024/25", ""), ("GB", "London", "Easter holidays", "2025-04-07", "2025-04-21", "2024/25", ""),
    ("GB", "London", "May half term", "2025-05-26", "2025-05-30", "2024/25", ""), ("GB", "London", "Summer holidays", "2025-07-23", "2025-09-02", "2024/25", ""),
    ("GB", "London", "October half term", "2025-10-27", "2025-10-31", "2025/26", ""), ("GB", "London", "Christmas holidays", "2025-12-22", "2026-01-02", "2025/26", ""),
    ("GB", "London", "February half term", "2026-02-16", "2026-02-20", "2025/26", ""), ("GB", "London", "Easter holidays", "2026-03-30", "2026-04-10", "2025/26", ""),
    ("GB", "London", "May half term", "2026-05-25", "2026-05-29", "2025/26", ""), ("GB", "London", "Summer holidays", "2026-07-22", "2026-09-01", "2025/26", ""),
    ("GB", "London", "October half term", "2026-10-26", "2026-10-30", "2026/27", ""), ("GB", "London", "Christmas holidays", "2026-12-21", "2027-01-01", "2026/27", ""),
    ("ES", "Comunidad de Madrid", "Navidad", "2024-12-21", "2025-01-07", "2024/25", ""), ("ES", "Comunidad de Madrid", "Semana Santa", "2025-04-11", "2025-04-21", "2024/25", ""),
    ("ES", "Comunidad de Madrid", "Verano", "2025-06-20", "2025-09-07", "2024/25", ""), ("ES", "Comunidad de Madrid", "Navidad", "2025-12-20", "2026-01-07", "2025/26", ""),
    ("ES", "Comunidad de Madrid", "Semana Santa", "2026-03-27", "2026-04-06", "2025/26", ""), ("ES", "Comunidad de Madrid", "Verano", "2026-06-19", "2026-09-07", "2025/26", ""),
    ("ES", "Comunidad de Madrid", "Navidad", "2026-12-19", "2027-01-07", "2026/27", ""),
    ("NL", "Regio Noord", "Herfstvakantie", "2024-10-19", "2024-10-27", "2024/25", ""), ("NL", "Regio Noord", "Kerstvakantie", "2024-12-21", "2025-01-05", "2024/25", ""),
    ("NL", "Regio Noord", "Voorjaarsvakantie", "2025-02-15", "2025-02-23", "2024/25", ""), ("NL", "Regio Noord", "Meivakantie", "2025-04-26", "2025-05-04", "2024/25", ""),
    ("NL", "Regio Noord", "Zomervakantie", "2025-07-12", "2025-08-24", "2024/25", ""), ("NL", "Regio Noord", "Herfstvakantie", "2025-10-18", "2025-10-26", "2025/26", ""),
    ("NL", "Regio Noord", "Kerstvakantie", "2025-12-20", "2026-01-04", "2025/26", ""), ("NL", "Regio Noord", "Voorjaarsvakantie", "2026-02-14", "2026-02-22", "2025/26", ""),
    ("NL", "Regio Noord", "Meivakantie", "2026-04-25", "2026-05-03", "2025/26", ""), ("NL", "Regio Noord", "Zomervakantie", "2026-07-04", "2026-08-16", "2025/26", ""),
    ("NL", "Regio Noord", "Herfstvakantie", "2026-10-17", "2026-10-25", "2026/27", ""), ("NL", "Regio Midden", "Herfstvakantie", "2026-10-10", "2026-10-18", "2026/27", ""),
    ("NL", "Regio Zuid", "Herfstvakantie", "2026-10-17", "2026-10-25", "2026/27", ""),
    ("DK", "København Kommune", "Efterårsferie (uge 42)", "2024-10-12", "2024-10-20", "2024/25", ""), ("DK", "København Kommune", "Juleferie", "2024-12-21", "2025-01-01", "2024/25", ""),
    ("DK", "København Kommune", "Vinterferie (uge 7)", "2025-02-08", "2025-02-16", "2024/25", ""), ("DK", "København Kommune", "Påskeferie", "2025-04-12", "2025-04-21", "2024/25", ""),
    ("DK", "København Kommune", "Sommerferie", "2025-06-28", "2025-08-10", "2024/25", ""), ("DK", "København Kommune", "Efterårsferie (uge 42)", "2025-10-11", "2025-10-19", "2025/26", ""),
    ("DK", "København Kommune", "Juleferie", "2025-12-20", "2026-01-04", "2025/26", ""), ("DK", "København Kommune", "Vinterferie (uge 7)", "2026-02-07", "2026-02-15", "2025/26", ""),
    ("DK", "København Kommune", "Påskeferie", "2026-03-28", "2026-04-06", "2025/26", ""), ("DK", "København Kommune", "Sommerferie", "2026-06-27", "2026-08-09", "2025/26", ""),
    ("DK", "København Kommune", "Efterårsferie (uge 42)", "2026-10-10", "2026-10-18", "2026/27", ""),
    ("AE", "Dubai (MoE/KHDA)", "Mid-term break", "2025-10-13", "2025-10-19", "2025/26", ""), ("AE", "Dubai (MoE/KHDA)", "Winter break", "2025-12-08", "2026-01-04", "2025/26", ""),
    ("AE", "Dubai (MoE/KHDA)", "Spring break", "2026-03-16", "2026-03-29", "2025/26", ""), ("AE", "Dubai (MoE/KHDA)", "Summer break", "2026-07-03", "2026-08-23", "2025/26", ""),
    ("AE", "Dubai (MoE/KHDA)", "Mid-term break", "2026-10-12", "2026-10-18", "2026/27", "provisional"), ("AE", "Dubai (MoE/KHDA)", "Winter break", "2026-12-07", "2027-01-03", "2026/27", "provisional"),
    ("US", "New York City DOE", "Winter recess", "2024-12-24", "2025-01-01", "2024/25", ""), ("US", "New York City DOE", "Midwinter recess", "2025-02-17", "2025-02-21", "2024/25", ""),
    ("US", "New York City DOE", "Spring recess", "2025-04-14", "2025-04-18", "2024/25", ""), ("US", "New York City DOE", "Summer", "2025-06-27", "2025-09-03", "2024/25", ""),
    ("US", "New York City DOE", "Rosh Hashanah (schools closed)", "2025-09-22", "2025-09-23", "2025/26", ""), ("US", "New York City DOE", "Yom Kippur (schools closed)", "2025-10-02", "2025-10-02", "2025/26", ""),
    ("US", "New York City DOE", "Diwali (schools closed)", "2025-10-20", "2025-10-20", "2025/26", ""), ("US", "New York City DOE", "Thanksgiving recess", "2025-11-27", "2025-11-28", "2025/26", ""),
    ("US", "New York City DOE", "Winter recess", "2025-12-24", "2026-01-02", "2025/26", ""), ("US", "New York City DOE", "Midwinter recess", "2026-02-16", "2026-02-20", "2025/26", ""),
    ("US", "New York City DOE", "Spring recess", "2026-04-02", "2026-04-10", "2025/26", ""), ("US", "New York City DOE", "Summer", "2026-06-26", "2026-09-09", "2025/26", ""),
    ("US", "New York City DOE", "Rosh Hashanah (schools closed)", "2026-09-11", "2026-09-14", "2026/27", ""), ("US", "New York City DOE", "Yom Kippur (schools closed)", "2026-09-21", "2026-09-21", "2026/27", ""),
    ("US", "New York City DOE", "Diwali (schools closed)", "2026-11-09", "2026-11-09", "2026/27", ""), ("US", "New York City DOE", "Thanksgiving recess", "2026-11-26", "2026-11-27", "2026/27", ""),
    ("CA", "Toronto DSB", "Winter break", "2024-12-23", "2025-01-03", "2024/25", ""), ("CA", "Toronto DSB", "March break", "2025-03-17", "2025-03-21", "2024/25", ""),
    ("CA", "Toronto DSB", "Summer", "2025-06-27", "2025-09-01", "2024/25", ""), ("CA", "Toronto DSB", "Winter break", "2025-12-22", "2026-01-02", "2025/26", ""),
    ("CA", "Toronto DSB", "March break", "2026-03-16", "2026-03-20", "2025/26", ""), ("CA", "Toronto DSB", "Summer", "2026-06-26", "2026-09-07", "2025/26", ""),
    ("CA", "Toronto DSB", "Winter break", "2026-12-21", "2027-01-01", "2026/27", ""),
    ("JP", "東京都(公立)", "冬休み", "2024-12-25", "2025-01-07", "2024", ""), ("JP", "東京都(公立)", "春休み", "2025-03-25", "2025-04-06", "2024", ""),
    ("JP", "東京都(公立)", "夏休み", "2025-07-19", "2025-08-31", "2025", ""), ("JP", "東京都(公立)", "冬休み", "2025-12-25", "2026-01-07", "2025", ""),
    ("JP", "東京都(公立)", "春休み", "2026-03-25", "2026-04-05", "2025", ""), ("JP", "東京都(公立)", "夏休み", "2026-07-18", "2026-08-31", "2026", ""),
    ("JP", "大阪府(公立)", "夏休み", "2026-07-20", "2026-08-24", "2026", ""), ("JP", "東京都(公立)", "冬休み", "2026-12-25", "2027-01-07", "2026", ""),
    ("KR", "서울특별시교육청", "여름방학", "2025-07-21", "2025-08-17", "2025", ""), ("KR", "서울특별시교육청", "겨울방학", "2025-12-31", "2026-03-01", "2025", ""),
    ("KR", "서울특별시교육청", "여름방학", "2026-07-20", "2026-08-16", "2026", ""), ("KR", "서울특별시교육청", "겨울방학", "2027-01-06", "2027-03-01", "2026", "예정"),
    ("KR", "서울특별시교육청", "겨울방학", "2025-01-03", "2025-03-02", "2024", ""),
    ("CN", "北京市", "寒假", "2025-01-18", "2025-02-16", "2024-2025", ""), ("CN", "北京市", "暑假", "2025-07-05", "2025-08-31", "2024-2025", ""),
    ("CN", "北京市", "寒假", "2026-01-17", "2026-02-22", "2025-2026", ""), ("CN", "北京市", "暑假", "2026-07-04", "2026-08-31", "2025-2026", ""),
    ("CN", "上海市", "寒假", "2026-01-24", "2026-02-28", "2025-2026", ""), ("CN", "上海市", "暑假", "2026-07-01", "2026-08-31", "2025-2026", ""),
    ("CN", "四川省(成都)", "暑假", "2026-07-08", "2026-08-31", "2025-2026", ""),
    ("HK", "EDB", "Christmas and New Year Holidays", "2024-12-23", "2025-01-01", "2024/25", ""), ("HK", "EDB", "Lunar New Year Holidays", "2025-01-27", "2025-02-07", "2024/25", ""),
    ("HK", "EDB", "Easter Holidays", "2025-04-17", "2025-04-26", "2024/25", ""), ("HK", "EDB", "Summer vacation", "2025-07-19", "2025-08-31", "2024/25", ""),
    ("HK", "EDB", "Christmas and New Year Holidays", "2025-12-22", "2026-01-01", "2025/26", ""), ("HK", "EDB", "Lunar New Year Holidays", "2026-02-14", "2026-02-24", "2025/26", ""),
    ("HK", "EDB", "Easter Holidays", "2026-04-02", "2026-04-11", "2025/26", ""), ("HK", "EDB", "Summer vacation", "2026-07-18", "2026-08-31", "2025/26", ""),
    ("TW", "教育部", "寒假", "2025-01-21", "2025-02-10", "113", ""), ("TW", "教育部", "暑假", "2025-07-01", "2025-08-29", "113", ""),
    ("TW", "教育部", "寒假", "2026-01-21", "2026-02-11", "114", ""), ("TW", "教育部", "暑假", "2026-07-01", "2026-08-29", "114", ""),
    ("SG", "MOE", "September holidays", "2024-08-31", "2024-09-08", "2024", ""), ("SG", "MOE", "Year-end holidays", "2024-11-16", "2024-12-31", "2024", ""),
    ("SG", "MOE", "March holidays", "2025-03-15", "2025-03-23", "2025", ""), ("SG", "MOE", "June holidays", "2025-05-31", "2025-06-29", "2025", ""),
    ("SG", "MOE", "September holidays", "2025-09-06", "2025-09-14", "2025", ""), ("SG", "MOE", "Year-end holidays", "2025-11-22", "2025-12-31", "2025", ""),
    ("SG", "MOE", "March holidays", "2026-03-14", "2026-03-22", "2026", ""), ("SG", "MOE", "June holidays", "2026-05-30", "2026-06-28", "2026", ""),
    ("SG", "MOE", "September holidays", "2026-09-05", "2026-09-13", "2026", ""), ("SG", "MOE", "Year-end holidays", "2026-11-21", "2026-12-31", "2026", ""),
    ("AU", "NSW (Eastern division)", "Term 3 holidays (spring)", "2024-09-30", "2024-10-11", "2024", ""), ("AU", "NSW (Eastern division)", "Summer holidays", "2024-12-20", "2025-01-31", "2024", ""),
    ("AU", "NSW (Eastern division)", "Term 1 holidays", "2025-04-14", "2025-04-25", "2025", ""), ("AU", "NSW (Eastern division)", "Term 2 holidays", "2025-07-07", "2025-07-18", "2025", ""),
    ("AU", "NSW (Eastern division)", "Term 3 holidays (spring)", "2025-09-29", "2025-10-10", "2025", ""), ("AU", "NSW (Eastern division)", "Summer holidays", "2025-12-20", "2026-02-01", "2025", ""),
    ("AU", "NSW (Eastern division)", "Term 1 holidays", "2026-04-07", "2026-04-17", "2026", ""), ("AU", "NSW (Eastern division)", "Term 2 holidays", "2026-07-06", "2026-07-17", "2026", ""),
    ("AU", "NSW (Eastern division)", "Term 3 holidays (spring)", "2026-09-28", "2026-10-09", "2026", ""), ("AU", "NSW (Eastern division)", "Summer holidays", "2026-12-18", "2027-01-27", "2026", ""),
]
SH = mkdir(C / "school_holidays")
with open(SH / "school_holidays_aggregated.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["country", "subdivision", "holiday_name", "first_day", "last_day", "school_year", "remarks"])
    for r in S:
        w.writerow(r)
# France: ministry-style file (semicolon, 'fin des cours' / 'reprise' semantics)
FR = [("Vacances de la Toussaint", "2024-10-19", "2024-11-04", "Zones A, B, C"), ("Vacances de Noël", "2024-12-21", "2025-01-06", "Zones A, B, C"),
      ("Vacances d'Hiver", "2025-02-15", "2025-03-03", "Zone C"), ("Vacances d'Hiver", "2025-02-22", "2025-03-10", "Zone B"),
      ("Vacances de Printemps", "2025-04-12", "2025-04-28", "Zone C"), ("Vacances de Printemps", "2025-04-19", "2025-05-05", "Zone B"),
      ("Pont de l'Ascension", "2025-05-28", "2025-06-02", "Zones A, B, C"), ("Vacances d'Été", "2025-07-05", "2025-09-01", "Zones A, B, C"),
      ("Vacances de la Toussaint", "2025-10-18", "2025-11-03", "Zones A, B, C"), ("Vacances de Noël", "2025-12-20", "2026-01-05", "Zones A, B, C"),
      ("Vacances d'Hiver", "2026-02-21", "2026-03-09", "Zone C"), ("Vacances d'Hiver", "2026-02-14", "2026-03-02", "Zone B"),
      ("Vacances de Printemps", "2026-04-18", "2026-05-04", "Zone C"), ("Vacances de Printemps", "2026-04-11", "2026-04-27", "Zone B"),
      ("Pont de l'Ascension", "2026-05-13", "2026-05-18", "Zones A, B, C"), ("Vacances d'Été", "2026-07-04", "2026-09-01", "Zones A, B, C"),
      ("Vacances de la Toussaint", "2026-10-17", "2026-11-02", "Zones A, B, C"), ("Vacances de Noël", "2026-12-19", "2027-01-04", "Zones A, B, C")]
with open(SH / "fr-calendrier-scolaire.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Description", "Population", "Date de début", "Date de fin", "Zones", "annee_scolaire"])
    for name, a, b, z in FR:
        sy = f"{d(a).year}-{d(a).year + 1}" if d(a).month >= 9 else f"{d(a).year - 1}-{d(a).year}"
        w.writerow([name, "-", a + "T00:00:00+01:00" if d(a).month in (10, 11, 12, 1, 2, 3) else a + "T00:00:00+02:00",
                    b + "T00:00:00+01:00" if d(b).month in (10, 11, 12, 1, 2, 3) else b + "T00:00:00+02:00", z, sy])
(SH / "README.txt").write_text("school_holidays_aggregated.csv: first_day/last_day inclusive (days without lessons).\n"
                               "fr-calendrier-scolaire.csv: national open-data layout; 'Date de début' = evening of last school day (fin des cours),\n"
                               "'Date de fin' = day classes resume (reprise). Paris = Zone C, Cannes (Nice académie) = Zone B.\n", encoding="utf-8")

# --------------------------------------------------------------------------------------- retail & cultural calendar
R = []


def add(a, b, name, local, scope, cat, rel, src="RetailCal"):
    R.append([a, b, name, local, scope, cat, rel, src])


for y, gw, sing in ((2024, ("2024-10-01", "2024-10-07"), None), (2025, ("2025-10-01", "2025-10-08"), None), (2026, ("2026-10-01", "2026-10-07"), None)):
    add(*gw, f"China National Day Golden Week {y}", "国庆黄金周", "CN outbound + domestic", "travel_peak", "Chinese outbound tourism peak: Europe, Japan, Korea, HK, SEA")
add("2027-10-01", "2027-10-07", "China National Day Golden Week 2027", "国庆黄金周", "CN outbound + domestic", "travel_peak", "tentative")
for y, a, b in ((2025, "2025-01-28", "2025-02-04"), (2026, "2026-02-15", "2026-02-23"), (2027, "2027-02-06", "2027-02-12")):
    add(a, b, f"Chinese New Year / Spring Festival {y}", "春节", "CN, HK, TW, SG, KR(Seollal), overseas Chinese", "travel_peak", "Gifting before, outbound travel during")
for y, a, b in ((2024, "2024-09-16", "2024-09-18"), (2025, "2025-10-05", "2025-10-08"), (2026, "2026-09-24", "2026-09-26"), (2027, "2027-09-14", "2027-09-16")):
    add(a, b, f"Chuseok {y}", "추석 연휴", "KR", "travel_peak", "Korean outbound travel spike (Japan, Europe) around the holiday")
for y, a, b in ((2025, "2025-04-26", "2025-05-06"), (2026, "2026-04-29", "2026-05-06"), (2027, "2027-04-29", "2027-05-05")):
    add(a, b, f"Golden Week Japan {y}", "ゴールデンウィーク", "JP", "travel_peak", "Japanese domestic/outbound travel")
for y, a in ((2024, "2024-10-31"), (2025, "2025-10-20"), (2026, "2026-11-08"), (2027, "2027-10-29")):
    add(a, a, f"Diwali {y}", "दीपावली", "IN, SG, AE, GB, US diaspora", "cultural", "Gifting/jewellery; Indian travellers to Dubai/London")
for y, a, b in ((2025, "2025-03-01", "2025-03-29"), (2026, "2026-02-18", "2026-03-19"), (2027, "2027-02-08", "2027-03-09")):
    add(a, b, f"Ramadan {y}", "رمضان", "AE, GCC, SG, global Muslim", "religious", "Daytime traffic down, evening malls busy; Eid shopping peak at the end")
for y, a in ((2025, "2025-03-30"), (2026, "2026-03-20"), (2027, "2027-03-09")):
    add(a, (d(a) + TD(3)).isoformat(), f"Eid al-Fitr {y}", "عيد الفطر", "AE, GCC", "religious", "GCC outbound travel (London, Paris, Milan, Geneva)")
for y, a in ((2025, "2025-06-06"), (2026, "2026-05-27"), (2027, "2027-05-16")):
    add(a, (d(a) + TD(3)).isoformat(), f"Eid al-Adha {y}", "عيد الأضحى", "AE, GCC", "religious", "GCC summer travel starts")
for y in (2024, 2025, 2026, 2027):
    add(f"{y}-10-20" if y >= 2025 else f"{y}-10-14", f"{y}-11-11", f"Singles' Day (Double 11) {y} incl. presales", "双十一", "CN e-commerce (Tmall, JD, Douyin)",
        "ecommerce", "Presales start ~Oct 20 (2026: Oct 20 20:00 CST); offline luxury traffic softens; price-match requests")
    add(f"{y}-12-12", f"{y}-12-12", f"Double 12 {y}", "双十二", "CN", "ecommerce", "")
    tg = nth_wd(y, 11, 3, 4)
    add(tg.isoformat(), tg.isoformat(), f"Thanksgiving {y}", "Thanksgiving", "US", "holiday", "")
    add((tg + TD(1)).isoformat(), (tg + TD(4)).isoformat(), f"Black Friday - Cyber Monday {y}", "Black Friday", "US, GB, EU, AU",
        "promo", "Luxury brands mostly do not discount; multibrand/department stores do")
    add(f"{y}-12-26", f"{y}-12-26", f"Boxing Day {y}", "Boxing Day", "GB, CA, AU, HK", "promo", "Sales start (UK dept stores)")
    add(f"{y}-11-11", f"{y}-11-11", f"Pepero Day {y}", "빼빼로데이", "KR", "cultural", "")
    add(f"{y}-03-14", f"{y}-03-14", f"White Day {y}", "ホワイトデー/화이트데이", "JP, KR", "cultural", "") if y > 2024 else None
    add(f"{y}-05-20", f"{y}-05-20", f"520 {y}", "520 网络情人节", "CN", "cultural", "Gifting day") if y > 2024 else None
    add(f"{y}-06-18", f"{y}-06-18", f"618 Shopping Festival {y}", "618", "CN", "ecommerce", "") if y > 2024 else None
for y, a, b in ((2024, "2024-09-21", "2024-10-06"), (2025, "2025-09-20", "2025-10-05"), (2026, "2026-09-19", "2026-10-04"), (2027, "2027-09-18", "2027-10-03")):
    add(a, b, f"Oktoberfest {y}", "Oktoberfest / Wiesn", "München", "event", "~6-7 million visitors; hotel prices peak; tracht not down jackets")
for y, sc, ss in ((2025, ("2025-01-04", "2025-02-28"), ("2025-07-05", "2025-08-31")), (2026, ("2026-01-03", "2026-02-28"), ("2026-07-04", "2026-08-31"))):
    add(*sc, f"Saldi invernali Lombardia/Lazio {y}", "Saldi invernali", "IT", "sales_season", "")
    add(*ss, f"Saldi estivi {y}", "Saldi estivi", "IT", "sales_season", "")
for y, sc, ss in ((2025, ("2025-01-08", "2025-02-04"), ("2025-06-25", "2025-07-22")), (2026, ("2026-01-07", "2026-02-03"), ("2026-06-24", "2026-07-21")),
                  (2027, ("2027-01-13", "2027-02-09"), ("2027-06-23", "2027-07-20"))):
    add(*sc, f"Soldes d'hiver {y}", "Soldes d'hiver", "FR", "sales_season", "")
    add(*ss, f"Soldes d'été {y}", "Soldes d'été", "FR", "sales_season", "")
for y in (2024, 2025, 2026):
    add(f"{y}-12-15", f"{y + 1}-01-29", f"Dubai Shopping Festival {y}/{y + 1}", "مهرجان دبي للتسوق", "Dubai", "event", "Mall promotions, raffle; tourist peak")
add("2026-10-09", "2026-10-11", "Singapore Grand Prix 2026", "F1 Singapore Grand Prix", "Singapore (Marina Bay)", "event", "Marina Bay road closures; hotel ADR spike")
add("2025-10-03", "2025-10-05", "Singapore Grand Prix 2025", "F1 Singapore Grand Prix", "Singapore (Marina Bay)", "event", "")
add("2024-09-20", "2024-09-22", "Singapore Grand Prix 2024", "F1 Singapore Grand Prix", "Singapore (Marina Bay)", "event", "")
add("2026-11-01", "2026-11-01", "Japan: brand price revisions effective (several luxury houses)", "価格改定", "JP", "pricing", "Pre-buying ahead of price increases is common in Japan")
add("2026-10-09", "2026-10-09", "Hangul Day long weekend", "한글날", "KR", "holiday", "Fri Oct 9 -> 3-day weekend; also Oct 3-5 (substitute) long weekend")
add("2026-09-19", "2026-09-23", "Silver Week Japan 2026", "シルバーウィーク", "JP", "travel_peak", "5-day holiday (Sep 19-23), rare alignment")
add("2026-10-12", "2026-10-12", "Thanksgiving Canada / Columbus Day US 2026", "Thanksgiving / Columbus Day", "CA, US", "holiday", "")
add("2026-10-26", "2026-10-30", "UK October half term", "Half term", "GB", "school", "")
add("2026-10-17", "2026-11-01", "Vacances de la Toussaint 2026", "Toussaint", "FR", "school", "")
for y in (2024, 2025, 2026):
    add(f"{y}-12-01", f"{y}-12-24", f"Christmas gifting season {y}", "Christmas", "global (N hemisphere)", "season", "Peak weeks for outerwear and gifting")
RC = mkdir(C / "retail_cultural")
R = [r for r in R if r]
R.sort(key=lambda r: r[0])
with open(RC / "retail_cultural_calendar_2024_2027.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["start_date", "end_date", "event_name", "local_name", "geo_scope", "category", "retail_relevance", "source"])
    w.writerows(R)

# fashion weeks (fashion-calendar provider JSON, mixed date formats per contributor)
FW = [("New York Fashion Week", "Womenswear SS25", "2024-09-06", "2024-09-11"), ("London Fashion Week", "Womenswear SS25", "2024-09-13", "2024-09-17"),
      ("Milano Moda Donna", "Womenswear SS25", "2024-09-17", "2024-09-23"), ("Paris Fashion Week", "Womenswear SS25", "2024-09-23", "2024-10-01"),
      ("Shanghai Fashion Week", "SS25", "2024-10-09", "2024-10-16"), ("Seoul Fashion Week", "SS25", "2024-09-03", "2024-09-07"),
      ("Milano Moda Uomo", "Menswear FW25", "2025-01-17", "2025-01-21"), ("Paris Fashion Week Men", "Menswear FW25", "2025-01-21", "2025-01-26"),
      ("New York Fashion Week", "Womenswear FW25", "2025-02-06", "2025-02-11"), ("London Fashion Week", "Womenswear FW25", "2025-02-20", "2025-02-24"),
      ("Milano Moda Donna", "Womenswear FW25", "2025-02-25", "2025-03-03"), ("Paris Fashion Week", "Womenswear FW25", "2025-03-03", "2025-03-11"),
      ("Milano Moda Uomo", "Menswear SS26", "2025-06-20", "2025-06-24"), ("Paris Fashion Week Men", "Menswear SS26", "2025-06-24", "2025-06-29"),
      ("New York Fashion Week", "Womenswear SS26", "2025-09-11", "2025-09-16"), ("London Fashion Week", "Womenswear SS26", "2025-09-18", "2025-09-22"),
      ("Milano Moda Donna", "Womenswear SS26", "2025-09-23", "2025-09-29"), ("Paris Fashion Week", "Womenswear SS26", "2025-09-29", "2025-10-07"),
      ("Shanghai Fashion Week", "SS26", "2025-10-09", "2025-10-17"), ("Seoul Fashion Week", "SS26", "2025-09-02", "2025-09-06"),
      ("Milano Moda Uomo", "Menswear FW26", "2026-01-16", "2026-01-20"), ("Paris Fashion Week Men", "Menswear FW26", "2026-01-20", "2026-01-25"),
      ("New York Fashion Week", "Womenswear FW26", "2026-02-12", "2026-02-17"), ("London Fashion Week", "Womenswear FW26", "2026-02-19", "2026-02-23"),
      ("Milano Moda Donna", "Womenswear FW26", "2026-02-24", "2026-03-02"), ("Paris Fashion Week", "Womenswear FW26", "2026-03-02", "2026-03-10"),
      ("Milano Moda Uomo", "Menswear SS27", "2026-06-19", "2026-06-23"), ("Paris Fashion Week Men", "Menswear SS27", "2026-06-23", "2026-06-28"),
      ("Tokyo Fashion Week", "SS27", "2026-08-31", "2026-09-05"), ("Seoul Fashion Week", "SS27", "2026-09-01", "2026-09-05"),
      ("New York Fashion Week", "Womenswear SS27", "2026-09-10", "2026-09-15"), ("London Fashion Week", "Womenswear SS27", "2026-09-17", "2026-09-21"),
      ("Milano Moda Donna", "Womenswear SS27", "2026-09-22", "2026-09-28"), ("Paris Fashion Week", "Womenswear SS27", "2026-09-29", "2026-10-07"),
      ("Shanghai Fashion Week", "SS27", "2026-10-09", "2026-10-16"), ("Copenhagen Fashion Week", "SS27", "2026-08-04", "2026-08-07"),
      ("Milano Moda Uomo", "Menswear FW27", "2027-01-15", "2027-01-19"), ("Paris Fashion Week Men", "Menswear FW27", "2027-01-19", "2027-01-24")]
CITY = {"New York Fashion Week": "New York", "London Fashion Week": "London", "Milano Moda Donna": "Milano", "Milano Moda Uomo": "Milano",
        "Paris Fashion Week": "Paris", "Paris Fashion Week Men": "Paris", "Shanghai Fashion Week": "Shanghai", "Seoul Fashion Week": "Seoul",
        "Tokyo Fashion Week": "Tokyo", "Copenhagen Fashion Week": "København"}
items = []
for i, (n, s, a, b) in enumerate(FW):
    fmt_a, fmt_b = a, b
    if n.startswith("Milano"):
        fmt_a, fmt_b = d(a).strftime("%d/%m/%Y"), d(b).strftime("%d/%m/%Y")
    items.append({"id": f"fw-{i + 1:03d}", "name": n, "season": s, "city": CITY[n], "start": fmt_a, "end": fmt_b,
                  "official_schedule_published": d(a) < d("2026-10-22"),
                  "notes": "dates as published by the organising chamber" if n.startswith("Milano") else ""})
write_json(C / "fashion_weeks" / "fashion_calendar_export.json", {"exported_at": "2026-10-20T08:12:44Z", "count": len(items), "items": items})
print("calendars done")
