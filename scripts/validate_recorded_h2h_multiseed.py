#!/usr/bin/env python3
"""Validate a multi-seed recorded head-to-head bundle.

Usage:
    python scripts/validate_recorded_h2h_multiseed.py [proof-results/recorded_h2h_*_10seed/]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from validate_recorded_h2h import validate_bundle


REQUIRED_ROOT_FILES = [
    "summary.json",
    "per_seed_summaries.json",
    "seeds.json",
    "summary_table.csv",
    "summary_table.md",
    "leaderboard.csv",
    "leaderboard.md",
    "pairwise_accuracy_delta.csv",
    "pairwise_accuracy_delta.md",
    "win_rate_matrix.csv",
    "win_rate_matrix.md",
    "per_seed_breakdown.csv",
    "per_seed_breakdown.md",
    "per_seed_accuracy_matrix.csv",
    "per_seed_accuracy_matrix.md",
    "proof_digest.md",
    "seed_bundle_index.csv",
    "seed_bundle_index.md",
]


def _check_required_files(bundle_dir: Path, errors: list[str]) -> None:
    for rel in REQUIRED_ROOT_FILES:
        if not (bundle_dir / rel).exists():
            errors.append(f"Missing required file: {rel}")


def _load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path.name}: {exc}")
    return None


def _validate_aggregate_math(bundle_dir: Path, errors: list[str]) -> None:
    summary_obj = _load_json(bundle_dir / "summary.json", errors)
    per_seed_obj = _load_json(bundle_dir / "per_seed_summaries.json", errors)
    if not isinstance(summary_obj, dict) or not isinstance(per_seed_obj, list) or not per_seed_obj:
        return

    baselines = sorted(summary_obj.keys())
    for baseline in baselines:
        agg = summary_obj.get(baseline, {})
        if not isinstance(agg, dict):
            errors.append(f"summary.json baseline entry is not an object: {baseline}")
            continue

        values: list[float] = []
        for seed_summary in per_seed_obj:
            if not isinstance(seed_summary, dict):
                errors.append("per_seed_summaries.json contains non-object seed entry")
                return
            baseline_metrics = seed_summary.get(baseline, {})
            if not isinstance(baseline_metrics, dict):
                errors.append(f"Seed summary missing baseline metrics: {baseline}")
                return
            values.append(float(baseline_metrics.get("accuracy", 0.0)))

        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        std = variance ** 0.5

        agg_mean = float(agg.get("accuracy", 0.0))
        agg_std = float(agg.get("accuracy_std", 0.0))
        if abs(agg_mean - mean) > 1e-6:
            errors.append(
                f"Accuracy mean mismatch for {baseline}: summary={agg_mean:.6f}, recomputed={mean:.6f}"
            )
        if abs(agg_std - std) > 1e-6:
            errors.append(
                f"Accuracy std mismatch for {baseline}: summary={agg_std:.6f}, recomputed={std:.6f}"
            )


def validate_multiseed_bundle(bundle_dir: Path) -> list[str]:
    errors: list[str] = []

    _check_required_files(bundle_dir, errors)

    seeds_obj = _load_json(bundle_dir / "seeds.json", errors)
    per_seed_obj = _load_json(bundle_dir / "per_seed_summaries.json", errors)
    if isinstance(seeds_obj, list) and isinstance(per_seed_obj, list):
        if len(seeds_obj) != len(per_seed_obj):
            errors.append(
                f"Seed count mismatch: seeds.json has {len(seeds_obj)} entries but per_seed_summaries.json has {len(per_seed_obj)}"
            )

        for seed in seeds_obj:
            seed_dir = bundle_dir / f"seed_{seed}"
            if not seed_dir.exists():
                errors.append(f"Missing seed bundle directory: {seed_dir.name}")
                continue
            seed_errors = validate_bundle(seed_dir)
            for seed_error in seed_errors:
                errors.append(f"{seed_dir.name}: {seed_error}")

    _validate_aggregate_math(bundle_dir, errors)

    if errors:
        print(f"FAIL  {bundle_dir.name} ({len(errors)} errors)")
        for error in errors:
            print(f"  ERROR: {error}")
    else:
        seed_count = len(seeds_obj) if isinstance(seeds_obj, list) else "?"
        print(f"OK    {bundle_dir.name} (recorded multiseed, seeds={seed_count})")

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        proof_dir = Path("proof-results")
        bundles = sorted(proof_dir.glob("recorded_h2h_*seed*/"))
        if not bundles:
            print("No recorded_h2h_*seed* bundles found in proof-results/")
            sys.exit(0)
    else:
        bundles = [Path(arg) for arg in sys.argv[1:]]

    all_errors: list[str] = []
    for bundle in bundles:
        all_errors.extend(validate_multiseed_bundle(bundle))

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
