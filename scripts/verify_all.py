from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


COMMANDS = [
    [PYTHON, "-m", "pytest", "tests", "-q"],
    [PYTHON, "scripts/run_core_pipeline.py", "--invalid-samples", "data/invalid_samples"],
    [PYTHON, "scripts/run_benchmark.py"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"$ {' '.join(command)}")
        subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, check=True)
    print("All verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
