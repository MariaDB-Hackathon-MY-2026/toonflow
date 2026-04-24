# JSON vs TOON benchmark protocol

The benchmark compares the same source payload in two transport formats:

1. canonical compact JSON
2. TOONFlow's compact TOON-style field-path output

Metrics captured:
- UTF-8 payload bytes
- estimated token count using a repeatable local `len(text) / 4` heuristic
- byte and token savings percentage
- conversion time in milliseconds

The token metric is intentionally labelled as an estimate. A model-specific
tokenizer can be swapped in later while keeping the same result schema.

Run locally:

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```
