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

## Reliability focus
The system should visibly support:
- validation
- error logging
- ingestion status tracking
- batch processing
