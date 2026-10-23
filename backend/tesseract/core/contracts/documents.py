from datetime import date
from typing import Literal, Self

from pydantic import JsonValue, model_validator

from .common import Count, Instant, NonNegative, SourceRecord, Text, ordered, require_pair


class SourceDocument(SourceRecord):
    source_type: Literal[
        "email",
        "voice_note",
        "chat_message",
        "report",
        "external_feed",
        "system_api",
        "clarification_reply",
    ]
    connector: Text
    uri: Text
    content_hash: Text
    origin: str | None
    author_ref: str | None = None
    language: str | None = None
    business_date: date | None = None
    event_start: Instant | None = None
    event_end: Instant | None = None
    thread_key: str | None = None
    parent_document_id: str | None = None
    text: str
    text_version: Text
    meta: dict[str, JsonValue]

    @model_validator(mode="after")
    def event_interval(self) -> Self:
        ordered(self.event_start, self.event_end)
        return self


class Segment(SourceRecord):
    document_id: Text
    text_version: Text
    idx: Count
    text: str
    char_start: Count
    char_end: Count
    locator: str | None = None
    t_start_s: NonNegative | None = None
    t_end_s: NonNegative | None = None
    is_quoted: bool

    @model_validator(mode="after")
    def intervals(self) -> Self:
        ordered(self.char_start, self.char_end)
        if self.char_end - self.char_start != len(self.text):
            raise ValueError("segment offsets must span its canonical text in Unicode code points")
        require_pair(self.t_start_s, self.t_end_s)
        ordered(self.t_start_s, self.t_end_s)
        return self

    def validate_against(self, document: SourceDocument) -> None:
        if self.document_id != document.id or self.text_version != document.text_version:
            raise ValueError("segment must refer to this document and text version")
        if self.char_end > len(document.text):
            raise ValueError("segment lies outside the document")
        if document.text[self.char_start : self.char_end] != self.text:
            raise ValueError("segment text must match the canonical document slice")
