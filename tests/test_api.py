import pytest
from fastapi.testclient import TestClient

from toonflow.api import app, store


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_store_between_tests():
    store.clear()


def valid_payload(payload_id="api-001"):
    return {
        "id": payload_id,
        "entity": "invoice",
        "timestamp": "2026-04-24T10:00:00Z",
        "data": {"customer": {"name": "Alice"}, "amount": 245.5},
    }


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_validate_endpoint_accepts_valid_payload():
    response = client.post("/validate", json=valid_payload("api-validate-001"))
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_validate_endpoint_rejects_non_object_without_crashing():
    response = client.post("/validate", json=["not", "object"])
    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["errors"] == ["Payload must be a JSON object"]


def test_convert_endpoint_returns_toon_and_fields():
    response = client.post("/convert", json=valid_payload("api-convert-001"))
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "converted"
    assert "entity: invoice" in body["toon_payload"]
    assert body["extracted_fields"]["data.customer.name"] == "Alice"


def test_convert_endpoint_returns_400_for_invalid_payload():
    response = client.post("/convert", json={"entity": "invoice"})
    assert response.status_code == 400
    assert response.json()["detail"]["status"] == "rejected"


def test_ingest_read_and_export_record_flow():
    payload = valid_payload("api-ingest-001")
    ingest = client.post("/ingest", json=payload)
    assert ingest.status_code == 200
    assert ingest.json()["stored"] is True

    read = client.get("/records/api-ingest-001")
    assert read.status_code == 200
    assert read.json()["status"] == "validated"

    exported = client.get("/records/api-ingest-001/export")
    assert exported.status_code == 200
    assert exported.json()["json"]["entity"] == "invoice"
    assert exported.json()["extracted_fields"]["data.amount"] == 245.5

    json_export = client.get("/records/api-ingest-001/export", params={"format": "json"})
    assert json_export.status_code == 200
    assert json_export.json()["format"] == "json"
    assert json_export.json()["json"]["id"] == "api-ingest-001"

    toon_export = client.get("/records/api-ingest-001/export", params={"format": "toon"})
    assert toon_export.status_code == 200
    assert toon_export.json()["format"] == "toon"
    assert "entity: invoice" in toon_export.json()["toon"]


def test_export_rejects_unknown_format():
    assert client.post("/ingest", json=valid_payload("api-export-format-001")).status_code == 200
    response = client.get("/records/api-export-format-001/export", params={"format": "xml"})
    assert response.status_code == 400
    assert "format must be" in response.json()["detail"]["message"]


def test_ingest_stores_rejected_records_for_audit():
    response = client.post("/ingest", json={"id": "api-bad-001", "entity": "invoice"})
    assert response.status_code == 400
    assert response.json()["detail"]["stored"] is True

    stored = client.get("/records/api-bad-001")
    assert stored.status_code == 200
    assert stored.json()["status"] == "rejected"
    assert stored.json()["validation_errors"]


def test_missing_record_returns_404():
    response = client.get("/records/does-not-exist")
    assert response.status_code == 404


def test_list_records_endpoint_includes_ingested_records():
    assert client.post("/ingest", json=valid_payload("api-list-001")).status_code == 200
    response = client.get("/records")
    assert response.status_code == 200
    assert [item["payload_id"] for item in response.json()] == ["api-list-001"]
