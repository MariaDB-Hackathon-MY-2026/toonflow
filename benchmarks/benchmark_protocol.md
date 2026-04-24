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

Run locally:

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```
