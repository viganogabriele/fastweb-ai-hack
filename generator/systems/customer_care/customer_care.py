"""Customer care (Zendesk-like) ticket export + comment threads."""
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R = C.rng("customer_care")
OUT = C.OUT / "customer_care"
OUT.mkdir(parents=True, exist_ok=True)
st = C.stores().set_index("store_id")


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "store_" + re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


STORE_TAG = {sid: slug(st.store_name[sid]) for sid in st.index}
LOCALE = {"it": "it", "fr": "fr", "en": "en-US", "en-GB": "en-GB", "de": "de", "es": "es", "ja": "ja", "ko": "ko", "zh": "zh-cn", "tw": "zh-tw", "hk": "zh-tw"}
GROUP = {"it": "EU Care", "fr": "EU Care", "de": "EU Care", "es": "EU Care", "en-GB": "EU Care", "en": "US Care", "ja": "Japan Care",
         "ko": "Korea Care", "zh": "China Care", "tw": "APAC Care", "hk": "APAC Care"}
AGENTS = {"EU Care": ["Giulia M.", "Pierre D.", "Sarah O.", "Lukas B.", "Carmen R."], "US Care": ["Jasmine T.", "Kevin O."],
          "Japan Care": ["Yuki S.", "Haruto K."], "Korea Care": ["Min-ji P.", "Seo-yeon L."], "China Care": ["Li Na", "Zhang Wei"],
          "APAC Care": ["Karen W.", "Jason T."]}
CHANNELS = {"it": ["email", "web", "chat", "whatsapp", "phone"], "fr": ["email", "web", "chat", "phone"], "de": ["email", "web", "phone"],
            "es": ["email", "web", "whatsapp"], "en": ["email", "web", "chat", "phone", "instagram_dm"], "en-GB": ["email", "web", "chat"],
            "ja": ["email", "web", "line", "phone"], "ko": ["kakaotalk", "web", "email"], "zh": ["wechat", "web"], "tw": ["line", "web", "email"],
            "hk": ["whatsapp", "web", "email"]}
COUNTRY = {"it": "IT", "fr": "FR", "de": "DE", "es": "ES", "en": "US", "en-GB": "GB", "ja": "JP", "ko": "KR", "zh": "CN", "tw": "TW", "hk": "HK"}
REGION = {"IT": "EU", "FR": "EU", "DE": "EU", "ES": "EU", "GB": "EU", "US": "US", "JP": "AP", "KR": "AP", "CN": "AP", "TW": "AP", "HK": "AP"}

