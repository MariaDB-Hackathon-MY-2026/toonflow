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
""".strip()


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
    """.strip()

    params = (
        record.payload_id,
        record.source,
        json.dumps(record.original_json, ensure_ascii=False, separators=(",", ":")),
        record.toon_payload,
        json.dumps(record.extracted_fields, ensure_ascii=False, separators=(",", ":")),
        record.status,
        json.dumps(record.validation_errors, ensure_ascii=False),
        json.dumps(record.validation_warnings, ensure_ascii=False),
        record.created_at.replace(tzinfo=None),
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
    with connection.cursor() as cursor:
        cursor.execute(SCHEMA_SQL)
    connection.commit()


def store_record(connection: Any, record: IngestRecord) -> None:
    sql, params = build_insert_statement(record)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
    connection.commit()

