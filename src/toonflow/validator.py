from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .models import ValidationResult


REQUIRED_TOP_LEVEL_KEYS = ("entity", "timestamp", "data")


def _is_iso_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_payload(payload: Mapping[str, Any]) -> ValidationResult:
    """Validate the minimum JSON contract used by the first TOONFlow slice.

    The validator is intentionally conservative: it does not try to impose a full
    business schema yet, but it rejects payloads that cannot be ingested safely.
    """

    if not isinstance(payload, Mapping):
        return ValidationResult(ok=False, errors=["Payload must be a JSON object"])

    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in payload:
            errors.append(f"Missing required top-level key: {key}")

    entity = payload.get("entity")
    if entity is not None and not isinstance(entity, str):
        errors.append("'entity' must be a string")
    elif entity == "":
        errors.append("'entity' cannot be empty")

    timestamp = payload.get("timestamp")
    if timestamp is not None and not isinstance(timestamp, str):
        errors.append("'timestamp' must be an ISO-8601 string")
    elif timestamp == "":
        errors.append("'timestamp' cannot be empty")
    elif isinstance(timestamp, str) and not _is_iso_timestamp(timestamp):
        errors.append("'timestamp' must be a valid ISO-8601 timestamp")

    data_obj = payload.get("data")
    if data_obj is not None and not isinstance(data_obj, Mapping):
        errors.append("'data' must be a JSON object")
    elif isinstance(data_obj, Mapping) and len(data_obj) == 0:
        warnings.append("'data' object is empty")

    if payload.get("id") is None:
        warnings.append("Payload does not include an 'id'; a generated payload_id will be used")
    elif not isinstance(payload.get("id"), str):
        errors.append("'id' must be a string when provided")

    try:
        json.dumps(payload)
    except (TypeError, ValueError):
        errors.append("Payload must be JSON serialisable")

    record_count = 1 if isinstance(data_obj, Mapping) else 0
    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, record_count=record_count)
