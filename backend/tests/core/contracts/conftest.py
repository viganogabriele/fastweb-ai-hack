import pytest

from tessera.core.contracts import Segment, SourceDocument


@pytest.fixture
def source_fields():
    return {
        "id": "doc-1",
        "version": "v1",
        "available_at": "2026-10-22T19:00:00+02:00",
        "availability_basis": "email_date",
        "source_refs": [
            {"uri": "test://email/1", "content_hash": "hash-1"},
        ],
    }


@pytest.fixture
def derived_fields(source_fields):
    return {
        **source_fields,
        "id": "artifact-1",
        "run_id": "run-1",
        "scenario_id": "historical",
        "computed_at": "2026-10-22T20:00:00Z",
        "input_refs": [
            {"kind": "SourceDocument", "id": "doc-1", "version": "v1"},
        ],
        "producer": "test.module",
        "producer_version": "v1",
    }


@pytest.fixture
def document(source_fields):
    return SourceDocument(
        **source_fields,
        source_type="email",
        connector="src.email",
        uri="test://email/1",
        content_hash="hash-1",
        origin=None,
        text="Salve 🧥 店: 5 clienti, zero pezzi.",
        text_version="text-v1",
        meta={},
    )


@pytest.fixture
def segment(source_fields, document):
    start = document.text.index("5 clienti")
    return Segment(
        **{**source_fields, "id": "segment-1"},
        document_id=document.id,
        text_version=document.text_version,
        idx=0,
        text=document.text[start:],
        char_start=start,
        char_end=len(document.text),
        is_quoted=False,
    )
