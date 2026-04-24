from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def _flatten_lines(obj: Any, prefix: str = "") -> list[str]:
    lines: list[str] = []

    if isinstance(obj, Mapping):
        for key, value in obj.items():
            field = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, Mapping):
                lines.extend(_flatten_lines(value, field))
            elif isinstance(value, list):
                lines.append(f"{field}[]: {len(value)}")
                for index, item in enumerate(value):
                    item_field = f"{field}[{index}]"
                    if isinstance(item, Mapping):
                        lines.extend(_flatten_lines(item, item_field))
                    else:
                        lines.append(f"{item_field}: {_format_scalar(item)}")
            else:
                lines.append(f"{field}: {_format_scalar(value)}")
    else:
        lines.append(f"value: {_format_scalar(obj)}")

    return lines


def json_to_toon(payload: Mapping[str, Any]) -> str:
    """Return a compact field-path representation suitable for prompt transport.

    This first implementation uses explicit flattened paths so the output remains
    easy to inspect, benchmark, and map back to SQL-friendly extracted fields.
    """

    return "\n".join(_flatten_lines(payload))


def flatten_query_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extract scalar/queryable fields from a JSON object.

    Nested scalar fields are represented with dot paths. Lists are represented by a
    length field, and scalar lists also get a joined preview value.
    """

    fields: dict[str, Any] = {}

    def visit(obj: Any, prefix: str = "") -> None:
        if not isinstance(obj, Mapping):
            return

        for key, value in obj.items():
            field = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, Mapping):
                visit(value, field)
            elif isinstance(value, list):
                fields[f"{field}.__len__"] = len(value)
                if value and all(not isinstance(item, (Mapping, list)) for item in value):
                    fields[field] = ",".join(str(item) for item in value)
            else:
                fields[field] = value

    visit(payload)
    return fields

