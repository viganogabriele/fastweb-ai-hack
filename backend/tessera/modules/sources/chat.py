"""ING-07 module: ``src.chat`` turns the chat exports into one document per message.

Exports live in ``internal_comms/chat_exports/``, each in its native format: WhatsApp (Android
``.txt`` with locale-dependent dates, iOS ``_chat.txt`` folders), KakaoTalk, LINE, WeChat
(WeChatMsg) and Microsoft Teams (Graph JSON). Every message is its own ``SourceDocument``
(``chat_message``) with one ``Segment`` spanning its text: a message is available from its own
timestamp (``generated/README.md`` §4), so messages written after ``as_of`` stay out of the run
and an export never leaks its later lines into an earlier evening.

Which stores a chat covers is declared per export in ``EXPORTS``, never guessed from the text:
a store chat has one store (``meta.store_id``), a group chat has several (``meta.scope_store_ids``
only, so ``ing.extract`` does not attribute it to one store). An export is read only when its
scope meets the run's stores: hold-out chats (ROM01) enter only runs that include them.

Local timestamps are read in the scope's time zone; Teams timestamps are UTC. System lines
(encryption notices, call records), deleted or recalled messages and media-only placeholders
are dropped and counted. A line that matches no message pattern, an unknown export or an
unreadable file is reported, never silently skipped.

The module is disabled by default (Could, RFC §4): enabling it adds one extraction call per
message to ``ing.extract``.
"""

import csv
import hashlib
import html
import json
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tessera.core.config import get_settings
from tessera.core.contracts import ModuleManifest, ModuleResult, Segment, SourceDocument

DOC_VERSION = "v1"
TEXT_VERSION = "chat-v1"
ROOT = "internal_comms/chat_exports"

MANIFEST = ModuleManifest(
    id="src.chat",
    version="1",
    layer="sources",
    description="Chat exports (WhatsApp, KakaoTalk, LINE, WeChat, Teams), one document per message",
    requires=(),
    optional_inputs=(),
    produces=("SourceDocument", "Segment"),
    enabled=False,
    mode="live",
    params_schema={"type": "object", "properties": {}, "additionalProperties": False},
)


@dataclass(frozen=True)
class Message:
    """One parsed message; ``at`` is aware, ``line`` is 1-based in the export file."""

    at: datetime
    author: str | None
    text: str
    line: int
    raw: str
    native_id: str | None = None
    reply_to: str | None = None
    attachments: tuple[str, ...] = ()


@dataclass
class Parsed:
    messages: list[Message] = field(default_factory=list)
    unparsed: list[int] = field(default_factory=list)  # 1-based line numbers


@dataclass(frozen=True)
class Export:
    """A known export: path under ``chat_exports/``, parser, slug for ids and its store scope.

    ``scope`` is a tuple of store ids, or a region name resolved against the master data.
    """

    path: str
    format: str
    slug: str
    scope: tuple[str, ...] | str
    language: str | None


EXPORTS = (
    Export("Chat WhatsApp con MIL01 Team.txt", "whatsapp", "wa-mil01-team", ("MIL01",), "it"),
    Export(
        "Chat de WhatsApp con Serrano Equipo.txt", "whatsapp", "wa-mad01-serrano", ("MAD01",), "es"
    ),
    Export(
        "Discussion WhatsApp avec Boutique Paris SH.txt",
        "whatsapp",
        "wa-par01-sh",
        ("PAR01",),
        "fr",
    ),
    Export(
        "WhatsApp Chat - ROM01 Condotti/_chat.txt",
        "whatsapp_ios",
        "wa-rom01-condotti",
        ("ROM01",),
        "it",
    ),
    Export(
        "KakaoTalk_20261022_0914_52_몽클레르 점장방.txt",
        "kakaotalk",
        "kakao-kr-managers",
        ("SEL01", "SEL02", "BUS01"),
        "ko",
    ),
    Export(
        "[LINE] 銀座・表参道・心斎橋 店長会.txt",
        "line",
        "line-jp-managers",
        ("TYO01", "TYO02", "OSA01"),
        "ja",
    ),
    Export(
        "微信群聊_华区门店管理群_20261022.txt",
        "wechat",
        "wechat-cn-managers",
        ("SHA01", "BJS01", "CDU01"),
        "zh-CN",
    ),
    Export(
        "Teams_RetailOpsEMEA_Stock-and-Transfers_export_20261022.json",
        "teams",
        "teams-emea-stock",
        "EMEA",
        None,
    ),
)

