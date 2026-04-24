from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.models import IngestRecord
from toonflow.storage import (
    SCHEMA_SQL,
    build_delete_fields_statement,
    build_export_payload,
    build_field_rows,
    build_insert_statement,
    create_schema,
    schema_statements,
    store_record,
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


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        if self.connection.fail_on_execute:
            raise RuntimeError("simulated storage failure")
        self.connection.executed.append((sql, params))


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.commits = 0
        self.rollbacks = 0
        self.fail_on_execute = False

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


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


def test_validation_rejects_payload_id_that_exceeds_storage_limit():
    payload = sample_payload() | {"id": "x" * 129}
    result = validate_payload(payload)
    assert result.ok is False
    assert any("128 characters" in err for err in result.errors)


def test_validation_rejects_non_strict_json_values():
    payload = sample_payload() | {"data": {"amount": float("nan")}}
    result = validate_payload(payload)
    assert result.ok is False
    assert any("strict JSON" in err for err in result.errors)


def test_validation_rejects_extracted_field_paths_that_exceed_schema_limit():
    very_long_key = "x" * 260
    payload = sample_payload() | {"data": {very_long_key: "value"}}
    result = validate_payload(payload)
    assert result.ok is False
    assert any("field path exceeds" in err for err in result.errors)


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


def test_toon_conversion_embeds_nested_lists_as_json_not_python_repr():
    toon = json_to_toon({"matrix": [[1, 2], ["a", "b"]]})
    assert "- [1,2]" in toon
    assert '- ["a","b"]' in toon
    assert "['a', 'b']" not in toon


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


def test_flatten_query_fields_extracts_nested_list_scalars():
    fields = flatten_query_fields({"data": {"matrix": [[1, 2], [3, 4]]}})
    assert fields["data.matrix.__len__"] == 2
    assert fields["data.matrix[0].__len__"] == 2
    assert fields["data.matrix[0][1]"] == 2
    assert fields["data.matrix[1][0]"] == 3


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


def test_storage_uses_strict_json_serialisation():
    record = IngestRecord(
        payload_id="bad-json",
        source="test",
        original_json={"value": float("nan")},
        toon_payload="",
        extracted_fields={},
        status="rejected",
    )
    try:
        build_insert_statement(record)
    except ValueError as exc:
        assert "JSON" in str(exc) or "range" in str(exc)
    else:
        raise AssertionError("Expected strict JSON serialisation failure")


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


def test_storage_helpers_create_schema_and_store_record_transactionally():
    payload = sample_payload()
    record = IngestRecord(
        payload_id="demo-001",
        source="demo-ui",
        original_json=payload,
        toon_payload=json_to_toon(payload),
        extracted_fields=flatten_query_fields(payload),
        status="validated",
    )
    conn = FakeConnection()
    create_schema(conn)
    assert conn.commits == 1
    assert any("toon_record_fields" in sql for sql, _ in conn.executed)

    store_record(conn, record)
    assert conn.commits == 2
    assert any("INSERT INTO toon_records" in sql for sql, _ in conn.executed)
    assert any("DELETE FROM toon_record_fields" in sql for sql, _ in conn.executed)
    assert any("INSERT INTO toon_record_fields" in sql for sql, _ in conn.executed)


def test_storage_helpers_roll_back_on_failure():
    conn = FakeConnection()
    conn.fail_on_execute = True
    try:
        create_schema(conn)
    except RuntimeError as exc:
        assert "simulated storage failure" in str(exc)
    else:
        raise AssertionError("Expected simulated storage failure")
    assert conn.commits == 0
    assert conn.rollbacks == 1


def test_schema_contains_dual_storage_columns():
    assert "toon_payload" in SCHEMA_SQL
    assert "extracted_fields" in SCHEMA_SQL
    assert "original_json" in SCHEMA_SQL
    assert "toon_record_fields" in SCHEMA_SQL
    assert "field_path" in SCHEMA_SQL
    statements = schema_statements()
    assert len(statements) == 2
    assert statements[0].startswith("CREATE TABLE IF NOT EXISTS toon_records")
    assert statements[1].startswith("CREATE TABLE IF NOT EXISTS toon_record_fields")
