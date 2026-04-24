# Local development

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run tests

```bash
PYTHONPATH=src python -m pytest tests -q
```

## Current backend slice

The current implementation covers:
- JSON validation
- JSON to compact TOON-style conversion
- SQL-friendly field extraction
- MariaDB dual-storage schema draft
- service/API skeleton