# ---------------------------------------------------------------- authored customer messages
# (subject, description) per language; placeholders {sz} {order} {store} {d}
M = {}
M["TIB"] = {
    "it": [("Gilet TIB cerniera rotta", "Buongiorno, ho acquistato un gilet TIB nero a fine agosto ({store}). Dopo neanche un mese il cursore della zip si è staccato. Per un capo da 990 euro mi sembra assurdo. Come procediamo?"),
           ("zip difettosa", "salve il carrello della cerniera del gilet tib si è sfilato, l'ho comprato online ordine {order}. voglio il rimborso non la riparazione"),
           ("RECLAMO TIB", "Secondo gilet TIB in famiglia con la zip rotta!!! Mio marito e mio figlio, comprati a settembre. Inaccettabile."),
           ("Gilet uomo - problema zip", "Gentili, allego foto: il tirazip del gilet si muove ma non chiude più. Taglia {sz}. Grazie")],
    "fr": [("Zip cassé gilet TIB", "Bonjour, la tirette de mon gilet TIB s'est détachée après 3 semaines. Acheté à {store}. Que proposez-vous ?"),
           ("Problème fermeture éclair", "Commande {order}. Le curseur du zip ne tient pas. Je souhaite un remboursement."),
           ("gilet tib défectueux", "le zip du gilet ne remonte plus, la pièce métallique est partie. pas content du tout")],
    "en-GB": [("TIB gilet zip broken", "Hi, the zip slider on my TIB gilet came off completely, bought in {store} in September. Is this a known problem? Size {sz}."),
              ("Faulty zip - order {order}", "Zip pull detached on first wear basically. Want a refund please, not a repair that takes 6 weeks.")],
    "en": [("Zipper broke on TIB vest", "My TIB vest zipper slider came off after a couple weeks. Order {order}. For $1,000+ this is really disappointing."),
           ("TIB vest defect", "Hi - bought the TIB at {store}, zipper doesn't lock anymore and the slider pops off. What are my options?")],
    "de": [("Reißverschluss TIB Weste defekt", "Guten Tag, bei meiner TIB Weste ist der Schieber vom Reißverschluss abgegangen. Gekauft im September online, Bestellung {order}. Bitte um Erstattung."),
           ("TIB kaputt", "Schieber weg, Weste nicht mehr zu schließen. Größe {sz}.")],
    "es": [("Cremallera chaleco TIB", "Hola, la cremallera de mi chaleco TIB se ha roto (el cursor se salió). Lo compré en {store}. Quiero devolverlo.")],
    "ja": [("TIBベスト ファスナー不良", "先月購入したTIBベストのファスナーのスライダーが外れてしまいました。注文番号 {order}。返品・返金を希望します。")],
    "ko": [("TIB 조끼 지퍼 불량", "TIB 조끼 지퍼 손잡이가 빠졌어요. 산 지 한 달도 안 됐는데요. 환불 가능한가요?")],
    "zh": [("TIB马甲拉链坏了", "你好，我在官网买的TIB马甲，拉链头掉了，订单号{order}，要求退款。")],
}
M["ARNEB"] = {
    "it": [("Arneb taglia", "Ho preso l'Arneb in {sz} come sempre ma è enorme. Posso cambiarlo con una taglia in meno? ordine {order}"),
           ("cambio taglia parka", "il parka arneb veste molto grande, vorrei la taglia sotto")],
    "fr": [("Arneb trop grand", "Bonjour, la parka Arneb taille {sz} est beaucoup trop grande, je fais normalement du {sz}. Échange possible ?")],
    "en": [("Arneb sizing", "Ordered my usual size {sz} in the Arneb parka and it's huge in the shoulders. Does it run large? Exchange for one size down?"),
           ("exchange Arneb", "Need to exchange Arneb for smaller size. Order {order}.")],
    "en-GB": [("Arneb fits big", "Arneb arrived, way too big. Your size guide says {sz} for my chest. Can I swap?")],
    "de": [("Arneb Größe", "Der Arneb Parka fällt sehr groß aus. Umtausch in eine Größe kleiner bitte. Bestellnummer {order}")],
    "ja": [("アルネブ サイズ交換", "アルネブを購入しましたが、思ったより大きいです。ワンサイズ下に交換できますか？")],
    "ko": [("아르넵 사이즈 교환", "아르넵 사이즈가 너무 크게 나왔어요. 한 사이즈 작은 걸로 교환 부탁드려요.")],
    "zh": [("ARNEB 尺码", "ARNEB派克太大了，平时穿{sz}，能换小一码吗？")],
}
M["ILVPINK"] = {
    "ko": [("일바로 핑크 재입고", "일바로 핑크 {sz} 사이즈 재입고 언제 되나요?? 알림 신청했는데 연락이 없어요"),
           ("윤하은 패딩", "윤하은이 입은 핑크 패딩 일바로 맞죠? 온라인에서 언제 다시 살 수 있나요"),
           ("재입고 문의", "공홈에서 7시 반에 들어갔는데 이미 품절… 다음 입고 날짜 알려주세요. {sz} 사이즈요"),
           ("청담 매장 대기", "청담점에 일바로 핑크 대기 걸어놨는데 순번이 어떻게 되나요? 언제 받을 수 있는지"),
           ("일바로 핑크 0", "0 사이즈 하나만 구해주세요 ㅠㅠ 선물용이에요"), ("품절 너무 빨라요", "알림 받고 들어갔는데 바로 품절. 이게 말이 되나요?")],
    "ja": [("イルヴァロ ピンク 再入荷", "イルヴァロのピンク、サイズ{sz}の再入荷予定を教えてください。"),
           ("ピンクのダウン", "ユン・ハウンさんが着ていたピンクのダウンはどこで買えますか？オンラインは売り切れです。"),
           ("再入荷通知", "再入荷通知を登録しましたが、本当に連絡来ますか？")],
    "zh": [("ILVARO粉色补货", "尹夏恩同款粉色ILVARO什么时候补货？{sz}码"), ("粉色羽绒服", "请问粉色ILVARO 什么时候有货，可以预订吗"),
           ("缺货", "微信小程序一直显示缺货，门店也没有，到底什么时候到？")],
    "tw": [("ILVARO 粉紅色", "請問 ILVARO 粉紅色 {sz} 號什麼時候會再到貨？"), ("預購", "可以預購粉色ILVARO嗎")],
    "hk": [("ILVARO pink restock", "Hi when will ILVARO pink be back? size {sz}. Canton Road said no stock"), ("粉紅色ILVARO", "請問粉紅色 ILVARO 幾時有返貨？")],
    "en": [("Pink Ilvaro", "Is the Ilvaro in powder pink coming back? Size {sz}. I signed up for notify me."),
           ("restock Ilvaro pink", "the pink one Yoon Ha-eun wore - when is the restock? sold out everywhere")],
    "en-GB": [("Ilvaro powder pink", "Any chance of Ilvaro pink in {sz} in London? Website sold out.")],
    "fr": [("Ilvaro rose", "Bonjour, la doudoune Ilvaro rose poudré sera-t-elle réassortie en {sz} ?")],
    "it": [("Ilvaro rosa", "Buongiorno, quando torna disponibile l'Ilvaro rosa cipria taglia {sz}?")],
}
M["ILVBLK"] = {
    "ko": [("일바로 블랙", "핑크 없으면 블랙이라도… 일바로 블랙 {sz} 언제 입고돼요?")], "zh": [("ILVARO黑色", "ILVARO 黑色{sz}码也缺货了吗？")],
    "en": [("Ilvaro black", "Ilvaro black size {sz} showing sold out, when back?")], "ja": [("イルヴァロ 黒", "イルヴァロの黒 {sz} も在庫なしですか")],
}
M["MAIRE"] = {
    "ko": [("마이레 블랙", "마이레 블랙 {sz} 사이즈 언제 재입고 되나요? 파리 매장에도 없었어요"), ("마이레 검정 재입고", "드라마에 나온 마이레 블랙 재입고 알림 부탁드려요")],
    "fr": [("Maire noire", "Bonjour, la Maire noire en {sz} est indisponible partout, réassort prévu ?"), ("Maire noir rupture", "Pourquoi la Maire noire est en rupture depuis des semaines ?")],
    "en-GB": [("Maire black", "Is the Maire in black coming back in {sz}? Harrods said end of October")],
    "en": [("Maire black restock", "When will Maire black size {sz} be available online?")],
    "it": [("Maire nera", "Buongiorno, la Maire nera taglia {sz} quando torna? Il negozio di Montenapoleone non ce l'ha")],
    "ja": [("マイレ 黒", "マイレの黒 {sz} 再入荷予定はありますか")], "zh": [("Maire黑色", "Maire 黑色 {sz}码 什么时候有货")],
}
M["AMB"] = {"it": [("Ambrine marrone", "Vorrei l'Ambrine marrone in {sz}, ovunque esaurita. Quando arriva?")],
            "fr": [("Ambrine marron", "L'Ambrine marron chocolat en {sz} sera disponible quand ?")],
            "en-GB": [("Ambrine brown", "Ambrine in brown size {sz}, sold out online - restock date?")], "es": [("Ambrine marrón", "¿Cuándo vuelve el Ambrine marrón talla {sz}?")]}
