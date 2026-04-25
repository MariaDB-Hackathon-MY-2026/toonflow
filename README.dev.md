# Local development

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

The main requirements install FastAPI with its standard CLI/runtime extras and Streamlit for the evaluator demo.

For live MariaDB connector work, install MariaDB Connector/C on the host first, then run:

```bash
python -m pip install -r requirements-mariadb.txt
```

MariaDB connection settings are read from environment variables:

```bash
export TOONFLOW_DB_HOST=localhost
export TOONFLOW_DB_PORT=3306
export TOONFLOW_DB_USER=toonflow
export TOONFLOW_DB_PASSWORD=...
export TOONFLOW_DB_NAME=toonflow
```

## Run tests

```bash
PYTHONPATH=src python -m pytest tests -q
```

## Run core ingestion pipeline

```bash
PYTHONPATH=src python scripts/run_core_pipeline.py
```

This exercises the first backend path end-to-end: validate JSON, convert valid records to TOON, extract SQL-friendly fields, and store accepted/rejected records with ingestion status.

To include invalid sample payloads and verify rejected records remain auditable:

```bash
PYTHONPATH=src python scripts/run_core_pipeline.py --invalid-samples data/invalid_samples
```

To run the same core path against MariaDB after setting the environment variables above:

```bash
PYTHONPATH=src python scripts/run_mariadb_pipeline.py
```

It also accepts `--invalid-samples data/invalid_samples` for the same rejection/audit path against MariaDB.

The test suite includes an optional live MariaDB integration test. It is skipped unless the `TOONFLOW_DB_*` environment variables are configured.

## Current core backend slice

The current implementation covers:
- JSON validation and rejected-record auditing
- JSON to compact TOON-style conversion
- SQL-friendly field extraction
- MariaDB dual-storage schema and repository path
- core ingestion scripts for in-memory and MariaDB-backed storage

## Core API endpoints

```bash
PYTHONPATH=src fastapi dev src/toonflow/api.py
```

Implemented endpoints:
- `GET /health`
- `GET /demo`
- `POST /validate`
- `POST /convert`
- `POST /evaluate`
- `POST /ingest`
- `POST /batch/ingest`
- `POST /query`
- `GET /records`
- `GET /records/search`
- `GET /records/{payload_id}`
- `GET /records/{payload_id}/export`

Export supports `?format=full`, `?format=json`, or `?format=toon`.


## Run JSON vs TOON benchmark

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```

## Run full verification

```bash
PYTHONPATH=src python scripts/verify_all.py
```

## Streamlit demo flow

Run the evaluator-facing demo:

```bash
PYTHONPATH=src streamlit run demo/streamlit_app.py
```

The Streamlit demo supports pasted JSON evaluation, ingestion into an in-memory demo store, hybrid extracted-field query, and TOON export.

## FastAPI service flow

Run the API service, then open `/demo` for the lightweight API-hosted fallback page:

```bash
PYTHONPATH=src fastapi dev src/toonflow/api.py
```
