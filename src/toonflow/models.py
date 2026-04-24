from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class IngestRequest:
    source: str
    payload: dict[str, Any]
    payload_id: str | None = None
    received_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    record_count: int = 0


@dataclass(slots=True)
class IngestRecord:
    payload_id: str
    source: str
    original_json: dict[str, Any]
    toon_payload: str
    extracted_fields: dict[str, Any]
    status: str
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)