M["LCM"] = {"it": [("Cardigan logo M", "Cerco il cardigan con logo taglia M, sul sito non c'è e in negozio nemmeno")],
            "en-GB": [("Logo cardigan medium", "Logo cardigan in M sold out - will it come back?")], "fr": [("Cardigan M", "Le cardigan logo en M est indisponible ?")]}
M["DELAY"] = {
    "it": [("Ordine in ritardo", "Il mio ordine {order} doveva arrivare ieri, il tracking è fermo da 3 giorni"), ("dove è il mio pacco", "ordine {order} ancora in transito???")],
    "fr": [("Retard de livraison", "Ma commande {order} n'est toujours pas arrivée, le suivi indique 'incident'")],
    "en": [("Where is my order", "Order {order} still says in transit, it was supposed to be here Monday"), ("late delivery", "Tracking hasn't updated since Friday. Order {order}.")],
    "en-GB": [("Delivery delay", "Order {order} - DHL says held, why?")], "de": [("Lieferung verspätet", "Bestellung {order} immer noch nicht da")],
    "ja": [("配送遅延", "注文{order}がまだ届きません")], "zh": [("物流太慢", "订单{order}一直在清关，什么时候能到？")],
    "ko": [("청담 예약 상품", "청담점에서 예약한 상품이 세관 때문에 늦어진다고 들었어요. 언제 받을 수 있나요?"),
           ("배송 지연", "주문 {order} 배송이 너무 늦어요")],
}
M["JPPRICE"] = {"ja": [("価格改定について", "11月1日の価格改定前に注文すれば旧価格になりますか？"), ("値上げ前の予約", "店舗で取り置きしている商品は旧価格で購入できますか？"),
                       ("値上げ", "マヤの値上げ後の価格を教えてください"), ("価格改定のお知らせ", "お手紙をいただきましたが、オンラインも同じく11/1からですか")]}
M["D11"] = {"zh": [("双十一价格", "天猫双十一预售价比门店便宜，门店可以按天猫价格吗？"), ("价保", "我上周在门店买的，现在天猫预售更便宜，能退差价吗"),
                   ("双11", "官网小程序有双十一活动吗")]}
M["POLARIS_EU"] = {"fr": [("Polaris taille", "La Polaris oversize taille {sz} est petite, est-ce normal ?")],
                   "it": [("Polaris vestibilità", "Il piumino Polaris veste piccolo, per essere oversize. Reso possibile?")],
                   "en": [("Polaris fit", "Polaris oversized runs small? Size {sz} feels tight")], "de": [("Polaris zu klein", "Polaris fällt klein aus, Rücksendung bitte")]}
M["POLARIS_CN"] = {"zh": [("Polaris 斗篷", "Polaris 斗篷白色还有货吗？"), ("Genius Polaris", "Polaris 羽绒服 M码 上海门店有吗")],
                   "hk": [("Polaris", "Polaris cape 仲有冇貨?")]}
