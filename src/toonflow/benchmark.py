from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from .converter import json_to_toon


DEFAULT_COST_PER_MILLION_TOKENS_USD = 0.15


@dataclass(slots=True)
class BenchmarkResult:
    payload_name: str
    json_bytes: int
    toon_bytes: int
    byte_savings: int
    byte_savings_percent: float
    json_token_estimate: int
    toon_token_estimate: int
    token_savings: int
    token_savings_percent: float
    json_estimated_cost_usd: float
    toon_estimated_cost_usd: float
    estimated_cost_savings_usd: float
    records_per_second: float
    conversion_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def estimate_tokens(text: str) -> int:
    """Approximate token count for repeatable local benchmarking.

    The hackathon demo should label this as an estimate. Exact tokenizer-based
    counts can be swapped in later without changing the benchmark output shape.
    """

    if not text:
        return 0
    return max(1, round(len(text) / 4))


def percentage_savings(original: int, compact: int) -> float:
    if original <= 0:
        return 0.0
    return round(((original - compact) / original) * 100, 2)


def estimate_cost_usd(tokens: int, cost_per_million_tokens: float = DEFAULT_COST_PER_MILLION_TOKENS_USD) -> float:
    return round((tokens / 1_000_000) * cost_per_million_tokens, 8)


def benchmark_payload(payload: dict[str, Any], payload_name: str = "payload") -> BenchmarkResult:
    start = perf_counter()
    toon_payload = json_to_toon(payload)
    conversion_ms = (perf_counter() - start) * 1000

    json_payload = canonical_json(payload)
    json_bytes = len(json_payload.encode("utf-8"))
    toon_bytes = len(toon_payload.encode("utf-8"))
    json_tokens = estimate_tokens(json_payload)
    toon_tokens = estimate_tokens(toon_payload)
    json_cost = estimate_cost_usd(json_tokens)
    toon_cost = estimate_cost_usd(toon_tokens)
    records_per_second = round(1000 / conversion_ms, 2) if conversion_ms > 0 else 0.0

    return BenchmarkResult(
        payload_name=payload_name,
        json_bytes=json_bytes,
        toon_bytes=toon_bytes,
        byte_savings=json_bytes - toon_bytes,
        byte_savings_percent=percentage_savings(json_bytes, toon_bytes),
        json_token_estimate=json_tokens,
        toon_token_estimate=toon_tokens,
        token_savings=json_tokens - toon_tokens,
        token_savings_percent=percentage_savings(json_tokens, toon_tokens),
        json_estimated_cost_usd=json_cost,
        toon_estimated_cost_usd=toon_cost,
        estimated_cost_savings_usd=round(json_cost - toon_cost, 8),
        records_per_second=records_per_second,
        conversion_ms=round(conversion_ms, 4),
    )


def benchmark_payloads(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results = [benchmark_payload(payload, name) for name, payload in payloads.items()]
    totals = {
        "json_bytes": sum(item.json_bytes for item in results),
        "toon_bytes": sum(item.toon_bytes for item in results),
        "json_token_estimate": sum(item.json_token_estimate for item in results),
        "toon_token_estimate": sum(item.toon_token_estimate for item in results),
        "json_estimated_cost_usd": round(sum(item.json_estimated_cost_usd for item in results), 8),
        "toon_estimated_cost_usd": round(sum(item.toon_estimated_cost_usd for item in results), 8),
        "conversion_ms": round(sum(item.conversion_ms for item in results), 4),
    }
    totals["byte_savings"] = totals["json_bytes"] - totals["toon_bytes"]
    totals["byte_savings_percent"] = percentage_savings(totals["json_bytes"], totals["toon_bytes"])
    totals["token_savings"] = totals["json_token_estimate"] - totals["toon_token_estimate"]
    totals["token_savings_percent"] = percentage_savings(
        totals["json_token_estimate"], totals["toon_token_estimate"]
    )
    totals["estimated_cost_savings_usd"] = round(
        totals["json_estimated_cost_usd"] - totals["toon_estimated_cost_usd"], 8
    )
    totals["records_per_second"] = round((len(results) * 1000) / totals["conversion_ms"], 2) if totals["conversion_ms"] else 0.0
    return {
        "results": [item.to_dict() for item in results],
        "totals": totals,
    }


def load_json_payloads(directory: str | Path) -> dict[str, dict[str, Any]]:
    base = Path(directory)
    payloads: dict[str, dict[str, Any]] = {}
    for path in sorted(base.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            payloads[path.stem] = json.load(handle)
    return payloads


def write_benchmark_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    totals = report["totals"]
    lines = [
        "# JSON vs TOON Benchmark Results",
        "",
        "| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in report["results"]:
        lines.append(
            f"| {item['payload_name']} | {item['json_bytes']} | {item['toon_bytes']} | "
            f"{item['byte_savings_percent']}% | {item['token_savings_percent']}% | {item['conversion_ms']} |"
        )
    lines.extend(
        [
            "",
            "## Totals",
            "",
            f"- JSON bytes: {totals['json_bytes']}",
            f"- TOON bytes: {totals['toon_bytes']}",
            f"- Byte savings: {totals['byte_savings_percent']}%",
            f"- Estimated token savings: {totals['token_savings_percent']}%",
            f"- Estimated cost savings: ${totals['estimated_cost_savings_usd']}",
            f"- Conversion throughput: {totals['records_per_second']} records/sec",
            "",
            "Token and cost values are estimates for repeatable local comparison.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
