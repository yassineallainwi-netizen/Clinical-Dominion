# Clinical Dominion Verification Harness

## Quick start (CI/local)

From repo root:

```bash
python tools/verify_project.py
```

This runs:
1. Deep JSON validation for all cases (`tools/verify_cases.py`)
2. Core TODO placeholder scan
3. Basic `.rpy` sanity checks

Exit code is non-zero on failure.

## Create a new case (template + generator safety)

### Option A — copy template manually
1. Copy `game/cases/_template_case.json` to a new filename (for example `game/cases/neph_007.json`).
2. Replace placeholders in all EN/FR fields.
3. Ensure each choice has `nextNodeId` and each terminal node has `terminalOutcome`.

### Option B — use generator (recommended)

```bash
python tools/new_case.py
```

The generator prompts for:
- case id
- specialty
- difficulty baseline (`easy`, `standard`, `hard`)

Safety behavior:
- auto-fills required top-level keys
- writes output under `game/cases/`
- refuses to overwrite existing files

## Validate authoring changes

```bash
python tools/verify_project.py
python tools/verify_and_fix.py
```

## Common authoring mistakes

- Missing bilingual content (`en`/`fr`) on node text or choices.
- Missing `nextNodeId` on a choice.
- `nextNodeId` pointing to a node that does not exist.
- Missing `terminalOutcome` for terminal nodes (all choices end with `END`).
- Wrong difficulty keys (must be exactly: `MED3`, `INTERN`, `PGY1`, `PGY4`, `SPECIALIST`).
- Non-test cases with fewer than 8 nodes or no boss node marker.

## Ren'Py runtime checks (SDK machine)

Run lint/compile/test via Ren'Py CLI:

### Linux/macOS
```bash
export RENPY_BIN=/path/to/renpy.sh
tools/run_renpy_checks.sh
```

### Windows
```bat
set RENPY_BIN=C:\path\to\renpy.exe
tools\run_renpy_checks.bat
```

These scripts run:
- `lint`
- `compile --compile`
- `test`

If the CLI is missing, they print setup instructions and exit with code 2.

## Release gate recommendation

A release candidate should pass both:
1. `python tools/verify_project.py`
2. `tools/run_renpy_checks.(sh|bat)` on a Ren'Py SDK environment

## Auto verify + fix loop

```bash
python tools/verify_and_fix.py
```

This script reruns project verification in a loop and applies safe automatic fixes for known schema/format issues between iterations.
