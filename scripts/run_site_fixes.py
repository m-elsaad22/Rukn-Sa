#!/usr/bin/env python3
"""Run live /sa trust, hub, taxonomy, image, and money-page fixes in order."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

STEPS = [
    "live_snippets.py",
    "fix_cities_taxonomy.py",
    "rewrite_service_hubs.py",
    "fix_core_pages.py",
    "expand_money_pages.py",
    "assign_featured_images.py",
]


def run_step(name: str) -> int:
    print(f"\n===== {name} =====", flush=True)
    proc = subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=str(ROOT))
    return proc.returncode


def main() -> None:
    only = sys.argv[1:] 
    names = only or STEPS
    failed = []
    for name in names:
        code = run_step(name)
        if code != 0:
            failed.append((name, code))
            print(f"FAILED {name} exit {code}", flush=True)
    if failed:
        print("FAILED STEPS", failed)
        sys.exit(1)
    print("ALL STEPS DONE")


if __name__ == "__main__":
    main()
