#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "game" / "cases"
MAX_ITERS = 5


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return p.returncode, p.stdout + p.stderr


def autofix_cases_schema():
    changed = 0
    for fp in sorted(CASES.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        dirty = False
        for node in data.get("nodes", []):
            choices = node.get("choices", [])
            for c in choices:
                if "nextNodeId" not in c and "next" in c:
                    c["nextNodeId"] = c["next"]
                    dirty = True
            targets = [c.get("nextNodeId", c.get("next")) for c in choices]
            if targets and all(t == "END" for t in targets) and "terminalOutcome" not in node:
                node["terminalOutcome"] = "neutral"
                dirty = True
        if dirty:
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed += 1
    return changed


def autofix_rpy_tabs():
    changed = 0
    for fp in (ROOT / "game").rglob("*.rpy"):
        text = fp.read_text(encoding="utf-8")
        if "\t" in text:
            fp.write_text(text.replace("\t", "    "), encoding="utf-8")
            changed += 1
    return changed


def main():
    renpy_available = subprocess.run(["bash", "-lc", "command -v renpy >/dev/null 2>&1"], cwd=ROOT).returncode == 0

    for i in range(1, MAX_ITERS + 1):
        print(f"\n=== Verify/Fix iteration {i} ===")
        rc, out = run([sys.executable, "tools/verify_project.py"])
        print(out.strip())

        renpy_rc = 0
        if renpy_available:
            renpy_rc, renpy_out = run(["bash", "tools/run_renpy_checks.sh"])
            print(renpy_out.strip())

        if rc == 0 and renpy_rc == 0:
            print("ALL CHECKS PASSED")
            return 0

        changed = 0
        changed += autofix_cases_schema()
        changed += autofix_rpy_tabs()
        print(f"Auto-fixes applied: {changed} file(s)")

        if changed == 0:
            print("No further automatic fixes available.")
            break

    return 1


if __name__ == "__main__":
    sys.exit(main())
