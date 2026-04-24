# Architecture

## High-level flow
1. JSON payload enters via API or batch upload
2. Input validation checks structure and required fields
3. Valid payload is converted from JSON to TOON
4. MariaDB stores:
   - the TOON payload
   - extracted query-friendly fields
   - metadata and ingestion status
5. Record can be queried, compared, and exported back out

## Main components
- **Ingestion API**: accepts single or batch payloads
- **Validation layer**: checks payloads before storage
- **Conversion layer**: transforms JSON into TOON
- **Storage layer**: MariaDB dual-storage design
- **Benchmark layer**: compares JSON vs TOON metrics
- **Demo layer**: interactive evaluator-facing workflow

## Data design intent
The architecture separates compact AI-oriented transport from normal SQL usability:
- TOON is used for compact storage / prompt-oriented workflows
- extracted fields are used for filtering, indexing, and reporting

## Core ingestion contract
The end-to-end backend path for the first implementation slice is:

1. validate the JSON envelope (`entity`, `timestamp`, `data`, optional string `id`)
2. reject malformed payloads with validation errors and ingestion status
3. convert valid payloads into TOON
4. flatten scalar fields into SQL-friendly paths such as `entity` or `data.amount`
5. persist both accepted and rejected records so failures are auditable

## MariaDB dual storage
The storage design keeps two complementary shapes:

- `toon_records`: full original JSON, TOON payload, extracted field JSON, metadata, status, errors, warnings
- `toon_record_fields`: relational field rows with `field_path`, string/number/boolean typed values, and indexes for query paths

This keeps the original payload and compact TOON representation intact while still allowing SQL-style lookup over extracted fields.

## Core API contract
The focused API layer for the first retrieval flow exposes:

- `POST /validate` for schema checks without storage
- `POST /convert` for JSON-to-TOON conversion previews
- `POST /ingest` for validation, conversion, extraction, and storage
- `GET /records` and `GET /records/{payload_id}` for retrieval
- `GET /records/{payload_id}/export?format=json|toon|full` for export

Rejected ingests return HTTP 400 but are still stored as rejected audit records.

## Reliability focus
The system should visibly support:
- validation
- error logging
- ingestion status tracking
- batch processing


## Demo and benchmark layer
The final demo layer builds on the core API:

- `/batch/ingest` stores mixed valid/invalid payload batches and reports partial failures
- `/evaluate` validates, converts, extracts fields, and returns JSON vs TOON metrics without storing
- `/query` filters stored records by extracted fields and returns TOON payloads for downstream AI context
- `/demo` provides a lightweight evaluator page for paste/evaluate/ingest/query flow
- benchmark scripts generate JSON and Markdown summaries for payload size, estimated tokens/cost, conversion latency, and throughput
