# Submission Readiness

TOONFlow is ready for organizer review from PR #11.

## Implemented scope
- JSON validation and ingestion with accepted/rejected record tracking
- JSON-to-TOON conversion for nested objects, arrays, and scalar fields
- SQL-friendly extracted-field storage alongside compact TOON payloads
- MariaDB schema and repository adapter for dual storage
- FastAPI endpoints for validation, conversion, ingest, batch ingest, record lookup, query, and export
- Interactive Streamlit evaluator flow for pasted JSON, metrics, ingest, hybrid query, and TOON export
- JSON vs TOON benchmark protocol, JSON result output, and Markdown report
- Full verification script for tests, core pipeline, and benchmark generation

## Verification evidence
Latest local verification command:

```bash
PYTHONPATH=src python scripts/verify_all.py
```

Latest result:

```text
73 passed, 1 skipped
Processed 12 payload(s)
Accepted: 10
Rejected: 2
Stored records: 12
JSON bytes: 18439
TOON bytes: 11023
Byte savings: 40.22%
Estimated token savings: 40.23%
All verification checks passed.
```

## Review notes
- Optional live MariaDB integration test is skipped unless `TOONFLOW_DB_*` environment variables are configured.
- The default local path uses the in-memory repository so reviewers can run tests and demo flows without a MariaDB instance.
- MariaDB-specific setup is documented in `README.dev.md` and `requirements-mariadb.txt`.
