# JSON vs TOON benchmark protocol

The benchmark compares each source payload in two transport formats:

1. canonical compact JSON
2. TOONFlow compact TOON-style output

Metrics captured:
- UTF-8 payload bytes
- estimated token count using a repeatable local `len(text) / 4` heuristic
- byte and token savings percentage
- estimated API cost using a configurable cost-per-million-token assumption
- conversion time in milliseconds
- derived conversion throughput in records per second

Token and cost values are estimates for repeatable local comparison, not pricing claims.

## Sample corpus

The default local corpus keeps one small invoice demo as a low-gain control and adds seven richer, realistic payloads: support ticket escalation, audit events, order fulfillment, patient observation telemetry, cold-chain logistics, inventory replenishment, and service health telemetry. These samples intentionally cover repeated scalar object arrays and nested metadata because that is where TOON's table form can remove repeated JSON key names without changing the underlying data shape, while still retaining less favorable conversational/text-heavy support data.

Run locally:

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```
