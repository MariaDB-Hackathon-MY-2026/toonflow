from __future__ import annotations

import json
from typing import Any

from .models import IngestRecord
from .storage import SCHEMA_SQL, build_insert_statement


class MariaDBRecordRepository:
    """Repository adapter for MariaDB Connector/Python style connections."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_schema(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL)
        self.connection.commit()

    def save(self, record: IngestRecord) -> IngestRecord:
        sql, params = build_insert_statement(record)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
        self.connection.commit()
        return record

    def get(self, payload_id: str) -> dict[str, Any] | None:
        sql = """
        SELECT payload_id, source, original_json, toon_payload, extracted_fields,
               status, validation_errors, validation_warnings, created_at
        FROM toon_records
        WHERE payload_id = %s
        """.strip()
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (payload_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(row)

    def list(self) -> list[dict[str, Any]]:
        sql = """
        SELECT payload_id, source, original_json, toon_payload, extracted_fields,
               status, validation_errors, validation_warnings, created_at
        FROM toon_records
        ORDER BY created_at DESC
        """.strip()
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]


def _loads(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return {
        'payload_id': row[0],
        'source': row[1],
        'json': _loads(row[2]),
        'toon': row[3],
        'extracted_fields': _loads(row[4]),
        'status': row[5],
        'validation_errors': _loads(row[6]),
        'validation_warnings': _loads(row[7]),
        'created_at': row[8].isoformat() if hasattr(row[8], 'isoformat') else str(row[8]),
    }
