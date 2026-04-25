# Development Roadmap

## Phase 1 — Project organisation (23 Apr)
- Finalise scope
- Break work into tasks
- Set milestones and documentation

## Phase 2 — Core ingestion path (23–24 Apr)
- Implement JSON validation
- Implement JSON to TOON conversion
- Define MariaDB schema
- Store payloads, metadata, and extracted fields

Status: implemented in PR #13. Sample JSON payloads can be validated, converted to TOON, flattened into queryable fields, and stored through the in-memory or MariaDB repository paths. Invalid samples are stored as rejected records with validation errors so ingestion failures remain auditable.

## Phase 3 — API and retrieval flow (24–25 Apr)
- Add ingest endpoint(s)
- Add read/export endpoint(s)
- Add validation and conversion helpers

## Phase 4 — Batch and benchmark work (25–27 Apr)
- Add batch ingestion flow
- Define benchmark protocol
- Measure payload size, token count, estimated cost, conversion time, and ingestion throughput

## Phase 5 — Demo and polish (27–28 Apr)
- Build simple interactive demo
- Add one hybrid SQL + TOON workflow
- Improve docs and setup instructions

## Phase 6 — Final validation (28 Apr)
- Bug fixing
- Demo rehearsal
- Benchmark verification
- Repo cleanup
