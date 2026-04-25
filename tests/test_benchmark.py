from pathlib import Path

from toonflow.benchmark import (
    REFERENCE_BASELINE,
    benchmark_baseline_comparison,
    benchmark_distribution,
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
    assert report["totals"]["payload_count"] == 1
    assert report["distribution"]["payload_count"] == 1
    assert report["distribution"]["lowest_byte_savings_payload"]["payload_name"] == "invoice"
    assert report["baseline_comparison"]["baseline_label"] == REFERENCE_BASELINE["label"]


def test_benchmark_baseline_comparison_shows_lift_from_reference_baseline():
    comparison = benchmark_baseline_comparison(
        {
            "payload_count": 11,
            "json_bytes": 21_526,
            "toon_bytes": 12_558,
            "byte_savings_percent": 41.66,
            "token_savings_percent": 41.67,
        },
        REFERENCE_BASELINE,
    )

    assert comparison["baseline_payload_count"] == 2
    assert comparison["current_payload_count"] == 11
    assert comparison["byte_savings_lift_points"] == 32.27
    assert comparison["token_savings_lift_points"] == 32.11
    assert comparison["json_corpus_size_multiplier"] == 39.64


def test_benchmark_distribution_handles_payload_variance():
    distribution = benchmark_distribution(
        [
            {"payload_name": "low", "byte_savings_percent": 10.0, "token_savings_percent": 12.0},
            {"payload_name": "mid", "byte_savings_percent": 30.0, "token_savings_percent": 32.0},
            {"payload_name": "high", "byte_savings_percent": 50.0, "token_savings_percent": 52.0},
        ]
    )

    assert distribution["payload_count"] == 3
    assert distribution["byte_savings_percent_range"] == {"min": 10.0, "max": 50.0}
    assert distribution["median_byte_savings_percent"] == 30.0
    assert distribution["mean_token_savings_percent"] == 32.0
    assert distribution["lowest_byte_savings_payload"]["payload_name"] == "low"
    assert distribution["highest_byte_savings_payload"]["payload_name"] == "high"


def test_default_sample_corpus_keeps_meaningful_savings():
    samples_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    report = benchmark_payloads(load_json_payloads(samples_dir))

    assert report["totals"]["byte_savings_percent"] >= 40.0
    assert report["totals"]["token_savings_percent"] >= 40.0


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
    assert "distribution" in json_output.read_text(encoding="utf-8")
    markdown = md_output.read_text(encoding="utf-8")
    assert "JSON vs TOON Benchmark Results" in markdown
    assert "Distribution checks" in markdown
    assert "Baseline comparison" in markdown
    assert "Lift vs baseline" in markdown
    assert "Weighted totals use full corpus bytes" in markdown
    assert "lower-gain controls" in markdown
