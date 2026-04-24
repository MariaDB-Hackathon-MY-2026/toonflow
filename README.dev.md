# Local development

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

For live MariaDB connector work, install MariaDB Connector/C on the host first, then run:

```bash
python -m pip install -r requirements-mariadb.txt
```

## Run tests

```bash
PYTHONPATH=src python -m pytest tests -q
```

## Run JSON vs TOON benchmark

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```

## Current backend slice

The current implementation covers:
- JSON validation
- JSON to compact TOON-style conversion
- SQL-friendly field extraction
- MariaDB dual-storage schema draft
- service/API skeleton
- benchmark tooling for JSON vs TOON payload size, token estimate, and conversion time
