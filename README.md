# TOONFlow for MariaDB

TOONFlow is a reliability-focused JSON-to-TOON ingestion gateway for MariaDB. It accepts standard JSON payloads, validates them, converts them into TOON, stores compact TOON alongside SQL-queryable extracted fields, and demonstrates measurable efficiency gains for LLM-oriented workflows.

## Problem
AI applications often need to send database records into LLM prompts for summarisation, search, analysis, or agent workflows. Many teams already store and exchange this data as JSON, but JSON repeats field names heavily, especially in operational batches such as invoices, telemetry windows, audit logs, tickets, or inventory records.

That repeated structure increases prompt size, token usage, and cost. At the same time, teams still need normal database behaviour: validation, auditability, storage, and SQL-queryable fields.

TOONFlow solves this by adding a MariaDB-backed ingestion layer that keeps JSON workflows familiar while producing compact TOON output for AI use.

## Who it is for
- **Developers** building AI features on top of existing JSON APIs or MariaDB-backed applications
- **Data teams** preparing structured operational records for LLM prompts
- **MariaDB users** who want AI-ready compact data without giving up SQL-friendly querying
- **Evaluators / judges** who need a simple demo showing JSON input, TOON output, storage, query, and benchmark evidence

## How users would use it
1. Send or paste a JSON payload into TOONFlow.
2. TOONFlow validates the payload and records accepted/rejected status.
3. Valid JSON is converted into compact TOON text.
4. MariaDB stores the original JSON, the TOON payload, validation metadata, and extracted query-friendly fields.
5. Users query records through extracted fields, then export TOON for downstream AI prompts.
6. Benchmark reports show how much smaller the TOON representation is compared with JSON.

## Why token savings matter
LLM prompts are usually priced and limited by token count. Smaller structured data means users can fit more records into a prompt, reduce cost, and keep AI context cleaner. In the included benchmark corpus, TOONFlow shows **41.66% byte savings** and **41.67% estimated token savings** versus compact JSON across realistic sample payloads.

## Core value proposition
- **Low-friction adoption path** from JSON to TOON
- **MariaDB-backed dual storage**: original JSON + compact TOON payload + query-friendly relational fields
- **Reliability-focused ingestion** with validation, logging, rejected-record tracking, and auditability
- **Measurable benchmark evidence** for JSON vs TOON byte and estimated token savings
- **Simple interactive demo** showing evaluate, ingest, query, and export flows

## Implemented scope
1. Reliable JSON ingestion pipeline
2. Dual-storage MariaDB schema
3. Core conversion and record APIs
4. Batch ingestion support
5. Benchmark protocol and results
6. Simple Streamlit evaluator demo
7. Clear documentation and setup guidance

## Project docs
- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [Technology Stack](docs/technology-stack.md)
- [Development Roadmap](docs/development-roadmap.md)
- [Resources](docs/resources.md)
- [Submission Readiness](docs/submission-readiness.md)
- [Task Breakdown](tasks/task-breakdown.md)
- [Implementation Plan](implementation_plan.md)

## Tech stack
- MariaDB
- Python
- FastAPI
- Streamlit
- MariaDB Connector/Python
- Custom TOON-style converter

## Fastest reviewer path

From a fresh clone, force the local branch to match the latest project branch and run the verification/demo flow.

### macOS / Linux / Git Bash

```bash
git clone https://github.com/MariaDB-Hackathon-MY-2026/toonflow.git
cd toonflow
git fetch origin dominiclow/project-setup
git checkout -B dominiclow/project-setup origin/dominiclow/project-setup
git log -1 --oneline
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/verify_all.py
PYTHONPATH=src streamlit run demo/streamlit_app.py
```

### Windows PowerShell

```powershell
git clone https://github.com/MariaDB-Hackathon-MY-2026/toonflow.git
cd toonflow
git fetch origin dominiclow/project-setup
git checkout -B dominiclow/project-setup origin/dominiclow/project-setup
git log -1 --oneline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python scripts/verify_all.py
streamlit run demo/streamlit_app.py
```

The default demo uses an in-memory store, so reviewers do not need a live MariaDB server for the main verification path. MariaDB setup is optional for testing the live database repository path.

## Quick verification

If the repository is already checked out:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/verify_all.py
```

Latest verification result: `77 passed, 1 skipped`; core pipeline and benchmark generation both pass. Current benchmark totals show 41.66% byte savings and 41.67% estimated token savings across the realistic sample corpus, with the generated report showing a +32.27 percentage-point byte-savings lift versus the original two-payload benchmark baseline, corpus-profile notes for every sample, and role-level savings for operational batches versus controls.

## Run the demo

```bash
PYTHONPATH=src streamlit run demo/streamlit_app.py
```

## Current status
TOONFlow is implementation-complete for the planned hackathon scope. The verification steps above show the current tested state.
