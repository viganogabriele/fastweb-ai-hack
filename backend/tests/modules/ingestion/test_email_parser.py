from datetime import datetime, timedelta, timezone

import pytest

from tesseract.core.config import REPO_ROOT
from tesseract.modules.ingestion.email_parser import html_to_text, parse_eml, segment

EMAILS = REPO_ROOT / "generated" / "sources" / "store_emails"  # dev stores only
needs_dataset = pytest.mark.skipif(not EMAILS.exists(), reason="dataset not checked out")


def load(path: str):
    return parse_eml((EMAILS / path).read_bytes())


def assert_offsets(e) -> None:
    for i, s in enumerate(e.segments):
        assert s.idx == i
        assert e.text[s.char_start : s.char_end] == s.text
        assert s.text.strip()


def eml(body: str, subject: str = "Chiusura", extra: str = "", ctype: str = "text/plain") -> bytes:
    return (
        "From: Anna Rossi <anna@example.com>\r\nTo: ops@example.com\r\n"
        f"Subject: {subject}\r\nDate: Thu, 22 Oct 2026 21:05:00 +0200\r\n{extra}"
        f'MIME-Version: 1.0\r\nContent-Type: {ctype}; charset="utf-8"\r\n'
        "Content-Transfer-Encoding: 8bit\r\n\r\n" + body
    ).encode()


@needs_dataset
def test_real_italian_closing_email() -> None:
    e = load("MIL01/20260901_2025_MIL01.eml")
    assert e.subject == "Chiusura MIL01 - 01/09"
    assert e.sender_address == "giulia.ferrandi@valentino-retail.example"
    assert e.sent_at == datetime(2026, 9, 1, 20, 25, 39, tzinfo=timezone(timedelta(hours=2)))
    assert not e.is_reply and not e.is_forward and e.body_source == "plain"
    assert not any(s.is_quoted for s in e.segments)
    assert any("cardigan logo blu e nero" in s.text for s in e.segments)
    assert "=\n" not in e.text  # quoted-printable soft breaks decoded
    assert len(e.content_hash) == 64
    assert_offsets(e)


@needs_dataset
def test_real_french_reply_flags_quoted_original() -> None:
    e = load("PAR01/20260925_2214_PAR01_re1.eml")
    assert e.is_reply and e.thread_subject == "PAR01 - Closing 25/09"
    assert e.in_reply_to is not None
    own, quoted = [s for s in e.segments if not s.is_quoted], [s for s in e.segments if s.is_quoted]
    assert any("Aurea noire non servies" in s.text for s in own)
    assert quoted[0].text.startswith("Le ven. 25 sept. 2026")
    assert any("Aurea noire : 3 demandes" in s.text for s in quoted)
    assert "3 demandes" not in e.own_text
    assert_offsets(e)


@needs_dataset
def test_real_japanese_iso_2022_jp_email() -> None:
    e = load("TYO01/20260906_2140_TYO01.eml")
    assert e.subject == "銀座店 日報 9/6(日)"
    assert e.sent_at is not None and e.sent_at.utcoffset() == timedelta(hours=9)
    assert any("NOVA黒が7点" in s.text for s in e.segments)
    assert_offsets(e)


@needs_dataset
def test_real_attachment_is_listed_not_parsed() -> None:
    e = load("MIL01/20261007_1142_MIL01.eml")
    assert [(a.filename, a.inline) for a in e.attachments] == [
        ("lista_attesa_maire_nera_MIL01.xlsx", False)
    ]
    assert e.attachments[0].content_type.endswith("spreadsheetml.sheet")
    assert e.attachments[0].size_bytes > 0
    assert "lista d'attesa della Aurea nera" in e.text


@needs_dataset
def test_real_forward_marks_original_as_quoted() -> None:
    e = load("MIL01/20261001_1124_MIL01_fwd.eml")
    assert e.is_forward and not e.is_reply
    assert "Vi giro la mail" in e.own_text
    assert "zip" not in e.own_text
    assert any(s.is_quoted and "-----Messaggio originale-----" in s.text for s in e.segments)


@needs_dataset
def test_all_dev_emails_parse_with_valid_offsets() -> None:
    hold_out = {"ROM01", "PAR02", "LON02", "ZRH01", "NYC02"}
    hold_out |= {"TYO02", "SEL02", "BJS01", "TPE01", "DXB01"}
    paths = [p for p in EMAILS.glob("*/*.eml") if p.parent.name not in hold_out]
    assert len(paths) > 1000
    for p in paths:
        e = parse_eml(p.read_bytes())
        assert e.sent_at is not None and e.text, p.name
        assert_offsets(e)


def test_outlook_from_sent_block_starts_quote() -> None:
    body = "OK grazie\n\nFrom: Marco\nSent: Thursday\nTo: Anna\n\nAurea nera finita"
    e = parse_eml(eml(body, subject="R: Chiusura"))
    assert e.is_reply
    assert [s.is_quoted for s in e.segments] == [False, True, True]
    assert e.own_text == "OK grazie"


