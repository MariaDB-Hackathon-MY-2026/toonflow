from __future__ import annotations

from typing import Any

try:
    from fastapi import Body, FastAPI, HTTPException
except ImportError:  # keeps the core package importable without API extras
    Body = None
    FastAPI = None
    HTTPException = Exception

from .models import IngestRecord, IngestRequest
from .repository import InMemoryRecordStore
from .service import build_ingest_record, convert_only, export_record, summarize_record, validate_only


store = InMemoryRecordStore()
app = FastAPI(title="TOONFlow API") if FastAPI else None


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

    @app.post("/validate")
    def validate_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        return validate_only(payload)

    @app.post("/convert")
    def convert_endpoint(payload: Any = Body(...)) -> dict[str, Any]:
        result = convert_only(payload)
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

    @app.get("/records")
    def list_records_endpoint() -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.list()]

    @app.get("/records/{payload_id}")
    def read_record_endpoint(payload_id: str) -> dict[str, Any]:
        return summarize_record(_record_or_404(payload_id))

    @app.get("/records/{payload_id}/export")
    def export_record_endpoint(payload_id: str, format: str = "full") -> dict[str, Any]:
        return _export_record_as(_record_or_404(payload_id), format)
