#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, desc):
    print(f"\n==> {desc}")
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout.rstrip())
    if p.stderr:
        print(p.stderr.rstrip())
    return p.returncode


def check_rpy_sanity():
    errors = []
    for path in sorted((ROOT / "game").rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        if "\t" in text:
            errors.append(f"{path.relative_to(ROOT)}: contains tab indentation")
        if text.count('"') % 2 != 0:
            errors.append(f"{path.relative_to(ROOT)}: odd number of double quotes (possible syntax typo)")
    if errors:
        print("RPY SANITY FAILED")
        for e in errors:
            print(f" - {e}")
        return 1
    print("RPY SANITY PASSED")
    return 0


def main():
    fail = 0
    fail |= run([sys.executable, "tools/verify_cases.py"], "Deep case validation")
    todo_rc = run(["rg", "-n", "TODO|todo", "game"], "No TODO scan")
    if todo_rc == 0:
        print("TODO placeholders found")
        fail |= 1
    elif todo_rc == 1:
        print("No TODO placeholders found")
    else:
        fail |= 1
    fail |= check_rpy_sanity()

    if fail:
        print("\nPROJECT VERIFICATION FAILED")
        return 1

    print("\nPROJECT VERIFICATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
