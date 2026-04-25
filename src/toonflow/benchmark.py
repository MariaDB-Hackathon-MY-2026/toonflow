from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any

from .converter import json_to_toon


DEFAULT_COST_PER_MILLION_TOKENS_USD = 0.15

REFERENCE_BASELINE = {
    "label": "pre-polish two-payload sample corpus",
    "payload_count": 2,
    "json_bytes": 543,
    "toon_bytes": 492,
    "byte_savings_percent": 9.39,
    "token_savings_percent": 9.56,
}

SAMPLE_PROFILES = {
    "demo_invoice": {
        "domain": "billing",
        "role": "small-document control",
        "shape": "single compact invoice",
        "why_included": "keeps a low-gain, non-tabular baseline in the corpus",
    },
    "demo_support_ticket": {
        "domain": "customer support",
        "role": "text-heavy control",
        "shape": "ticket escalation with messages and reconciliation rows",
        "why_included": "shows savings are lower when conversational text dominates repeated keys",
    },
    "demo_audit_event_batch": {
        "domain": "security/audit",
        "role": "operational batch",
        "shape": "repeated audit event rows with nested batch metadata",
        "why_included": "models audit exports where repeated scalar event objects are natural",
    },
    "demo_order_fulfillment": {
        "domain": "commerce/logistics",
        "role": "operational batch",
        "shape": "order lines and fulfillment event rows",
        "why_included": "models order handoff data with repeated line-item structures",
    },
    "demo_patient_observation": {
        "domain": "healthcare telemetry",
        "role": "operational batch",
        "shape": "vital readings and medication event rows",
        "why_included": "models repeated clinical observations plus patient context",
    },
    "demo_cold_chain_shipment": {
        "domain": "cold-chain logistics",
        "role": "operational batch",
        "shape": "sensor readings and handoff rows",
        "why_included": "models shipment telemetry where tabular readings are expected",
    },
    "demo_inventory_replenishment": {
        "domain": "warehouse inventory",
        "role": "operational batch",
        "shape": "SKU positions, dock schedule rows, and forecast metadata",
        "why_included": "models inventory planning payloads with repeated SKU rows",
    },
    "demo_service_health_window": {
        "domain": "service reliability",
        "role": "operational batch",
        "shape": "route metrics, SLO metadata, and deploy events",
        "why_included": "models production health windows with repeated route metrics",
    },
    "demo_energy_meter_interval_batch": {
        "domain": "energy IoT",
        "role": "operational batch",
        "shape": "meter interval readings, exception rows, and summary data",
        "why_included": "models interval meter exports with repeated reading rows",
    },
    "demo_retail_store_shift": {
        "domain": "retail operations",
        "role": "operational batch",
        "shape": "transactions, inventory movement, cash reconciliation, and alerts",
        "why_included": "models POS shift close data with repeated reconciliation rows",
    },
    "demo_telecom_cell_kpi_window": {
        "domain": "telecom operations",
        "role": "operational batch",
        "shape": "cell KPI rows, alarm events, and operational actions",
        "why_included": "models RAN monitoring windows with repeated metric rows",
    },
}


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
    conversion_ms: float
    records_per_second: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def estimate_tokens(text: str) -> int:
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
    conversion_ms = max((perf_counter() - start) * 1000, 0.0001)

    json_payload = canonical_json(payload)
    json_bytes = len(json_payload.encode("utf-8"))
    toon_bytes = len(toon_payload.encode("utf-8"))
    json_tokens = estimate_tokens(json_payload)
    toon_tokens = estimate_tokens(toon_payload)
    json_cost = estimate_cost_usd(json_tokens)
    toon_cost = estimate_cost_usd(toon_tokens)

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
        conversion_ms=round(conversion_ms, 4),
        records_per_second=round(1000 / conversion_ms, 2),
    )