# Media-only messages carry no readable claim; deleted/recalled ones carry none any more.
PLACEHOLDERS = {
    "<Media omessi>",
    "<Multimedia omitido>",
    "<Médias omis>",
    "<Media omitted>",
    "immagine omessa",
    "image omitted",
    "video omitted",
    "sticker omitted",
    "사진",
    "동영상",
    "이모티콘",
    "투표",
    "[写真]",
    "[スタンプ]",
    "[動画]",
    "[图片]",
    "[表情]",
    "[视频]",
}
DELETED = {
    "Questo messaggio è stato eliminato",
    "Hai eliminato questo messaggio",
    "Se eliminó este mensaje",
    "Eliminaste este mensaje",
    "Ce message a été supprimé",
    "Vous avez supprimé ce message",
    "This message was deleted",
    "You deleted this message",
    "撤回了一条消息",
    "삭제된 메시지입니다.",
}
VOICE_PLACEHOLDER = re.compile(r'^\[语音\]\s*\d+"?$')
ATTACHED = re.compile(r"^<(?:allegato|attached|adjunto|pièce jointe): [^>]+>$")


@dataclass(frozen=True)
class StoreInfo:
    timezone: str
    region: str


@dataclass
class Batch:
    documents: list[tuple[SourceDocument, list[Segment]]] = field(default_factory=list)
    dropped: dict[str, int] = field(default_factory=dict)  # reason -> count, available ones only
    problems: list[str] = field(default_factory=list)  # "<uri>: <reason>"


def load_stores(sources_dir: Path) -> dict[str, StoreInfo]:
    path = sources_dir / "erp" / "master_data" / "stores.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        return {
            row["store_id"]: StoreInfo(timezone=row["timezone"], region=row["region"])
            for row in csv.DictReader(stream)
        }


def _lines(text: str) -> list[str]:
    return text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _clean(text: str) -> str:
    # WhatsApp iOS marks attachments and edits with LEFT-TO-RIGHT MARK.
    return text.replace("‎", "").strip()


def _extend(messages: list[Message], continuation: str, number: int) -> None:
    last = messages[-1]
    messages[-1] = Message(
        at=last.at,
        author=last.author,
        text=f"{last.text}\n{continuation}",
        line=last.line,
        raw=f"{last.raw}\n{continuation}",
    )


WA_ANDROID = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2}|\d{4}),? (\d{1,2}):(\d{2}) - (.*)$")
WA_IOS = re.compile(
    r"^\[(\d{1,2})/(\d{1,2})/(\d{2}|\d{4}),? (\d{1,2}):(\d{2})(?::(\d{2}))?\] (.*)$"
)


def _year(value: str) -> int:
    return int(value) + 2000 if len(value) == 2 else int(value)


def _whatsapp(text: str, tz: ZoneInfo, pattern: re.Pattern[str]) -> Parsed:
    """Day-first dates, as in every locale of the dataset (it, es, fr)."""
    parsed = Parsed()
    for number, line in enumerate(_lines(text), 1):
        match = pattern.match(_clean(line))
        if match is None:
            if parsed.messages and line.strip():
                _extend(parsed.messages, line, number)
            elif line.strip():
                parsed.unparsed.append(number)
            continue
        day, month, year, hour, minute = (match.group(i) for i in range(1, 6))
        second = match.group(6) if pattern is WA_IOS else None
        body = match.group(match.lastindex)
        at = datetime(
            _year(year), int(month), int(day), int(hour), int(minute), int(second or 0), tzinfo=tz
        )
        author, sep, content = body.partition(": ")
        if not sep:  # system line: encryption notice, group changes
            author, content = None, body
        parsed.messages.append(Message(at, author, _clean(content), number, line))
    return parsed


