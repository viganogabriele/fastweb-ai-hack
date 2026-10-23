"""Marketing / CRM: Salesforce campaign + member exports, PR seeding log, social listening alerts,
clienteling notes (multilingual), store waitlist / reservations."""
import datetime as dt
import string
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R = C.rng("marketing_crm")
OUT = C.OUT / "marketing"
OUT.mkdir(parents=True, exist_ok=True)
st = C.stores().set_index("store_id")
pos = C.pos_lines()
lost = C.lost_sales()
UTC = ZoneInfo("UTC")
ALNUM = string.ascii_letters + string.digits


def sfid(prefix):
    return prefix + "5g" + "".join(R.choice(list(ALNUM), 13))


def sf_ts(day, hh, mm, store):
    t = dt.datetime.combine(C.d(day), dt.time(hh, mm), tzinfo=ZoneInfo(st.timezone[store])).astimezone(UTC)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000+0000")


# ------------------------------------------------------------------ client accounts (from POS identified customers)
cust = pos[pos.customer_id.notna()].groupby("customer_id").agg(store=("store_id", "first"), nat=("customer_nationality", "first"),
                                                                 first=("business_date", "min"), spend=("net_amount", "sum")).reset_index()
ACC = {c: sfid("001") for c in cust.customer_id}
cust_by_store_day = pos[pos.customer_id.notna() & (pos.line_type == "SALE")].groupby(["store_id", "business_date"]).customer_id.apply(
    lambda x: sorted(set(x))).to_dict()

