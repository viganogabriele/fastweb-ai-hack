import pytest
from pydantic import ValidationError

from tesseract.core.contracts import Evidence, MetricFact, Observation, Quantity


@pytest.mark.parametrize("unit", ["units", "customers", "requests", "visitors", "percent"])
def test_units_are_preserved_without_conversion(unit):
    quantity = Quantity(kind="exact", value=5, unit=unit)
    assert Quantity.model_validate_json(quantity.model_dump_json()).unit == unit


@pytest.mark.parametrize(
    "payload",
    [
        {"kind": "exact", "unit": "units"},
        {"kind": "exact", "value": 5},
        {"kind": "exact", "value": 5, "low": 3, "unit": "units"},
        {"kind": "range", "low": 8, "high": 2, "unit": "units"},
        {"kind": "range", "low": 2, "unit": "units"},
        {"kind": "range", "low": 2, "high": 5, "value": 3, "unit": "units"},
        {"kind": "vague", "value": 3, "unit": "units"},
        {"kind": "unknown", "low": 0, "high": 0},
        {"kind": "exact", "value": -1, "unit": "customers"},
        {"kind": "exact", "value": 5, "unit": "money"},
        {"kind": "exact", "value": 5, "unit": "units", "currency": "EUR"},
        {"kind": "exact", "value": 5, "unit": "money", "currency": "eur"},
        {"kind": "exact", "value": 5, "unit": "pieces"},
        {"kind": "exact", "value": float("inf"), "unit": "units"},
        {"kind": "range", "low": float("nan"), "high": 5, "unit": "units"},
    ],
)
def test_invalid_quantities_are_rejected(payload):
    with pytest.raises(ValidationError):
        Quantity(**payload)


def test_missing_zero_vague_and_signed_money_remain_distinct():
    assert Quantity(kind="unknown").value is None
    assert Quantity(kind="vague", unit="units", raw="alcuni").value is None
    assert Quantity(kind="exact", unit="units", value=0).value == 0
    assert Quantity(kind="range", unit="requests", low=2, high=4).high == 4
    assert Quantity(kind="exact", unit="money", currency="EUR", value=-10).value == -10
    assert Quantity(kind="exact", unit="percent", value=-10).value == -10


def make_evidence(document, segment, **changes):
    return Evidence(
        **{
            "document_id": document.id,
            "document_version": document.version,
            "segment_id": segment.id,
            "quote": "5 clienti",
            "char_start": segment.char_start,
            "char_end": segment.char_start + len("5 clienti"),
            **changes,
        }
    )


def test_unicode_offsets_and_json_roundtrip(document, segment, derived_fields):
    evidence = make_evidence(document, segment)
    evidence.validate_against(document, segment)
    # The coat emoji adds a UTF-16 code unit; canonical offsets remain code points.
    prefix = document.text[: evidence.char_start]
    assert len(prefix.encode("utf-16-le")) // 2 == evidence.char_start + 1
    observation = Observation(
        **derived_fields,
        document_id=document.id,
        kind="unmet_demand",
        store_id="MIL01",
        quantity=Quantity(kind="exact", value=5, unit="customers"),
        direction="up",
        attribution="reported",
        negated=False,
        evidence=[evidence],
        extractor_version="v1",
    )
    restored = Observation.model_validate_json(observation.model_dump_json())
    assert restored == observation
    assert restored.quantity.unit == "customers"


@pytest.mark.parametrize(
    "changes",
    [
        {"quote": "5 persons"},  # Same length is insufficient: text must match exactly.
        {"document_version": "v2"},
        {"segment_id": "other"},
        {"char_start": 0, "char_end": 9},
        {"t_start_s": 0, "t_end_s": 1},
    ],
)
def test_evidence_rejects_wrong_text_version_membership_and_invented_audio(
    document, segment, changes
):
    with pytest.raises(ValueError):
        make_evidence(document, segment, **changes).validate_against(document, segment)


def test_evidence_does_not_normalize_unicode(document, segment):
    payload = document.model_dump()
    payload["text"] = "cafe\u0301"
    doc = type(document)(**payload)
    seg = type(segment)(
        **{
            **segment.model_dump(),
            "text": doc.text,
            "char_start": 0,
            "char_end": 5,
        }
    )
    with pytest.raises(ValueError):
        Evidence(
            document_id=doc.id,
            document_version=doc.version,
            segment_id=seg.id,
            quote="café",
            char_start=0,
            char_end=4,
        ).validate_against(doc, seg)


def test_real_audio_interval_must_be_contained(document, segment):
    timed_segment = type(segment)(**{**segment.model_dump(), "t_start_s": 3, "t_end_s": 8})
    make_evidence(document, segment, t_start_s=4, t_end_s=6).validate_against(
        document, timed_segment
    )
    with pytest.raises(ValueError):
        make_evidence(document, segment, t_start_s=2, t_end_s=6).validate_against(
            document, timed_segment
        )


def test_metric_missing_definition_blocks_comparability(derived_fields):
    payload = dict(
        **derived_fields,
        document_id="doc-1",
        metric="net_sales",
        value=None,
        unit="money",
        scope={"store_id": "MIL01"},
        period_start="2026-10-21T00:00:00Z",
        period_end="2026-10-22T00:00:00Z",
        locator="Sheet1!A2",
        mapping_version="v1",
        comparability_status="unknown",
    )
    assert MetricFact(**payload).value is None
    with pytest.raises(ValidationError, match="definition"):
        MetricFact(**{**payload, "comparability_status": "comparable"})