KAKAO_DAY = re.compile(r"^-+ (\d{4})년 (\d{1,2})월 (\d{1,2})일 .*-+$")
KAKAO_MESSAGE = re.compile(r"^\[([^\]]+)\] \[(오전|오후) (\d{1,2}):(\d{2})\] (.*)$")


def _kakaotalk(text: str, tz: ZoneInfo) -> Parsed:
    parsed = Parsed()
    day: date | None = None
    for number, line in enumerate(_lines(text), 1):
        stripped = line.strip()
        if number <= 2 or not stripped:  # title and save date
            continue
        if match := KAKAO_DAY.match(stripped):
            day = date(*(int(match.group(i)) for i in range(1, 4)))
            continue
        match = KAKAO_MESSAGE.match(stripped)
        if match is None or day is None:
            if match is None and parsed.messages:
                _extend(parsed.messages, line, number)
            else:
                parsed.unparsed.append(number)
            continue
        author, half, hour, minute, content = match.groups()
        hour_24 = int(hour) % 12 + (12 if half == "오후" else 0)
        at = datetime(day.year, day.month, day.day, hour_24, int(minute), tzinfo=tz)
        parsed.messages.append(Message(at, author, content.strip(), number, line))
    return parsed


LINE_DAY = re.compile(r"^(\d{4})/(\d{2})/(\d{2})\(.\)$")
LINE_MESSAGE = re.compile(r"^(\d{1,2}):(\d{2})\t(.*)$")


def _line(text: str, tz: ZoneInfo) -> Parsed:
    parsed = Parsed()
    day: date | None = None
    for number, line in enumerate(_lines(text), 1):
        stripped = line.strip()
        if number <= 2 or not stripped:  # title and save date
            continue
        if match := LINE_DAY.match(stripped):
            day = date(*(int(match.group(i)) for i in range(1, 4)))
            continue
        match = LINE_MESSAGE.match(line)
        if match is None or day is None:
            if match is None and parsed.messages:
                _extend(parsed.messages, line, number)
            else:
                parsed.unparsed.append(number)
            continue
        hour, minute, rest = match.groups()
        author, sep, content = rest.partition("\t")
        if not sep:  # system line: calls, members joining
            author, content = None, rest
        at = datetime(day.year, day.month, day.day, int(hour), int(minute), tzinfo=tz)
        parsed.messages.append(Message(at, author or None, content.strip(), number, line))
    return parsed


WECHAT_HEADER = re.compile(r"^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (.+)$")


def _wechat(text: str, tz: ZoneInfo) -> Parsed:
    """WeChatMsg: a ``====`` rule ends the header, then ``<time> <author>`` and content lines."""
    parsed = Parsed()
    lines = _lines(text)
    start = next((i for i, line in enumerate(lines) if line.startswith("====")), None)
    if start is None:
        parsed.unparsed.append(1)
        return parsed
    pending: tuple[datetime, str, int, list[str]] | None = None

    def flush() -> None:
        if pending is None:
            return
        at, author, number, body = pending
        if not body:
            parsed.unparsed.append(number)
            return
        content = "\n".join(body)
        raw = "\n".join([lines[number - 1], *body])
        parsed.messages.append(Message(at, author, content.strip(), number, raw))

    for index in range(start + 1, len(lines)):
        line, number = lines[index], index + 1
        if match := WECHAT_HEADER.match(line):
            flush()
            values = [int(match.group(i)) for i in range(1, 7)]
            pending = (datetime(*values, tzinfo=tz), match.group(7).strip(), number, [])
        elif line.strip():
            if pending is None:
                parsed.unparsed.append(number)
            else:
                pending[3].append(line)
    flush()
    return parsed


