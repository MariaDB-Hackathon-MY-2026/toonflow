from fastapi.testclient import TestClient

from toonflow.api import app


client = TestClient(app)


def valid_payload():
    return {
        'id': 'api-001',
        'entity': 'invoice',
        'timestamp': '2026-04-23T12:00:00Z',
        'data': {'customer': {'name': 'Alice'}, 'amount': 245.50},
    }


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_validate_and_convert_endpoints():
    assert client.post('/validate', json=valid_payload()).json()['ok'] is True
    converted = client.post('/convert', json=valid_payload())
    assert converted.status_code == 200
    assert converted.json()['status'] == 'converted'


def test_ingest_read_and_export_flow():
    ingest = client.post('/ingest', json=valid_payload())
    assert ingest.status_code == 200
    payload_id = ingest.json()['payload_id']
    read = client.get(f'/records/{payload_id}')
    assert read.status_code == 200
    exported = client.get(f'/records/{payload_id}/export')
    assert exported.status_code == 200
    assert exported.json()['json']['entity'] == 'invoice'


def test_invalid_ingest_returns_400():
    response = client.post('/ingest', json={'entity': 'invoice'})
    assert response.status_code == 400


def test_batch_ingest_endpoint():
    response = client.post('/batch/ingest', json=[valid_payload(), {'entity': 'invoice'}])
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 2
    assert body['accepted'] == 1
    assert body['rejected'] == 1
