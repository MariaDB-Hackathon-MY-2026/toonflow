import os

import pytest

from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.db import connect_mariadb, load_mariadb_config
from toonflow.mariadb_repository import MariaDBRecordRepository
from toonflow.models import IngestRecord


REQUIRED_ENV = ("TOONFLOW_DB_HOST", "TOONFLOW_DB_USER", "TOONFLOW_DB_PASSWORD", "TOONFLOW_DB_NAME")


def live_db_available() -> bool:
    return all(os.environ.get(name) for name in REQUIRED_ENV)


@pytest.mark.skipif(not live_db_available(), reason="live MariaDB environment variables are not configured")
def test_live_mariadb_core_ingestion_path():
    payload = {
        "id": "live-test-001",
        "entity": "invoice",
        "timestamp": "2026-04-24T10:00:00Z",
        "data": {"customer": {"name": "Alice"}, "amount": 245.5},
    }
    record = IngestRecord(
        payload_id=payload["id"],
        source="live-test",
        original_json=payload,
        toon_payload=json_to_toon(payload),
        extracted_fields=flatten_query_fields(payload),
        status="validated",
    )

    connection = connect_mariadb(load_mariadb_config())
    repo = MariaDBRecordRepository(connection)
    repo.create_schema()
    repo.save(record)

    stored = repo.get("live-test-001")
    assert stored is not None
    assert stored["status"] == "validated"
    assert stored["extracted_fields"]["data.customer.name"] == "Alice"

    matches = repo.find_by_field("entity", "invoice")
    assert any(item["payload_id"] == "live-test-001" for item in matches)