TAG = re.compile(r"<[^>]+>")
BLOCK_END = re.compile(r"</p>|<br\s*/?>|</div>|</li>", re.IGNORECASE)


def teams_text(content: str) -> str:
    """Graph ``html`` bodies: paragraphs to lines, tags (``<at>`` mentions too) to their text."""
    text = BLOCK_END.sub("\n", content)
    text = html.unescape(TAG.sub("", text))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _teams(text: str) -> Parsed:
    parsed = Parsed()
    try:
        export = json.loads(text)
        top = export["value"]
    except (ValueError, KeyError, TypeError):
        parsed.unparsed.append(1)
        return parsed
    flat = []
    for message in top:
        flat.append(message)
        flat.extend(message.get("replies") or ())
    for message in flat:
        native_id = str(message.get("id") or "")
        try:
            at = datetime.fromisoformat(message["createdDateTime"].replace("Z", "+00:00"))
            body = message["body"]
            content = body["content"]
        except (KeyError, TypeError, ValueError):
            parsed.unparsed.append(1)
            continue
        if message.get("messageType") != "message" or message.get("deletedDateTime"):
            content = ""
        elif body.get("contentType") == "html":
            content = teams_text(content)
        user = ((message.get("from") or {}).get("user") or {}).get("displayName")
        parsed.messages.append(
            Message(
                at=at.astimezone(UTC),
                author=user,
                text=content.strip(),
                line=1,
                raw=json.dumps(message, ensure_ascii=False, sort_keys=True),
                native_id=native_id or None,
                reply_to=str(message["replyToId"]) if message.get("replyToId") else None,
                attachments=tuple(
                    a["name"] for a in message.get("attachments") or () if a.get("name")
                ),
            )
        )
    return parsed


def parse(text: str, fmt: str, tz: ZoneInfo) -> Parsed:
    parsers: dict[str, Callable[[], Parsed]] = {
        "whatsapp": lambda: _whatsapp(text, tz, WA_ANDROID),
        "whatsapp_ios": lambda: _whatsapp(text, tz, WA_IOS),
        "kakaotalk": lambda: _kakaotalk(text, tz),
        "line": lambda: _line(text, tz),
        "wechat": lambda: _wechat(text, tz),
        "teams": lambda: _teams(text),
    }
    return parsers[fmt]()


def drop_reason(message: Message) -> str | None:
    text = message.text
    if message.author is None:
        return "system"
    if not text:
        return "deleted" if message.native_id else "empty"
    if text in DELETED:
        return "deleted"
    if text in PLACEHOLDERS or VOICE_PLACEHOLDER.match(text) or ATTACHED.match(text):
        return "media_only"
    return None


def resolve_scope(export: Export, stores: dict[str, StoreInfo]) -> tuple[str, ...]:
    if isinstance(export.scope, str):
        return tuple(sorted(s for s, info in stores.items() if info.region == export.scope))
    return export.scope


