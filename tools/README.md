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