def test_angle_quotes_inline_and_blank_quote_lines() -> None:
    e = parse_eml(eml("Sì confermo\n> quante Aurea?\n>\n> 3 in T2\nGrazie"))
    assert [(s.text, s.is_quoted) for s in e.segments] == [
        ("Sì confermo", False),
        ("> quante Aurea?", True),
        ("> 3 in T2", True),
        ("Grazie", False),
    ]


def test_code_point_offsets_with_emoji_and_cjk() -> None:
    e = parse_eml(eml("今日 🎉 很好\n\n粉色 IRIDIA 断码 👍"))
    assert_offsets(e)
    s = e.segments[1]
    assert e.text[s.char_start : s.char_start + 2] == "粉色"
    assert s.char_start == len("今日 🎉 很好\n\n")


def test_crlf_and_trailing_spaces_are_canonicalized() -> None:
    e = parse_eml(eml("riga uno   \r\nriga due\r\n\r\n\r\n"))
    assert e.text == "riga uno\nriga due"
    assert len(e.segments) == 1


def test_forward_and_reply_prefixes() -> None:
    assert parse_eml(eml("x", subject="WG: Info")).is_forward
    assert parse_eml(eml("x", subject="RV: Info")).is_forward
    assert parse_eml(eml("x", subject="回复：回复：日报")).thread_subject == "日报"
    e = parse_eml(eml("x", subject="Re: Fw: Info"))
    assert e.is_reply and not e.is_forward and e.thread_subject == "Info"
    e = parse_eml(eml("x", subject="Inventario: ok", extra="In-Reply-To: <a@b>\r\n"))
    assert e.is_reply and e.thread_subject == "Inventario: ok"


def test_html_only_body_with_blockquote() -> None:
    html = (
        "<html><head><style>p{}</style></head><body><p>Ciao &amp; grazie</p>"
        "<table><tr><td>Sales</td><td>HK$194,400</td></tr></table>"
        "<blockquote><p>Aurea nera?</p></blockquote></body></html>"
    )
    e = parse_eml(eml(html, ctype="text/html"))
    assert e.body_source == "html"
    assert "Ciao & grazie" in e.text and "Sales\tHK$194,400" in e.text
    assert [s.is_quoted for s in e.segments] == [False, False, True]
    assert "p{}" not in e.text


def test_empty_body_and_missing_date() -> None:
    raw = b"From: a@b\r\nSubject: foto\r\nMIME-Version: 1.0\r\nContent-Type: text/plain\r\n\r\n"
    e = parse_eml(raw)
    assert e.text == "" and e.segments == () and e.sent_at is None


def test_segment_helper_on_plain_text() -> None:
    segs = segment("a\nb\n\nc")
    assert [(s.text, s.char_start, s.char_end) for s in segs] == [("a\nb", 0, 3), ("c", 5, 6)]


def test_html_to_text_strips_scripts() -> None:
    assert html_to_text("<script>x=1</script><div>uno</div><div>due</div>").split() == [
        "uno",
        "due",
    ]


def test_header_like_lines_in_own_report_are_not_a_quote() -> None:
    e = parse_eml(eml("Da: Giulia (MIL01)\nData: 22/10\nFatturato 85k, 3 Aurea nere perse"))
    assert not any(s.is_quoted for s in e.segments)
    assert "3 Aurea nere perse" in e.own_text


def raw_eml(body: bytes, charset: str) -> bytes:
    return (
        b"From: a@example.com\r\nSubject: Chiusura\r\nDate: Thu, 22 Oct 2026 21:05:00 +0200\r\n"
        b"MIME-Version: 1.0\r\nContent-Type: text/plain; charset=" + charset.encode() + b"\r\n"
        b"Content-Transfer-Encoding: 8bit\r\n\r\n" + body
    )


@pytest.mark.parametrize(
    ("body", "charset", "text", "warning"),
    [
        ("perché 3 Aurea".encode(), "utf-8", "perché 3 Aurea", None),
        (
            "perché 3 Aurea".encode("cp1252"),
            "utf-8",
            "perché 3 Aurea",
            "utf-8->windows-1252",
        ),
        ("perché".encode(), "x-unknown", "perché", "x-unknown->utf-8"),
        ("perché".encode(), "us-ascii", "perché", "us-ascii->utf-8"),
        (
            "粉色 Iridia 䶮".encode("gb18030"),
            "gb2312",
            "粉色 Iridia 䶮",
            "gb2312->gb18030",
        ),
    ],
)
def test_charset_fallback_keeps_exact_text_and_warns(body, charset, text, warning) -> None:
    e = parse_eml(raw_eml(body, charset))
    assert e.text == text and "�" not in e.text
    assert e.warnings == ((f"charset_fallback:{warning}",) if warning else ())


def test_undecodable_bytes_are_replaced_with_a_warning() -> None:
    e = parse_eml(raw_eml(b"ok \xff\xfe", "iso-2022-jp"))
    assert e.text.startswith("ok") and e.warnings == ("charset_replaced:iso-2022-jp",)
