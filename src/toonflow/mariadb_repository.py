from __future__ import annotations

import json
from typing import Any

from .models import IngestRecord
from .storage import (
    SCHEMA_SQL,
    build_delete_fields_statement,
    build_field_insert_statement,
    build_field_rows,
    build_insert_statement,
    schema_statements,
)


class MariaDBRecordRepository:
    """Repository adapter for MariaDB Connector/Python style connections."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_schema(self) -> None:
        try:
            with self.connection.cursor() as cursor:
                for statement in schema_statements():
                    cursor.execute(statement)
            self.connection.commit()
        except Exception:
            self._rollback_if_supported()
            raise

    def save(self, record: IngestRecord) -> IngestRecord:
        try:
            sql, params = build_insert_statement(record)
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                delete_sql, delete_params = build_delete_fields_statement(record.payload_id)
                cursor.execute(delete_sql, delete_params)
                for row in build_field_rows(record):
                    field_sql, field_params = build_field_insert_statement(row)
                    cursor.execute(field_sql, field_params)
            self.connection.commit()
            return record
        except Exception:
            self._rollback_if_supported()
            raise

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

    def find_by_field(self, field_path: str, value: Any) -> list[dict[str, Any]]:
        sql = """
        SELECT r.payload_id, r.source, r.original_json, r.toon_payload, r.extracted_fields,
               r.status, r.validation_errors, r.validation_warnings, r.created_at
        FROM toon_records r
        JOIN toon_record_fields f ON f.payload_id = r.payload_id
        WHERE f.field_path = %s
          AND (
              f.value_string = %s
              OR f.value_number = %s
              OR f.value_boolean = %s
              OR (%s AND f.value_string IS NULL AND f.value_number IS NULL AND f.value_boolean IS NULL)
          )
        ORDER BY r.created_at DESC
        """.strip()
        string_value = None if value is None else str(value)
        number_value = _as_float(value)
        bool_value = _as_bool(value)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (field_path, string_value, number_value, bool_value, value is None))
            rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]

    def _rollback_if_supported(self) -> None:
        if hasattr(self.connection, "rollback"):
            self.connection.rollback()


def _loads(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


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
