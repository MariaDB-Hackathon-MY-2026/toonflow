from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import IngestRecord


SUPPORTED_OPERATORS = {"eq", "contains", "gt", "gte", "lt", "lte"}


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def field_matches(actual: Any, expected: Any, operator: str = "eq") -> bool:
    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"Unsupported operator: {operator}")

    if operator == "eq":
        return str(actual) == str(expected)
    if operator == "contains":
        return str(expected).lower() in str(actual).lower()

    actual_number = _as_float(actual)
    expected_number = _as_float(expected)
    if actual_number is None or expected_number is None:
        return False
    if operator == "gt":
        return actual_number > expected_number
    if operator == "gte":
        return actual_number >= expected_number
    if operator == "lt":
        return actual_number < expected_number
    return actual_number <= expected_number


def query_records(
    records: Iterable[IngestRecord],
    field: str,
    value: Any,
    operator: str = "eq",
) -> list[IngestRecord]:
    return [
        record
        for record in records
        if field in record.extracted_fields
        and field_matches(record.extracted_fields[field], value, operator)
    ]


def build_sql_preview(field: str, operator: str = "eq") -> dict[str, Any]:
    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"Unsupported operator: {operator}")

    json_path = '$."' + field.replace('"', '\\"') + '"'
    extracted_value = "JSON_UNQUOTE(JSON_EXTRACT(extracted_fields, %s))"
    op_map = {
        "eq": "=",
        "contains": "LIKE",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
    }
    comparator = op_map[operator]
    sql = f"""
    SELECT payload_id, source, toon_payload, extracted_fields
    FROM toon_records
    WHERE {extracted_value} {comparator} %s
    ORDER BY created_at DESC
    """.strip()
    return {
        "sql": sql,
        "params": [json_path, "%value%" if operator == "contains" else "value"],
        "note": "Preview only; the demo query uses extracted fields, then returns the TOON payload for downstream AI context.",
    }


def hybrid_query_response(
    records: Iterable[IngestRecord],
    field: str,
    value: Any,
    operator: str = "eq",
) -> dict[str, Any]:
    matches = query_records(records, field, value, operator)
    return {
        "query": {"field": field, "operator": operator, "value": value},
        "sql_preview": build_sql_preview(field, operator),
        "matched_count": len(matches),
        "records": [
            {
                "payload_id": record.payload_id,
                "source": record.source,
                "status": record.status,
                "matched_value": record.extracted_fields.get(field),
                "toon_payload": record.toon_payload,
                "extracted_fields": record.extracted_fields,
            }
            for record in matches
        ],
    }