# ------------------------------------------------------------------ note templates
T = {
    "AUREA": {
        "it": ["cliente coreana vuole Aurea nera tg {sz}, chiamare quando rientra. Non interessata a beige/blu",
               "Aurea nero {sz} x2 richieste oggi (coreane). lasciato numero, KakaoTalk ok",
               "sig.ra {ini} cerca Aurea nera tg {sz} per la figlia, torna in Corea il {d}. Se arriva prima avvisare!!",
               "ennesima richiesta aurea nera taglia {sz}. niente. proposto Aria nero, no grazie",
               "Aurea nera tg {sz} - cliente in hotel fino al {d}, si può consegnare in hotel?",
               "coreane x3 per la Aurea NERA. {sz} e {sz2}. Abbiamo solo beige e blu. Lista attesa"],
        "fr": ["Cliente coréenne, veut la Aurea noire en {sz}. Rappeler dès réception. Pas intéressée par le beige.",
               "3 clientes coréennes ce matin pour Aurea noir {sz}/{sz2}, rien en stock. Coordonnées Kakao prises.",
               "Mme {ini} – Aurea noir taille {sz}, repart à Séoul le {d}. Si arrivage avant, livrer à l'hôtel.",
               "Encore la Aurea noire... taille {sz}. Plus rien depuis le 22. Liste d'attente.",
               "cliente veut Aurea noir {sz} vue dans un drama coréen, montre la photo sur son tel. pas de stock.",
               "Aurea noire {sz} – la cliente a déjà essayé Galeries Lafayette, rien non plus"],
        "en": ["Korean client, wants Aurea black size {sz}. Call when back in, she's in London till {d}.",
               "Aurea black {sz} - waitlist. Client says she saw it on a K-drama actress. Doesn't want navy.",
               "x2 Korean tourists asking Aurea black {sz} and {sz2}. Nothing on floor, nothing at DC. Took WhatsApp.",
               "personal shopper asking AGAIN for black Aurea sz {sz} for her client. told her maybe w/c 19th",
               "Aurea blk {sz} req. no stock. client left disappointed, bought a beanie"],
        "ko": ["Aurea 블랙 {sz} 사이즈 문의. 입고되면 연락 요청 (카톡)", "고객님 Aurea 블랙 {sz} 대기 등록. 베이지는 원하지 않으심",
               "드라마에서 본 Aurea 블랙 찾으심. {sz} 품절, 재입고 일정 문의", "Aurea 검정 {sz}/{sz2} 두 분 문의. 재입고 미정 안내"],
        "ja": ["Aurea ブラック {sz} ご希望。入荷次第ご連絡。", "お客様 Aureaの黒 サイズ{sz} 再入荷待ち。ベージュはNG。",
               "Aurea黒 {sz} お問い合わせ、韓国のドラマで見たとのこと"],
        "zh": ["客户要Aurea黑色{sz}码，到货请微信通知", "Aurea 黑色 {sz} 缺货，客人留了微信，下周再来", "黑色Aurea {sz}码 又一个客人问，全国都没货"],
        "de": ["Kundin möchte Aurea schwarz Gr. {sz}, bitte anrufen wenn wieder da.", "Aurea schwarz {sz} angefragt, nicht lieferbar. Marine wollte sie nicht."],
        "es": ["Clienta pregunta por Aurea negro talla {sz}, sin stock. Dejó teléfono."],
    },
    "MAIRE_PRE": {
        "it": ["Aurea nera tg {sz} non disponibile, cliente richiama", "chiesta Aurea nero {sz}, esaurita in negozio. DC?"],
        "fr": ["Aurea noire {sz} demandée, rupture en boutique", "cliente veut Aurea noir {sz}, on regarde le réassort"],
        "en": ["Aurea black {sz} asked, none on floor", "client after Aurea black sz {sz}, out of stock here"],
        "ko": ["Aurea 블랙 {sz} 문의, 매장 재고 없음"], "ja": ["Aurea 黒 {sz} 在庫なし"], "zh": ["Aurea 黑色 {sz} 码 店里没货"],
        "de": ["Aurea schwarz {sz} nicht da"], "es": ["Aurea negro {sz} sin stock"], "hk": ["Aurea 黑色 {sz} 碼 冇貨"], "tw": ["Aurea 黑色 {sz} 缺貨"],
    },
    "ILVPINK_PRE": {
        "it": ["Iridia rosa {sz} chiesta, non abbiamo la taglia"], "fr": ["Iridia rose {sz} - pas la taille"], "en": ["Iridia pink {sz} - size not in store"],
        "ko": ["Iridia 핑크 {sz} 사이즈 없음"], "ja": ["イルヴァロ ピンク {sz} サイズ欠品"], "zh": ["IRIDIA 粉色 {sz} 码 没有"], "de": ["Iridia rosa {sz} fehlt"],
        "es": ["Iridia rosa talla {sz} no hay"], "hk": ["IRIDIA 粉紅 {sz} 碼 冇貨"], "tw": ["IRIDIA 粉色 {sz} 號 缺貨"],
    },
    "ILVPINK": {
        "ko": ["Iridia 핑크 {sz} 대기. 윤하은 착용 제품 맞냐고 확인하심", "핑크 Iridia 문의 오늘만 열 건 넘음. {sz} 사이즈 대기 리스트 등록",
               "VIP 고객님 Iridia 핑크 {sz} 홀드 요청. 입고 시 바로 연락", "인디핑크 Iridia 언제 들어오냐고 계속 전화옴. 10/8 입고 예정이라고 안내함",
               "Iridia 핑크 {sz} 따님 선물용, 입고되면 택배 가능 여부 문의", "핑크 Iridia {sz} - 블랙 권해드렸는데 핑크만 원하심"],
        "ja": ["イルヴァロ ピンク {sz} 入荷待ち。LUMIEREのユン・ハウンさん着用と同じかご確認あり", "ピンクのショート（イルヴァロ）お問い合わせ多数。{sz}で予約希望",
               "価格改定前にイルヴァロピンクを買いたいとのこと。{sz}", "イルヴァロ510 {sz} 再入荷のご連絡希望（LINE）"],
        "zh": ["尹夏恩同款粉色IRIDIA {sz}码，客人要求到货第一时间通知", "粉色IRIDIA {sz}码 客人想付定金预订，已解释不能收定金",
               "今天至少8个客人问粉色IRIDIA，全部缺货", "IRIDIA 粉色 {sz} 码，客人从苏州过来的，很失望"],
        "tw": ["客人要 IRIDIA 粉紅 {sz} 號，到貨請 LINE 通知", "IRIDIA 粉色 {sz} 預約，尹夏恩同款"],
        "hk": ["客人要粉紅色 IRIDIA {sz} 碼, 到貨 WhatsApp 通知", "IRIDIA pink {sz} – client from Shenzhen, will come back weekend",
               "粉紅 IRIDIA 全線冇貨, 客人留電話 {tel}"],
        "en": ["IRIDIA pink {sz} – client showed Yoon Ha-eun photo. Waitlist.", "Pink Iridia sz {sz} request, KR student. Offered black, declined.",
               "pink iridia {sz}?? third today. no stock anywhere in SEA"],
        "fr": ["Iridia rose poudré {sz} – cliente coréenne, photo de la chanteuse. Rien."],
        "it": ["Iridia rosa tg {sz}, cliente cinese con foto della cantante coreana. Non abbiamo niente"],
    },
    "AMB": {
        "it": ["Amalia marrone tg {sz}, cliente abituale. In attesa. Il nero non le piace",
               "cappotto Amalia cioccolato {sz} – esaurito, VIC chiede quando arriva. detto novembre"],
        "fr": ["Amalia marron chocolat taille {sz} – liste d'attente. 'le marron c'est la couleur de la saison'",
               "Cliente fidèle, Amalia marron {sz}, rappeler. Ne veut pas le noir."],
        "en": ["Amalia brown size {sz}, waiting list. Tried the black, not the same."],
        "es": ["Clienta quiere Amalia marrón talla {sz}. Llamar cuando llegue. No le vale el negro."],
        "zh": ["Amalia 咖啡色 {sz}码 缺货，客人等"], "ja": ["アンブリン ブラウン {sz} 入荷待ち"], "ko": ["Amalia 브라운 {sz} 대기"], "de": ["Amalia braun Gr. {sz} gewünscht"],
    },
    "LCM": {
        "it": ["cardigan logo M nero, cliente lo vuole per regalo, M finito da giovedì", "Vlogo Cardigan tg M blu – chiesto a Rinascente, aspettiamo",
               "cliente abituale cardigan logo M. ritorna sabato. tenere da parte se arriva", "Ennesimo cardigan M. Scaffale vuoto in M, S e L a pacchi",
               "cardigan logo M: il cliente ha provato L, troppo grande. lasciato numero"],
        "en": ["Vlogo Cardigan M request, none left", "cardigan M navy - waitlist"], "fr": ["Cardigan logo M – plus de M"], "es": ["Cárdigan logo M agotado"],
        "zh": ["Logo开衫M码没有了"], "ja": ["ロゴカーディガン M 完売"], "ko": ["로고 가디건 M 품절"], "de": ["Vlogo Cardigan M ausverkauft"],
    },
    "ARTEM": {
        "it": ["Artem: consigliata una taglia in meno, veste grande (preso {a} invece di {b})", "Artem cambio taglia {b}->{a}, veste abbondante"],
        "fr": ["Artem taille grand – conseillé une taille en dessous ({a})", "échange Artem {b} contre {a}, trop large aux épaules"],
        "en": ["Artem runs big, client exchanged {b} for {a}", "Artem - advised size down, took {a}"],
        "de": ["Artem fällt groß aus – eine Größe kleiner empfohlen ({a})"], "ja": ["アルネブは大きめ。ワンサイズ下（{a}）をおすすめ"],
        "ko": ["Artem 한 사이즈 크게 나옴, {a} 추천"], "zh": ["ARTEM 偏大，建议小一码（{a}）"], "es": ["Artem talla grande, cambio {b} por {a}"],
    },
    "VEL": {
        "it": ["Gilet VEL: cursore della zip si è staccato dopo 2 settimane. Cliente arrabbiato, reso", "VEL reso per cerniera, non vuole riparazione",
               "altro VEL con la zip rotta. 3° questa settimana"],
        "fr": ["VEL : la tirette du zip s'est cassée. Retour.", "Gilet VEL zip HS, client mécontent, remboursement"],
        "en": ["VEL vest zip slider came off, client wants refund not repair", "VEL returned - zip. Client: 'for this price??'"],
        "es": ["chaleco VEL: se rompió la cremallera, cliente quiere devolución"], "de": ["VEL Weste: Reißverschluss-Schieber kaputt, Kunde will Geld zurück"],
        "ja": ["VELベスト ファスナーのスライダー外れ、返品"], "ko": ["VEL 조끼 지퍼 고장 반품"], "zh": ["VEL 马甲拉链头掉了，客人要求退货"],
    },
    "JPPRICE": {"ja": ["11月の価格改定前に購入希望。{sty} {sz}", "値上げ前にまとめ買い（Aurea・Nova）。在庫確認依頼", "価格改定のお手紙を見てご来店。{sty} {sz} お取り置き",
                       "改定前価格での予約可能か質問あり。不可とご説明", "ご主人様分もあわせて購入、値上げ前に"]},
    "ASTRA": {"zh": ["ASTRA 披肩 很喜欢，客人买了白色", "Astra 羽绒服 客人觉得版型很好，买了黑色{szA}", "Couture Astra 再来一件给朋友"],
                "it": ["Astra: provato, piccolo e caro. Non acquista", "Astra oversize veste piccolo?? strano per un oversize"],
                "fr": ["Astra trop petit et trop cher selon la cliente"], "en": ["Astra Oversized feels small, client passed", "Astra - liked the cape, price a stretch"],
                "de": ["Astra zu klein, zu teuer"]},
    "D11": {"zh": ["客人问门店能不能按天猫双十一价格", "双11预售价格比门店低，客人犹豫，说回去网上买", "老客户问双十一有没有门店专属活动"]},
    "SYD": {"en": ["Client wants jersey polo navy L, we have 2 left. Lots of asks for tees. Nobody looking at puffers, it's 25 degrees",
                   "asked for light jacket / windbreaker, nothing in store. sent to website", "tees in white M/L - asked 4 times today",
                   "client from Melbourne wanted Mario windbreaker, it's gone (SS26 returned to DC??)"]},
    "COLD": {"de": ["Kälte: Kundin will Monteluce Gr. {szM}, ausverkauft, Warteliste", "Schnee! Mützen fast weg, Kunde wollte Handschuhe schwarz",
                    "Cosimo {szM} gesucht, nicht mehr da"],
             "en": ["cold snap - client after Monteluce {szM}, none left", "everyone wants long down today"], "fr": ["Grand froid, cliente cherche Liviana {sz} noir"]},
    "MAYA_MAD": {"es": ["cliente quiere NOVA negro talla {szM}, solo tenemos azul marino (error del almacén)", "NOVA negro {szM} – le ofrecí el azul, no quiere",
                        "otro cliente por NOVA negro. ¿Cuándo llega el negro?"]},
    "GW": {"it": ["gruppo clienti cinesi, acquistato 3 Nova, tax free. Chiedono anche Aurea nera", "cliente cinese VIC (WeChat) - prenota visita sabato"],
           "fr": ["Clients chinois Golden Week, détaxe, Nova noir x2", "groupe chinois - beaucoup de questions sur Aurea noir"]},
    "ROUTINE": {
        "it": ["Appuntamento sabato h 11, prova Liviana", "compleanno 12/11 - mandare biglietto", "preferisce colori scuri, tg 2 donna / 5 uomo",
               "chiamata di ringraziamento fatta", "ritiro orlo pantalone pronto", "VIC, passato a salutare, nessun acquisto"],
        "fr": ["RDV samedi 15h, essayage Fiammetta", "anniversaire le 03/11", "remerciement envoyé", "préfère être contactée par WhatsApp"],
        "en": ["appointment Thu 4pm", "thank-you note sent", "prefers WhatsApp, not calls", "VIC - bought Nova last year, interested in Couture"],
        "de": ["Termin Samstag 11 Uhr", "Dankeskarte geschickt"], "es": ["Cita el sábado a las 12", "nota de agradecimiento enviada"],
        "ja": ["土曜日11時ご来店予約", "お礼状送付済み", "お誕生日 11/20"], "ko": ["토요일 오후 2시 방문 예약", "감사 문자 발송"],
        "zh": ["周六下午预约试穿", "已发感谢微信", "生日11月"], "hk": ["星期六預約試身", "已WhatsApp多謝客人"], "tw": ["週六預約"],
    },
}
LANG = {"it": "it", "fr": "fr", "en": "en", "de": "de", "es": "es", "ja": "ja", "ko": "ko", "zh-CN": "zh", "zh-HK": "hk", "zh-TW": "tw"}
CHANNEL = {"it": ["WhatsApp", "Call", "Note"], "fr": ["WhatsApp", "Call", "Note"], "en": ["WhatsApp", "Call", "Note", "Email"],
           "de": ["Call", "Note"], "es": ["WhatsApp", "Note"], "ja": ["LINE", "Call", "Note"], "ko": ["KakaoTalk", "Note"],
           "zh": ["WeChat", "Note"], "hk": ["WhatsApp", "WeChat"], "tw": ["LINE", "Note"]}