def benchmark_payloads(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results = [benchmark_payload(payload, name) for name, payload in payloads.items()]
    totals = {
        "payload_count": len(results),
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
    totals["token_savings_percent"] = percentage_savings(totals["json_token_estimate"], totals["toon_token_estimate"])
    totals["estimated_cost_savings_usd"] = round(
        totals["json_estimated_cost_usd"] - totals["toon_estimated_cost_usd"], 8
    )
    totals["records_per_second"] = round((len(results) * 1000) / totals["conversion_ms"], 2) if totals["conversion_ms"] else 0.0
    result_dicts = [item.to_dict() for item in results]
    return {
        "results": result_dicts,
        "totals": totals,
        "distribution": benchmark_distribution(result_dicts),
        "corpus_profile": benchmark_corpus_profile(result_dicts),
        "baseline_comparison": benchmark_baseline_comparison(totals, REFERENCE_BASELINE),
    }


def benchmark_baseline_comparison(
    totals: dict[str, Any], baseline: dict[str, int | float | str]
) -> dict[str, int | float | str]:
    return {
        "baseline_label": baseline["label"],
        "baseline_payload_count": baseline["payload_count"],
        "baseline_json_bytes": baseline["json_bytes"],
        "baseline_toon_bytes": baseline["toon_bytes"],
        "baseline_byte_savings_percent": baseline["byte_savings_percent"],
        "baseline_token_savings_percent": baseline["token_savings_percent"],
        "current_payload_count": totals.get("payload_count", 0),
        "current_json_bytes": totals["json_bytes"],
        "current_toon_bytes": totals["toon_bytes"],
        "current_byte_savings_percent": totals["byte_savings_percent"],
        "current_token_savings_percent": totals["token_savings_percent"],
        "byte_savings_lift_points": round(
            totals["byte_savings_percent"] - float(baseline["byte_savings_percent"]), 2
        ),
        "token_savings_lift_points": round(
            totals["token_savings_percent"] - float(baseline["token_savings_percent"]), 2
        ),
        "json_corpus_size_multiplier": round(totals["json_bytes"] / float(baseline["json_bytes"]), 2),
    }


def benchmark_corpus_profile(results: list[dict[str, Any]]) -> dict[str, Any]:
    profiles = []
    role_counts: dict[str, int] = {}
    domains: set[str] = set()
    for item in results:
        payload_name = item["payload_name"]
        profile = SAMPLE_PROFILES.get(
            payload_name,
            {
                "domain": "unprofiled",
                "role": "unprofiled",
                "shape": "custom benchmark payload",
                "why_included": "not part of the default documented corpus",
            },
        )
        role = profile["role"]
        domain = profile["domain"]
        role_counts[role] = role_counts.get(role, 0) + 1
        domains.add(domain)
        profiles.append({"payload_name": payload_name, **profile})

    return {
        "payload_count": len(results),
        "profiled_payload_count": sum(1 for item in profiles if item["role"] != "unprofiled"),
        "domains": sorted(domains),
        "role_counts": dict(sorted(role_counts.items())),
        "profiles": profiles,
    }


def benchmark_distribution(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "payload_count": 0,
            "byte_savings_percent_range": {"min": 0.0, "max": 0.0},
            "token_savings_percent_range": {"min": 0.0, "max": 0.0},
            "median_byte_savings_percent": 0.0,
            "mean_byte_savings_percent": 0.0,
            "median_token_savings_percent": 0.0,
            "mean_token_savings_percent": 0.0,
            "lowest_byte_savings_payload": None,
            "highest_byte_savings_payload": None,
        }

    lowest_byte = min(results, key=lambda item: item["byte_savings_percent"])
    highest_byte = max(results, key=lambda item: item["byte_savings_percent"])
    lowest_token = min(results, key=lambda item: item["token_savings_percent"])
    highest_token = max(results, key=lambda item: item["token_savings_percent"])
    byte_savings_values = [item["byte_savings_percent"] for item in results]
    token_savings_values = [item["token_savings_percent"] for item in results]
    return {
        "payload_count": len(results),
        "byte_savings_percent_range": {
            "min": lowest_byte["byte_savings_percent"],
            "max": highest_byte["byte_savings_percent"],
        },
        "token_savings_percent_range": {
            "min": lowest_token["token_savings_percent"],
            "max": highest_token["token_savings_percent"],
        },
        "median_byte_savings_percent": round(median(byte_savings_values), 2),
        "mean_byte_savings_percent": round(mean(byte_savings_values), 2),
        "median_token_savings_percent": round(median(token_savings_values), 2),
        "mean_token_savings_percent": round(mean(token_savings_values), 2),
        "lowest_byte_savings_payload": {
            "payload_name": lowest_byte["payload_name"],
            "byte_savings_percent": lowest_byte["byte_savings_percent"],
        },
        "highest_byte_savings_payload": {
            "payload_name": highest_byte["payload_name"],
            "byte_savings_percent": highest_byte["byte_savings_percent"],
        },
    }


def load_json_payloads(directory: str | Path) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for path in sorted(Path(directory).glob("*.json")):
        payloads[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def write_benchmark_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    totals = report["totals"]
    results = report["results"]
    distribution = report.get("distribution") or benchmark_distribution(results)
    corpus_profile = report.get("corpus_profile") or benchmark_corpus_profile(results)
    baseline = report.get("baseline_comparison")
    byte_range = distribution["byte_savings_percent_range"]
    lowest_byte = distribution["lowest_byte_savings_payload"]
    highest_byte = distribution["highest_byte_savings_payload"]
    lines = [
        "# JSON vs TOON Benchmark Results",
        "",
        "| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in results:
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
        ]
    )
    if baseline:
        lines.extend(
            [
                "## Baseline comparison",
                "",
                f"- Reference baseline: {baseline['baseline_label']} ({baseline['baseline_payload_count']} payloads)",
                f"- Baseline savings: {baseline['baseline_byte_savings_percent']}% bytes; {baseline['baseline_token_savings_percent']}% estimated tokens",
                f"- Current savings: {baseline['current_byte_savings_percent']}% bytes; {baseline['current_token_savings_percent']}% estimated tokens",
                f"- Lift vs baseline: +{baseline['byte_savings_lift_points']} percentage points bytes; +{baseline['token_savings_lift_points']} percentage points estimated tokens",
                f"- Corpus size: {baseline['current_json_bytes']} JSON bytes, {baseline['json_corpus_size_multiplier']}x the baseline JSON byte volume",
                "- The comparison uses the original measured two-payload benchmark as a reference point; it is not a claim that every payload shape will see the same lift.",
                "",
            ]
        )
    lines.extend(
        [
            "## Corpus profile",
            "",
            f"- Profiled payloads: {corpus_profile['profiled_payload_count']} of {corpus_profile['payload_count']}",
            f"- Domains covered: {', '.join(corpus_profile['domains'])}",
            f"- Role counts: {', '.join(f'{role}: {count}' for role, count in corpus_profile['role_counts'].items())}",
            "",
            "| Payload | Domain | Role | Shape | Why included |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for profile in corpus_profile["profiles"]:
        lines.append(
            f"| {profile['payload_name']} | {profile['domain']} | {profile['role']} | "
            f"{profile['shape']} | {profile['why_included']} |"
        )
    lines.extend(
        [
            "",
            "## Distribution checks",
            "",
            f"- Payload count: {distribution['payload_count']}",
            f"- Per-payload byte savings range: {byte_range['min']}% to {byte_range['max']}%",
            f"- Median per-payload byte savings: {distribution['median_byte_savings_percent']}%",
            f"- Unweighted average per-payload byte savings: {distribution['mean_byte_savings_percent']}%",
            f"- Median per-payload token savings: {distribution['median_token_savings_percent']}%",
            f"- Lowest-gain sample: {lowest_byte['payload_name']} ({lowest_byte['byte_savings_percent']}%)",
            f"- Highest-gain sample: {highest_byte['payload_name']} ({highest_byte['byte_savings_percent']}%)",
            "- Weighted totals use full corpus bytes and token estimates, not unweighted per-payload averages.",
            "",
            "## Interpretation",
            "",
            "Savings are strongest for realistic operational batches with repeated object rows, where TOON's tabular form avoids repeating JSON keys for every row.",
            "The small invoice and text-heavy support ticket remain in the corpus as lower-gain controls, so the totals are not based only on favorable telemetry-style payloads.",
            "Conversion timings are local runtime observations and can vary between runs; byte and token totals are stable for a fixed corpus.",
            "",
            "Token and cost values are estimates for repeatable local comparison.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
