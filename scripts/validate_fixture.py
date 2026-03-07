#!/usr/bin/env python3
"""Validate recorded-session fixtures.

Usage examples:
    python scripts/validate_fixture.py recorded_sessions/fixtures/example_minimal.json
    python scripts/validate_fixture.py --all
    python scripts/validate_fixture.py --all --check-trace-hash
    python scripts/validate_fixture.py fixture.json --strict-warnings
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "recorded_sessions" / "schema" / "session_fixture.schema.json"
FIXTURES_DIR = REPO_ROOT / "recorded_sessions" / "fixtures"
TRACES_DIR = REPO_ROOT / "recorded_sessions" / "traces"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})\b")

try:
    import jsonschema  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


@dataclass
class ValidationResult:
    fixture_path: Path
    fixture: dict[str, Any]
    errors: list[str]
    warnings: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _candidate_trace_paths(fixture_path: Path, fixture: dict[str, Any]) -> list[Path]:
    out: list[Path] = []
    conversion = fixture.get("conversion", {})
    raw_input = conversion.get("input_trace")
    if isinstance(raw_input, str) and raw_input.strip():
        p = Path(raw_input)
        if p.is_absolute():
            out.append(p)
        else:
            out.append((fixture_path.parent / p).resolve())
            out.append((REPO_ROOT / p).resolve())

    trace_id = fixture.get("source", {}).get("trace_id")
    if isinstance(trace_id, str) and trace_id:
        out.append((TRACES_DIR / f"{trace_id}.json").resolve())

    # De-duplicate while preserving order.
    dedup: list[Path] = []
    seen = set()
    for p in out:
        key = str(p)
        if key not in seen:
            seen.add(key)
            dedup.append(p)
    return dedup


# ---------------------------------------------------------------------------
# Validation layers
# ---------------------------------------------------------------------------


def _validate_with_jsonschema(fixture: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(fixture), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{label}: {loc}: {err.message}")
    return errors


def _validate_structural(fixture: dict[str, Any], label: str) -> list[str]:
    """Fallback validation when jsonschema is unavailable."""
    errors: list[str] = []
    required_top = [
        "schema_version",
        "fixture_id",
        "source",
        "session_context",
        "turns",
        "ground_truth",
        "held_fixed",
        "redaction",
        "conversion",
    ]
    for key in required_top:
        if key not in fixture:
            errors.append(f"{label}: missing required top-level field '{key}'")

    turns = fixture.get("turns")
    if not isinstance(turns, list) or len(turns) == 0:
        errors.append(f"{label}: 'turns' must be a non-empty array")
    else:
        for i, turn in enumerate(turns):
            for field in ["turn_id", "user_input", "available_documents", "expected_output", "rubric", "trace_ref"]:
                if field not in turn:
                    errors.append(f"{label}: turns[{i}]: missing required field '{field}'")

    source = fixture.get("source", {})
    for field in ["product_version", "capture_date", "trace_id", "trace_export_format", "trace_sha256", "trace_turn_count"]:
        if field not in source:
            errors.append(f"{label}: source: missing required field '{field}'")

    gt = fixture.get("ground_truth", {})
    for field in ["total_turns", "labeling_method", "requires_human_review"]:
        if field not in gt:
            errors.append(f"{label}: ground_truth: missing required field '{field}'")

    hf = fixture.get("held_fixed", {})
    for field in ["prompt_template_hash", "context_budget_tokens", "correction_budget"]:
        if field not in hf:
            errors.append(f"{label}: held_fixed: missing required field '{field}'")

    return errors


def _validate_semantic(
    fixture: dict[str, Any],
    label: str,
    fixture_path: Path,
    check_trace_hash: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    turns = fixture.get("turns", [])
    if isinstance(turns, list):
        turn_ids = [t.get("turn_id") for t in turns if isinstance(t, dict)]
        expected_turn_ids = list(range(len(turns)))
        if turn_ids != expected_turn_ids:
            errors.append(f"{label}: turn_id values must be contiguous 0..N-1 (got {turn_ids[:8]})")

        for idx, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(f"{label}: turns[{idx}] must be an object")
                continue

            if not str(turn.get("user_input", "")).strip():
                errors.append(f"{label}: turns[{idx}].user_input must be non-empty")
            if not str(turn.get("expected_output", "")).strip():
                errors.append(f"{label}: turns[{idx}].expected_output must be non-empty")

            trace_ref = turn.get("trace_ref", {})
            if isinstance(trace_ref, dict):
                tref = trace_ref.get("turn_ref")
                if isinstance(tref, int) and tref != idx:
                    errors.append(
                        f"{label}: turns[{idx}].trace_ref.turn_ref={tref} but expected {idx}"
                    )

            docs = turn.get("available_documents", [])
            if isinstance(docs, list):
                doc_ids = [d.get("doc_id") for d in docs if isinstance(d, dict)]
                if len(doc_ids) != len(set(doc_ids)):
                    errors.append(f"{label}: turns[{idx}] has duplicate doc_id values")
                for d_idx, doc in enumerate(docs):
                    if not isinstance(doc, dict):
                        errors.append(f"{label}: turns[{idx}].available_documents[{d_idx}] must be object")
                        continue
                    has_material = any(doc.get(k) for k in ["content", "excerpt", "content_sha256"])
                    if not has_material:
                        errors.append(
                            f"{label}: turns[{idx}].available_documents[{d_idx}] needs content/excerpt/content_sha256"
                        )
            else:
                errors.append(f"{label}: turns[{idx}].available_documents must be an array")

    gt = fixture.get("ground_truth", {})
    if isinstance(gt, dict):
        total_turns = gt.get("total_turns")
        if isinstance(total_turns, int) and total_turns != len(turns):
            errors.append(
                f"{label}: ground_truth.total_turns={total_turns} but fixture has {len(turns)} turns"
            )

    source = fixture.get("source", {})
    if isinstance(source, dict):
        trace_turn_count = source.get("trace_turn_count")
        if isinstance(trace_turn_count, int) and trace_turn_count != len(turns):
            errors.append(
                f"{label}: source.trace_turn_count={trace_turn_count} but fixture has {len(turns)} turns"
            )

        capture_date = _parse_date(source.get("capture_date"))
        if capture_date is None:
            errors.append(f"{label}: source.capture_date must be YYYY-MM-DD")
        elif capture_date > date.today():
            errors.append(
                f"{label}: source.capture_date {capture_date.isoformat()} is in the future"
            )

    hf = fixture.get("held_fixed", {})
    if isinstance(hf, dict):
        context_budget = hf.get("context_budget_tokens")
        if isinstance(context_budget, int) and context_budget < 64:
            warnings.append(
                f"{label}: held_fixed.context_budget_tokens={context_budget} is unusually low for replay"
            )

    redaction = fixture.get("redaction", {})
    if isinstance(redaction, dict) and redaction.get("redacted"):
        redaction_scan_targets: list[str] = []
        for turn in turns if isinstance(turns, list) else []:
            if not isinstance(turn, dict):
                continue
            redaction_scan_targets.append(str(turn.get("user_input", "")))
            redaction_scan_targets.append(str(turn.get("expected_output", "")))
            for doc in turn.get("available_documents", []):
                if isinstance(doc, dict) and isinstance(doc.get("content"), str):
                    redaction_scan_targets.append(doc["content"])

        joined = "\n".join(redaction_scan_targets)
        if EMAIL_RE.search(joined):
            warnings.append(f"{label}: redaction.redacted=true but fixture still appears to contain email-like text")
        if PHONE_RE.search(joined):
            warnings.append(f"{label}: redaction.redacted=true but fixture still appears to contain phone-like text")

    if check_trace_hash:
        expected_sha = source.get("trace_sha256") if isinstance(source, dict) else None
        candidates = _candidate_trace_paths(fixture_path, fixture)
        trace_path = next((p for p in candidates if p.exists()), None)
        if trace_path is None:
            warnings.append(
                f"{label}: --check-trace-hash enabled but no source trace file found near conversion.input_trace/recorded_sessions/traces"
            )
        elif isinstance(expected_sha, str) and expected_sha.startswith("sha256:"):
            actual = _sha256(trace_path)
            expected = expected_sha.split(":", 1)[1]
            if actual != expected:
                errors.append(
                    f"{label}: trace hash mismatch for {_safe_rel(trace_path)}: expected {expected}, got {actual}"
                )
        else:
            errors.append(f"{label}: source.trace_sha256 missing or malformed")

    return errors, warnings


def validate_fixture(
    fixture_path: Path,
    schema: dict[str, Any],
    check_trace_hash: bool,
) -> ValidationResult:
    fixture = _load_json(fixture_path)
    label = _safe_rel(fixture_path)

    if HAS_JSONSCHEMA:
        errors = _validate_with_jsonschema(fixture, schema, label)
    else:
        errors = _validate_structural(fixture, label)

    sem_errors, sem_warnings = _validate_semantic(
        fixture,
        label,
        fixture_path,
        check_trace_hash,
    )
    errors.extend(sem_errors)

    return ValidationResult(
        fixture_path=fixture_path,
        fixture=fixture,
        errors=errors,
        warnings=sem_warnings,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def print_summary(result: ValidationResult) -> None:
    fixture = result.fixture
    label = _safe_rel(result.fixture_path)
    turns = fixture.get("turns", [])
    source = fixture.get("source", {})
    gt = fixture.get("ground_truth", {})
    hf = fixture.get("held_fixed", {})
    redaction = fixture.get("redaction", {})

    print(f"\n--- {label} ---")
    print(f"  checked_at:          {_now_iso()}")
    print(f"  schema_version:      {fixture.get('schema_version', '?')}")
    print(f"  fixture_id:          {fixture.get('fixture_id', '?')}")
    print(f"  trace_id:            {source.get('trace_id', '?')}")
    print(f"  trace_export_format: {source.get('trace_export_format', '?')}")
    print(f"  source version:      {source.get('product_version', '?')}")
    print(f"  capture date:        {source.get('capture_date', '?')}")
    print(f"  turns:               {len(turns)}")
    print(f"  complexity:          {gt.get('complexity_tier', '?')}")
    print(f"  labeling_method:     {gt.get('labeling_method', '?')}")
    print(f"  requires_review:     {gt.get('requires_human_review', '?')}")
    print(f"  context budget:      {hf.get('context_budget_tokens', '?')} tokens")
    print(f"  correction budget:   {hf.get('correction_budget', '?')}")
    print(f"  redacted:            {redaction.get('redacted', '?')}")

    total_docs = sum(len(t.get("available_documents", [])) for t in turns if isinstance(t, dict))
    has_graph = any(t.get("graph_snapshot") is not None for t in turns if isinstance(t, dict))
    print(f"  total docs:          {total_docs} across all turns")
    print(f"  graph snapshots:     {'yes' if has_graph else 'none'}")

    if result.warnings:
        print("\n  Warnings:")
        for w in result.warnings:
            print(f"    - {w}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate recorded-session fixtures.")
    parser.add_argument("fixtures", nargs="*", help="Fixture JSON files to validate.")
    parser.add_argument("--all", action="store_true", help="Validate all fixtures in recorded_sessions/fixtures/.")
    parser.add_argument(
        "--check-trace-hash",
        action="store_true",
        help="Verify source.trace_sha256 against the trace file when available.",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Fail if any warning is emitted.",
    )
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
    results: list[ValidationResult] = []
    for p in paths:
        if not p.exists():
            print(f"Missing fixture: {p}", file=sys.stderr)
            return 1
        results.append(validate_fixture(p, schema, check_trace_hash=args.check_trace_hash))

    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    for r in results:
        print_summary(r)

    if total_errors:
        print(f"\nValidation FAILED ({total_errors} error(s)):")
        for r in results:
            for e in r.errors:
                print(f"  {e}")
        return 1

    if args.strict_warnings and total_warnings:
        print(f"\nValidation FAILED due to warnings (--strict-warnings): {total_warnings}")
        for r in results:
            for w in r.warnings:
                print(f"  {w}")
        return 1

    validator_note = "jsonschema" if HAS_JSONSCHEMA else "structural fallback"
    print(
        f"\nAll {len(results)} fixture(s) valid ({validator_note})"
        f" with {total_warnings} warning(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