def pick_text(sig, lang, **kw):
    pool = T[sig].get(lang) or T[sig].get("en") or next(iter(T[sig].values()))
    txt = str(R.choice(pool))
    kw.setdefault("ini", str(R.choice(list("KLPSJHMYC"))) + ".")
    kw.setdefault("d", "")
    kw.setdefault("tel", f"{int(R.integers(1000, 9999))}")
    for k_ in ("sz", "sz2", "a", "b", "szM", "szA", "sty"):
        kw.setdefault(k_, "")
    try:
        return txt.format(**kw)
    except (KeyError, IndexError):
        return txt


def lang_of(store):
    return LANG[st.language[store]]


notes = []


def add_note(store, day, sig, client=None, **kw):
    lg = lang_of(store)
    if sig in ("ILVPINK",) and store in ("SIN01",):
        lg = "en"
    if sig == "ILVPINK" and store in ("PAR01", "PAR02"):
        lg = "fr"
    txt = pick_text(sig, lg, **kw)
    # human noise
    if R.random() < 0.08:
        txt = txt.lower()
    if R.random() < 0.05:
        txt = txt + " " + str(R.choice(["!!", "??", "(urgente)", "- vedi foto", "/ cc SM", "ok"]))
    hh = int(R.integers(10, 20))
    sa_pool = pos[(pos.store_id == store)].sales_associate.dropna().unique()
    owner = str(R.choice(sa_pool)) if len(sa_pool) else f"{store}-SA01"
    notes.append(dict(Id=sfid("00T"), AccountId=ACC.get(client, "") if client else "", Client_External_Id__c=client or "",
                      OwnerAlias=owner, Store__c=C.CRM_CODE[store], Subject=str(R.choice(CHANNEL[lg])),
                      ActivityDate=C.d(day).isoformat(), CreatedDate=sf_ts(day, hh, int(R.integers(0, 60)), store),
                      Status="Completed", Description=txt, Type="Clienteling", _sig=sig, _store=store))


