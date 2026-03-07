#!/usr/bin/env python3
"""Validate a recorded head-to-head artifact bundle.

Usage:
    python scripts/validate_recorded_h2h.py [proof-results/recorded_h2h_*/]

Checks all publishability criteria from recorded_head2head_spec.md:
  1. Fixture hash matches verification/fixture_hash.sha256
  2. Trace hashes match verification/trace_hashes.sha256
  3. All queries have trace entries (count match)
  4. Scoring is reproducible from traces
  5. Baseline configs are recorded in metadata.yaml
  6. Git SHA is recorded in metadata.yaml
  7. At least 3 baselines compared (full_brain + 1 RAG + 1 ablation)
  8. Results summary exists (scoring/summary_table.md)

Reports status: publishable, draft, scaffold, or FAIL.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def validate_bundle(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    # -- Required structure --
    readme = bundle_dir / "README.md"
    metadata_path = bundle_dir / "metadata.yaml"
    if not readme.exists():
        errors.append("Missing README.md")
    if not metadata_path.exists():
        errors.append("Missing metadata.yaml")
        return errors  # can't continue without metadata

    # -- Metadata validation --
    meta = None
    if yaml is not None:
        with open(metadata_path) as f:
            meta = yaml.safe_load(f)
        required_keys = ["format_version", "status", "bundle_id", "family"]
        for k in required_keys:
            if k not in meta:
                errors.append(f"metadata.yaml missing required key: {k}")

        status = meta.get("status", "unknown")
    else:
        status = "unknown"
        warnings.append("PyYAML not installed; metadata keys not checked")

    # -- Expected subdirs --
    for subdir in ["traces", "scoring", "verification"]:
        d = bundle_dir / subdir
        if not d.exists():
            if status == "scaffold":
                warnings.append(f"{subdir}/ not yet created (scaffold status)")
            else:
                errors.append(f"Missing required directory: {subdir}/")

    # -- Fixture hash check (criterion 1) --
    fixture = bundle_dir / "fixture.yaml"
    fixture_hash_file = bundle_dir / "verification" / "fixture_hash.sha256"
    if fixture.exists() and fixture_hash_file.exists():
        actual = _sha256(fixture)
        expected = fixture_hash_file.read_text().strip().split()[0]
        if actual != expected:
            errors.append(f"Fixture hash mismatch: {actual} != {expected}")
    elif status not in ("scaffold",):
        if not fixture.exists():
            errors.append("Missing fixture.yaml")
        if not fixture_hash_file.exists():
            warnings.append("Missing verification/fixture_hash.sha256")

    # -- Trace hash check (criterion 2) --
    traces_dir = bundle_dir / "traces"
    trace_hash_file = bundle_dir / "verification" / "trace_hashes.sha256"
    if traces_dir.exists() and trace_hash_file.exists():
        expected_hashes = {}
        for line in trace_hash_file.read_text().strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                expected_hashes[parts[1]] = parts[0]
        for trace_file in sorted(traces_dir.glob("*.jsonl")):
            actual_hash = _sha256(trace_file)
            exp = expected_hashes.get(trace_file.name)
            if exp and actual_hash != exp:
                errors.append(f"Trace hash mismatch for {trace_file.name}")

    # -- Trace JSONL structure + completeness (criterion 3 & 4) --
    trace_query_counts: dict[str, int] = {}
    if traces_dir.exists():
        jsonl_files = list(traces_dir.glob("*.jsonl"))
        for jf in jsonl_files:
            qcount = 0
            with open(jf) as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if "event" not in obj:
                            errors.append(f"{jf.name}:{i} missing 'event' key")
                            break
                        if obj["event"] == "query_response":
                            qcount += 1
                    except json.JSONDecodeError as e:
                        errors.append(f"{jf.name}:{i} invalid JSON: {e}")
                        break
            trace_query_counts[jf.stem] = qcount

    # Check query count vs fixture
    if fixture.exists() and yaml is not None and trace_query_counts:
        with open(fixture) as f:
            fix = yaml.safe_load(f)
        fixture_queries = sum(len(s.get("queries", [])) for s in fix.get("steps", []))
        for bl_name, count in trace_query_counts.items():
            if count != fixture_queries:
                errors.append(
                    f"Trace completeness: {bl_name} has {count} query_response events, "
                    f"expected {fixture_queries}"
                )

    # -- Scoring reproducibility (criterion 4) --
    repro_file = bundle_dir / "verification" / "scoring_reproducibility.txt"
    if repro_file.exists():
        repro_text = repro_file.read_text()
        if "FAIL" in repro_text and "Overall: PASS" not in repro_text:
            errors.append("Scoring reproducibility check failed")
    elif status not in ("scaffold",):
        warnings.append("Missing verification/scoring_reproducibility.txt")

    # -- Baseline configs recorded (criterion 5) --
    if meta is not None:
        baselines_run = meta.get("baselines_run", [])
        if not baselines_run and status not in ("scaffold",):
            errors.append("metadata.yaml has no baselines_run entries")

    # -- Git SHA recorded (criterion 6) --
    if meta is not None:
        git_sha = meta.get("git_sha")
        if not git_sha and status not in ("scaffold",):
            warnings.append("metadata.yaml missing git_sha")

    # -- At least 3 baselines (criterion 7) --
    num_baselines = len(trace_query_counts)
    required_baselines = {"full_brain"}  # must include full_brain
    rag_baselines = {"vector_rag", "vector_rag_rerank"}
    ablation_baselines = {"graph_route_pg", "route_fn_only", "static_graph", "heuristic_stateful"}

    if num_baselines > 0:
        present = set(trace_query_counts.keys())
        if not (present & required_baselines):
            errors.append("Missing required baseline: full_brain")
        if not (present & rag_baselines):
            errors.append("Missing required RAG baseline (vector_rag or vector_rag_rerank)")
        if not (present & ablation_baselines):
            errors.append("Missing required ablation baseline")
        if num_baselines < 3:
            errors.append(f"Only {num_baselines} baselines; minimum 3 required")

    # -- Results summary exists (criterion 8) --
    summary_md = bundle_dir / "scoring" / "summary_table.md"
    if summary_md.exists():
        if summary_md.stat().st_size == 0:
            errors.append("scoring/summary_table.md is empty")
    elif status not in ("scaffold",):
        errors.append("Missing scoring/summary_table.md")

    # -- Determine overall status --
    if status == "scaffold" and not trace_query_counts:
        label = "scaffold"
    elif errors:
        label = "FAIL"
    elif warnings:
        label = "draft (warnings)"
    else:
        label = "publishable" if status != "scaffold" else "draft"

    # -- Report --
    if errors:
        print(f"FAIL  {bundle_dir.name} ({len(errors)} errors)")
        for e in errors:
            print(f"  ERROR: {e}")
    elif label == "scaffold":
        print(f"OK    {bundle_dir.name} (scaffold, {len(warnings)} warnings)")
        for w in warnings:
            print(f"  WARN:  {w}")
    else:
        print(f"OK    {bundle_dir.name} (status={label})")
        if num_baselines:
            print(f"  Baselines: {num_baselines}")
            if fixture.exists() and yaml is not None:
                with open(fixture) as f:
                    fix = yaml.safe_load(f)
                fq = sum(len(s.get("queries", [])) for s in fix.get("steps", []))
                print(f"  Fixture queries: {fq}")
        for w in warnings:
            print(f"  WARN:  {w}")

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        # Auto-discover bundles
        proof_dir = Path("proof-results")
        bundles = sorted(proof_dir.glob("recorded_h2h_*/"))
        if not bundles:
            print("No recorded_h2h_* bundles found in proof-results/")
            sys.exit(0)
    else:
        bundles = [Path(a) for a in sys.argv[1:]]

    all_errors: list[str] = []
    for b in bundles:
        errs = validate_bundle(b)
        all_errors.extend(errs)

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