BG = {
    "it": [("Info riparazione", "Il mio piumino ha un piccolo strappo sulla manica, fate riparazioni?"), ("Fattura", "Mi servirebbe la fattura con partita IVA per l'ordine {order}"),
           ("Reso", "Vorrei restituire l'ordine {order}, come faccio?"), ("Appuntamento", "Vorrei prenotare un appuntamento a {store} sabato"),
           ("Autenticità", "Ho comprato un Maya usato, come verifico se è originale?"), ("lavaggio piumino", "Come si lava il piumino? lavatrice?")],
    "fr": [("Détaxe", "Je n'ai pas reçu le remboursement de la détaxe de mon achat à {store}"), ("Retour", "Comment retourner la commande {order} ?"),
           ("Entretien", "Comment nettoyer une doudoune Moncler ?"), ("Compte", "Je n'arrive pas à me connecter à mon compte"),
           ("Emballage cadeau", "Est-il possible d'avoir un emballage cadeau ?")],
    "en": [("Return label", "Can you send me a return label for {order}?"), ("Repair", "Down leaking from my jacket seam, repair options?"),
           ("Account", "Password reset email never arrives"), ("Gift card", "Gift card balance?"), ("Fake check", "Is this seller on eBay legit?"),
           ("Order status", "When will order {order} ship?"), ("Store hours", "Is {store} open on Sunday?")],
    "en-GB": [("Refund not received", "Returned {order} two weeks ago, no refund yet"), ("Repair", "Zip on my Maya (5 years old) broken, can you repair?"),
              ("VAT", "Do you ship to Jersey without VAT?")],
    "de": [("Rücksendung", "Wie kann ich {order} zurückschicken?"), ("Reinigung", "Kann ich die Daunenjacke in die Reinigung geben?"), ("Rechnung", "Bitte Rechnung für {order}")],
    "es": [("Devolución", "Quiero devolver el pedido {order}"), ("Tax free", "No he recibido el reembolso tax free"), ("Cita", "Quisiera una cita en {store}")],
    "ja": [("返品について", "注文{order}を返品したいです"), ("お手入れ", "ダウンのクリーニング方法を教えてください"), ("修理", "ボタンが取れました。修理できますか"),
           ("ギフト包装", "ギフトラッピングはできますか")],
    "ko": [("교환 문의", "사이즈 교환하고 싶어요"), ("정품 확인", "중고로 산 마야 정품인지 확인 가능한가요"), ("세탁", "패딩 세탁 방법 알려주세요"), ("매장 방문 예약", "청담점 방문 예약하고 싶어요")],
    "zh": [("发票", "订单{order}需要开发票"), ("退货", "怎么退货"), ("真假", "代购买的Maya怎么验真"), ("会员", "会员积分怎么查")],
    "tw": [("退貨", "請問如何退貨"), ("營業時間", "台北101 週日營業嗎")],
    "hk": [("Repair", "件褸有個窿, 可唔可以整?"), ("退款", "退咗貨未收到退款")],
}
CAT = {"TIB": "product_defect", "ARNEB": "size_fit", "ILVPINK": "product_availability", "ILVBLK": "product_availability",
       "MAIRE": "product_availability", "AMB": "product_availability", "LCM": "product_availability", "DELAY": "delivery_delay",
       "JPPRICE": "price_inquiry", "D11": "price_inquiry", "POLARIS_EU": "size_fit", "POLARIS_CN": "product_availability"}
STYLE = {"TIB": ("TIB", "J10911A00305-999"), "ARNEB": ("ARNEB", "J10911A00577-999"), "ILVPINK": ("ILVARO", "J20931A00618-510"),
         "ILVBLK": ("ILVARO", "J20931A00618-999"), "MAIRE": ("MAIRE", "J20931A00012-999"), "AMB": ("AMBRINE", "J20931A00622-23R"),
         "LCM": ("LOGO CARDIGAN", "I10919B00011-999"), "POLARIS_EU": ("POLARIS OVERSIZED", "G20921A00902-999"),
         "POLARIS_CN": ("POLARIS CAPE", "G20921A00901-001")}
TAGS = {"TIB": [["zip_defect"], ["zipper"], ["cerniera"], ["tib_zip"], ["defect", "zipper"]], "ARNEB": [["size_exchange", "arneb"], ["fit_large"]],
        "ILVPINK": [["restock", "ilvaro"], ["notify_me", "ilvaro_pink"], ["oos"]], "ILVBLK": [["restock"]], "MAIRE": [["restock", "maire"], ["oos"]],
        "AMB": [["restock"]], "LCM": [["oos"]], "DELAY": [["wismo"], ["delay", "carrier"]], "JPPRICE": [["price_increase"]], "D11": [["price_match", "d11"]],
        "POLARIS_EU": [["fit_small", "genius"]], "POLARIS_CN": [["genius"]]}

