"""Format hand-written chat data into realistic export files.
Run: .venv/bin/python generator/internal_comms/chats/build.py
"""
import datetime as dt
import hashlib
import importlib
import json
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from common import OUT, check_texts  # noqa: E402

D = OUT / "chat_exports"
D.mkdir(parents=True, exist_ok=True)
TEXTS = {}


def _key_android(ts, fmt):
    if fmt == "android_fr":
        return dt.datetime.strptime(ts, "%d/%m/%Y %H:%M")
    return dt.datetime.strptime(ts, "%d/%m/%y, %H:%M")


def collect(mod):
    for i, (ts, a, t) in enumerate(mod.MSGS):
        if a is not None and isinstance(t, str) and len(t.split()) > 8:
            TEXTS[f"{mod.__name__}:{i}"] = t


def whatsapp_android(mod):
    fmt = mod.FORMAT
    msgs = sorted(mod.MSGS, key=lambda m: _key_android(m[0], fmt))  # stable sort
    lines = []
    for ts, a, t in msgs:
        if fmt == "android_es":
            ts = ts  # already d/m/yy
        sep = " - "
        if a is None:
            lines.append(f"{ts}{sep}{t}")
        elif t.startswith(("Marco ha aggiunto", "Lucía añadió")):
            lines.append(f"{ts}{sep}{t}")
        else:
            body = t.replace("\n", "\n")
            lines.append(f"{ts}{sep}{a}: {body}")
    (D / mod.TITLE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    collect(mod)


def whatsapp_ios(mod):
    msgs = sorted(mod.MSGS, key=lambda m: dt.datetime.strptime(m[0], "%d/%m/%y, %H:%M:%S"))
    lines = []
    folder = D / mod.TITLE.split("/")[0]
    folder.mkdir(parents=True, exist_ok=True)
    for ts, a, t in msgs:
        if a is None:
            lines.append(f"[{ts}] {mod.__name__ and 'ROM01 Condotti'}: ‎{t}")
            continue
        if isinstance(t, tuple):
            _, n, kind, stamp = t
            fn = f"{n:08d}-{kind}-{stamp}.jpg"
            # tiny placeholder file so the export folder looks real
            (folder / fn).write_bytes(bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffd9"))
            lines.append(f"[{ts}] {a}: ‎<allegato: {fn}>")
        else:
            lines.append(f"[{ts}] {a}: {t}")
    (D / mod.TITLE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    collect(mod)


def teams(mod):
    def uid(s):
        return str(uuid.UUID(hashlib.md5(s.encode()).hexdigest()))

    def html(text, mentions):
        parts = [p for p in text.split("\n\n")]
        out = "".join(f"<p>{p}</p>" for p in parts)
        for i, m in enumerate(mentions):
            out = out.replace(f"@{m}", f'<at id="{i}">{m}</at>')
        return out

    def msg(ts, author, text, reacts, mentions, reply_to=None):
        t = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M")
        mid = str(int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000) + len(text) % 997)
        created = t.strftime("%Y-%m-%dT%H:%M:") + f"{(len(text) * 7) % 60:02d}.{(len(author) * 37) % 1000:03d}Z"
        reactions = []
        for rt, n in reacts:
            for k in range(n):
                reactions.append({"reactionType": rt, "createdDateTime": created, "user": {"user": {"id": uid(f'r{rt}{k}{mid}'), "displayName": None}}})
        return {
            "id": mid, "replyToId": reply_to, "etag": mid, "messageType": "message",
            "createdDateTime": created, "lastModifiedDateTime": created, "lastEditedDateTime": None, "deletedDateTime": None,
            "subject": None, "summary": None, "chatId": None, "importance": "normal", "locale": "en-us",
            "webUrl": f"https://teams.microsoft.com/l/message/19%3Aretailopsemea-stock%40thread.tacv2/{mid}",
            "channelIdentity": {"teamId": uid("team-retail-ops-emea"), "channelId": "19:retailopsemea-stock@thread.tacv2"},
            "from": {"application": None, "device": None, "user": {"id": uid(author), "displayName": author, "userIdentityType": "aadUser",
                                                                   "tenantId": uid("tenant")}},
            "body": {"contentType": "html", "content": html(text, mentions)},
            "attachments": ([{"id": uid("att" + mid), "contentType": "reference", "contentUrl":
                              "https://moncler.sharepoint.example/sites/RetailOpsEMEA/Shared%20Documents/Allocation/MAIRE_999_alloc_wave_1610.xlsx",
                              "name": "MAIRE_999_alloc_wave_1610.xlsx"}] if "attached file" in text else []),
            "mentions": [{"id": i, "mentionText": m, "mentioned": {"user": {"id": uid(m), "displayName": m, "userIdentityType": "aadUser"}}}
                         for i, m in enumerate(mentions)],
            "reactions": reactions,
        }

    messages = []
    for root, replies in mod.THREADS:
        r = msg(*root)
        r["replies"] = []
        for rep in replies:
            r["replies"].append(msg(*rep, reply_to=r["id"]))
            if len(rep[2].split()) > 8:
                TEXTS[f"teams:{rep[0]}{rep[1]}"] = re.sub("<[^>]+>", "", rep[2])
        messages.append(r)
        TEXTS[f"teams:{root[0]}{root[1]}"] = re.sub("<[^>]+>", "", root[2])
    out = {"@odata.context": "https://graph.microsoft.com/v1.0/$metadata#teams('...')/channels('...')/messages",
           "exportedDateTime": "2026-10-22T07:12:44Z", "exportedBy": "Retail Ops EMEA - eDiscovery export (M. Colombo)",
           "team": {"id": uid("team-retail-ops-emea"), "displayName": "Retail Ops EMEA"},
           "channel": {"id": "19:retailopsemea-stock@thread.tacv2", "displayName": "Stock & Transfers"},
           "value": messages}
    (D / mod.TITLE).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def kakao(mod):
    WD = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    msgs = sorted(mod.MSGS, key=lambda m: dt.datetime.strptime(m[0], "%Y-%m-%d %H:%M"))
    lines = [f"{mod.GROUP} 님과 카카오톡 대화", f"저장한 날짜 : {mod.SAVED}", ""]
    cur = None
    for ts, a, t in msgs:
        d = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M")
        if d.date() != cur:
            cur = d.date()
            lines.append("")
            lines.append(f"--------------- {d.year}년 {d.month}월 {d.day}일 {WD[d.weekday()]} ---------------")
        if a is None:
            lines.append(t)
            continue
        h = d.hour % 12 or 12
        ap = "오전" if d.hour < 12 else "오후"
        lines.append(f"[{a}] [{ap} {h}:{d.minute:02d}] {t}")
    (D / mod.TITLE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for i, (ts, a, t) in enumerate(mod.MSGS):
        if len(t) > 25:
            TEXTS[f"kakao:{i}"] = t


def line_jp(mod):
    WD = "月火水木金土日"
    msgs = sorted(mod.MSGS, key=lambda m: dt.datetime.strptime(m[0], "%Y-%m-%d %H:%M"))
    lines = [f"[LINE] {mod.GROUP}のトーク履歴", f"保存日時：{mod.SAVED}", ""]
    cur = None
    for ts, a, t in msgs:
        d = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M")
        if d.date() != cur:
            cur = d.date()
            if len(lines) > 3:
                lines.append("")
            lines.append(f"{d.year}/{d.month:02d}/{d.day:02d}({WD[d.weekday()]})")
        if a is None:
            lines.append(f"{d.hour:02d}:{d.minute:02d}\t{t}")
        else:
            t2 = t.replace("\n", "\n")
            if "\n" in t2:
                t2 = '"' + t2 + '"'
            lines.append(f"{d.hour:02d}:{d.minute:02d}\t{a}\t{t2}")
    (D / mod.TITLE).write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    for i, (ts, a, t) in enumerate(mod.MSGS):
        if len(t) > 25:
            TEXTS[f"line:{i}"] = t


def wechat(mod):
    msgs = sorted(mod.MSGS, key=lambda m: dt.datetime.strptime(m[0], "%Y-%m-%d %H:%M:%S"))
    lines = [f"微信群聊记录导出  群名称：{mod.GROUP}", f"导出时间：{mod.SAVED}    导出工具：WeChatMsg v2.1", f"消息总数：{len(msgs)}", "=" * 40, ""]
    for ts, a, t in msgs:
        if a is None:
            lines.append(f"{ts} 系统消息")
        else:
            lines.append(f"{ts} {a}")
        lines.append(t)
        lines.append("")
    (D / mod.TITLE).write_text("\n".join(lines), encoding="utf-8")
    for i, (ts, a, t) in enumerate(mod.MSGS):
        if len(t) > 25:
            TEXTS[f"wechat:{i}"] = t


if __name__ == "__main__":
    for name in ["wa_mil01", "wa_par01", "wa_mad01"]:
        whatsapp_android(importlib.import_module(name))
    whatsapp_ios(importlib.import_module("wa_rom01"))
    teams(importlib.import_module("teams_emea"))
    for name, fn in [("kakao_kr", kakao), ("line_jp", line_jp), ("wechat_cn", wechat)]:
        try:
            fn(importlib.import_module(name))
        except ModuleNotFoundError:
            print("missing", name)
    check_texts(TEXTS)
    for p in sorted(D.rglob("*")):
        if p.is_file() and not p.name.endswith(".jpg"):
            print(p.relative_to(D), p.stat().st_size)
