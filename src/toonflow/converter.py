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
    text = str(value)
    if text and "\n" not in text and not any(char in text for char in ",[]{}"):
        return text
    return json.dumps(text, ensure_ascii=False)


def _inline_list(values: list[Any]) -> str:
    return "[" + ",".join(_format_scalar(value) for value in values) + "]"


def _is_scalar(value: Any) -> bool:
    return not isinstance(value, (Mapping, list))


def _table_columns(values: list[Any]) -> list[str] | None:
    if not values or not all(isinstance(item, Mapping) for item in values):
        return None

    first_keys = list(values[0].keys())
    if not first_keys:
        return None

    for item in values:
        if list(item.keys()) != first_keys:
            return None
        if not all(_is_scalar(value) for value in item.values()):
            return None
    return [str(key) for key in first_keys]


def _toon_lines(obj: Any, indent: int = 0) -> list[str]:
    pad = " " * indent
    lines: list[str] = []

    if not isinstance(obj, Mapping):
        return [f"{pad}value: {_format_scalar(obj)}"]

    for key, value in obj.items():
        if isinstance(value, Mapping):
            lines.append(f"{pad}{key}:")
            lines.extend(_toon_lines(value, indent + 2))
        elif isinstance(value, list):
            if all(not isinstance(item, (Mapping, list)) for item in value):
                lines.append(f"{pad}{key}: {_inline_list(value)}")
            elif columns := _table_columns(value):
                lines.append(f"{pad}{key}[{len(value)}]{{{','.join(columns)}}}:")
                for item in value:
                    row = ",".join(_format_scalar(item[column]) for column in columns)
                    lines.append(f"{' ' * (indent + 2)}{row}")
            else:
                lines.append(f"{pad}{key}[{len(value)}]:")
                for item in value:
                    if isinstance(item, Mapping):
                        child_lines = _toon_lines(item, indent + 4)
                        if child_lines:
                            first = child_lines[0].lstrip()
                            lines.append(f"{' ' * (indent + 2)}- {first}")
                            lines.extend(child_lines[1:])
                    else:
                        lines.append(f"{' ' * (indent + 2)}- {_format_scalar(item)}")
        else:
            lines.append(f"{pad}{key}: {_format_scalar(value)}")

    return lines


def json_to_toon(payload: Mapping[str, Any]) -> str:
    """Return a compact TOON-style representation suitable for prompt transport."""

    return "\n".join(_toon_lines(payload))


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
