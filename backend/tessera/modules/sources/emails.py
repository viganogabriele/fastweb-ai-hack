"""ING-02 module: ``src.email`` turns the run's store mailboxes into documents and segments.

For every store of the run it parses ``store_emails/<STORE>/*.eml`` with the ING-02 parser and
writes one ``SourceDocument`` plus its ``Segment``s per mail. A mail is available at its
``Date:`` header (``generated/README.md`` §4): mails dated after ``as_of`` stay out of the run,
and mails without a usable date are skipped and reported, never dated by guess.

Ids, text and fields are those of the DATA-01a fixtures for the same file, so fixtures and real
runs are interchangeable at this boundary: ``doc-<file stem>`` and ``<doc id>-seg<idx>``.
Replies point to the parent mail of the same run through ``In-Reply-To`` (any mail available at
``as_of``: auto-replies can be dated seconds before the mail they answer). The thread key is the
root of that parent chain, so a reply whose ``References:`` lists only its direct parent stays
in the parent's thread; without a parent in the run it falls back to the mail's own headers.
Language is the store's language from the master data.

The optional ``files`` param restricts the run to a preselected sample of mailbox files
(``<STORE>/<file>.eml``, e.g. an evaluation sample); the ``as_of`` rule still applies, and a
listed file that is missing or outside the run's stores is reported, never silently dropped.
"""

import csv
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tessera.core.config import get_settings
from tessera.core.contracts import ModuleManifest, ModuleResult, Segment, SourceDocument
from tessera.modules.ingestion.email_parser import ParsedEmail, parse_eml

DOC_VERSION = "v1"

MANIFEST = ModuleManifest(
    id="src.email",
    version="1",
    layer="sources",
    description="Store closing emails (.eml) of the run's stores as documents and segments",
    requires=(),
    optional_inputs=(),
    produces=("SourceDocument", "Segment"),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string", "pattern": r"^[A-Z0-9]+/[^/]+\.eml$"},
                "minItems": 1,
                "uniqueItems": True,
            }
        },
        "additionalProperties": False,
    },
)


@dataclass(frozen=True)
class Store:
    language: str
    timezone: str
    currency: str = ""


@dataclass
class Batch:
    """Documents in publication order (parents first) and what was left out, with reasons."""

    documents: list[tuple[SourceDocument, list[Segment]]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # "<uri>: <reason>"
    missing_mailboxes: list[str] = field(default_factory=list)


def load_stores(sources_dir: Path) -> dict[str, Store]:
    path = sources_dir / "erp" / "master_data" / "stores.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        return {
            row["store_id"]: Store(
                language=row["language"],
                timezone=row["timezone"],
                currency=row.get("currency") or "",
            )
            for row in csv.DictReader(stream)
        }


def doc_id(relative: str) -> str:
    return "doc-" + Path(relative).stem.lower().replace("_", "-")


def thread_root(parsed: ParsedEmail) -> str | None:
    return (parsed.references[0] if parsed.references else parsed.in_reply_to) or parsed.message_id


def build_document(
    relative: str,
    parsed: ParsedEmail,
    store_id: str,
    store: Store,
    parent_id: str | None,
    thread_key: str | None = None,
) -> tuple[SourceDocument, list[Segment]]:
    """``relative`` is the path under ``store_emails/``, e.g. ``MIL01/20261009_1035_MIL01.eml``."""
    if parsed.sent_at is None:
        raise ValueError("a document needs the mail's Date: header")
    uri = f"dataset://store_emails/{relative}"
    content_hash = f"sha256:{parsed.content_hash}"
    common = {
        "version": DOC_VERSION,
        "available_at": parsed.sent_at,
        "availability_basis": "email_date_header",
        "source_refs": ({"uri": uri, "content_hash": content_hash},),
    }
    document_id = doc_id(relative)
    document = SourceDocument(
        id=document_id,
        **common,
        source_type="email",
        connector=MANIFEST.id,
        uri=uri,
        content_hash=content_hash,
        origin=parsed.sender_address,
        author_ref=parsed.sender_name,
        language=store.language,
        business_date=parsed.sent_at.astimezone(ZoneInfo(store.timezone)).date(),
        thread_key=thread_key or thread_root(parsed),
        parent_document_id=parent_id,
        text=parsed.text,
        text_version=parsed.parser_version,
        meta={
            "store_id": store_id,
            "message_id": parsed.message_id,
            "in_reply_to": parsed.in_reply_to,
            "subject": parsed.subject,
            "thread_subject": parsed.thread_subject,
            "is_reply": parsed.is_reply,
            "is_forward": parsed.is_forward,
            "body_source": parsed.body_source,
            "attachments": [
                {
                    "filename": a.filename,
                    "content_type": a.content_type,
                    "size_bytes": a.size_bytes,
                    "inline": a.inline,
                }
                for a in parsed.attachments
            ],
            "parser_warnings": list(parsed.warnings),
        },
    )
    segments = [
        Segment(
            id=f"{document_id}-seg{s.idx}",
            **common,
            document_id=document_id,
            text_version=parsed.parser_version,
            idx=s.idx,
            text=s.text,
            char_start=s.char_start,
            char_end=s.char_end,
            is_quoted=s.is_quoted,
        )
        for s in parsed.segments
    ]
    for segment in segments:
        segment.validate_against(document)
    return document, segments


