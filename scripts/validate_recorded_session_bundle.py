#!/usr/bin/env python3
"""Validate proof-results/recorded_sessions/* bundle layout and consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REQUIRED_MODES = ["no_brain", "vector_only", "graph_prior_only", "learned_route"]
OPTIONAL_MODES = ["full_brain", "online"]
TURN_SCORE_FIELDS = [
    "turn_id",
    "success",
    "rubric_score",
    "corrections_needed",
    "prompt_context_size",
    "latency_proxy",
    "cost_proxy",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _validate_mode_scores(
    bundle_name: str,
    mode_name: str,
    mode_payload: dict[str, Any],
    expected_turns: int,
    strict: bool,
) -> list[str]:
    errors: list[str] = []
    turns = mode_payload.get("turns", [])

    if not isinstance(turns, list):
        errors.append(f"{bundle_name}: scores.{mode_name}.turns must be an array")
        return errors

    if strict and len(turns) != expected_turns:
        errors.append(
            f"{bundle_name}: mode {mode_name} has {len(turns)} turn rows, expected {expected_turns}"
        )

    for idx, row in enumerate(turns):
        if not isinstance(row, dict):
            errors.append(f"{bundle_name}: scores.{mode_name}.turns[{idx}] must be object")
            continue
        missing = [f for f in TURN_SCORE_FIELDS if f not in row]
        if missing:
            errors.append(
                f"{bundle_name}: scores.{mode_name}.turns[{idx}] missing fields: {', '.join(missing)}"
            )

    aggregates = mode_payload.get("aggregates")
    if strict and not isinstance(aggregates, dict):
        errors.append(f"{bundle_name}: scores.{mode_name}.aggregates must be object")

    return errors


def validate_bundle(bundle_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    name = bundle_dir.name

    fixture_path = bundle_dir / "fixture.json"
    metadata_path = bundle_dir / "metadata.yaml"
    score_card_path = bundle_dir / "score_card.json"
    score_card_md = bundle_dir / "score_card.md"
    readme_path = bundle_dir / "README.md"
    fixture_hash_path = bundle_dir / "verification" / "fixture_hash.sha256"

    for path in [fixture_path, metadata_path, score_card_path, score_card_md, readme_path, fixture_hash_path]:
        if not path.exists():
            errors.append(f"{name}: missing {path.relative_to(bundle_dir)}")

    if errors:
        return errors, warnings

    fixture = _load_json(fixture_path)
    metadata = _load_metadata(metadata_path)
    score_card = _load_json(score_card_path)

    fixture_id = fixture.get("fixture_id")
    if metadata.get("fixture_id") != fixture_id:
        errors.append(f"{name}: metadata.fixture_id does not match fixture.json fixture_id")
    if score_card.get("fixture_id") != fixture_id:
        errors.append(f"{name}: score_card.fixture_id does not match fixture.json fixture_id")

    recorded_hash = fixture_hash_path.read_text(encoding="utf-8").strip().split()[0]
    actual_hash = _sha256(fixture_path)
    if recorded_hash != actual_hash:
        errors.append(f"{name}: verification/fixture_hash.sha256 does not match fixture.json")

    status = metadata.get("status", "unknown")
    if status not in {"scaffold", "draft", "publishable"}:
        errors.append(f"{name}: metadata.status must be scaffold/draft/publishable")

    required_modes = score_card.get("required_modes", [])
    if required_modes != REQUIRED_MODES:
        warnings.append(f"{name}: score_card.required_modes differs from canonical required modes")

    scores = score_card.get("scores", {})
    if not isinstance(scores, dict):
        errors.append(f"{name}: score_card.scores must be an object")
        return errors, warnings

    expected_turns = len(fixture.get("turns", [])) if isinstance(fixture.get("turns"), list) else 0
    strict = status in {"draft", "publishable"}

    for mode in REQUIRED_MODES:
        payload = scores.get(mode)
        if payload is None:
            errors.append(f"{name}: missing required mode in score_card.scores: {mode}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{name}: score_card.scores.{mode} must be object")
            continue
        errors.extend(_validate_mode_scores(name, mode, payload, expected_turns, strict))

    for mode in OPTIONAL_MODES:
        payload = scores.get(mode)
        if payload is not None and isinstance(payload, dict):
            errors.extend(_validate_mode_scores(name, mode, payload, expected_turns, strict=False))

    if strict:
        missing_aggregates = []
        for mode in REQUIRED_MODES:
            payload = scores.get(mode, {})
            if isinstance(payload, dict) and not payload.get("aggregates"):
                missing_aggregates.append(mode)
        if missing_aggregates:
            errors.append(
                f"{name}: required mode aggregates missing for {', '.join(missing_aggregates)}"
            )

    return errors, warnings


def _discover_bundles(root: Path) -> list[Path]:
    if not root.exists():
        return []
    bundles: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_"):
            continue
        if (child / "fixture.json").exists() or (child / "metadata.yaml").exists():
            bundles.append(child)
    return bundles


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate recorded-session bundle directories.")
    parser.add_argument("bundles", nargs="*", help="Bundle directories")
    parser.add_argument(
        "--root",
        default="proof-results/recorded_sessions",
        help="Bundle root used when no bundle paths are provided",
    )
    args = parser.parse_args()

    if args.bundles:
        bundles = [Path(p) for p in args.bundles]
    else:
        bundles = _discover_bundles(Path(args.root))

    if not bundles:
        print("No recorded session bundles found.")
        return 0

    all_errors: list[str] = []
    all_warnings: list[str] = []

    for bundle in bundles:
        if not bundle.exists():
            all_errors.append(f"missing bundle path: {bundle}")
            continue

        errors, warnings = validate_bundle(bundle)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        if errors:
            print(f"FAIL  {bundle.name} ({len(errors)} errors)")
            for e in errors:
                if e.startswith(f"{bundle.name}:"):
                    print(f"  ERROR: {e.split(':', 1)[1].strip()}")
                else:
                    print(f"  ERROR: {e}")
            continue

        status = _load_metadata(bundle / "metadata.yaml").get("status", "unknown")
        print(f"OK    {bundle.name} (status={status})")
        for w in warnings:
            if w.startswith(f"{bundle.name}:"):
                print(f"  WARN:  {w.split(':', 1)[1].strip()}")

    if all_warnings:
        print(f"\nWarnings: {len(all_warnings)}")
    if all_errors:
        print(f"Errors: {len(all_errors)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
