from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from toonflow.benchmark import benchmark_payloads, load_json_payloads, write_benchmark_report, write_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run JSON vs TOON benchmark over sample payloads.")
    parser.add_argument("--samples", default=str(ROOT / "data" / "samples"), help="Directory of JSON samples")
    parser.add_argument("--output", default=str(ROOT / "benchmarks" / "latest_results.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "benchmarks" / "latest_report.md"))
    args = parser.parse_args()

    payloads = load_json_payloads(args.samples)
    if not payloads:
        raise SystemExit(f"No JSON sample payloads found in {args.samples}")

    report = benchmark_payloads(payloads)
    write_benchmark_report(report, args.output)
    write_markdown_report(report, args.markdown_output)
    totals = report["totals"]
    print(f"Benchmarked {len(payloads)} payload(s)")
    print(f"JSON bytes: {totals['json_bytes']}")
    print(f"TOON bytes: {totals['toon_bytes']}")
    print(f"Byte savings: {totals['byte_savings_percent']}%")
    print(f"Estimated token savings: {totals['token_savings_percent']}%")
    print(f"Estimated cost savings: ${totals['estimated_cost_savings_usd']}")
    print(f"Conversion throughput: {totals['records_per_second']} records/sec")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
