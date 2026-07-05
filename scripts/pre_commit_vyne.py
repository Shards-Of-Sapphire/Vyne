#!/usr/bin/env python3
"""Pre-commit runner for Vyne: scans staged Python files and fails commit on critical findings.

This script is intentionally lightweight and calls the module CLI so it works in dev and CI.
"""
import sys
import subprocess
from pathlib import Path

files = [f for f in sys.argv[1:] if Path(f).suffix == '.py']
if not files:
    sys.exit(0)

failed = False
for f in files:
    print(f"[vyne] scanning {f} ...")
    res = subprocess.run([sys.executable, "-m", "vyne.cli", f])
    if res.returncode != 0:
        failed = True

if failed:
    print("\nVyne pre-commit: blocked commit due to findings. Run `vyne <file>` to inspect.`")
    sys.exit(1)

print("\nVyne pre-commit: no critical findings detected.")
sys.exit(0)
