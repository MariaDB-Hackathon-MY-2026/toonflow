from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def main() -> int:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory(prefix="toonflow-verify-") as tmpdir:
        tmp = Path(tmpdir)
        commands = [
            [PYTHON, "-m", "pytest", "tests", "-q"],
            [PYTHON, "scripts/run_core_pipeline.py", "--invalid-samples", "data/invalid_samples"],
            [
                PYTHON,
                "scripts/run_benchmark.py",
                "--output",
                str(tmp / "latest_results.json"),
                "--markdown-output",
                str(tmp / "latest_report.md"),
            ],
        ]
        for command in commands:
            print(f"$ {' '.join(command)}")
            subprocess.run(command, cwd=ROOT, env=env, check=True)
    print("All verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
