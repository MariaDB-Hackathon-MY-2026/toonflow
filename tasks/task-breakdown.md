# Task Breakdown

## Ownership
All tasks are currently assigned to: **Dominic Low**

## Planned GitHub issue breakdown

### 1. Project organisation and documentation
- Set up repo structure
- Finalise scope summary
- Publish roadmap and architecture docs
- Maintain task tracking
- Start: 23 Apr 2026
- Target completion: 23 Apr 2026

### 2. JSON validation and ingestion pipeline
- Accept JSON input
- Validate schema / structure
- Record failures and ingestion status
- Start: 23 Apr 2026
- Target completion: 24 Apr 2026
- Implementation status: end-to-end backend path added with accepted/rejected record handling, strict JSON checks, ISO timestamp validation, and audit-friendly error storage.

### 3. JSON to TOON conversion layer
- Convert validated JSON payloads to TOON
- Add conversion tests / sample records
- Start: 23 Apr 2026
- Target completion: 24 Apr 2026
- Implementation status: converter added with compact nested/object-list formatting, scalar list handling, SQL-friendly field extraction, and sample coverage.

### 4. MariaDB schema and dual-storage design
- Store TOON payloads
- Store extracted SQL-queryable fields
- Store metadata
- Start: 23 Apr 2026
- Target completion: 24 Apr 2026
- Implementation status: MariaDB schema added for `toon_records` plus indexed `toon_record_fields`, with repository upsert, field-row refresh, rollback handling, and queryable field rows.

### 5. Core API endpoints
- Ingest record
- Read record by ID
- Export record in JSON / TOON
- Validation helper endpoint(s)
- Start: 24 Apr 2026
- Target completion: 25 Apr 2026
- Status: implemented in PR #14. Focused API added for health, validation, conversion, ingest, list, read, and JSON/TOON export. Invalid ingests are stored as rejected records for audit.

### 6. Batch ingestion support
- Multi-record ingest path
- Basic batch error reporting
- Start: 25 Apr 2026
- Target completion: 26 Apr 2026

### 7. Benchmark protocol and measurements
- Define benchmark inputs and method
- Measure payload size, token count, estimated cost, conversion time, ingestion throughput
- Start: 25 Apr 2026
- Target completion: 27 Apr 2026

### 8. Interactive demo
- Paste JSON
- Validate
- Convert/store
- Compare JSON vs TOON metrics
- Run one hybrid query
- Export record
- Start: 27 Apr 2026
- Target completion: 28 Apr 2026

### 9. Testing, polish, and final demo readiness
- Reliability pass
- Docs cleanup
- Demo rehearsal
- Final repo cleanup
- Start: 28 Apr 2026
- Target completion: 28 Apr 2026
