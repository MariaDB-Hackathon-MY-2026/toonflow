from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.models import IngestRecord
from toonflow.storage import SCHEMA_SQL, build_export_payload, build_insert_statement
from toonflow.validator import validate_payload


def sample_payload():
    return {
        "id": "demo-001",
        "entity": "invoice",
        "timestamp": "2026-04-23T12:00:00Z",
        "data": {
            "customer": {"name": "Alice", "tier": "gold"},
            "amount": 245.50,
            "currency": "MYR",
            "tags": ["priority", "renewal"],
        },
    }


def test_validation_accepts_expected_payload():
    result = validate_payload(sample_payload())
    assert result.ok is True
    assert result.errors == []
    assert result.record_count == 1


def test_validation_rejects_missing_required_keys():
    result = validate_payload({"entity": "invoice"})
    assert result.ok is False
    assert any("timestamp" in err for err in result.errors)
    assert any("data" in err for err in result.errors)


def test_toon_conversion_returns_inspectable_compact_string():
    toon = json_to_toon(sample_payload())
    assert isinstance(toon, str)
    assert "entity:" in toon
    assert "data.customer.name:" in toon
    assert len(toon) < len(str(sample_payload())) * 2


def test_flatten_query_fields_extracts_nested_paths():
    fields = flatten_query_fields(sample_payload())
    assert fields["entity"] == "invoice"
    assert fields["data.customer.name"] == "Alice"
    assert fields["data.tags.__len__"] == 2


def test_storage_helpers_prepare_sql_and_export_payload():
    payload = sample_payload()
    record = IngestRecord(
        payload_id="demo-001",
        source="demo-ui",
        original_json=payload,
        toon_payload=json_to_toon(payload),
        extracted_fields=flatten_query_fields(payload),
        status="validated",
    )
    sql, params = build_insert_statement(record)
    assert "INSERT INTO toon_records" in sql
    assert len(params) == 9
    exported = build_export_payload(record)
    assert exported["payload_id"] == "demo-001"
    assert exported["json"]["entity"] == "invoice"


def test_schema_contains_dual_storage_columns():
    assert "toon_payload" in SCHEMA_SQL
    assert "extracted_fields" in SCHEMA_SQL
    assert "original_json" in SCHEMA_SQL
