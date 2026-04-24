from __future__ import annotations

from typing import Any

from .benchmark import benchmark_payload
from .converter import flatten_query_fields, json_to_toon
from .validator import validate_payload


def evaluate_payload(payload: dict[str, Any], payload_name: str = "payload") -> dict[str, Any]:
    """Build the demo/evaluator response for one pasted JSON payload."""

    validation = validate_payload(payload)
    if not validation.ok:
        return {
            "status": "rejected",
            "validation": {
                "ok": False,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
            "toon_payload": "",
            "extracted_fields": {},
            "metrics": None,
        }

    metrics = benchmark_payload(payload, payload_name)
    return {
        "status": "ready",
        "validation": {
            "ok": True,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "toon_payload": json_to_toon(payload),
        "extracted_fields": flatten_query_fields(payload),
        "metrics": metrics.to_dict(),
    }
