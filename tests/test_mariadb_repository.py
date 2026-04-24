from toonflow.converter import flatten_query_fields, json_to_toon
from toonflow.mariadb_repository import MariaDBRecordRepository
from toonflow.models import IngestRecord


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.last_sql = None
        self.last_params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params
        self.connection.executed.append((sql, params))

    def fetchone(self):
        return self.connection.fetchone_result

    def fetchall(self):
        return self.connection.fetchall_result


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.commits = 0
        self.fetchone_result = None
        self.fetchall_result = []

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1


def sample_record():
    payload = {
        'id': 'demo-001',
        'entity': 'invoice',
        'timestamp': '2026-04-23T12:00:00Z',
        'data': {'amount': 245.5},
    }
    return IngestRecord(
        payload_id='demo-001',
        source='test',
        original_json=payload,
        toon_payload=json_to_toon(payload),
        extracted_fields=flatten_query_fields(payload),
        status='validated',
    )


def test_create_schema_executes_schema_and_commits():
    conn = FakeConnection()
    repo = MariaDBRecordRepository(conn)
    repo.create_schema()
    assert 'CREATE TABLE IF NOT EXISTS toon_records' in conn.executed[0][0]
    assert any('CREATE TABLE IF NOT EXISTS toon_record_fields' in sql for sql, _ in conn.executed)
    assert conn.commits == 1


def test_save_executes_insert_and_commits():
    conn = FakeConnection()
    repo = MariaDBRecordRepository(conn)
    repo.save(sample_record())
    sql, params = conn.executed[0]
    assert 'INSERT INTO toon_records' in sql
    assert params[0] == 'demo-001'
    assert any('INSERT INTO toon_record_fields' in sql for sql, _ in conn.executed)
    assert conn.commits == 1


def test_get_maps_row_to_dict():
    conn = FakeConnection()
    conn.fetchone_result = (
        'demo-001',
        'test',
        '{"entity":"invoice"}',
        'entity: invoice',
        '{"entity":"invoice"}',
        'validated',
        '[]',
        '[]',
        '2026-04-23 12:00:00',
    )
    repo = MariaDBRecordRepository(conn)
    result = repo.get('demo-001')
    assert result['payload_id'] == 'demo-001'
    assert result['json']['entity'] == 'invoice'
    assert result['status'] == 'validated'
