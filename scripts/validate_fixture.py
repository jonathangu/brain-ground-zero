#!/usr/bin/env python3
"""Validate a recorded-session fixture against the JSON schema.

Usage:
    python scripts/validate_fixture.py recorded_sessions/fixtures/example_minimal.json
    python scripts/validate_fixture.py --all   # validates every .json in recorded_sessions/fixtures/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "recorded_sessions" / "schema" / "session_fixture.schema.json"
FIXTURES_DIR = REPO_ROOT / "recorded_sessions" / "fixtures"

# ---------------------------------------------------------------------------
# Minimal validator that works without jsonschema installed.
# If the `jsonschema` package is available it uses full Draft 2020-12
# validation; otherwise it falls back to structural checks.
# ---------------------------------------------------------------------------

try:
    import jsonschema  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _validate_with_jsonschema(fixture: dict, schema: dict, path: str) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(fixture), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"  {path}: {loc}: {err.message}")
    return errors


def _validate_structural(fixture: dict, path: str) -> list[str]:
    """Fallback validation when jsonschema is not installed."""
    errors: list[str] = []
    required_top = ["fixture_id", "source", "session_context", "turns", "ground_truth", "held_fixed"]
    for key in required_top:
        if key not in fixture:
            errors.append(f"  {path}: missing required top-level field '{key}'")

    if not isinstance(fixture.get("turns"), list) or len(fixture.get("turns", [])) == 0:
        errors.append(f"  {path}: 'turns' must be a non-empty array")
    else:
        for i, turn in enumerate(fixture["turns"]):
            for field in ["turn_id", "user_input", "available_documents", "expected_output", "rubric"]:
                if field not in turn:
                    errors.append(f"  {path}: turns[{i}]: missing required field '{field}'")

    hf = fixture.get("held_fixed", {})
    for field in ["prompt_template_hash", "context_budget_tokens", "correction_budget"]:
        if field not in hf:
            errors.append(f"  {path}: held_fixed: missing required field '{field}'")

    return errors


def validate_fixture(fixture_path: Path, schema: dict) -> list[str]:
    fixture = _load_json(fixture_path)
    label = str(fixture_path.relative_to(REPO_ROOT))
    if HAS_JSONSCHEMA:
        return _validate_with_jsonschema(fixture, schema, label)
    return _validate_structural(fixture, label)


def print_summary(fixture_path: Path, fixture: dict) -> None:
    label = fixture_path.relative_to(REPO_ROOT)
    turns = fixture.get("turns", [])
    gt = fixture.get("ground_truth", {})
    hf = fixture.get("held_fixed", {})
    print(f"\n--- {label} ---")
    print(f"  fixture_id:       {fixture.get('fixture_id', '?')}")
    print(f"  source version:   {fixture.get('source', {}).get('product_version', '?')}")
    print(f"  capture date:     {fixture.get('source', {}).get('capture_date', '?')}")
    print(f"  matter type:      {fixture.get('session_context', {}).get('matter_type', '?')}")
    print(f"  turns:            {len(turns)}")
    print(f"  complexity:       {gt.get('complexity_tier', '?')}")
    print(f"  context budget:   {hf.get('context_budget_tokens', '?')} tokens")
    print(f"  correction budget:{hf.get('correction_budget', '?')}")

    has_graph = any(t.get("graph_snapshot") is not None for t in turns)
    total_docs = sum(len(t.get("available_documents", [])) for t in turns)
    print(f"  total docs:       {total_docs} across all turns")
    print(f"  graph snapshots:  {'yes' if has_graph else 'none'}")

    # Checklist
    print("\n  Checklist:")
    print(f"    [{'x' if fixture.get('fixture_id') else ' '}] fixture_id present")
    print(f"    [{'x' if len(turns) > 0 else ' '}] at least one turn")
    print(f"    [{'x' if hf.get('prompt_template_hash') else ' '}] prompt_template_hash set")
    print(f"    [{'x' if hf.get('context_budget_tokens') else ' '}] context_budget_tokens set")
    print(f"    [{'x' if hf.get('correction_budget') is not None else ' '}] correction_budget set")
    all_rubrics = all("rubric" in t for t in turns)
    print(f"    [{'x' if all_rubrics else ' '}] all turns have rubric")
    all_expected = all(t.get("expected_output") for t in turns)
    print(f"    [{'x' if all_expected else ' '}] all turns have expected_output")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate recorded-session fixtures.")
    parser.add_argument("fixtures", nargs="*", help="Fixture JSON files to validate.")
    parser.add_argument("--all", action="store_true", help="Validate all fixtures in recorded_sessions/fixtures/.")
    args = parser.parse_args()

    paths: list[Path] = []
    if args.all:
        paths = sorted(FIXTURES_DIR.glob("*.json"))
    else:
        paths = [Path(p) for p in args.fixtures]

    if not paths:
        print("No fixture files specified. Use --all or pass file paths.", file=sys.stderr)
        return 1

    schema = _load_json(SCHEMA_PATH)
    all_errors: list[str] = []

    for p in paths:
        errors = validate_fixture(p, schema)
        all_errors.extend(errors)
        fixture = _load_json(p)
        print_summary(p, fixture)

    if all_errors:
        print(f"\nValidation FAILED ({len(all_errors)} error(s)):")
        for e in all_errors:
            print(e)
        return 1

    validator_note = "(jsonschema)" if HAS_JSONSCHEMA else "(structural fallback)"
    print(f"\nAll {len(paths)} fixture(s) valid {validator_note}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
