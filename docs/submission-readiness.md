# Submission Readiness

TOONFlow is ready for organizer review from PR #11.

## Implemented scope
- JSON validation and ingestion with accepted/rejected record tracking
- JSON-to-TOON conversion for nested objects, arrays, and scalar fields
- SQL-friendly extracted-field storage alongside compact TOON payloads
- MariaDB schema and repository adapter for dual storage
- FastAPI endpoints for validation, conversion, ingest, batch ingest, record lookup, query, and export
- Interactive Streamlit evaluator flow for pasted JSON, metrics, ingest, hybrid query, and TOON export
- JSON vs TOON benchmark protocol, JSON result output, Markdown report, corpus-profile notes, and role-level savings breakdown
- Full verification script for tests, core pipeline, and benchmark generation

## Verification evidence
Latest local verification command:

```bash
PYTHONPATH=src python scripts/verify_all.py
```

Latest result:

```text
77 passed, 1 skipped
Processed 13 payload(s)
Accepted: 11
Rejected: 2
Stored records: 13
JSON bytes: 21526
TOON bytes: 12558
Byte savings: 41.66%
Estimated token savings: 41.67%
Lift vs original two-payload benchmark baseline: +32.27 percentage points byte savings; +32.11 percentage points estimated token savings
Corpus profile: 11 of 11 payloads documented across 11 realistic domains; role mix includes 9 operational batches, 1 small-document control, and 1 text-heavy control
Role breakdown: operational batches save 43.96% bytes / 43.97% estimated tokens; small-document control saves 8.7% / 8.7%; text-heavy control saves 25.34% / 25.3%
All verification checks passed.
```

## Review notes
- Optional live MariaDB integration test is skipped unless `TOONFLOW_DB_*` environment variables are configured.
- The default local path uses the in-memory repository so reviewers can run tests and demo flows without a MariaDB instance.
- MariaDB-specific setup is documented in `README.dev.md` and `requirements-mariadb.txt`.
