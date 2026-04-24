from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Protocol
from uuid import uuid4

from .converter import flatten_query_fields, json_to_toon
from .models import IngestRecord, IngestRequest
from .storage import build_export_payload
from .validator import validate_payload


class RecordRepository(Protocol):
    def save(self, record: IngestRecord) -> IngestRecord: ...


def _resolve_payload_id(payload: Any, explicit_payload_id: str | None) -> str:
    if explicit_payload_id:
        return explicit_payload_id
    payload_id = payload.get('id') if isinstance(payload, Mapping) else None
    if isinstance(payload_id, str) and payload_id:
        return payload_id
    return str(uuid4())


def _copy_payload_for_audit(payload: Any) -> Any:
    copied_payload = dict(payload) if isinstance(payload, Mapping) else payload
    try:
        json.dumps(copied_payload, allow_nan=False)
    except (TypeError, ValueError):
        return {
            "_audit_note": "Payload was not strict JSON serialisable; stored repr for audit.",
            "raw_repr": repr(payload),
        }
    return copied_payload


def build_ingest_record(request: IngestRequest) -> IngestRecord:
    validation = validate_payload(request.payload)
    payload_id = _resolve_payload_id(request.payload, request.payload_id)
    toon_payload = json_to_toon(request.payload) if validation.ok else ''
    extracted_fields = flatten_query_fields(request.payload) if validation.ok else {}
    status = 'validated' if validation.ok else 'rejected'
    return IngestRecord(
        payload_id=payload_id,
        source=request.source,
        original_json=_copy_payload_for_audit(request.payload),
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


def ingest_payload(payload: Any, source: str = 'api', payload_id: str | None = None) -> dict[str, Any]:
    request = IngestRequest(source=source, payload=payload, payload_id=payload_id)
    record = build_ingest_record(request)
    return summarize_record(record)


def ingest_and_store_payload(
    payload: Any,
    repository: RecordRepository,
    source: str = 'pipeline',
    payload_id: str | None = None,
) -> dict[str, Any]:
    request = IngestRequest(source=source, payload=payload, payload_id=payload_id)
    record = build_ingest_record(request)
    repository.save(record)
    result = summarize_record(record)
    result['stored'] = True
    return result


def batch_ingest_and_store_payloads(
    payloads: list[Any],
    repository: RecordRepository,
    source: str = 'pipeline-batch',
) -> dict[str, Any]:
    records = build_batch_records(payloads, source=source)
    for record in records:
        repository.save(record)
    accepted = [record for record in records if record.status == 'validated']
    rejected = [record for record in records if record.status == 'rejected']
    return {
        'total': len(records),
        'accepted': len(accepted),
        'rejected': len(rejected),
        'stored': len(records),
        'records': [summarize_record(record) for record in records],
    }


def validate_only(payload: Any) -> dict[str, Any]:
    result = validate_payload(payload)
    return {
        'ok': result.ok,
        'errors': result.errors,
        'warnings': result.warnings,
        'record_count': result.record_count,
    }


def convert_only(payload: Any) -> dict[str, Any]:
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


def batch_ingest_payloads(payloads: list[Any], source: str = 'batch') -> dict[str, Any]:
    records = build_batch_records(payloads, source=source)
    accepted = [record for record in records if record.status == 'validated']
    rejected = [record for record in records if record.status == 'rejected']
    return {
        'total': len(records),
        'accepted': len(accepted),
        'rejected': len(rejected),
        'records': [summarize_record(record) for record in records],
    }


def build_batch_records(payloads: list[Any], source: str = 'batch') -> list[IngestRecord]:
    return [build_ingest_record(IngestRequest(source=source, payload=payload)) for payload in payloads]


def export_record(record: IngestRecord) -> dict[str, Any]:
    return build_export_payload(record)