# volume schedule: (signal, langs weights, start, end, total, shape)
SCHED = [
    ("TIB", {"it": 5, "fr": 3, "en-GB": 2, "en": 2, "de": 2, "es": 2, "ja": 1, "ko": 1, "zh": 1}, "2026-09-25", "2026-10-21", 85, "ramp"),
    ("ARNEB", {"en": 3, "en-GB": 2, "de": 2, "it": 2, "fr": 2, "ja": 1, "ko": 1, "zh": 1}, "2026-09-10", "2026-10-21", 38, "flat"),
    ("ILVPINK", {"ko": 8, "ja": 4, "zh": 5, "tw": 2, "hk": 2, "en": 2, "en-GB": 1, "fr": 1, "it": 1}, "2026-10-02", "2026-10-21", 190, "decay"),
    ("ILVBLK", {"ko": 2, "zh": 2, "en": 1, "ja": 1}, "2026-10-04", "2026-10-21", 22, "flat"),
    ("MAIRE", {"ko": 3, "fr": 3, "en-GB": 2, "it": 2, "en": 1, "ja": 1, "zh": 1}, "2026-09-16", "2026-10-17", 58, "flat"),
    ("AMB", {"it": 2, "fr": 2, "en-GB": 1, "es": 1}, "2026-09-20", "2026-10-21", 16, "flat"),
    ("LCM", {"it": 2, "en-GB": 1, "fr": 1}, "2026-10-05", "2026-10-21", 9, "flat"),
    ("DELAY", {"it": 2, "fr": 2, "en": 3, "en-GB": 2, "de": 1, "ja": 1, "zh": 2, "ko": 2}, "2026-08-01", "2026-10-21", 70, "flat"),
    ("JPPRICE", {"ja": 1}, "2026-10-09", "2026-10-21", 28, "decay"),
    ("D11", {"zh": 1}, "2026-10-18", "2026-10-22", 16, "flat"),
    ("POLARIS_EU", {"fr": 2, "it": 2, "en": 2, "de": 1}, "2026-09-26", "2026-10-21", 15, "flat"),
    ("POLARIS_CN", {"zh": 3, "hk": 1}, "2026-09-22", "2026-10-15", 12, "decay"),
]
BG_W = {"it": 10, "fr": 8, "en": 14, "en-GB": 7, "de": 5, "es": 4, "ja": 7, "ko": 6, "zh": 7, "tw": 2, "hk": 2}
SIZES = {"TIB": ["2", "3", "4", "5"], "ARNEB": ["3", "4", "5", "6"], "ILVPINK": ["00", "0", "1", "2"], "ILVBLK": ["0", "1", "2"],
         "MAIRE": ["0", "1", "2"], "AMB": ["0", "1", "2"], "LCM": ["M"], "POLARIS_EU": ["S", "M", "L"], "POLARIS_CN": ["M"]}
LANG_STORES = {"it": ["MIL01", "MIL02", "ROM01", "VEN01"], "fr": ["PAR01", "PAR02", "CAN01", "GVA01"], "en-GB": ["LON01", "LON02"],
               "en": ["NYC01", "NYC02", "BHS01", "MIA01"], "de": ["MUN01", "BER01", "ZRH01"], "es": ["MAD01"], "ja": ["TYO01", "TYO02", "OSA01"],
               "ko": ["SEL01", "SEL02", "BUS01"], "zh": ["SHA01", "BJS01", "CDU01"], "tw": ["TPE01"], "hk": ["HKG01"]}


OPEN = {"it": ["", "", "Buongiorno, ", "Salve, ", "Gentile servizio clienti, ", "Buonasera. ", "Ciao, "],
        "fr": ["", "", "Bonjour, ", "Bonsoir, ", "Madame, Monsieur, ", "Bonjour,\n"],
        "en": ["", "", "Hi, ", "Hello, ", "Hi there - ", "Good morning, "], "en-GB": ["", "", "Hi, ", "Hello, ", "Good afternoon, "],
        "de": ["", "Guten Tag, ", "Hallo, ", "Sehr geehrte Damen und Herren, "], "es": ["", "Hola, ", "Buenos días, "],
        "ja": ["", "お世話になっております。", "こんにちは。", "突然のご連絡失礼いたします。"], "ko": ["", "", "안녕하세요. ", "문의드립니다. "],
        "zh": ["", "", "你好，", "您好，"], "tw": ["", "您好，"], "hk": ["", "Hi, ", "你好, "]}
CLOSE = {"it": ["", "", " Grazie", " Grazie mille.", " Cordiali saluti", " attendo vostre notizie", " Grazie, buona giornata"],
         "fr": ["", "", " Merci", " Cordialement", " Merci d'avance.", " Bonne journée"],
         "en": ["", "", " Thanks", " Thank you!", " Thanks in advance", " Regards"], "en-GB": ["", "", " Thanks", " Many thanks", " Kind regards"],
         "de": ["", " Danke", " Mit freundlichen Grüßen", " Vielen Dank"], "es": ["", " Gracias", " Un saludo"],
         "ja": ["", "よろしくお願いいたします。", "ご確認お願いします。"], "ko": ["", "", " 감사합니다.", " 답변 부탁드려요", " 빠른 답변 부탁드립니다"],
         "zh": ["", "", "谢谢", "麻烦尽快回复", "谢谢！"], "tw": ["", "謝謝"], "hk": ["", " thx", " 唔該"]}
EXTRA = {
    "ILVPINK": {"ko": ["선물용이에요.", "다른 색은 생각 없어요.", "매장에도 전화했는데 없대요.", "해외 매장이라도 괜찮아요.", "알림 문자 왔는데 들어가니까 품절."],
                "ja": ["プレゼント用です。", "店舗にも問い合わせましたが在庫なしでした。", "黒ではなくピンクが欲しいです。"],
                "zh": ["是送人的。", "其他颜色不考虑。", "门店说要等很久。", "代购价格太离谱了。"],
                "en": ["It's a gift.", "Happy to pick up in any store.", "Black isn't the same."], "en-GB": ["Happy to travel to Harrods."],
                "fr": ["C'est pour un cadeau."], "it": ["È per un regalo."], "tw": ["送禮用"], "hk": ["送禮用"]},
    "TIB": {"it": ["Ho lo scontrino.", "Allego foto.", "Usato pochissimo."], "fr": ["J'ai le ticket.", "Photos jointes."],
            "en": ["Photos attached.", "Barely worn."], "en-GB": ["Photos attached.", "Worn maybe 5 times."], "de": ["Fotos anbei."],
            "es": ["Tengo el ticket."], "ja": ["写真を添付します。"], "ko": ["사진 첨부합니다."], "zh": ["附照片。"]},
    "MAIRE": {"ko": ["파리 여행 중이에요.", "서울 매장도 없대요."], "fr": ["Je suis passée deux fois en boutique."], "en-GB": ["Harrods had nothing either."],
              "it": ["Sono passata due volte."], "en": ["Checked two stores already."]},
}


