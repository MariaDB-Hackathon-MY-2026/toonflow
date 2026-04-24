from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
except ImportError:  # keep import-safe for local module testing
    FastAPI = None
    HTTPException = Exception
    HTMLResponse = None

from .evaluator import evaluate_payload
from .query import hybrid_query_response
from .repository import InMemoryRecordStore
from .service import (
    batch_ingest_payloads,
    build_batch_records,
    build_ingest_record,
    convert_only,
    export_record,
    summarize_record,
    validate_only,
)


store = InMemoryRecordStore()

app = FastAPI(title='TOONFlow API') if FastAPI else None


DEMO_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>TOONFlow Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
    textarea { width: 100%; min-height: 260px; font-family: ui-monospace, monospace; }
    button { margin: 0.5rem 0.5rem 0.5rem 0; padding: 0.6rem 1rem; }
    pre { background: #111827; color: #e5e7eb; padding: 1rem; overflow: auto; }
  </style>
</head>
<body>
  <h1>TOONFlow evaluator</h1>
  <p>Paste JSON, validate it, convert it to TOON, and inspect extracted MariaDB query fields.</p>
  <textarea id="payload">{"id":"demo-ui-001","entity":"invoice","timestamp":"2026-04-24T10:00:00Z","data":{"customer":{"name":"Alice"},"amount":245.5}}</textarea>
  <br />
  <button onclick="send('/evaluate')">Evaluate</button>
  <button onclick="send('/ingest')">Ingest</button>
  <button onclick="queryDemo()">Query entity=invoice</button>
  <pre id="output">Ready.</pre>
  <script>
    async function send(path) {
      const payload = JSON.parse(document.getElementById('payload').value);
      const response = await fetch(path, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
      document.getElementById('output').textContent = JSON.stringify(await response.json(), null, 2);
    }
    async function queryDemo() {
      const response = await fetch('/query', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({field: 'entity', operator: 'eq', value: 'invoice'}) });
      document.getElementById('output').textContent = JSON.stringify(await response.json(), null, 2);
    }
  </script>
</body>
</html>
""".strip()

if app is not None:
    @app.get('/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    @app.get('/demo', response_class=HTMLResponse)
    def demo_page() -> str:
        return DEMO_HTML

    @app.post('/validate')
    def validate_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        return validate_only(payload)

    @app.post('/convert')
    def convert_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        result = convert_only(payload)
        if result['status'] == 'rejected':
            raise HTTPException(status_code=400, detail=result)
        return result

    @app.post('/evaluate')
    def evaluate_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        result = evaluate_payload(payload, payload_name=str(payload.get('id', 'payload')))
        if result['status'] == 'rejected':
            raise HTTPException(status_code=400, detail=result)
        return result

    @app.post('/ingest')
    def ingest_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        record = build_ingest_record_from_api(payload)
        result = summarize_record(record)
        if record.status == 'rejected':
            raise HTTPException(status_code=400, detail=result)
        store.save(record)
        return result

    @app.post('/batch/ingest')
    def batch_ingest_endpoint(payloads: list[dict[str, Any]]) -> dict[str, Any]:
        result = batch_ingest_payloads(payloads, source='api-batch')
        for record in build_batch_records(payloads, source='api-batch'):
            if record.status == 'validated':
                store.save(record)
        return result

    @app.post('/query')
    def query_endpoint(query: dict[str, Any]) -> dict[str, Any]:
        field = str(query.get('field', ''))
        value = query.get('value')
        operator = str(query.get('operator', 'eq'))
        if not field:
            raise HTTPException(status_code=400, detail={'message': 'field is required'})
        try:
            return hybrid_query_response(store.list(), field, value, operator)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail={'message': str(exc)}) from exc

    @app.get('/records')
    def list_records_endpoint() -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.list()]

    @app.get('/records/search')
    def search_records_endpoint(field: str, value: str) -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.find_by_field(field, value)]

    @app.get('/records/{payload_id}')
    def read_record_endpoint(payload_id: str) -> dict[str, Any]:
        record = store.get(payload_id)
        if record is None:
            raise HTTPException(status_code=404, detail={'message': 'Record not found'})
        return summarize_record(record)

    @app.get('/records/{payload_id}/export')
    def export_record_endpoint(payload_id: str) -> dict[str, Any]:
        record = store.get(payload_id)
        if record is None:
            raise HTTPException(status_code=404, detail={'message': 'Record not found'})
        return export_record(record)


def build_ingest_record_from_api(payload: dict[str, Any]):
    from .models import IngestRequest

    return build_ingest_record(IngestRequest(source='api', payload=payload))
