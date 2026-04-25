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
        "timestamp": "2026-04-24T10:00:00Z",
        "data": {"customer": {"name": "Alice"}, "amount": 245.5},
    }


def test_canonical_json_is_compact_and_stable():
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_estimate_tokens_costs_and_savings_are_repeatable():
    assert estimate_tokens("abcd") == 1
    assert estimate_cost_usd(1_000_000, 0.15) == 0.15
    assert percentage_savings(100, 75) == 25.0


def test_benchmark_payload_returns_expected_metric_shape():
    result = benchmark_payload(payload(), "invoice")
    assert result.payload_name == "invoice"
    assert result.json_bytes > 0
    assert result.toon_bytes > 0
    assert result.json_token_estimate > 0
    assert result.records_per_second > 0


def test_benchmark_payloads_returns_totals():
    report = benchmark_payloads({"invoice": payload()})
    assert len(report["results"]) == 1
    assert "estimated_cost_savings_usd" in report["totals"]
    assert "records_per_second" in report["totals"]


def test_default_sample_corpus_keeps_meaningful_savings():
    samples_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    report = benchmark_payloads(load_json_payloads(samples_dir))

    assert report["totals"]["byte_savings_percent"] >= 25.0
    assert report["totals"]["token_savings_percent"] >= 25.0


def test_load_and_write_benchmark_reports(tmp_path: Path):
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(canonical_json(payload()), encoding="utf-8")
    loaded = load_json_payloads(tmp_path)
    assert loaded["sample"]["entity"] == "invoice"

    report = benchmark_payloads(loaded)
    json_output = tmp_path / "report.json"
    md_output = tmp_path / "report.md"
    write_benchmark_report(report, json_output)
    write_markdown_report(report, md_output)
    assert "json_bytes" in json_output.read_text(encoding="utf-8")
    assert "JSON vs TOON Benchmark Results" in md_output.read_text(encoding="utf-8")