def compose(sig, lang, core):
    o = str(R.choice(OPEN.get(lang, [""])))
    c = str(R.choice(CLOSE.get(lang, [""])))
    ex = EXTRA.get(sig, {}).get(lang)
    mid = (" " + str(R.choice(ex))) if ex and R.random() < 0.45 else ""
    txt = f"{o}{core}{mid}{c}".strip()
    if lang in ("it", "fr", "en", "en-GB", "es") and R.random() < 0.12:
        txt = txt.lower()
    return txt


def wchoice(d):
    ks = list(d)
    w = np.array([d[k] for k in ks], dtype=float)
    return ks[int(R.choice(len(ks), p=w / w.sum()))]


def order_no(lang):
    return f"MC-{REGION[COUNTRY[lang]]}-26-0{int(R.integers(400000, 499999))}"


tickets = []
tid = [418200]


def make(sig, lang, day):
    pool = (M[sig] if sig != "BG" else BG).get(lang)
    if not pool:
        return
    subj, desc = pool[int(R.integers(0, len(pool)))]
    store = str(R.choice(LANG_STORES[lang]))
    sz = str(R.choice(SIZES.get(sig, ["M"])))
    o = order_no(lang)
    desc = desc.format(sz=sz, order=o, store=st.store_name[store] if R.random() < 0.6 else str(R.choice(C.STORE_ALIASES[store])), d="")
    desc = compose(sig, lang, desc)
    subj = subj.format(sz=sz, order=o)
    ch = str(R.choice(CHANNELS[lang]))
    if ch in ("chat", "whatsapp", "kakaotalk", "line", "wechat", "instagram_dm") and R.random() < 0.3:
        desc += " " + str(R.choice(["🙏", "😭", "😡", "??", "!!", "😢", "ㅠㅠ" if lang == "ko" else "..."]))
    tz = {"it": 2, "fr": 2, "de": 2, "es": 2, "en-GB": 1, "en": -4, "ja": 9, "ko": 9, "zh": 8, "tw": 8, "hk": 8}[lang]
    local_h = int(R.integers(7, 24))
    created = dt.datetime.combine(day, dt.time(local_h, int(R.integers(0, 60)), int(R.integers(0, 60)))) - dt.timedelta(hours=tz)
    if sig == "ILVPINK" and day == dt.date(2026, 10, 2):
        created = dt.datetime.combine(day, dt.time(int(R.integers(7, 12)), int(R.integers(0, 60)))) - dt.timedelta(hours=tz)
    cutoff = dt.datetime(2026, 10, 22, 6, 40)
    if created > cutoff:
        created = cutoff - dt.timedelta(minutes=int(R.integers(5, 400)))
    tid[0] += int(R.integers(1, 6))
    grp = GROUP[lang]
    cat = CAT.get(sig, "")
    if sig == "BG":
        cat = str(R.choice(["order_status", "returns_refund", "repair_care", "other", "store_experience", "returns_refund", "order_status"]))
    age = (dt.datetime(2026, 10, 22, 7, 0) - created).total_seconds() / 3600
    if age < 20:
        status = str(R.choice(["new", "open"]))
    elif age < 72:
        status = str(R.choice(["open", "pending", "solved"]))
    else:
        status = str(R.choice(["solved", "closed", "closed", "pending"]))
    solved = created + dt.timedelta(hours=float(R.uniform(2, 70))) if status in ("solved", "closed") else None
    updated = solved or (created + dt.timedelta(hours=float(R.uniform(0.05, max(0.1, min(age, 90))))))
    tags = list(TAGS.get(sig, [[]])[int(R.integers(0, len(TAGS.get(sig, [[]]))))]) if sig != "BG" else []
    style, sku = STYLE.get(sig, ("", ""))
    sku_txt = ""
    if sku:
        u = R.random()
        sku_txt = f"{sku}-{sz}" if u < 0.35 else (sku if u < 0.55 else "")
    store_field = STORE_TAG[store] if R.random() < 0.35 or sig in ("TIB",) and R.random() < 0.5 else ""
    tickets.append(dict(Id=tid[0], Subject=subj, Status=status, Priority=str(R.choice(["low", "normal", "normal", "normal", "high"])) if sig != "TIB" else str(R.choice(["normal", "high"])),
                        Requester=f"Customer {int(R.integers(10000, 99999))}", **{"Requester locale": LOCALE[lang]},
                        **{"Created at": created.strftime("%Y-%m-%d %H:%M:%S"), "Updated at": updated.strftime("%Y-%m-%d %H:%M:%S"),
                           "Solved at": solved.strftime("%Y-%m-%d %H:%M:%S") if solved else ""},
                        Channel=ch, Group=grp, Assignee=str(R.choice(AGENTS[grp])) if status != "new" else "", Tags=" ".join(tags),
                        **{"Category [list]": cat, "Product/Style [txt]": style if R.random() < 0.7 else "", "SKU [txt]": sku_txt,
                           "Store [list]": store_field, "Order number [txt]": o if ("{order}" in str(pool) or sig in ("DELAY",)) and R.random() < 0.8 else "",
                           "Country [list]": COUNTRY[lang]},
                        Satisfaction=str(R.choice(["offered", "unoffered", "good", "bad"])) if status in ("solved", "closed") else "unoffered",
                        Description=desc, _sig=sig, _lang=lang, _day=day))


