from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # keep import-safe for local module testing
    FastAPI = None
    HTTPException = Exception

from .service import ingest_payload

app = FastAPI(title='TOONFlow API') if FastAPI else None

if app is not None:
    @app.get('/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    @app.post('/ingest')
    def ingest_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        result = ingest_payload(payload, source='api')
        if result['status'] == 'rejected':
            raise HTTPException(status_code=400, detail=result)
        return result
