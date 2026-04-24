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


def test_demo_page_loads():
    response = client.get('/demo')
    assert response.status_code == 200
    assert 'TOONFlow evaluator' in response.text


def test_validate_and_convert_endpoints():
    assert client.post('/validate', json=valid_payload()).json()['ok'] is True
    converted = client.post('/convert', json=valid_payload())
    assert converted.status_code == 200
    assert converted.json()['status'] == 'converted'


def test_evaluate_endpoint_returns_metrics_and_toon():
    response = client.post('/evaluate', json=valid_payload())
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ready'
    assert body['metrics']['json_bytes'] > 0
    assert body['toon_payload']


def test_ingest_read_and_export_flow():
    ingest = client.post('/ingest', json=valid_payload())
    assert ingest.status_code == 200
    payload_id = ingest.json()['payload_id']
    read = client.get(f'/records/{payload_id}')
    assert read.status_code == 200
    exported = client.get(f'/records/{payload_id}/export')
    assert exported.status_code == 200
    assert exported.json()['json']['entity'] == 'invoice'


def test_search_records_endpoint_matches_extracted_field():
    payload = valid_payload() | {'id': 'api-search-001'}
    assert client.post('/ingest', json=payload).status_code == 200
    response = client.get('/records/search', params={'field': 'entity', 'value': 'invoice'})
    assert response.status_code == 200
    assert any(item['payload_id'] == 'api-search-001' for item in response.json())


def test_query_endpoint_returns_hybrid_results():
    payload = valid_payload() | {'id': 'api-query-001'}
    assert client.post('/ingest', json=payload).status_code == 200
    response = client.post('/query', json={'field': 'entity', 'operator': 'eq', 'value': 'invoice'})
    assert response.status_code == 200
    body = response.json()
    assert body['matched_count'] >= 1
    assert 'JSON_EXTRACT' in body['sql_preview']['sql']
    assert any(item['payload_id'] == 'api-query-001' for item in body['records'])


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
