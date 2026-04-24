from __future__ import annotations

from typing import Any
from uuid import uuid4

from .converter import flatten_query_fields, json_to_toon
from .models import IngestRecord, IngestRequest
from .storage import build_export_payload
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


def summarize_record(record: IngestRecord) -> dict[str, Any]:
    return {
        'payload_id': record.payload_id,
        'source': record.source,
        'status': record.status,
        'toon_payload': record.toon_payload,
        'extracted_fields': record.extracted_fields,
        'validation_errors': record.validation_errors,
        'validation_warnings': record.validation_warnings,
        'created_at': record.created_at.isoformat(),
    }


def ingest_payload(payload: dict[str, Any], source: str = 'api', payload_id: str | None = None) -> dict[str, Any]:
    request = IngestRequest(source=source, payload=payload, payload_id=payload_id)
    record = build_ingest_record(request)
    return summarize_record(record)


def validate_only(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_payload(payload)
    return {
        'ok': result.ok,
        'errors': result.errors,
        'warnings': result.warnings,
        'record_count': result.record_count,
    }


def convert_only(payload: dict[str, Any]) -> dict[str, Any]:
    validation = validate_payload(payload)
    if not validation.ok:
        return {
            'status': 'rejected',
            'toon_payload': '',
            'validation_errors': validation.errors,
            'validation_warnings': validation.warnings,
        }
    return {
        'status': 'converted',
        'toon_payload': json_to_toon(payload),
        'extracted_fields': flatten_query_fields(payload),
        'validation_errors': validation.errors,
        'validation_warnings': validation.warnings,
    }


def batch_ingest_payloads(payloads: list[dict[str, Any]], source: str = 'batch') -> dict[str, Any]:
    records = build_batch_records(payloads, source=source)
    accepted = [record for record in records if record.status == 'validated']
    rejected = [record for record in records if record.status == 'rejected']
    return {
        'total': len(records),
        'accepted': len(accepted),
        'rejected': len(rejected),
        'records': [summarize_record(record) for record in records],
    }


def build_batch_records(payloads: list[dict[str, Any]], source: str = 'batch') -> list[IngestRecord]:
    return [build_ingest_record(IngestRequest(source=source, payload=payload)) for payload in payloads]


def export_record(record: IngestRecord) -> dict[str, Any]:
    return build_export_payload(record)
