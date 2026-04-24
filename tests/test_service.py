from toonflow.service import (
    batch_ingest_and_store_payloads,
    batch_ingest_payloads,
    build_ingest_record,
    convert_only,
    ingest_and_store_payload,
    ingest_payload,
    validate_only,
)
from toonflow.models import IngestRequest
from toonflow.repository import InMemoryRecordStore


def valid_payload():
    return {
        'entity': 'invoice',
        'timestamp': '2026-04-23T12:00:00Z',
        'data': {'customer': {'name': 'Alice'}, 'amount': 245.50},
    }


def test_build_ingest_record_valid_payload():
    request = IngestRequest(source='test', payload=valid_payload())
    record = build_ingest_record(request)
    assert record.status == 'validated'
    assert record.toon_payload
    assert record.extracted_fields['data.customer.name'] == 'Alice'


def test_ingest_payload_rejected_on_invalid_payload():
    result = ingest_payload({'entity': 'invoice'}, source='test')
    assert result['status'] == 'rejected'
    assert result['toon_payload'] == ''
    assert result['validation_errors']


def test_ingest_payload_rejects_non_object_without_crashing():
    result = ingest_payload(['not', 'object'], source='test', payload_id='bad-list')
    assert result['payload_id'] == 'bad-list'
    assert result['status'] == 'rejected'
    assert result['validation_errors'] == ['Payload must be a JSON object']


def test_invalid_payload_id_type_is_not_used_as_storage_id():
    request = IngestRequest(source='test', payload=valid_payload() | {'id': 123})
    record = build_ingest_record(request)
    assert record.status == 'rejected'
    assert isinstance(record.payload_id, str)
    assert record.payload_id != '123'


def test_ingest_and_store_rejects_non_object_json_without_crashing():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload(['not', 'an', 'object'], store, source='test', payload_id='bad-list')
    stored = store.get('bad-list')
    assert result['status'] == 'rejected'
    assert stored is not None
    assert stored.original_json == ['not', 'an', 'object']
    assert stored.validation_errors == ['Payload must be a JSON object']


def test_rejected_non_serialisable_payload_keeps_auditable_json_safe_repr():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload({'entity': 'invoice', 'bad': {1, 2}}, store, source='test', payload_id='bad-set')
    stored = store.get('bad-set')
    assert result['status'] == 'rejected'
    assert stored is not None
    assert stored.original_json['_audit_note'].startswith('Payload was not strict JSON serialisable')
    assert 'bad' in stored.original_json['raw_repr']


def test_validate_and_convert_helpers():
    validation = validate_only(valid_payload())
    assert validation['ok'] is True
    conversion = convert_only(valid_payload())
    assert conversion['status'] == 'converted'
    assert conversion['toon_payload']


def test_batch_ingest_summarises_accepted_and_rejected():
    result = batch_ingest_payloads([valid_payload(), {'entity': 'invoice'}], source='test')
    assert result['total'] == 2
    assert result['accepted'] == 1
    assert result['rejected'] == 1


def test_ingest_and_store_payload_persists_valid_record_end_to_end():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload(valid_payload(), store, source='test', payload_id='stored-001')
    assert result['status'] == 'validated'
    assert result['stored'] is True
    stored = store.get('stored-001')
    assert stored is not None
    assert stored.toon_payload
    assert stored.extracted_fields['data.customer.name'] == 'Alice'


def test_ingest_and_store_payload_persists_rejected_record_with_errors():
    store = InMemoryRecordStore()
    result = ingest_and_store_payload({'entity': 'invoice'}, store, source='test', payload_id='bad-001')
    assert result['status'] == 'rejected'
    stored = store.get('bad-001')
    assert stored is not None
    assert stored.validation_errors
    assert stored.toon_payload == ''


def test_batch_ingest_and_store_payloads_persists_all_statuses():
    store = InMemoryRecordStore()
    result = batch_ingest_and_store_payloads([valid_payload(), {'entity': 'invoice'}], store, source='test')
    assert result['total'] == 2
    assert result['stored'] == 2
    assert len(store.list()) == 2
