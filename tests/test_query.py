import pytest

from toonflow.models import IngestRecord
from toonflow.query import build_sql_preview, field_matches, hybrid_query_response, query_records


def record(payload_id="r1", amount=245.5):
    return IngestRecord(
        payload_id=payload_id,
        source="test",
        original_json={},
        toon_payload="entity: invoice",
        extracted_fields={"entity": "invoice", "data.amount": amount},
        status="validated",
    )


def test_field_matches_supported_operators():
    assert field_matches("invoice", "invoice") is True
    assert field_matches("priority billing", "billing", "contains") is True
    assert field_matches(10, 5, "gt") is True
    assert field_matches(10, 10, "gte") is True
    assert field_matches(5, 10, "lt") is True
    assert field_matches(5, 5, "lte") is True


def test_query_records_filters_extracted_fields():
    matches = query_records([record("a", 100), record("b", 300)], "data.amount", 200, "gt")
    assert [item.payload_id for item in matches] == ["b"]


def test_build_sql_preview_describes_mariadb_json_field_lookup():
    preview = build_sql_preview("data.amount", "gte")
    assert "JSON_EXTRACT(extracted_fields" in preview["sql"]
    assert preview["params"][0] == '$."data.amount"'


def test_hybrid_query_response_returns_toon_payloads():
    response = hybrid_query_response([record()], "entity", "invoice")
    assert response["matched_count"] == 1
    assert response["records"][0]["toon_payload"] == "entity: invoice"


def test_invalid_operator_raises():
    with pytest.raises(ValueError):
        field_matches("a", "a", "bad")
