import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_core_pipeline_script_can_include_invalid_samples(tmp_path: Path):
    output = tmp_path / "pipeline.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_core_pipeline.py"),
        "--samples",
        str(ROOT / "data" / "samples"),
        "--invalid-samples",
        str(ROOT / "data" / "invalid_samples"),
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, check=True, capture_output=True, text=True)
    assert "Rejected: 2" in completed.stdout
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["accepted"] == 2
    assert report["rejected"] == 2
    rejected = [record for record in report["records"] if record["status"] == "rejected"]
    assert len(rejected) == 2
    assert all(record["validation_errors"] for record in rejected)
