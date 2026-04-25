# TOONFlow for MariaDB

TOONFlow is a reliability-focused JSON-to-TOON ingestion gateway for MariaDB. It accepts standard JSON payloads, validates them, converts them into TOON, stores compact TOON alongside SQL-queryable extracted fields, and demonstrates measurable efficiency gains for LLM-oriented workflows.

## Problem
Teams already working with JSON need a low-friction way to adopt TOON benefits inside MariaDB without losing familiar SQL workflows.

## Core value proposition
- **Low-friction adoption path** from JSON to TOON
- **Dual storage**: compact TOON payload + query-friendly relational fields
- **Reliability-focused ingestion** with validation, logging, and error handling
- **Measurable benchmark evidence** for JSON vs TOON efficiency
- **Simple interactive demo** for evaluators

## Planned must-have scope
1. Reliable JSON ingestion pipeline
2. Dual-storage MariaDB schema
3. Core conversion and record APIs
4. Batch ingestion support
5. Benchmark protocol and results
6. Simple interactive demo
7. Clear documentation and setup guidance

## Project docs
- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [Technology Stack](docs/technology-stack.md)
- [Development Roadmap](docs/development-roadmap.md)
- [Resources](docs/resources.md)
- [Task Breakdown](tasks/task-breakdown.md)
- [Implementation Plan](implementation_plan.md)

## Tech stack
- MariaDB
- Python
- FastAPI
- MariaDB Connector/Python
- TOON Python tooling
- Streamlit

## Current focus
Project organisation, issue breakdown, architecture planning, and benchmark-driven delivery.
