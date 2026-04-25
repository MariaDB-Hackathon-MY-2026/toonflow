from __future__ import annotations

from typing import Any

try:
    from fastapi import Body, FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
except ImportError:  # keeps the core package importable without API extras
    Body = None
    FastAPI = None
    HTTPException = Exception
    HTMLResponse = None

from .evaluator import evaluate_payload
from .models import IngestRecord, IngestRequest
from .query import hybrid_query_response
from .repository import InMemoryRecordStore
from .service import build_batch_records, build_ingest_record, convert_only, export_record, summarize_record, validate_only


store = InMemoryRecordStore()
app = FastAPI(title="TOONFlow API") if FastAPI else None


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
  <p>Paste JSON, validate it, convert/store it, compare metrics, query extracted fields, and export TOON.</p>
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


def _record_or_404(payload_id: str) -> IngestRecord:
    record = store.get(payload_id)
    if record is None:
        raise HTTPException(status_code=404, detail={"message": "Record not found"})
    return record


def _export_record_as(record: IngestRecord, export_format: str) -> dict[str, Any]:
    if export_format == "full":
        return export_record(record)
    if export_format == "json":
        return {
            "payload_id": record.payload_id,
            "format": "json",
            "json": record.original_json,
            "status": record.status,
            "validation_errors": record.validation_errors,
        }
    if export_format == "toon":
        return {
            "payload_id": record.payload_id,
            "format": "toon",
            "toon": record.toon_payload,
            "status": record.status,
            "validation_errors": record.validation_errors,
        }
    raise HTTPException(status_code=400, detail={"message": "format must be one of: full, json, toon"})


if app is not None:

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/demo", response_class=HTMLResponse)
    def demo_page() -> str:
        return DEMO_HTML

    @app.post("/validate")
    def validate_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        return validate_only(payload)

    @app.post("/convert")
    def convert_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        result = convert_only(payload)
        if result["status"] == "rejected":
            raise HTTPException(status_code=400, detail=result)
        return result

    @app.post("/evaluate")
    def evaluate_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        result = evaluate_payload(payload, payload_name=str(payload.get("id", "payload")) if isinstance(payload, dict) else "payload")
        if result["status"] == "rejected":
            raise HTTPException(status_code=400, detail=result)
        return result

    @app.post("/ingest")
    def ingest_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        record = build_ingest_record(IngestRequest(source="api", payload=payload))
        store.save(record)
        result = summarize_record(record) | {"stored": True}
        if record.status == "rejected":
            raise HTTPException(status_code=400, detail=result)
        return result

    @app.post("/batch/ingest")
    def batch_ingest_endpoint(payloads: list[Any] = Body(...)) -> dict[str, Any]:
        records = build_batch_records(payloads, source="api-batch")
        for record in records:
            store.save(record)
        accepted = [record for record in records if record.status == "validated"]
        rejected = [record for record in records if record.status == "rejected"]
        return {
            "total": len(records),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "stored": len(records),
            "records": [summarize_record(record) for record in records],
        }

    @app.post("/query")
    def query_endpoint(query: dict[str, Any] = Body(...)) -> dict[str, Any]:
        field = str(query.get("field", ""))
        value = query.get("value")
        operator = str(query.get("operator", "eq"))
        if not field:
            raise HTTPException(status_code=400, detail={"message": "field is required"})
        try:
            return hybrid_query_response(store.list(), field, value, operator)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc

    @app.get("/records")
    def list_records_endpoint() -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.list()]

    @app.get("/records/search")
    def search_records_endpoint(field: str, value: str) -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.find_by_field(field, value)]

    @app.get("/records/{payload_id}")
    def read_record_endpoint(payload_id: str) -> dict[str, Any]:
        return summarize_record(_record_or_404(payload_id))

    @app.get("/records/{payload_id}/export")
    def export_record_endpoint(payload_id: str, format: str = "full") -> dict[str, Any]:
        return _export_record_as(_record_or_404(payload_id), format)