def client_for(store, day):
    cl = cust_by_store_day.get((store, C.d(day).isoformat()))
    if cl and R.random() < 0.55:
        return str(R.choice(cl))
    return None


KEY = {"J20931A00012-999": "AUREA", "J20931A00618-510": "ILVPINK", "J20931A00622-23R": "AMB", "I10919B00011-999": "LCM", "I10919B00011-742": "LCM"}
SIZES_W = ["00", "0", "1", "2", "3", "4"]
for r in lost.itertuples():
    sig = KEY.get(r.sku)
    if not sig:
        continue
    if sig == "LCM" and (r.size != "M" or r.date < "2026-10-01" or (r.store_id == "MIL01" and r.date < "2026-10-08")):
        continue
    p = {"AUREA": 0.22, "ILVPINK": 0.30, "AMB": 0.45, "LCM": 0.5}[sig]
    if sig == "AUREA" and r.date < "2026-09-17":
        sig, p = "MAIRE_PRE", 0.15
    if sig == "ILVPINK" and r.date < "2026-10-02":
        sig, p = "ILVPINK_PRE", 0.2
    if st.store_type[r.store_id] == "Resort":
        p *= 0.3
    if R.random() > p:
        continue
    sz2 = SIZES_W[min(5, SIZES_W.index(r.size) + 1)] if r.size in SIZES_W else r.size
    dleave = (C.d(r.date) + dt.timedelta(days=int(R.integers(2, 9)))).strftime("%d/%m")
    add_note(r.store_id, r.date, sig, client_for(r.store_id, r.date), sz=r.size, sz2=sz2, d=dleave)

# ARTEM size exchanges / VEL defects from POS returns
ret = pos[pos.line_type == "RETURN"]
for r in ret[ret.sku.str.startswith("J10911A00577") & (ret.return_reason.isin(["SIZE", "EXCHANGE_SIZE"]))].itertuples():
    if R.random() < 0.45:
        b = r.size
        a = str(int(b) - 1) if b.isdigit() and int(b) > 1 else b
        add_note(r.store_id, r.business_date, "ARTEM", r.customer_id if isinstance(r.customer_id, str) else None, a=a, b=b)
for r in ret[ret.return_reason == "DEF"].itertuples():
    if R.random() < 0.3:
        add_note(r.store_id, r.business_date, "VEL", r.customer_id if isinstance(r.customer_id, str) else None)
# Japan price increase pre-buying
sale = pos[pos.line_type == "SALE"]
jp = sale[sale.store_id.isin(["TYO01", "TYO02", "OSA01"]) & (sale.business_date >= "2026-10-10") &
          (sale.sku.str.startswith("J10911A00034") | sale.sku.str.startswith("J20931A00012"))]
for r in jp.sample(frac=0.12, random_state=3).itertuples():
    add_note(r.store_id, r.business_date, "JPPRICE", r.customer_id if isinstance(r.customer_id, str) else None, sz=r.size,
             sty="Nova" if r.sku.startswith("J10911A00034") else "Aurea")
# ASTRA feedback
pol = sale[sale.sku.str.startswith("G2092") & (sale.business_date >= "2026-09-24")]
for r in pol.sample(frac=0.06, random_state=4).itertuples():
    lg = lang_of(r.store_id)
    if lg in ("zh", "hk", "tw") or lg in ("it", "fr", "en", "de"):
        add_note(r.store_id, r.business_date, "ASTRA", r.customer_id if isinstance(r.customer_id, str) else None, szA=r.size)
for sid in ["SHA01", "BJS01", "CDU01"]:
    for day in ["2026-10-20", "2026-10-21"]:
        for _ in range(int(R.integers(1, 4))):
            add_note(sid, day, "D11", client_for(sid, day))
for day in C.daterange("2026-09-01", "2026-10-21"):
    if R.random() < 0.25:
        add_note("SYD01", day, "SYD", client_for("SYD01", day))
for sid in ["MUN01", "ZRH01", "BER01", "GVA01", "CPH01", "AMS01"]:
    for day in C.daterange("2026-10-12", "2026-10-19"):
        if R.random() < 0.3:
            add_note(sid, day, "COLD", client_for(sid, day), szM=str(R.choice(["3", "4", "5"])), sz=str(R.choice(["1", "2"])))
for day in C.daterange("2026-09-21", "2026-10-06"):
    if R.random() < 0.5:
        add_note("MAD01", day, "MAYA_MAD", client_for("MAD01", day), szM=str(R.choice(["3", "4", "5"])))
for sid in ["MIL01", "PAR01", "PAR02"]:
    for day in C.daterange("2026-09-30", "2026-10-08"):
        if R.random() < 0.35:
            add_note(sid, day, "GW", client_for(sid, day))
# routine
for _ in range(420):
    sid = str(R.choice(st.index))
    day = C.d("2026-08-01") + dt.timedelta(days=int(R.integers(0, 82)))
    add_note(sid, day, "ROUTINE", client_for(sid, day))
nt = pd.DataFrame(notes).sort_values("CreatedDate")
# quirks: 2 notes saved twice (mobile app retry), one store code typo
dupl = nt.sample(6, random_state=11)
nt = pd.concat([nt, dupl.assign(Id=[sfid("00T") for _ in range(len(dupl))])]).sort_values("CreatedDate")
nt.drop(columns=["_sig", "_store"]).to_csv(OUT / "salesforce_clienteling_notes_export.csv", index=False)
print("notes", len(nt), nt._sig.value_counts().to_dict())

# ------------------------------------------------------------------ waitlist / reservations (clienteling app)
KEYW = {"J20931A00012-999", "J20931A00618-510", "J20931A00622-23R", "I10919B00011-999", "I10919B00011-742", "J20931A00618-999", "J10911A00034-999"}
lw = lost[lost.sku.isin(KEYW)]
lw = lw[~((lw.sku.str.startswith("I10919B00011")) & (lw["size"] != "M"))]
lw = lw[~((lw.sku == "J10911A00034-999") & (lw.store_id != "MAD01"))]
days = sorted(lw.date.unique())
stock_series = {}
for day in C.daterange("2026-08-01", "2026-10-21"):
    s_ = C.store_stock(day)
    s_ = s_[s_.sku.isin(KEYW)]
    for r in s_.itertuples():
        stock_series.setdefault((r.store_id, r.sku, r.size), {})[day] = r.on_hand