def build_document(
    export: Export,
    message: Message,
    number: int,
    scope: tuple[str, ...],
    business_tz: ZoneInfo | None,
    parent_id: str | None,
) -> tuple[SourceDocument, list[Segment]]:
    uri = f"dataset://{ROOT}/{export.path}"
    locator = f"message:{message.native_id}" if message.native_id else f"line:{message.line}"
    content_hash = "sha256:" + hashlib.sha256(message.raw.encode()).hexdigest()
    common = {
        "version": DOC_VERSION,
        "available_at": message.at,
        "availability_basis": "chat_message_timestamp",
        "source_refs": ({"uri": uri, "content_hash": content_hash, "locator": locator},),
    }
    key = message.native_id or str(number)
    document_id = f"doc-chat-{export.slug}-{key}"
    document = SourceDocument(
        id=document_id,
        **common,
        source_type="chat_message",
        connector=MANIFEST.id,
        uri=uri,
        content_hash=content_hash,
        origin=None,
        author_ref=message.author,
        language=export.language,
        business_date=message.at.astimezone(business_tz).date() if business_tz else None,
        thread_key=f"chat-{export.slug}",
        parent_document_id=parent_id,
        text=message.text,
        text_version=TEXT_VERSION,
        meta={
            **({"store_id": scope[0]} if len(scope) == 1 else {}),
            "scope_store_ids": list(scope),
            "chat_format": export.format,
            "export": export.path,
            "locator": locator,
            "reply_to": message.reply_to,
            "attachments": list(message.attachments),
        },
    )
    segment = Segment(
        id=f"{document_id}-seg0",
        **common,
        document_id=document_id,
        text_version=TEXT_VERSION,
        idx=0,
        text=message.text,
        char_start=0,
        char_end=len(message.text),
        locator=locator,
        is_quoted=False,
    )
    segment.validate_against(document)
    return document, [segment]


def collect(
    sources_dir: Path,
    store_ids: Iterable[str],
    as_of: datetime,
    exports: Iterable[Export] = EXPORTS,
) -> Batch:
    """Messages of the exports whose scope meets ``store_ids``, as seen at ``as_of``.

    Pure apart from reading files.
    """
    root = (sources_dir / ROOT).resolve()
    stores = load_stores(sources_dir)
    run_stores = set(store_ids)
    batch = Batch()
    exports = tuple(exports)
    known = {export.path.split("/")[0] for export in exports}
    if root.is_dir():
        for entry in sorted(root.iterdir()):
            if entry.name not in known and not entry.name.startswith("."):
                batch.problems.append(f"dataset://{ROOT}/{entry.name}: unsupported chat export")
    for export in exports:
        scope = resolve_scope(export, stores)
        if not run_stores.intersection(scope):
            continue  # another lane's stores, or hold-out outside this run
        uri = f"dataset://{ROOT}/{export.path}"
        path = (root / export.path).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            batch.problems.append(f"{uri}: no such file")
            continue
        zones = {stores[s].timezone for s in scope if s in stores}
        # Group chats span one time zone in this dataset; a mixed scope has no local date.
        business_tz = ZoneInfo(zones.pop()) if len(zones) == 1 else None
        if export.format != "teams" and business_tz is None:
            batch.problems.append(f"{uri}: local timestamps but no single time zone in scope")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            batch.problems.append(f"{uri}: not UTF-8")
            continue
        parsed = parse(text, export.format, business_tz or ZoneInfo("UTC"))
        documents: dict[str, str] = {}
        for number, message in enumerate(parsed.messages, 1):
            if message.at > as_of:
                continue  # later messages and how many there are are future information
            if reason := drop_reason(message):
                batch.dropped[reason] = batch.dropped.get(reason, 0) + 1
                continue
            parent = documents.get(message.reply_to or "")
            document, segments = build_document(export, message, number, scope, business_tz, parent)
            if message.native_id:
                documents[message.native_id] = document.id
            batch.documents.append((document, segments))
        for line in parsed.unparsed:
            batch.problems.append(f"{uri}: line {line} is not a message")
    batch.documents.sort(key=lambda item: (item[0].available_at, item[0].id))
    return batch


def run(ctx, *, sources_dir: Path | None = None) -> ModuleResult:
    batch = collect(sources_dir or get_settings().sources_dir, ctx.spec.stores, ctx.spec.as_of)
    for document, segments in batch.documents:
        ctx.repo.put(document, *segments)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if batch.problems else "succeeded",
        counts={
            "documents": len(batch.documents),
            "segments": sum(len(segments) for _, segments in batch.documents),
            **{f"dropped_{reason}": n for reason, n in sorted(batch.dropped.items())},
        },
        errors=(),
        abstentions=tuple(batch.problems),
    )
