#!/usr/bin/env python3
"""Validate normalized OpenClaw trace exports used for fixture conversion."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "recorded_sessions" / "schema" / "openclaw_session_trace.schema.json"
TRACES_DIR = REPO_ROOT / "recorded_sessions" / "traces"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})\b")

try:
    import jsonschema  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _validate_with_jsonschema(payload: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{label}: {loc}: {err.message}")
    return errors


def _validate_structural(payload: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    required_top = [
        "trace_version",
        "trace_id",
        "source",
        "session_context",
        "prompt_template",
        "budgets",
        "turns",
        "redaction",
    ]
    for key in required_top:
        if key not in payload:
            errors.append(f"{label}: missing required field '{key}'")

    if payload.get("trace_version") != "openclaw_session_trace.v1":
        errors.append(f"{label}: trace_version must be openclaw_session_trace.v1")

    source = payload.get("source", {})
    if not isinstance(source, dict):
        errors.append(f"{label}: source must be object")
    else:
        for field in ["product_version", "capture_date", "exported_at"]:
            if field not in source:
                errors.append(f"{label}: source missing required field '{field}'")

    prompt_template = payload.get("prompt_template", {})
    if not isinstance(prompt_template, dict):
        errors.append(f"{label}: prompt_template must be object")
    else:
        for field in ["template_id", "template_sha256"]:
            if field not in prompt_template:
                errors.append(f"{label}: prompt_template missing required field '{field}'")

    budgets = payload.get("budgets", {})
    if not isinstance(budgets, dict):
        errors.append(f"{label}: budgets must be object")
    else:
        for field in ["context_budget_tokens", "correction_budget"]:
            if field not in budgets:
                errors.append(f"{label}: budgets missing required field '{field}'")

    redaction = payload.get("redaction", {})
    if not isinstance(redaction, dict):
        errors.append(f"{label}: redaction must be object")
    else:
        for field in ["redacted", "strategy"]:
            if field not in redaction:
                errors.append(f"{label}: redaction missing required field '{field}'")

    turns = payload.get("turns")
    if not isinstance(turns, list) or len(turns) == 0:
        errors.append(f"{label}: 'turns' must be a non-empty array")
    else:
        for i, turn in enumerate(turns):
            for field in ["turn_id", "user_input", "assistant_output", "available_documents"]:
                if field not in turn:
                    errors.append(f"{label}: turns[{i}]: missing required field '{field}'")
            docs = turn.get("available_documents") if isinstance(turn, dict) else None
            if not isinstance(docs, list):
                errors.append(f"{label}: turns[{i}].available_documents must be an array")
            else:
                for j, doc in enumerate(docs):
                    if not isinstance(doc, dict):
                        errors.append(f"{label}: turns[{i}].available_documents[{j}] must be object")
                        continue
                    if "doc_id" not in doc:
                        errors.append(f"{label}: turns[{i}].available_documents[{j}] missing doc_id")
                    has_material = any(doc.get(k) for k in ["content", "excerpt", "content_sha256"])
                    if not has_material:
                        errors.append(
                            f"{label}: turns[{i}].available_documents[{j}] requires content/excerpt/content_sha256"
                        )
    return errors


def _validate_semantic(payload: dict[str, Any], label: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    turns = payload.get("turns", [])
    if isinstance(turns, list):
        turn_ids = [t.get("turn_id") for t in turns if isinstance(t, dict)]
        expected = list(range(len(turns)))
        if turn_ids != expected:
            errors.append(f"{label}: turn_id values must be contiguous 0..N-1")

        for idx, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(f"{label}: turns[{idx}] must be an object")
                continue
            docs = turn.get("available_documents", [])
            if not isinstance(docs, list):
                errors.append(f"{label}: turns[{idx}].available_documents must be an array")
                continue
            doc_ids = [d.get("doc_id") for d in docs if isinstance(d, dict)]
            if len(doc_ids) != len(set(doc_ids)):
                errors.append(f"{label}: turns[{idx}] has duplicate doc_id values")
            if not str(turn.get("assistant_output", "")).strip():
                errors.append(f"{label}: turns[{idx}].assistant_output must be non-empty")

    source = payload.get("source", {})
    capture_date = source.get("capture_date") if isinstance(source, dict) else None
    if isinstance(capture_date, str):
        try:
            parsed = date.fromisoformat(capture_date)
            if parsed > date.today():
                errors.append(f"{label}: source.capture_date {capture_date} is in the future")
        except ValueError:
            errors.append(f"{label}: source.capture_date must be YYYY-MM-DD")

    budgets = payload.get("budgets", {})
    context_budget = budgets.get("context_budget_tokens") if isinstance(budgets, dict) else None
    if isinstance(context_budget, int) and context_budget < 64:
        warnings.append(f"{label}: budgets.context_budget_tokens={context_budget} is unusually low")

    redaction = payload.get("redaction", {})
    if isinstance(redaction, dict) and redaction.get("redacted"):
        scan: list[str] = []
        for turn in turns if isinstance(turns, list) else []:
            if not isinstance(turn, dict):
                continue
            scan.append(str(turn.get("user_input", "")))
            scan.append(str(turn.get("assistant_output", "")))
            for doc in turn.get("available_documents", []):
                if isinstance(doc, dict) and isinstance(doc.get("content"), str):
                    scan.append(doc["content"])
        joined = "\n".join(scan)
        if EMAIL_RE.search(joined):
            warnings.append(f"{label}: redaction.redacted=true but email-like text remains")
        if PHONE_RE.search(joined):
            warnings.append(f"{label}: redaction.redacted=true but phone-like text remains")

    return errors, warnings


def _print_summary(payload: dict[str, Any], path: Path, warnings: list[str]) -> None:
    label = _safe_rel(path)
    source = payload.get("source", {})
    redaction = payload.get("redaction", {})
    print(f"\n--- {label} ---")
    print(f"  trace_id:            {payload.get('trace_id', '?')}")
    print(f"  trace_version:       {payload.get('trace_version', '?')}")
    print(f"  source version:      {source.get('product_version', '?')}")
    print(f"  capture date:        {source.get('capture_date', '?')}")
    print(f"  turns:               {len(payload.get('turns', []))}")
    print(f"  context budget:      {payload.get('budgets', {}).get('context_budget_tokens', '?')}")
    print(f"  correction budget:   {payload.get('budgets', {}).get('correction_budget', '?')}")
    print(f"  redacted:            {redaction.get('redacted', '?')}")

    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate OpenClaw trace export JSON files.")
    parser.add_argument("traces", nargs="*", help="Trace JSON files")
    parser.add_argument("--all", action="store_true", help="Validate all traces in recorded_sessions/traces/")
    parser.add_argument("--strict-warnings", action="store_true", help="Fail on warnings")
    args = parser.parse_args()

    paths: list[Path]
    if args.all:
        paths = sorted(TRACES_DIR.glob("*.json"))
    else:
        paths = [Path(p) for p in args.traces]

    if not paths:
        print("No trace files specified. Use --all or pass file paths.", file=sys.stderr)
        return 1

    schema = _load_json(SCHEMA_PATH)

    total_errors = 0
    total_warnings = 0
    for path in paths:
        if not path.exists():
            print(f"Missing trace: {path}", file=sys.stderr)
            return 1

        payload = _load_json(path)
        label = _safe_rel(path)

        if HAS_JSONSCHEMA:
            errors = _validate_with_jsonschema(payload, schema, label)
        else:
            errors = _validate_structural(payload, label)
        sem_errors, warnings = _validate_semantic(payload, label)
        errors.extend(sem_errors)

        total_errors += len(errors)
        total_warnings += len(warnings)
        _print_summary(payload, path, warnings)

        if errors:
            print("  Errors:")
            for e in errors:
                print(f"    - {e}")

    if total_errors:
        print(f"\nValidation FAILED ({total_errors} error(s)).")
        return 1

    if args.strict_warnings and total_warnings:
        print(f"\nValidation FAILED due to warnings (--strict-warnings): {total_warnings}")
        return 1

    validator_note = "jsonschema" if HAS_JSONSCHEMA else "structural fallback"
    print(f"\nAll {len(paths)} trace file(s) valid ({validator_note}) with {total_warnings} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
