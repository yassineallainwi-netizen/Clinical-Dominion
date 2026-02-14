#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "game" / "cases"
DIFFS = {"MED3", "INTERN", "PGY1", "PGY4", "SPECIALIST"}
TERMINAL_OUTCOMES = {"success", "partial", "poor", "neutral"}


def err(errors, path, msg):
    errors.append(f"{path}: {msg}")


def validate_case(path: Path):
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path.name}: invalid json: {exc}"]

    required = ["id", "title", "specialty", "difficultyEffects", "topics", "startNode", "nodes", "debrief", "correctDiagnosis"]
    for key in required:
        if key not in data:
            err(errors, path.name, f"missing top-level key '{key}'")

    for localized_key in ["title"]:
        val = data.get(localized_key, {})
        if not isinstance(val, dict) or "en" not in val or "fr" not in val:
            err(errors, path.name, f"{localized_key} must include en/fr")

    debrief = data.get("debrief", {})
    for k in ["wentWell", "misses", "idealPlan"]:
        if not isinstance(debrief.get(k), dict) or "en" not in debrief.get(k, {}) or "fr" not in debrief.get(k, {}):
            err(errors, path.name, f"debrief.{k} must include en/fr")

    diff = set((data.get("difficultyEffects") or {}).keys())
    if diff != DIFFS:
        err(errors, path.name, f"difficultyEffects must contain exactly {sorted(DIFFS)}")

    nodes = data.get("nodes") or []
    if not (8 <= len(nodes) <= 12):
        err(errors, path.name, f"expected 8-12 nodes, found {len(nodes)}")

    node_ids = set()
    boss_count = 0
    terminal_nodes = 0
    for i, n in enumerate(nodes):
        nid = n.get("id")
        if not nid:
            err(errors, path.name, f"node[{i}] missing id")
            continue
        if nid in node_ids:
            err(errors, path.name, f"duplicate node id '{nid}'")
        node_ids.add(nid)

        for field in ["background", "speaker", "text", "choices"]:
            if field not in n:
                err(errors, path.name, f"node[{nid}] missing {field}")

        text = n.get("text", {})
        if not isinstance(text, dict) or "en" not in text or "fr" not in text:
            err(errors, path.name, f"node[{nid}].text must include en/fr")
        if "BOSS NODE" in str(text.get("en", "")) or "NOEUD BOSS" in str(text.get("fr", "")):
            boss_count += 1

        choices = n.get("choices", [])
        if not isinstance(choices, list) or not choices:
            err(errors, path.name, f"node[{nid}] has no choices")
            continue

        only_end = True
        for j, c in enumerate(choices):
            ctext = c.get("text", {})
            if not isinstance(ctext, dict) or "en" not in ctext or "fr" not in ctext:
                err(errors, path.name, f"node[{nid}].choice[{j}] text must include en/fr")
            nxt = c.get("nextNodeId", c.get("next"))
            if not nxt:
                err(errors, path.name, f"node[{nid}].choice[{j}] missing nextNodeId/next")
                continue
            if nxt != "END":
                only_end = False

        if only_end:
            terminal_nodes += 1
            out = n.get("terminalOutcome")
            if out not in TERMINAL_OUTCOMES:
                err(errors, path.name, f"node[{nid}] terminalOutcome must be one of {sorted(TERMINAL_OUTCOMES)}")

    start = data.get("startNode")
    if start and start not in node_ids:
        err(errors, path.name, f"startNode '{start}' not found in nodes")

    # graph checks
    for n in nodes:
        nid = n.get("id")
        for c in n.get("choices", []):
            nxt = c.get("nextNodeId", c.get("next"))
            if nxt and nxt != "END" and nxt not in node_ids:
                err(errors, path.name, f"node[{nid}] points to unknown next node '{nxt}'")

    non_terminal_dead_ends = []
    for n in nodes:
        nid = n.get("id")
        choice_targets = [c.get("nextNodeId", c.get("next")) for c in n.get("choices", [])]
        if choice_targets and all(t == "END" for t in choice_targets):
            # terminal node, already checked above
            continue
        if not choice_targets:
            non_terminal_dead_ends.append(nid)

    if non_terminal_dead_ends:
        err(errors, path.name, f"non-terminal dead-end nodes: {non_terminal_dead_ends}")

    if boss_count < 1:
        err(errors, path.name, "at least 1 boss node required")
    if terminal_nodes < 1:
        err(errors, path.name, "at least 1 terminal node required")

    return errors


def main():
    if not CASES_DIR.exists():
        print(f"ERROR: missing cases directory: {CASES_DIR}")
        return 2

    files = sorted(CASES_DIR.glob("*.json"))
    if len(files) != 10:
        print(f"ERROR: expected 10 seed cases, found {len(files)}")

    all_errors = []
    for f in files:
        all_errors.extend(validate_case(f))

    if all_errors:
        print("CASE VALIDATION FAILED")
        for e in all_errors:
            print(f" - {e}")
        return 1

    print(f"CASE VALIDATION PASSED ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
