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
- generated distribution checks, including per-payload range, median, unweighted average, and lowest/highest-gain samples

Token and cost values are estimates for repeatable local comparison, not pricing claims. Conversion timing and throughput are local runtime observations, so reviewers should treat byte/token totals as the stable benchmark signal for a fixed corpus.

## Sample corpus

The default local corpus keeps one small invoice demo as a low-gain control and adds ten richer, realistic payloads: support ticket escalation, audit events, order fulfillment, patient observation telemetry, cold-chain logistics, inventory replenishment, service health telemetry, energy meter interval readings, retail store shift reconciliation, and telecom cell KPI monitoring. These samples intentionally cover repeated scalar object arrays and nested metadata because that is where TOON's table form can remove repeated JSON key names without changing the underlying data shape, while still retaining less favorable small-document and conversational/text-heavy controls.

The JSON results include both weighted totals and a machine-readable distribution summary. The Markdown report renders the same distribution checks plus a short interpretation section so reviewers can see why savings vary by payload shape instead of treating the weighted total as a universal compression claim.

Run locally:

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```
