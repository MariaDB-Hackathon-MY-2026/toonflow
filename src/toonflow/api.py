from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # keep import-safe for local module testing
    FastAPI = None
    HTTPException = Exception

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

if app is not None:
    @app.get('/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    @app.post('/validate')
    def validate_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        return validate_only(payload)

    @app.post('/convert')
    def convert_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        result = convert_only(payload)
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

    @app.get('/records')
    def list_records_endpoint() -> list[dict[str, Any]]:
        return [summarize_record(record) for record in store.list()]

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
