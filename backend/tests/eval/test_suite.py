"""Include the oracle-free EVL-01 regressions in make check, in a separate process."""

import subprocess
import sys
from pathlib import Path


def test_evaluation_harness_and_product_isolation():
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "eval/tests", "-v"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
