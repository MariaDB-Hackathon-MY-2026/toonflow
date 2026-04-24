from toonflow.service import batch_ingest_payloads, build_ingest_record, convert_only, ingest_payload, validate_only
from toonflow.models import IngestRequest


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
