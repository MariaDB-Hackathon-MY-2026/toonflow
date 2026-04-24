from __future__ import annotations

import json
from typing import Any

from .models import IngestRecord


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS toon_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payload_id VARCHAR(128) NOT NULL UNIQUE,
    source VARCHAR(128) NOT NULL,
    original_json JSON NOT NULL,
    toon_payload LONGTEXT NOT NULL,
    extracted_fields JSON NOT NULL,
    status VARCHAR(32) NOT NULL,
    validation_errors JSON NOT NULL,
    validation_warnings JSON NOT NULL,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_payload_id (payload_id),
    INDEX idx_source (source),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS toon_record_fields (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payload_id VARCHAR(128) NOT NULL,
    field_path VARCHAR(255) NOT NULL,
    value_string TEXT NULL,
    value_number DOUBLE NULL,
    value_boolean BOOLEAN NULL,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_field_path (field_path),
    INDEX idx_payload_field (payload_id, field_path),
    INDEX idx_field_string (field_path, value_string(191)),
    INDEX idx_field_number (field_path, value_number),
    CONSTRAINT fk_toon_record_fields_payload
        FOREIGN KEY (payload_id) REFERENCES toon_records(payload_id)
        ON DELETE CASCADE
);
""".strip()


def schema_statements() -> list[str]:
    return [statement.strip() for statement in SCHEMA_SQL.split(";\n") if statement.strip()]


def dumps_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def build_insert_statement(record: IngestRecord) -> tuple[str, tuple[Any, ...]]:
    sql = """
    INSERT INTO toon_records (
        payload_id,
        source,
        original_json,
        toon_payload,
        extracted_fields,
        status,
        validation_errors,
        validation_warnings,
        created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        source = VALUES(source),
        original_json = VALUES(original_json),
        toon_payload = VALUES(toon_payload),
        extracted_fields = VALUES(extracted_fields),
        status = VALUES(status),
        validation_errors = VALUES(validation_errors),
        validation_warnings = VALUES(validation_warnings),
        created_at = VALUES(created_at)
    """.strip()

    params = (
        record.payload_id,
        record.source,
        dumps_json(record.original_json),
        record.toon_payload,
        dumps_json(record.extracted_fields),
        record.status,
        dumps_json(record.validation_errors),
        dumps_json(record.validation_warnings),
        record.created_at.replace(tzinfo=None),
    )
    return sql, params


def build_delete_fields_statement(payload_id: str) -> tuple[str, tuple[Any, ...]]:
    return "DELETE FROM toon_record_fields WHERE payload_id = %s", (payload_id,)


def build_field_rows(record: IngestRecord) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field_path, value in record.extracted_fields.items():
        row = {
            "payload_id": record.payload_id,
            "field_path": field_path,
            "value_string": None,
            "value_number": None,
            "value_boolean": None,
            "created_at": record.created_at.replace(tzinfo=None),
        }
        if isinstance(value, bool):
            row["value_boolean"] = value
            row["value_string"] = str(value).lower()
        elif isinstance(value, (int, float)):
            row["value_number"] = float(value)
            row["value_string"] = str(value)
        elif value is not None:
            row["value_string"] = str(value)
        rows.append(row)
    return rows


def build_field_insert_statement(row: dict[str, Any]) -> tuple[str, tuple[Any, ...]]:
    sql = """
    INSERT INTO toon_record_fields (
        payload_id,
        field_path,
        value_string,
        value_number,
        value_boolean,
        created_at
    ) VALUES (%s, %s, %s, %s, %s, %s)
    """.strip()
    params = (
        row["payload_id"],
        row["field_path"],
        row["value_string"],
        row["value_number"],
        row["value_boolean"],
        row["created_at"],
    )
    return sql, params


def build_export_payload(record: IngestRecord) -> dict[str, Any]:
    return {
        "payload_id": record.payload_id,
        "source": record.source,
        "status": record.status,
        "json": record.original_json,
        "toon": record.toon_payload,
        "extracted_fields": record.extracted_fields,
        "validation": {
            "errors": record.validation_errors,
            "warnings": record.validation_warnings,
        },
        "created_at": record.created_at.isoformat(),
    }


def create_schema(connection: Any) -> None:
    try:
        with connection.cursor() as cursor:
            for statement in schema_statements():
                cursor.execute(statement)
        connection.commit()
    except Exception:
        if hasattr(connection, "rollback"):
            connection.rollback()
        raise


def store_record(connection: Any, record: IngestRecord) -> None:
    try:
        sql, params = build_insert_statement(record)
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            delete_sql, delete_params = build_delete_fields_statement(record.payload_id)
            cursor.execute(delete_sql, delete_params)
            for row in build_field_rows(record):
                field_sql, field_params = build_field_insert_statement(row)
                cursor.execute(field_sql, field_params)
        connection.commit()
    except Exception:
        if hasattr(connection, "rollback"):
            connection.rollback()
        raise
