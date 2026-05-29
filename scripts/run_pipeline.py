"""Backward-compatible wrapper for the recurring discovery pipeline."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    command = [sys.executable, "scripts/run_discovery_pipeline.py", *sys.argv[1:]]
    print("$ " + " ".join(command), flush=True)
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
