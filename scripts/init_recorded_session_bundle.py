#!/usr/bin/env python3
"""Initialize a scaffold bundle for proof-results/recorded_sessions/<fixture_id>."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - fallback used only if pyyaml missing
    yaml = None  # type: ignore[assignment]

DEFAULT_OUTPUT_ROOT = Path("proof-results") / "recorded_sessions"
REQUIRED_MODES = ["no_brain", "vector_only", "graph_prior_only", "learned_route"]
OPTIONAL_MODES = ["full_brain", "online"]


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _iso_now() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_metadata(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(payload, f, sort_keys=False)


def _build_score_card_template(bundle_id: str, fixture_id: str) -> dict[str, Any]:
    scores = {}
    for mode in REQUIRED_MODES + OPTIONAL_MODES:
        scores[mode] = {
            "turns": [],
            "aggregates": {
                "success_rate": None,
                "mean_rubric_score": None,
                "total_corrections": None,
                "mean_prompt_context_size": None,
                "mean_latency_proxy": None,
                "total_cost_proxy": None,
            },
            "notes": "pending",
        }
    return {
        "format_version": "recorded_session_score_card.v1",
        "status": "scaffold",
        "bundle_id": bundle_id,
        "fixture_id": fixture_id,
        "required_modes": REQUIRED_MODES,
        "optional_modes": OPTIONAL_MODES,
        "scores": scores,
    }


def init_bundle(
    fixture_path: Path,
    output_root: Path,
    bundle_id: str | None,
    overwrite: bool,
) -> Path:
    fixture = _load_json(fixture_path)
    fixture_id = fixture.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id:
        raise ValueError("fixture_id missing from fixture JSON")

    out_id = bundle_id or fixture_id
    bundle_dir = output_root / out_id
    if bundle_dir.exists() and not overwrite:
        raise ValueError(f"Bundle already exists: {bundle_dir} (use --overwrite to update)")

    bundle_dir.mkdir(parents=True, exist_ok=True)
    fixture_out = bundle_dir / "fixture.json"
    fixture_out.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    fixture_hash = _sha256(fixture_out)
    verification_dir = bundle_dir / "verification"
    verification_dir.mkdir(parents=True, exist_ok=True)
    _write_text(verification_dir / "fixture_hash.sha256", f"{fixture_hash}  fixture.json\n")

    metadata = {
        "format_version": "recorded_session_bundle.v1",
        "status": "scaffold",
        "bundle_id": out_id,
        "fixture_id": fixture_id,
        "created_at": _iso_now(),
        "fixture_file": "fixture.json",
        "fixture_sha256": fixture_hash,
        "required_modes": REQUIRED_MODES,
        "optional_modes": OPTIONAL_MODES,
        "scoring_status": "pending",
        "notes": "Initialized scaffold bundle. Populate score_card.json with replay outputs.",
    }
    _write_metadata(bundle_dir / "metadata.yaml", metadata)

    score_card = _build_score_card_template(out_id, fixture_id)
    _write_text(bundle_dir / "score_card.json", json.dumps(score_card, indent=2) + "\n")

    score_card_md = """# Score Card (Scaffold)

This bundle is scaffold-only. No scored mode outputs are published yet.

## Required modes

| Mode | Status |
|---|---|
| no_brain | pending |
| vector_only | pending |
| graph_prior_only | pending |
| learned_route | pending |

## Optional modes

| Mode | Status |
|---|---|
| full_brain | pending |
| online | pending |
"""
    _write_text(bundle_dir / "score_card.md", score_card_md)

    verification_notes = """# Verification Notes

- `fixture_hash.sha256` records the hash of `fixture.json`.
- Add per-mode trace hashes and scoring reproducibility checks after replay.
"""
    _write_text(verification_dir / "README.md", verification_notes)

    readme = f"""# Recorded Session Bundle: {out_id}

Status: **scaffold**

This bundle was initialized from `{fixture_path}`.

## Files

- `fixture.json`
- `metadata.yaml`
- `score_card.json`
- `score_card.md`
- `verification/fixture_hash.sha256`

## Next steps

1. Replay fixture across required modes.
2. Fill per-turn rows and aggregates in `score_card.json`.
3. Update `score_card.md` with human-readable summary.
4. Run `python scripts/validate_recorded_session_bundle.py {bundle_dir}`.
"""
    _write_text(bundle_dir / "README.md", readme)

    return bundle_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a recorded-session scaffold bundle.")
    parser.add_argument("--fixture", required=True, help="Path to recorded-session fixture JSON")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output root directory (default: proof-results/recorded_sessions)",
    )
    parser.add_argument("--bundle-id", default=None, help="Optional bundle directory name")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing bundle directory contents")
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    if not fixture_path.exists():
        print(f"Fixture not found: {fixture_path}")
        return 1

    try:
        bundle_dir = init_bundle(
            fixture_path=fixture_path,
            output_root=Path(args.output_root),
            bundle_id=args.bundle_id,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        print(f"Initialization failed: {exc}")
        return 1

    print(f"Bundle scaffold created: {bundle_dir}")
    print(f"  Validate with: python scripts/validate_recorded_session_bundle.py {bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
