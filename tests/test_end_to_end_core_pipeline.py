from pathlib import Path

from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.repository import InMemoryRecordStore
from toonflow.service import batch_ingest_and_store_payloads, ingest_and_store_payload
from toonflow.storage import SCHEMA_SQL, build_field_rows


def payload():
    return {
        "id": "core-e2e-001",
        "entity": "invoice",
        "timestamp": "2026-04-24T10:00:00Z",
        "data": {
            "customer": {"name": "Alice"},
            "amount": 245.5,
            "approved": True,
            "items": [
                {"sku": "A-1", "qty": 2},
                {"sku": "B-2", "qty": 1},
            ],
        },
    }


def test_valid_payload_runs_validate_convert_extract_store_path():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload(payload(), store, source="core-test")

    stored = store.get("core-e2e-001")
    assert stored is not None
    assert result["status"] == "validated"
    assert stored.original_json["entity"] == "invoice"
    assert stored.toon_payload == json_to_toon(payload())
    assert stored.extracted_fields == flatten_query_fields(payload())
    assert stored.extracted_fields["data.items[0].sku"] == "A-1"

    field_rows = build_field_rows(stored)
    assert any(row["field_path"] == "data.amount" and row["value_number"] == 245.5 for row in field_rows)
    assert any(row["field_path"] == "data.approved" and row["value_boolean"] is True for row in field_rows)


def test_invalid_payload_is_rejected_but_still_auditable():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload({"entity": "invoice"}, store, source="core-test", payload_id="bad-e2e-001")

    stored = store.get("bad-e2e-001")
    assert stored is not None
    assert result["status"] == "rejected"
    assert stored.validation_errors
    assert stored.toon_payload == ""
    assert stored.extracted_fields == {}


def test_batch_pipeline_preserves_mixed_statuses():
    store = InMemoryRecordStore()
    result = batch_ingest_and_store_payloads([payload(), {"entity": "invoice"}], store, source="core-batch")

    assert result["total"] == 2
    assert result["accepted"] == 1
    assert result["rejected"] == 1
    assert len(store.list()) == 2


def test_schema_file_matches_runtime_schema_constant():
    schema_file = Path(__file__).resolve().parents[1] / "src" / "toonflow" / "schema.sql"
    assert schema_file.read_text(encoding="utf-8").strip() == SCHEMA_SQL
