from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from toonflow.db import connect_mariadb, load_mariadb_config
from toonflow.mariadb_repository import MariaDBRecordRepository
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
    parser = argparse.ArgumentParser(description="Run core ingestion pipeline against MariaDB.")
    parser.add_argument("--samples", default=str(ROOT / "data" / "samples"), help="Directory containing sample JSON files")
    parser.add_argument(
        "--invalid-samples",
        default=None,
        help="Optional directory of invalid JSON payloads to include for rejection/audit checks",
    )
    parser.add_argument("--skip-schema", action="store_true", help="Do not run CREATE TABLE IF NOT EXISTS first")
    args = parser.parse_args()

    payloads = load_payloads(Path(args.samples))
    if args.invalid_samples:
        payloads.extend(load_payloads(Path(args.invalid_samples)))
    if not payloads:
        raise SystemExit(f"No JSON payloads found in {args.samples}")

    config = load_mariadb_config()
    connection = connect_mariadb(config)
    repo = MariaDBRecordRepository(connection)
    if not args.skip_schema:
        repo.create_schema()

    result = batch_ingest_and_store_payloads(payloads, repo, source="mariadb-pipeline")
    print(f"Connected to MariaDB: {config.redacted()}")
    print(f"Processed {result['total']} payload(s)")
    print(f"Accepted: {result['accepted']}")
    print(f"Rejected: {result['rejected']}")
    print(f"Stored records: {result['stored']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
