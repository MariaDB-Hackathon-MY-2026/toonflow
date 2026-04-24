from __future__ import annotations

from collections.abc import Iterable

from .models import IngestRecord


class InMemoryRecordStore:
    """Small repository used by the demo/API before MariaDB is wired in."""

    def __init__(self) -> None:
        self._records: dict[str, IngestRecord] = {}

    def save(self, record: IngestRecord) -> IngestRecord:
        self._records[record.payload_id] = record
        return record

    def get(self, payload_id: str) -> IngestRecord | None:
        return self._records.get(payload_id)

    def list(self) -> list[IngestRecord]:
        return list(self._records.values())

    def find_by_field(self, field: str, value: str) -> list[IngestRecord]:
        return [
            record
            for record in self._records.values()
            if str(record.extracted_fields.get(field)) == value
        ]

    def save_many(self, records: Iterable[IngestRecord]) -> list[IngestRecord]:
        saved: list[IngestRecord] = []
        for record in records:
            saved.append(self.save(record))
        return saved

    def clear(self) -> None:
        self._records.clear()