def back_in_stock(store, sku, size, after):
    ser = stock_series.get((store, sku, size), {})
    prev = None
    for day in sorted(ser):
        if day <= C.d(after):
            prev = ser[day]
            continue
        if ser[day] > 0 and (prev is None or ser[day] > prev or prev == 0):
            return day
        prev = ser[day]
    return None


wl = []
wid = 52000
for r in lw.itertuples():
    p = 0.28 if st.store_type[r.store_id] == "Flagship" else 0.18
    n = int(R.binomial(int(r.lost), p))
    for _ in range(n):
        wid += int(R.integers(1, 5))
        created = C.d(r.date)
        client = client_for(r.store_id, created)
        bis = back_in_stock(r.store_id, r.sku, r.size, created)
        status, notified, closed = "OPEN", "", ""
        if bis:
            nd = bis + dt.timedelta(days=int(R.integers(0, 2)))
            if nd <= C.LAST_DAY:
                notified = sf_ts(nd, int(R.integers(10, 18)), int(R.integers(0, 60)), r.store_id)
                u = R.random()
                if u < 0.5 and nd + dt.timedelta(days=2) <= C.LAST_DAY:
                    status, closed = "FULFILLED", (nd + dt.timedelta(days=int(R.integers(0, 3)))).isoformat()
                elif u < 0.65:
                    status = "CANCELLED"
                    closed = nd.isoformat()
                else:
                    status = "NOTIFIED"
        elif (C.LAST_DAY - created).days > 21 and R.random() < 0.4:
            status = "EXPIRED"
        sku_txt = f"{r.sku}-{r.size}"
        u = R.random()
        if u < 0.2:
            sku_txt = r.sku
        elif u < 0.3:
            sku_txt = f"{C.STYLE_NAME[r.sku.split('-')[0]]} {C.color_name(r.sku.split('-')[1], 'en')}"
        wl.append(dict(waitlist_id=f"WL-{wid}", store_code=C.CRM_CODE[r.store_id], created_at=sf_ts(created, int(R.integers(10, 20)),
                                                                                                      int(R.integers(0, 60)), r.store_id),
                       client_id=client or "", client_type="KNOWN" if client else "WALK_IN_LEAD", item=sku_txt, size=r.size,
                       qty=1, deposit="N" if r.store_id not in ("TYO01", "TYO02", "OSA01") else str(R.choice(["N", "Y"])),
                       status=status, notified_at=notified, closed_on=closed,
                       channel=str(R.choice(CHANNEL[lang_of(r.store_id)]))))
wl = pd.DataFrame(wl)
# quirks: stale OPEN entries even though stock came back (associates never updated), duplicates, wrong store code
stale = wl[(wl.status == "NOTIFIED")].sample(frac=0.3, random_state=5).index
wl.loc[stale, ["status", "notified_at"]] = ["OPEN", ""]
dupl = wl[wl.client_id != ""].sample(12, random_state=6).copy()
dupl["waitlist_id"] = [f"WL-{wid + 10 + i}" for i in range(len(dupl))]
wl = pd.concat([wl, dupl])
two = wl[(wl.client_id != "") & (wl.store_code == C.CRM_CODE["PAR01"])].head(3).copy()
two["store_code"] = C.CRM_CODE["PAR02"]
two["waitlist_id"] = [f"WL-{wid + 40 + i}" for i in range(len(two))]
wl = pd.concat([wl, two]).sort_values("created_at")
bad = wl[wl.store_code == C.CRM_CODE["SEL01"]].sample(4, random_state=8).index
wl.loc[bad, "store_code"] = "KR1"
wl.to_csv(OUT / "store_waitlist_reservations.csv", index=False)
print("waitlist", len(wl), wl.status.value_counts().to_dict())

# ------------------------------------------------------------------ Salesforce campaigns + LON01 members
ev_day = C.LON01_EVENT["date"]
lon_buyers = sorted(set(pos[(pos.store_id == "LON01") & (pos.business_date == ev_day) & pos.customer_id.notna() & (pos.line_type == "SALE")].customer_id))
lon_other = sorted(set(pos[(pos.store_id == "LON01") & (pos.business_date < "2026-10-01") & pos.customer_id.notna()].customer_id) - set(lon_buyers))
purchasers = list(R.choice(lon_buyers, C.LON01_EVENT["purchasers"], replace=False))
others = list(R.choice(lon_other, C.LON01_EVENT["invited"] - len(purchasers), replace=False))
inv = purchasers + others
attended_np = others[: C.LON01_EVENT["attended"] - len(purchasers)]
rsvp_noshow = others[len(attended_np): len(attended_np) + (C.LON01_EVENT["rsvp_yes"] - C.LON01_EVENT["attended"])]
day_rev = pos[(pos.store_id == "LON01") & (pos.business_date == ev_day)].groupby("customer_id").net_amount.sum()
mem = []
camp_id = C.LON01_EVENT["crm_campaign_id"]
for c in inv:
    if c in purchasers:
        status = "Attended - Purchased"
    elif c in attended_np:
        status = "Attended"
    elif c in rsvp_noshow:
        status = "Responded - No Show"
    else:
        status = "Declined"
    mem.append(dict(Id=sfid("00v"), CampaignId=camp_id, ContactId=sfid("003"), AccountId=ACC.get(c, ""), External_Client_Id__c=c,
                    Status=status, HasResponded=status != "Declined" and True,
                    Plus_One__c=0, Event_Purchase_GBP__c=round(float(day_rev.get(c, 0)), 2) if c in purchasers else 0,
                    CreatedDate="2026-09-18T09:12:00.000+0000"))
att_idx = [i for i, m_ in enumerate(mem) if m_["Status"].startswith("Attended")]
for i in R.choice(att_idx, C.LON01_EVENT["plus_ones"], replace=False):
    mem[int(i)]["Plus_One__c"] = 1