for sig, langs, a, b, total, shape in SCHED:
    days = list(C.daterange(a, b))
    n = len(days)
    if shape == "ramp":
        w = np.linspace(0.3, 1.6, n)
    elif shape == "decay":
        w = np.array([0.5 ** (i / 4) + 0.12 for i in range(n)])
    else:
        w = np.ones(n)
    counts = R.multinomial(total, w / w.sum())
    for day, c in zip(days, counts):
        for _ in range(int(c)):
            make(sig, wchoice(langs), day)
for day in C.daterange("2026-08-01", "2026-10-22"):
    n = int(R.poisson(9 if day.weekday() < 5 else 6))
    if day == dt.date(2026, 10, 22):
        n = 3
    for _ in range(n):
        make("BG", wchoice(BG_W), day)

tk = pd.DataFrame(tickets)
# --- quirks
# mis-categorised defect tickets
m = tk[(tk._sig == "TIB")].sample(14, random_state=2).index
tk.loc[m, "Category [list]"] = [str(R.choice(["other", "returns_refund", ""])) for _ in m]
# empty category
m = tk.sample(frac=0.04, random_state=3).index
tk.loc[m, "Category [list]"] = ""
# duplicates: same customer two channels; one merged/closed
dups = tk[tk._sig.isin(["ILVPINK", "TIB", "DELAY"])].sample(18, random_state=4).copy()
dups["Id"] = [tid[0] + 50 + 3 * i for i in range(len(dups))]
dups["Channel"] = "email"
dups["Status"] = "closed"
dups["Tags"] = (dups.Tags + " merged").str.strip()
dups["Created at"] = (pd.to_datetime(dups["Created at"]) + pd.to_timedelta(R.integers(5, 300, len(dups)), unit="m")).dt.strftime("%Y-%m-%d %H:%M:%S")
tk = pd.concat([tk, dups])
# late import batch: kakaotalk tickets of Oct 3-4 imported on Oct 6 with Created at = import time
m = tk[(tk.Channel == "kakaotalk") & (tk._day.isin([dt.date(2026, 10, 3), dt.date(2026, 10, 4)]))].index
tk.loc[m, "Created at"] = "2026-10-06 01:12:44"
tk.loc[m, "Tags"] = (tk.loc[m, "Tags"] + " kakao_import").str.strip()
# agent who writes store names his own way
m = tk[(tk.Assignee == "Pierre D.") & (tk["Store [list]"] != "")].index
tk.loc[m, "Store [list]"] = tk.loc[m, "Store [list]"].str.replace("store_", "boutique-", regex=False).str.replace("_", "-")
tk = tk.sort_values("Created at")
tk.drop(columns=["_sig", "_lang", "_day"]).to_csv(OUT / "zendesk_tickets_export_2026-08-01_2026-10-22.csv", index=False)
print("tickets", len(tk), tk._sig.value_counts().to_dict())

