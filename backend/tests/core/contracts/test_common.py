from datetime import UTC

import pytest
from pydantic import ValidationError

from tessera.core.contracts import Segment, SourceDocument, StockFact


def test_instants_are_aware_utc_and_availability_can_be_unknown(document):
    assert document.available_at.tzinfo == UTC
    assert document.available_at.hour == 17
    payload = document.model_dump()
    payload["available_at"] = None
    payload["availability_basis"] = "availability_unknown"
    assert SourceDocument(**payload).available_at is None
    payload["available_at"] = "2026-10-22T19:00:00"
    with pytest.raises(ValidationError, match="timezone"):
        SourceDocument(**payload)


def test_unknown_fields_are_rejected_and_records_are_frozen(document):
    with pytest.raises(ValidationError, match="extra_forbidden"):
        SourceDocument(**{**document.model_dump(), "surprise": True})
    with pytest.raises(ValidationError, match="frozen"):
        document.version = "v2"


@pytest.mark.parametrize(
    "changes",
    [
        {"char_start": -1},
        {"char_end": 999},
        {"document_id": "other"},
        {"text_version": "text-v2"},
        {"t_start_s": 3},
        {"t_start_s": 5, "t_end_s": 2},
    ],
)
def test_segment_boundaries(document, segment, changes):
    with pytest.raises(ValueError):
        Segment(**{**segment.model_dump(), **changes}).validate_against(document)


def test_stock_unknown_is_not_zero(source_fields):
    payload = dict(
        **source_fields,
        location_id="MIL01",
        sku="STYLE-COLOR",
        size="2",
        snapshot_at="2026-10-21T18:00:00Z",
        qty=None,
        basis="atp",
        reservations_included=None,
        quality_holds_included=None,
        source_ref=source_fields["source_refs"][0],
    )
    assert StockFact(**payload).qty is None
    assert StockFact(**{**payload, "qty": 0}).qty == 0
    with pytest.raises(ValidationError):
        StockFact(**{**payload, "qty": float("nan")})
