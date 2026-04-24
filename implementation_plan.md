# Implementation Plan

## Goal
Build a reliability-focused JSON-to-TOON ingestion gateway for MariaDB that proves practical value for AI-ready data workflows.

## Delivery priorities
### Must-have
1. JSON input ingestion
2. Validation and error handling
3. JSON to TOON conversion
4. Dual storage in MariaDB
5. Core read/export APIs
6. Batch ingestion support
7. Benchmark protocol and measurements
8. Simple interactive evaluator demo

### Stretch goals
- Richer observability
- Additional benchmarking dimensions
- Extra UI polish
- Packaging improvements for reuse

## Delivery principle
Prefer proof over breadth: every major claim should be backed by either a working flow, a benchmark, or a clear demo step.

## Current proof for core ingestion
Status: implemented in PR #13. The first core backend path now has runnable evidence:

```bash
PYTHONPATH=src python -m pytest tests -q
PYTHONPATH=src python scripts/run_core_pipeline.py --invalid-samples data/invalid_samples
```

This verifies JSON validation, rejection/audit behaviour, JSON-to-TOON conversion, extracted SQL-friendly fields, and dual-storage preparation for MariaDB.
