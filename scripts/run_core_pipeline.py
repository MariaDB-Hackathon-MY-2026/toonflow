from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from toonflow.repository import InMemoryRecordStore
from toonflow.service import batch_ingest_and_store_payloads


def load_payloads(samples_dir: Path) -> list[dict]:
    payloads = []
    for path in sorted(samples_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "id" not in payload:
            payload["id"] = path.stem
        payloads.append(payload)
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the core validate -> convert -> dual-store pipeline.")
    parser.add_argument("--samples", default=str(ROOT / "data" / "samples"), help="Directory containing sample JSON files")
    parser.add_argument(
        "--invalid-samples",
        default=None,
        help="Optional directory of invalid JSON payloads to include for rejection/audit checks",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "processed" / "core_pipeline_results.json"),
        help="Output file for the pipeline summary",
    )
    args = parser.parse_args()

    samples_dir = Path(args.samples)
    payloads = load_payloads(samples_dir)
    if args.invalid_samples:
        payloads.extend(load_payloads(Path(args.invalid_samples)))
    if not payloads:
        raise SystemExit(f"No JSON payloads found in {samples_dir}")

    store = InMemoryRecordStore()
    result = batch_ingest_and_store_payloads(payloads, store, source="core-pipeline")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Processed {result['total']} payload(s)")
    print(f"Accepted: {result['accepted']}")
    print(f"Rejected: {result['rejected']}")
    print(f"Stored records: {result['stored']}")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
