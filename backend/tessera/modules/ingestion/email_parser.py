""".eml → canonical text + segments with code-point offsets (RFC §4.5, ING-02 pure).

The canonical text is the plain body (or the HTML body turned into text when there is no plain
part), with `\\n` newlines and trailing spaces removed. Segments are runs of non-blank lines of
the same kind, so `text[seg.char_start:seg.char_end] == seg.text` always holds. Offsets are
Python string indices, i.e. Unicode code points.

Quoted material is flagged, not removed: `>` lines, and everything from a reply/forward header
("Le … a écrit :", "-----Original Message-----", an Outlook `From:`/`Sent:` block...) to the end.
A forward's quoted part can still carry new facts (a customer's mail); deciding that is dedup's
job (INT-02), not the parser's. Attachments are listed with type and size, never parsed here.

Pure code: bytes in, dataclasses out. No DB, no LLM, no dataset paths.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes, policy
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr
from html import unescape
from html.parser import HTMLParser
from typing import Literal

PARSER_VERSION = "email-v1"

BodySource = Literal["plain", "html", "none"]

_REPLY_TOKENS = {"re", "r", "aw", "sv", "antw", "回复", "答复", "회신"}
_FORWARD_TOKENS = {"fw", "fwd", "wg", "tr", "i", "rv", "转发", "転送", "전달"}
_TOKENS = "|".join(sorted(_REPLY_TOKENS | _FORWARD_TOKENS))
_PREFIX = re.compile(rf"^\s*((?:{_TOKENS})\s*[:：]\s*)+", re.IGNORECASE)

# Lines that open a quoted/forwarded block that runs to the end of the body.
_QUOTE_HEADERS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"^-{2,}\s*(original message|ursprüngliche nachricht|messaggio originale|"
        r"message d'origine|mensaje original|oorspronkelijk bericht|原始邮件|原始郵件)\s*-{2,}$",
        r"^-{2,}\s*(forwarded message|messaggio inoltrato|message transféré|"
        r"mensaje reenviado|weitergeleitete nachricht|doorgestuurd bericht|"
        r"転送メッセージ|转发的消息|轉寄的郵件|전달된 메시지)\s*-{2,}$",
        r"^on .{4,120} wrote:$",
        r"^le .{4,120} a écrit\s?:$",
        r"^il giorno .{4,120} ha scritto:$",
        r"^am .{4,120} schrieb .{1,120}:$",
        r"^el .{4,120} escribió:$",
        r"^op .{4,120} schreef .{1,120}:$",
        r"^.{4,120}(写道|寫道)[:：]$",
        r"^.{4,120}님이 작성[:：]?$",
    )
]
_FROM_LINE = re.compile(r"^(from|da|von|de|van|fra|发件人|寄件者|差出人|보낸 사람)\s*[:：]", re.I)
_SENT_LINE = re.compile(
    r"^(sent|date|inviato|data|gesendet|datum|envoyé|enviado|fecha|verzonden|sendt|"
    r"发送时间|發送時間|日期|送信日時|보낸 날짜)\s*[:：]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Segment:
    idx: int
    text: str
    char_start: int
    char_end: int
    is_quoted: bool


@dataclass(frozen=True)
class Attachment:
    filename: str | None
    content_type: str
    size_bytes: int
    inline: bool


@dataclass(frozen=True)
class ParsedEmail:
    message_id: str | None
    in_reply_to: str | None
    references: tuple[str, ...]
    subject: str
    thread_subject: str  # subject without Re:/Fwd:/R:/AW:/回复：... prefixes
    sender_name: str | None
    sender_address: str | None
    to: tuple[str, ...]
    cc: tuple[str, ...]
    sent_at: datetime | None  # timezone-aware, with the sender's local offset
    is_reply: bool
    is_forward: bool
    text: str
    segments: tuple[Segment, ...]
    attachments: tuple[Attachment, ...]
    body_source: BodySource
    content_hash: str  # sha256 of the raw bytes
    parser_version: str = PARSER_VERSION

    @property
    def own_text(self) -> str:
        """Text written by the sender: non-quoted segments only."""
        return "\n\n".join(s.text for s in self.segments if not s.is_quoted)


def parse_eml(raw: bytes) -> ParsedEmail:
    msg = message_from_bytes(raw, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    subject = _header(msg, "subject") or ""
    prefix = _PREFIX.match(subject)
    prefixes = prefix.group(0) if prefix else ""
    first = re.split(r"\s*[:：]", prefixes.strip(), maxsplit=1)[0].lower()
    text, source = _body(msg)
    name, address = parseaddr(_header(msg, "from") or "")
    return ParsedEmail(
        message_id=_header(msg, "message-id"),
        in_reply_to=_header(msg, "in-reply-to"),
        references=tuple((_header(msg, "references") or "").split()),
        subject=subject,
        thread_subject=subject[len(prefixes) :].strip(),
        sender_name=name or None,
        sender_address=address.lower() or None,
        to=_addresses(msg, "to"),
        cc=_addresses(msg, "cc"),
        sent_at=_date(msg),
        is_reply=first in _REPLY_TOKENS or (not first and msg["in-reply-to"] is not None),
        is_forward=first in _FORWARD_TOKENS,
        text=text,
        segments=segment(text),
        attachments=_attachments(msg),
        body_source=source,
        content_hash=hashlib.sha256(raw).hexdigest(),
    )


def canonicalize(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


def segment(text: str) -> tuple[Segment, ...]:
    """Group consecutive non-blank lines of the same kind (own / quoted) into segments."""
    lines = text.split("\n")
    quoted_from = _quote_start(lines)
    segments: list[Segment] = []
    pos = 0
    current: tuple[int, int, bool] | None = None  # start, end, quoted
    for i, line in enumerate(lines):
        start, end = pos, pos + len(line)
        pos = end + 1
        blank = not line.strip() or line.strip() == ">"
        if blank:
            if current:
                segments.append(_segment(text, len(segments), *current))
                current = None
            continue
        quoted = i >= quoted_from or line.lstrip().startswith(">")
        if current and current[2] != quoted:
            segments.append(_segment(text, len(segments), *current))
            current = None
        current = (current[0], end, quoted) if current else (start, end, quoted)
    if current:
        segments.append(_segment(text, len(segments), *current))
    return tuple(segments)


def _segment(text: str, idx: int, start: int, end: int, quoted: bool) -> Segment:
    return Segment(idx, text[start:end], start, end, quoted)


def _quote_start(lines: list[str]) -> int:
    """Index of the first line of a reply/forward block, or len(lines) if none."""
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith(">"):
            continue
        if any(p.match(s) for p in _QUOTE_HEADERS):
            return i
        if _FROM_LINE.match(s) and any(_SENT_LINE.match(n.strip()) for n in lines[i + 1 : i + 4]):
            return i
    return len(lines)


def _body(msg: EmailMessage) -> tuple[str, BodySource]:
    part = msg.get_body(preferencelist=("plain",))
    if part is not None:
        return canonicalize(part.get_content()), "plain"
    part = msg.get_body(preferencelist=("html",))
    if part is not None:
        return canonicalize(html_to_text(part.get_content())), "html"
    return "", "none"


def _attachments(msg: EmailMessage) -> tuple[Attachment, ...]:
    out = []
    for part in msg.iter_attachments():
        payload = part.get_payload(decode=True) or b""
        out.append(
            Attachment(
                filename=part.get_filename(),
                content_type=part.get_content_type(),
                size_bytes=len(payload),
                inline=part.get_content_disposition() == "inline",
            )
        )
    return tuple(out)


def _header(msg: EmailMessage, name: str) -> str | None:
    value = msg.get(name)
    return " ".join(str(value).split()) if value is not None else None


def _addresses(msg: EmailMessage, name: str) -> tuple[str, ...]:
    values = [str(v) for v in msg.get_all(name, [])]
    return tuple(addr.lower() for _, addr in getaddresses(values) if addr)


def _date(msg: EmailMessage) -> datetime | None:
    header = msg.get("date")
    try:
        dt = header.datetime if header is not None else None
    except (AttributeError, TypeError, ValueError):
        return None
    return dt if dt is not None and dt.tzinfo is not None else None


class _HTMLText(HTMLParser):
    _BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "blockquote"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self.skip = 0
        self.quote = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "head"):
            self.skip += 1
        if tag == "blockquote":
            self.quote += 1
        if tag in self._BLOCK:
            self.parts.append("\n")
        if tag in ("td", "th"):
            self.parts.append("\t")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "head"):
            self.skip = max(0, self.skip - 1)
        if tag == "blockquote":
            self.quote = max(0, self.quote - 1)
        if tag in self._BLOCK:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        data = re.sub(r"\s+", " ", data)
        if self.quote:
            data = data.replace("\n", "\n> ")
            if not self.parts or self.parts[-1].endswith("\n"):
                data = "> " + data.lstrip()
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.handle_data(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.handle_data(unescape(f"&#{name};"))


def html_to_text(html: str) -> str:
    """Readable text from an HTML body: block tags become newlines, cells tabs, blockquote
    lines get a `> ` prefix so they are flagged as quoted."""
    p = _HTMLText()
    p.feed(html)
    p.close()
    lines = [
        re.sub(r"[ \t]*\t[ \t]*", "\t", line).strip(" ") for line in "".join(p.parts).split("\n")
    ]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