m_df = pd.DataFrame(mem)
m_df.loc[m_df.Status == "Declined", "HasResponded"] = True
m_df.to_csv(OUT / "salesforce_campaign_members_LON01_private_evening.csv", index=False)
rev = m_df.Event_Purchase_GBP__c.sum()

CAMP = [
    (camp_id, "UK | LON01 Private Client Evening FW26", "Client Event", "Completed", "2026-10-08", "2026-10-08", "GB01", 45, 39, 48000, 51230,
     f"Attended 36 (+9 guests). Purchasers 23, 27 transactions, GBP {rev:,.0f} (POS matched)"),
    (sfid("701"), "IT | MIL01 MFW VIC appointments", "Client Event", "Completed", "2026-09-22", "2026-09-28", "IT01", 80, 52, 60000, 58400, ""),
    (sfid("701"), "FR | PAR01 PFW private viewing", "Client Event", "Completed", "2026-10-03", "2026-10-03", "FR01", 60, 41, 75000, 79900, ""),
    (sfid("701"), "CN | Astra VIP preview Plaza 66", "Client Event", "Completed", "2026-09-26", "2026-09-26", "CN01", 120, 96, 95000, 101000, ""),
    (sfid("701"), "KR | BIFF Busan Centum corner", "Client Event", "Completed", "2026-10-01", "2026-10-10", "KR03", 0, 0, 38000, 36100, "walk-in, no invites"),
    (sfid("701"), "SG | F1 weekend cocktail MBS", "Client Event", "Completed", "2026-10-10", "2026-10-10", "SG01", 50, 33, 30000, 31800, ""),
    (sfid("701"), "CA | TIFF gifting lounge", "PR Event", "Completed", "2026-09-10", "2026-09-20", "CA01", 0, 0, 55000, 61200, ""),
    (sfid("701"), "JP | Price change letter 11/1", "Direct Mail", "In Progress", "2026-10-09", "2026-10-31", "JP01", 4120, 388, 12000, 9800,
     "LINE + DM; responses = store visits booked"),
    (sfid("701"), "CN | Golden Week outbound - WeChat tax-free", "WeChat", "Completed", "2026-09-28", "2026-10-08", "", 9800, 640, 25000, 22100,
     "targeting clients travelling to IT/FR/UK"),
    (sfid("701"), "GLOBAL | Newsletter FW26 Icons", "Email", "Completed", "2026-09-17", "2026-09-17", "", 412000, 23900, 8000, 8000,
     "hero: Aurea black, Nova, Liviana"),
    (sfid("701"), "GLOBAL | Newsletter Couture Astra", "Email", "Completed", "2026-09-24", "2026-09-24", "", 418500, 31100, 8000, 8000, ""),
    (sfid("701"), "EU | Newsletter Cold weather edit", "Email", "Completed", "2026-10-14", "2026-10-14", "", 188000, 12700, 6000, 6000, ""),
    (sfid("701"), "APAC | IRIDIA pink edit (social)", "Social", "In Progress", "2026-10-06", "2026-10-25", "", 0, 0, 35000, 14100,
     "launched after stock-out; links to sold-out PDP"),
    (sfid("701"), "KR | IRIDIA waitlist SMS", "SMS", "Planned", "2026-11-20", "2026-11-22", "KR02", 0, 0, 2000, 0, "to send when PO 4500222417 lands"),
]
cdf = pd.DataFrame(CAMP, columns=["Id", "Name", "Type", "Status", "StartDate", "EndDate", "Store__c", "NumberOfContacts", "NumberOfResponses",
                                  "BudgetedCost", "ActualCost", "Description"])
cdf["CurrencyIsoCode"] = cdf.Store__c.map(lambda s: {"GB01": "GBP", "CN01": "CNY", "KR03": "KRW", "KR02": "KRW", "SG01": "SGD", "CA01": "CAD",
                                                      "JP01": "JPY"}.get(s, "EUR"))
cdf.loc[cdf.CurrencyIsoCode != "EUR", "BudgetedCost"] = cdf.BudgetedCost  # NB: costs are EUR although currency says local (export quirk)
cdf.to_csv(OUT / "salesforce_campaigns_export.csv", index=False)

