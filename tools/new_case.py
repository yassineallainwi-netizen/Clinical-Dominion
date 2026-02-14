#!/usr/bin/env python3
"""Create a new Clinical Dominion case file from a safe authoring template."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "game" / "cases"
TEMPLATE_PATH = CASES_DIR / "_template_case.json"

BASELINE_OPTIONS = {
    "easy": {
        "MED3": ("high", "low"),
        "INTERN": ("high", "low"),
        "PGY1": ("medium", "medium"),
        "PGY4": ("medium", "high"),
        "SPECIALIST": ("low", "high"),
    },
    "standard": {
        "MED3": ("high", "low"),
        "INTERN": ("high", "medium"),
        "PGY1": ("medium", "medium"),
        "PGY4": ("low", "high"),
        "SPECIALIST": ("minimal", "high"),
    },
    "hard": {
        "MED3": ("medium", "medium"),
        "INTERN": ("medium", "medium"),
        "PGY1": ("low", "high"),
        "PGY4": ("minimal", "high"),
        "SPECIALIST": ("minimal", "high"),
    },
}


def prompt(text: str) -> str:
    value = input(text).strip()
    while not value:
        value = input(text).strip()
    return value


def load_template() -> dict:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template file not found: {TEMPLATE_PATH}")
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def update_difficulty(case_data: dict, baseline: str) -> None:
    for level, (clarity, penalty) in BASELINE_OPTIONS[baseline].items():
        case_data["difficultyEffects"][level]["clarity"] = clarity
        case_data["difficultyEffects"][level]["penalty"] = penalty


def sanitize_case_id(raw_id: str) -> str:
    case_id = raw_id.lower().strip()
    case_id = re.sub(r"[^a-z0-9_]+", "_", case_id)
    case_id = re.sub(r"_+", "_", case_id).strip("_")
    if not case_id:
        raise ValueError("Case id is empty after sanitization.")
    return case_id


def main() -> int:
    try:
        template = load_template()
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    raw_id = prompt("Case id (example: neph_007): ")
    specialty = prompt("Specialty (example: Nephrology): ")
    baseline = prompt("Difficulty baseline (easy/standard/hard): ").lower()

    if baseline not in BASELINE_OPTIONS:
        print("ERROR: baseline must be one of: easy, standard, hard")
        return 1

    try:
        case_id = sanitize_case_id(raw_id)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    output_path = CASES_DIR / f"{case_id}.json"
    if output_path.exists():
        print(f"ERROR: {output_path.name} already exists. Refusing to overwrite.")
        return 1

    case_data = template
    case_data["id"] = case_id
    case_data["specialty"] = specialty
    case_data["title"]["en"] = f"{specialty} Case: {case_id}"
    case_data["title"]["fr"] = f"Cas {specialty} : {case_id}"
    case_data["topics"] = [specialty.lower(), "stabilization"]
    case_data["correctDiagnosis"] = f"{case_id}_dx"

    for node in case_data.get("nodes", []):
        if "effects" in node.get("choices", [{}])[0]:
            pass
        for choice in node.get("choices", []):
            eff = choice.get("effects", {}).get("default", {})
            if eff.get("setDx") == "template_dx":
                eff["setDx"] = case_data["correctDiagnosis"]

    update_difficulty(case_data, baseline)

    output_path.write_text(json.dumps(case_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created: {output_path.relative_to(ROOT)}")
    print("Next: edit placeholders, then run `python tools/verify_project.py`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