# ---------------------------------------------------------------- comment threads (macros + follow ups)
MAC = {
    ("ILVPINK", "early"): {"ko": "안녕하세요 고객님, 문의하신 일바로 핑크는 현재 전 사이즈 품절입니다. 재입고 일정은 아직 확정되지 않았으며, 재입고 알림을 신청해 주시면 가장 먼저 안내드리겠습니다.",
                           "ja": "お問い合わせありがとうございます。イルヴァロ ピンクは現在完売しており、再入荷時期は未定でございます。再入荷通知のご登録をお願いいたします。",
                           "zh": "您好，ILVARO粉色目前全线售罄，补货时间暂未确定，请您在小程序登记到货提醒。",
                           "en": "Thank you for contacting us. The Ilvaro in powder pink is currently sold out and we don't have a confirmed restock date yet. Please sign up to 'notify me'."},
    ("ILVPINK", "late"): {"ko": "고객님, 일바로 핑크는 10월 말 재입고 예정입니다. 알림 신청 부탁드립니다.",
                          "ja": "イルヴァロ ピンクは11月中旬以降の入荷予定です。",
                          "zh": "您好，粉色ILVARO预计11月下旬到货。",
                          "en": "We expect new stock of the pink Ilvaro by the end of October."},
    ("TIB", "early"): {"it": "Gentile cliente, ci dispiace per l'inconveniente. Può inviarci delle foto del difetto e la prova d'acquisto? Valuteremo una riparazione.",
                       "en": "We're sorry to hear that. Could you send photos of the zip and proof of purchase? Our atelier will assess a repair.",
                       "fr": "Nous sommes désolés. Pourriez-vous nous envoyer des photos et la preuve d'achat ? Nous étudierons une réparation."},
    ("TIB", "late"): {"it": "Gentile cliente, abbiamo identificato un problema di qualità su un lotto limitato del gilet TIB. Le offriamo rimborso completo o sostituzione con un capo di un nuovo lotto. Le inviamo un'etichetta di reso.",
                      "en": "We have identified a quality issue affecting a limited batch of TIB vests. We can offer a full refund or a replacement from a new batch. A prepaid return label is attached.",
                      "fr": "Nous avons identifié un problème de qualité sur un lot limité du gilet TIB. Nous vous proposons un remboursement complet ou un échange. Étiquette retour jointe."},
    ("ARNEB", "any"): {"en": "The Arneb has a generous fit: we recommend choosing one size down. We'll be happy to exchange it.",
                       "it": "L'Arneb ha una vestibilità abbondante: consigliamo una taglia in meno. Procediamo con il cambio.",
                       "de": "Der Arneb fällt großzügig aus, wir empfehlen eine Größe kleiner. Gerne tauschen wir um."},
    ("JPPRICE", "any"): {"ja": "11月1日より価格改定を実施いたします。10月31日までにご注文・ご決済いただいた商品は現行価格でのご提供となります。店舗でのお取り置き商品も、10月31日までにお受け取りいただければ現行価格となります。"},
    ("D11", "any"): {"zh": "您好，门店与天猫旗舰店价格体系不同，门店暂不提供双十一价格匹配，敬请谅解。"},
    ("DELAY", "any"): {"en": "We apologise for the delay. The carrier has informed us of a temporary delay; your parcel should be delivered within 2-3 business days.",
                       "ko": "고객님, 통관 지연으로 입고가 늦어지고 있습니다. 청담점 입고 후 바로 연락드리겠습니다.",
                       "it": "Ci scusiamo per il ritardo, il corriere ha segnalato un rallentamento. Il pacco sarà consegnato entro 2-3 giorni lavorativi."},
}
threads = {}
sample = tk[tk._sig.isin(["ILVPINK", "TIB", "ARNEB", "JPPRICE", "D11", "DELAY", "MAIRE", "POLARIS_EU"])].sample(150, random_state=9)
from types import SimpleNamespace
for rr in sample.to_dict("records"):
    r = SimpleNamespace(Id=rr["Id"], Assignee=rr["Assignee"] if isinstance(rr["Assignee"], str) else "", Description=rr["Description"])
    sig, lang, day = rr["_sig"], rr["_lang"], rr["_day"]
    phase = "late" if (sig == "TIB" and day >= dt.date(2026, 10, 3)) or (sig == "ILVPINK" and day >= dt.date(2026, 10, 9) and R.random() < 0.5) else "early"
    key = (sig, phase) if (sig, phase) in MAC else (sig, "any")
    mac = MAC.get(key, {})
    lg = {"en-GB": "en", "tw": "zh", "hk": "zh"}.get(lang, lang)
    reply = mac.get(lg) or mac.get("en") or "Thank you for your message, we are looking into it."
    t0 = pd.to_datetime(tk.loc[tk.Id == r.Id, "Created at"].iloc[0])
    th = [dict(author="end-user", public=True, created_at=t0.strftime("%Y-%m-%dT%H:%M:%SZ"), body=r.Description),
          dict(author=r.Assignee or "Auto-reply", public=True, created_at=(t0 + pd.Timedelta(hours=float(R.uniform(0.5, 30)))).strftime("%Y-%m-%dT%H:%M:%SZ"),
               body=reply, via_macro=f"{sig.lower()}_{phase}")]
    if R.random() < 0.4:
        fu = {"ko": "알림 신청했는데 계속 품절이에요. 다른 매장 재고라도 확인해 주세요", "ja": "ありがとうございます。店舗在庫も確認いただけますか",
              "zh": "好的，那门店有没有？", "it": "Ok, procedo con il reso. Grazie", "fr": "D'accord, merci.", "en": "Ok thanks. Any store that has it?",
              "en-GB": "Fine. Can a store check?", "de": "Danke.", "es": "Gracias.", "tw": "好的謝謝", "hk": "OK 唔該"}.get(lang, "ok")
        th.append(dict(author="end-user", public=True, created_at=(t0 + pd.Timedelta(hours=float(R.uniform(31, 60)))).strftime("%Y-%m-%dT%H:%M:%SZ"), body=fu))
    if sig == "TIB" and R.random() < 0.5:
        th.append(dict(author=r.Assignee or "agent", public=False, created_at=(t0 + pd.Timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                       body=f"internal: batch check - customer unit in QN {C.TIB['qn']} scope? purchase date after mid-Aug -> yes"))
    threads[str(r.Id)] = th
with open(OUT / "zendesk_ticket_comments_sample.json", "w", encoding="utf-8") as f:
    json.dump(threads, f, ensure_ascii=False, indent=1)
print("threads", len(threads))
