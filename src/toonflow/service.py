from __future__ import annotations

from typing import Any
from uuid import uuid4

from .converter import flatten_query_fields, json_to_toon
from .models import IngestRecord, IngestRequest
from .validator import validate_payload


def build_ingest_record(request: IngestRequest) -> IngestRecord:
    validation = validate_payload(request.payload)
    payload_id = request.payload_id or request.payload.get('id') or str(uuid4())
    toon_payload = json_to_toon(request.payload) if validation.ok else ''
    extracted_fields = flatten_query_fields(request.payload) if validation.ok else {}
    status = 'validated' if validation.ok else 'rejected'
    return IngestRecord(
        payload_id=payload_id,
        source=request.source,
        original_json=dict(request.payload),
        toon_payload=toon_payload,
        extracted_fields=extracted_fields,
        status=status,
        validation_errors=validation.errors,
        validation_warnings=validation.warnings,
        created_at=request.received_at,
    )


def ingest_payload(payload: dict[str, Any], source: str = 'api', payload_id: str | None = None) -> dict[str, Any]:
    request = IngestRequest(source=source, payload=payload, payload_id=payload_id)
    record = build_ingest_record(request)
    return {
        'payload_id': record.payload_id,
        'status': record.status,
        'toon_payload': record.toon_payload,
        'extracted_fields': record.extracted_fields,
        'validation_errors': record.validation_errors,
        'validation_warnings': record.validation_warnings,
    }
