from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.models import IngestRecord
from toonflow.storage import (
    SCHEMA_SQL,
    build_delete_fields_statement,
    build_export_payload,
    build_field_rows,
    build_insert_statement,
)
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


def test_validation_rejects_bad_timestamp_and_id_type():
    payload = sample_payload() | {"id": 123, "timestamp": "not-a-date"}
    result = validate_payload(payload)
    assert result.ok is False
    assert any("timestamp" in err for err in result.errors)
    assert any("id" in err for err in result.errors)


def test_toon_conversion_returns_inspectable_compact_string():
    toon = json_to_toon(sample_payload())
    assert isinstance(toon, str)
    assert "entity:" in toon
    assert "customer:" in toon
    assert "name: Alice" in toon
    assert len(toon) < len(str(sample_payload())) * 2


def test_toon_conversion_uses_table_shape_for_repeated_objects():
    toon = json_to_toon({"messages": [{"sender": "a", "text": "hello"}, {"sender": "b", "text": "hi"}]})
    assert "messages[2]{sender,text}:" in toon
    assert "a,hello" in toon


def test_flatten_query_fields_extracts_nested_paths():
    fields = flatten_query_fields(sample_payload())
    assert fields["entity"] == "invoice"
    assert fields["data.customer.name"] == "Alice"
    assert fields["data.tags.__len__"] == 2


def test_flatten_query_fields_extracts_indexed_list_object_paths():
    payload = sample_payload() | {
        "data": {
            "messages": [
                {"sender": "customer", "text": "Need invoice help"},
                {"sender": "agent", "text": "Checking line items"},
            ]
        }
    }
    fields = flatten_query_fields(payload)
    assert fields["data.messages.__len__"] == 2
    assert fields["data.messages[0].sender"] == "customer"
    assert fields["data.messages[1].text"] == "Checking line items"


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
    assert "ON DUPLICATE KEY UPDATE" in sql
    assert len(params) == 9
    exported = build_export_payload(record)
    assert exported["payload_id"] == "demo-001"
    assert exported["json"]["entity"] == "invoice"

    delete_sql, delete_params = build_delete_fields_statement(record.payload_id)
    assert delete_sql == "DELETE FROM toon_record_fields WHERE payload_id = %s"
    assert delete_params == ("demo-001",)


def test_storage_builds_relational_field_rows_for_queryable_values():
    payload = sample_payload()
    record = IngestRecord(
        payload_id="demo-001",
        source="demo-ui",
        original_json=payload,
        toon_payload=json_to_toon(payload),
        extracted_fields=flatten_query_fields(payload),
        status="validated",
    )
    rows = build_field_rows(record)
    amount = next(row for row in rows if row["field_path"] == "data.amount")
    assert amount["value_number"] == 245.5
    customer = next(row for row in rows if row["field_path"] == "data.customer.name")
    assert customer["value_string"] == "Alice"


def test_schema_contains_dual_storage_columns():
    assert "toon_payload" in SCHEMA_SQL
    assert "extracted_fields" in SCHEMA_SQL
    assert "original_json" in SCHEMA_SQL
    assert "toon_record_fields" in SCHEMA_SQL
    assert "field_path" in SCHEMA_SQL
