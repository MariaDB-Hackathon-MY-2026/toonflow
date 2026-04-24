from pathlib import Path

from toonflow.benchmark import (
    benchmark_payload,
    benchmark_payloads,
    canonical_json,
    estimate_cost_usd,
    estimate_tokens,
    load_json_payloads,
    percentage_savings,
    write_benchmark_report,
    write_markdown_report,
)


def payload():
    return {
        "id": "bench-001",
        "entity": "invoice",
        "timestamp": "2026-04-23T12:00:00Z",
        "data": {"customer": {"name": "Alice"}, "amount": 245.5},
    }


def test_canonical_json_is_compact_and_stable():
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_estimate_tokens_and_savings_are_repeatable():
    assert estimate_tokens("abcd") == 1
    assert estimate_cost_usd(1_000_000, cost_per_million_tokens=0.15) == 0.15
    assert percentage_savings(100, 75) == 25.0


def test_benchmark_payload_returns_expected_metric_shape():
    result = benchmark_payload(payload(), "invoice")
    assert result.payload_name == "invoice"
    assert result.json_bytes > 0
    assert result.toon_bytes > 0
    assert result.json_token_estimate > 0
    assert result.json_estimated_cost_usd >= result.toon_estimated_cost_usd
    assert result.records_per_second >= 0
    assert result.conversion_ms >= 0


def test_benchmark_payloads_returns_totals():
    report = benchmark_payloads({"invoice": payload()})
    assert len(report["results"]) == 1
    assert report["totals"]["json_bytes"] >= report["results"][0]["json_bytes"]
    assert "estimated_cost_savings_usd" in report["totals"]
    assert "records_per_second" in report["totals"]


def test_load_and_write_benchmark_report(tmp_path: Path):
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(canonical_json(payload()), encoding="utf-8")
    loaded = load_json_payloads(tmp_path)
    assert loaded["sample"]["entity"] == "invoice"

    output = tmp_path / "report.json"
    write_benchmark_report(benchmark_payloads(loaded), output)
    assert output.exists()
    assert "json_bytes" in output.read_text(encoding="utf-8")

    markdown = tmp_path / "report.md"
    write_markdown_report(benchmark_payloads(loaded), markdown)
    assert "JSON vs TOON Benchmark Results" in markdown.read_text(encoding="utf-8")