def collect(
    sources_dir: Path,
    store_ids: Iterable[str],
    as_of: datetime,
    files: Iterable[str] | None = None,
) -> Batch:
    """Parse the mailboxes of ``store_ids`` as seen at ``as_of``, only ``files`` when given.

    Pure apart from reading files.
    """
    root = (sources_dir / "store_emails").resolve()
    stores = load_stores(sources_dir)
    batch = Batch()
    store_ids = set(store_ids)
    selected = None if files is None else set(files)
    for relative in sorted(selected or ()):
        if relative.split("/")[0] not in store_ids:
            batch.skipped.append(f"dataset://store_emails/{relative}: not a store of the run")
        elif not (root / relative).is_file():
            batch.skipped.append(f"dataset://store_emails/{relative}: no such file")
    available: list[tuple[datetime, str, str, ParsedEmail]] = []
    for store_id in sorted(store_ids):
        mailbox = (root / store_id).resolve()
        if store_id not in stores or not mailbox.is_relative_to(root) or not mailbox.is_dir():
            batch.missing_mailboxes.append(store_id)
            continue
        for path in sorted(mailbox.glob("*.eml")):
            relative = f"{store_id}/{path.name}"
            if selected is not None and relative not in selected:
                continue
            parsed = parse_eml(path.read_bytes())
            if parsed.sent_at is None:
                batch.skipped.append(f"dataset://store_emails/{relative}: no usable Date header")
            elif parsed.sent_at <= as_of:
                # Later mails are not counted either: their number is future information.
                available.append((parsed.sent_at, relative, store_id, parsed))
    available.sort(key=lambda item: item[:2])
    by_message_id: dict[str, int] = {}
    for index, (_, _, _, parsed) in enumerate(available):
        if parsed.message_id:
            by_message_id.setdefault(parsed.message_id, index)
    parents = {
        index: by_message_id.get(parsed.in_reply_to or "")
        for index, (_, _, _, parsed) in enumerate(available)
    }

    def root(index: int) -> int:
        seen = {index}
        while (parent := parents[index]) is not None and parent not in seen:
            seen.add(parent)
            index = parent
        return index

    for index, (_, relative, store_id, parsed) in enumerate(available):
        parent = parents[index]
        document, segments = build_document(
            relative,
            parsed,
            store_id,
            stores[store_id],
            doc_id(available[parent][1]) if parent is not None and parent != index else None,
            thread_root(available[root(index)][3]),
        )
        batch.documents.append((document, segments))
    return batch


def run(ctx, *, sources_dir: Path | None = None) -> ModuleResult:
    batch = collect(
        sources_dir or get_settings().sources_dir,
        ctx.spec.stores,
        ctx.spec.as_of,
        ctx.params.get("files"),
    )
    for document, segments in batch.documents:
        ctx.repo.put(document, *segments)
    errors = tuple(f"no mailbox for store {store_id}" for store_id in batch.missing_mailboxes)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors or batch.skipped else "succeeded",
        counts={
            "documents": len(batch.documents),
            "segments": sum(len(segments) for _, segments in batch.documents),
            "skipped": len(batch.skipped),
        },
        errors=errors,
        abstentions=tuple(batch.skipped),
    )