# ------------------------------------------------------------------ PR seeding log
SEED = [
    ("2026-08-18", "Chiara F.", "IT", "Talent Garden Agency", "NOVA 999", "4", "Delivered", "2026-08-29", "Instagram", 2100000, 38000, ""),
    ("2026-08-20", "Léa M.", "FR", "Agence Lumière", "AUREA 034", "1", "Posted", "2026-09-02", "Instagram", 860000, 14500, "beige requested by talent"),
    ("2026-08-25", "Park Ji-woo (actress)", "KR", "Starhaus Ent.", "AUREA 999", "0", "Posted", "2026-09-16", "Instagram / drama wardrobe",
     5400000, 120000, "wardrobe placement drama 'Winter Letters' ep.7 aired 16/09"),
    ("2026-08-27", "Kenta S.", "JP", "Tokyo Muse", "MISTRAL 999", "3", "Posted", "2026-09-10", "Instagram", 1200000, 21000, ""),
    ("2026-09-01", "Mia L.", "CN", "Shanghai Bloom", "IRIDIA 999", "0", "Posted", "2026-09-09", "Xiaohongshu", 3100000, 54000, ""),
    ("2026-09-01", "Jade W.", "HK", "HK Icons", "IRIDIA 20D", "1", "Posted", "2026-09-12", "Instagram", 940000, 12000, ""),
    ("2026-09-03", "Sofia R.", "IT", "Talent Garden Agency", "AMALIA 23R", "1", "Posted", "2026-09-08", "Instagram", 1500000, 31000, "brown!"),
    ("2026-09-05", "Ethan B.", "US", "WME", "ARTEM 999", "5", "Delivered", "", "", 0, 0, "asked exchange to size 4 (runs big)"),
    ("2026-09-08", "Olivia T.", "GB", "Storm", "LIVIANA 999", "1", "Posted", "2026-09-20", "Instagram", 720000, 11000, ""),
    ("2026-09-10", "Lucas D.", "FR", "Agence Lumière", "ASTRA CAPE 999", "M", "Posted", "2026-09-29", "Instagram", 650000, 9000, "PFW"),
    ("2026-09-12", "Zhou Yi", "CN", "Shanghai Bloom", "ASTRA OVERSIZED 999", "M", "Posted", "2026-09-24", "Weibo", 8200000, 160000, "launch day"),
    ("2026-09-12", "Han Seo-yeon", "KR", "Starhaus Ent.", "IRIDIA 999", "0", "Posted", "2026-09-26", "Instagram", 2300000, 41000, ""),
    ("2026-09-15", "Grace L.", "SG", "SEA Talent", "VLOGO T-SHIRT 001", "S", "Posted", "2026-09-20", "Instagram", 300000, 3000, ""),
    ("2026-09-18", "Ryan K.", "CA", "TIFF lounge", "MONTELUCE 999", "4", "Posted", "2026-09-14", "Instagram", 410000, 7000,
     "post date before sent date (sent through lounge, logged late)"),
    ("2026-09-20", "Marta G.", "ES", "Madrid Models", "NOVA 742", "2", "No post", "", "", 0, 0, ""),
    ("2026-09-22", "LUMIERE (group - stylist)", "KR", "Bloom Music Ent.", "ARIA 999 x4", "0/1", "Delivered", "", "", 0, 0,
     "for Paris FW wardrobe; NOT Iridia; Yoon Ha-eun NOT included (stylist pulled other brands)"),
    ("2026-09-24", "Lin Q.", "CN", "Shanghai Bloom", "ASTRA BALACLAVA 999", "TU", "Posted", "2026-09-25", "Douyin", 4100000, 70000, ""),
    ("2026-09-28", "Aiko N.", "JP", "Tokyo Muse", "AUREA 999", "1", "CANCELLED", "", "", 0, 0, "no stock black Aurea (DC 0)"),
    ("2026-10-02", "Yoon Ha-eun (LUMIERE)", "KR", "Bloom Music Ent.", "IRIDIA 510", "0", "NOT SEEDED", "2026-10-01", "Instagram/X/Weibo (press photos)",
     48000000, 0, "PR Seoul 02/10 09:40 KST: photographed 01/10 outside PFW show in IRIDIA powder pink. NOT in seeding list - own purchase / "
                  "stylist. Organic. Contact agency for thank-you gifting."),
    ("2026-10-05", "Yoon Ha-eun (LUMIERE)", "KR", "Bloom Music Ent.", "IRIDIA 510", "0", "ON HOLD", "", "", 0, 0,
     "gifting request rejected by WMS HK30: ATP 0. retry after top-up 08/10"),
    ("2026-10-12", "Valentina P.", "IT", "Vogue Italia (editorial)", "IRIDIA 510 x2", "00/0", "Delivered", "", "", 0, 0, "press samples IT10"),
    ("2026-10-14", "Noah S.", "US", "WME", "NOVA 999", "4", "Posted", "2026-10-18", "Instagram", 1300000, 19000, ""),
    ("2026-10-16", "Yoon Ha-eun (LUMIERE)", "KR", "Bloom Music Ent.", "IRIDIA 510", "0", "ON HOLD", "", "", 0, 0,
     "still pending - PR APAC asked HK30 again, no reply"),
]
sd = pd.DataFrame(SEED, columns=["Date sent / logged", "Talent", "Market", "Agency", "Item (style colour)", "Size", "Status", "Post date",
                                 "Platform", "Reach", "EMV (EUR)", "Notes"])
sd.to_excel(OUT / "PR_seeding_tracker_FW26.xlsx", index=False)

# ------------------------------------------------------------------ social listening alerts
AL = [
    ("2026-09-16T14:20:00Z", "KEYWORD_SPIKE", "Valentino Aurea", 1840, 310, "KR", "ko", 0.62, "Aurea, 발렌티노, 박지우, 겨울편지, 패딩",
     "윤겨울편지 7화에서 박지우 입은 패딩 발렌티노 Aurea 맞죠?? 블랙 너무 예쁨"),
    ("2026-09-18T09:05:00Z", "VOLUME_SPIKE", "Valentino Aurea black", 3920, 340, "KR,FR", "ko,fr", 0.55, "Aurea 블랙, 품절, 파리, 발렌티노",
     "파리 발렌티노 갔는데 Aurea 블랙 없음… 다 품절"),
    ("2026-09-22T11:40:00Z", "NEW_TOPIC", "Valentino Paris sold out", 610, 80, "KR,FR", "ko,fr,en", 0.10, "sold out, rupture, 품절, Saint-Honoré",
     "Aurea noire en rupture partout à Paris, même aux Galeries. Les touristes coréennes font la queue"),
    ("2026-09-24T02:10:00Z", "VOLUME_SPIKE", "Valentino Couture Astra", 22800, 2400, "CN,HK", "zh", 0.71, "Astra, 天才系列, 周一, 斗篷", "Astra斗篷太好看了，上海恒隆已经排队"),
    ("2026-09-27T16:00:00Z", "SENTIMENT_DROP", "Valentino Couture Astra", 1450, 1100, "FR,IT,GB,US", "fr,it,en", -0.22, "too small, trop petit, caro, overpriced",
     "Tried the Astra Oversized and it's... not oversized at all. And €2,400?"),
    ("2026-09-29T19:30:00Z", "NEW_TOPIC", "Valentino VEL zipper", 140, 15, "IT,FR,ES,DE", "it,fr,en", -0.68, "zip, cerniera, tirette, broken, rotta",
     "Gilet VEL comprato ad agosto, il cursore della zip si è staccato. Per 990€. Complimenti @valentino"),
    ("2026-10-01T21:05:00Z", "VOLUME_SPIKE", "Valentino pink / Yoon Ha-eun", 18600, 120, "KR", "ko,en", 0.88, "윤하은, 발렌티노, 핑크패딩, LUMIERE, PFW",
     "윤하은 파리 출국 착장 발렌티노 핑크 패딩 ㄷㄷ 제품명 아시는 분?"),
    ("2026-10-01T23:40:00Z", "VOLUME_SPIKE", "Valentino IRIDIA", 61200, 90, "KR,CN,JP,TW,HK", "ko,zh,ja", 0.86, "IRIDIA, Iridia, 尹夏恩同款, イルヴァロ",
     "尹夏恩同款 Valentino IRIDIA 粉色 已经全网断货了吧"),
    ("2026-10-02T03:15:00Z", "KEYWORD_MATCH", "IRIDIA sold out", 24300, 0, "KR,CN,JP", "ko,zh,ja", -0.15, "품절, 断货, 売り切れ, restock",
     "발렌티노 공홈 Iridia 핑크 7시 반에 다 품절됨 ㅠㅠ 재입고 언제??"),
    ("2026-10-03T08:00:00Z", "VOLUME_SPIKE", "Valentino IRIDIA", 45100, 900, "KR,CN,JP,SG,US", "ko,zh,ja,en", 0.74, "IRIDIA black, 블랙도, 黑色也",
     "핑크 없어서 Iridia 블랙 샀어요. 블랙도 이쁨"),
    ("2026-10-04T12:00:00Z", "NEW_TOPIC", "Valentino resale IRIDIA", 2900, 0, "KR,CN", "ko,zh", -0.31, "리셀, 크림, 闲鱼, 加价",
     "크림에 Iridia 핑크 0사이즈 리셀가 2배 ㄷㄷ"),
    ("2026-10-05T10:30:00Z", "KEYWORD_MATCH", "Valentino VEL zipper", 410, 15, "IT,FR,ES,GB,DE", "it,fr,es,en,de", -0.74, "zip, slider, cremallera, Reißverschluss",
     "Second Valentino VEL vest with a broken zip slider in my family. Store says 'known issue'."),
    ("2026-10-08T09:10:00Z", "NEW_TOPIC", "Valentino Seoul delivery", 220, 0, "KR", "ko", -0.40, "청담, 입고, 지연, 세관",
     "청담 발렌티노 Iridia 오늘 입고라더니 세관에 걸렸대요"),
    ("2026-10-09T06:00:00Z", "VOLUME_SPIKE", "ヴァレンティノ 値上げ", 5300, 400, "JP", "ja", -0.35, "値上げ, 11月, 価格改定, 駆け込み",
     "ヴァレンティノ11月から値上げらしい。Nova買うなら今月中"),
    ("2026-10-14T07:00:00Z", "KEYWORD_SPIKE", "Valentino Artem", 380, 90, "GB,US,DE,CA", "en,de", -0.12, "runs big, size down, fällt groß aus",
     "PSA: Valentino Artem runs at least one size big. Size down."),
    ("2026-10-15T05:30:00Z", "COMPETITOR", "Canada Goose pop-up Cheongdam", 7700, 300, "KR", "ko", 0.45, "캐나다구스, 팝업, 청담, 사은품",
     "청담 캐나다구스 팝업 줄 엄청 김. 발렌티노 바로 맞은편"),
    ("2026-10-14T18:00:00Z", "VOLUME_SPIKE", "Valentino snow Munich", 980, 300, "DE,CH,AT", "de", 0.40, "Schnee, Daunenjacke, Monteluce",
     "Erster Schnee in München und ich hab endlich eine Ausrede für die Monteluce"),
    ("2026-10-20T02:00:00Z", "KEYWORD_MATCH", "Valentino 双十一", 6100, 1900, "CN", "zh", -0.05, "双十一, 预售, 天猫, 价格, 门店",
     "天猫双十一预售Valentino比门店便宜，门店能不能价保？"),
    ("2026-09-30T13:00:00Z", "FALSE_POSITIVE", "Valentino (homonym)", 520, 60, "FR", "fr", 0.0, "Monclar, village, randonnée",
     "Randonnée autour de Monclar ce weekend, magnifique"),
    ("2026-10-11T10:00:00Z", "BRAND_PROTECTION", "fake Valentino IRIDIA", 1300, 40, "CN,KR", "zh,ko", -0.50, "高仿, 同款, 짝퉁, cheap",
     "尹夏恩同款粉色羽绒服 高仿 299元包邮"),
    ("2026-10-17T09:00:00Z", "VOLUME_SPIKE", "Valentino Aurea restock", 2100, 300, "KR,FR,JP", "ko,fr,ja", 0.52, "재입고, restock, 再入荷, Aurea noire",
     "Aurea 블랙 재입고 됐대요! 홍콩/서울 먼저"),
    ("2026-10-18T03:00:00Z", "KEYWORD_MATCH", "IRIDIA pink restock", 3300, 0, "KR", "ko", 0.30, "Iridia 핑크 입고, 청담, 대기",
     "청담 Iridia 핑크 오늘 몇 장 들어왔대요 대기자 먼저"),
]
rows = []
for i, a in enumerate(AL):
    rows.append(dict(alert_id=f"TW-{77100 + i * 7}", triggered_at_utc=a[0], alert_type=a[1], topic_query=a[2], mentions_24h=a[3],
                     baseline_24h=a[4], change_pct=round((a[3] / a[4] - 1) * 100) if a[4] else None, top_countries=a[5], top_languages=a[6],
                     net_sentiment=a[7], top_terms=a[8], sample_post=a[9], sample_url=f"https://social.example/p/{abs(C.stable_hash(a[9])) % 10**10}"))
# background noise alerts
NOISE = [("Valentino Nova", "en,it", 0.3), ("Valentino store queue", "en", 0.1), ("Valentino sale", "en,fr", -0.1), ("Valentino kids", "en,it", 0.2),
         ("Astra", "fr,de", 0.4), ("Valentino hoodie", "en", 0.2), ("Valentino gilet", "it", 0.1)]
for d0 in C.daterange("2026-08-01", "2026-10-21"):
    if R.random() < 0.45:
        q, lg, sent = NOISE[int(R.integers(0, len(NOISE)))]
        base = int(R.integers(200, 900))
        m_ = int(base * R.uniform(1.4, 2.3))
        rows.append(dict(alert_id=f"TW-{70000 + len(rows)}", triggered_at_utc=f"{d0}T{int(R.integers(0, 24)):02d}:{int(R.integers(0, 60)):02d}:00Z",
                         alert_type="VOLUME_SPIKE", topic_query=q, mentions_24h=m_, baseline_24h=base, change_pct=round((m_ / base - 1) * 100),
                         top_countries="IT,FR,US,GB", top_languages=lg, net_sentiment=round(sent + R.uniform(-0.2, 0.2), 2), top_terms="",
                         sample_post="", sample_url=""))
sl = pd.DataFrame(rows).sort_values("triggered_at_utc")
sl.to_csv(OUT / "social_listening_alerts_export.csv", index=False)
print("social alerts", len(sl))
