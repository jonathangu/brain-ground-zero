#!/usr/bin/env python3
"""Convert a normalized OpenClaw session trace into a recorded-session fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACE_SCHEMA_PATH = REPO_ROOT / "recorded_sessions" / "schema" / "openclaw_session_trace.schema.json"

try:
    import jsonschema  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _iso_now() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _slug(value: str) -> str:
    lower = value.lower().strip()
    clean = re.sub(r"[^a-z0-9._-]+", "-", lower)
    clean = re.sub(r"-+", "-", clean).strip("-")
    return clean or "fixture"


def _validate_trace(trace: dict[str, Any], trace_path: Path) -> list[str]:
    label = str(trace_path)
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
    for field in required_top:
        if field not in trace:
            errors.append(f"{label}: missing required field '{field}'")

    if trace.get("trace_version") != "openclaw_session_trace.v1":
        errors.append(f"{label}: trace_version must be openclaw_session_trace.v1")

    source = trace.get("source", {})
    if not isinstance(source, dict):
        errors.append(f"{label}: source must be an object")
    else:
        for field in ["product_version", "capture_date", "exported_at"]:
            if field not in source:
                errors.append(f"{label}: source missing required field '{field}'")

    prompt_template = trace.get("prompt_template", {})
    if not isinstance(prompt_template, dict):
        errors.append(f"{label}: prompt_template must be an object")
    else:
        for field in ["template_id", "template_sha256"]:
            if field not in prompt_template:
                errors.append(f"{label}: prompt_template missing required field '{field}'")

    budgets = trace.get("budgets", {})
    if not isinstance(budgets, dict):
        errors.append(f"{label}: budgets must be an object")
    else:
        for field in ["context_budget_tokens", "correction_budget"]:
            if field not in budgets:
                errors.append(f"{label}: budgets missing required field '{field}'")

    redaction = trace.get("redaction", {})
    if not isinstance(redaction, dict):
        errors.append(f"{label}: redaction must be an object")
    else:
        for field in ["redacted", "strategy"]:
            if field not in redaction:
                errors.append(f"{label}: redaction missing required field '{field}'")

    turns = trace.get("turns")
    if not isinstance(turns, list) or len(turns) == 0:
        errors.append(f"{label}: 'turns' must be a non-empty array")
    else:
        turn_ids: list[int] = []
        for idx, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(f"{label}: turns[{idx}] must be object")
                continue
            for field in ["turn_id", "user_input", "assistant_output", "available_documents"]:
                if field not in turn:
                    errors.append(f"{label}: turns[{idx}] missing '{field}'")
            turn_id = turn.get("turn_id")
            if isinstance(turn_id, int):
                turn_ids.append(turn_id)

            docs = turn.get("available_documents")
            if not isinstance(docs, list):
                errors.append(f"{label}: turns[{idx}].available_documents must be an array")
                continue
            for d_idx, doc in enumerate(docs):
                if not isinstance(doc, dict):
                    errors.append(f"{label}: turns[{idx}].available_documents[{d_idx}] must be object")
                    continue
                if not doc.get("doc_id"):
                    errors.append(f"{label}: turns[{idx}].available_documents[{d_idx}] missing doc_id")
                has_material = any(doc.get(k) for k in ["content", "excerpt", "content_sha256"])
                if not has_material:
                    errors.append(
                        f"{label}: turns[{idx}].available_documents[{d_idx}] needs content/excerpt/content_sha256"
                    )

        if turn_ids != list(range(len(turns))):
            errors.append(f"{label}: turn_id values must be contiguous 0..N-1")

    if HAS_JSONSCHEMA and TRACE_SCHEMA_PATH.exists():
        schema = _load_json(TRACE_SCHEMA_PATH)
        validator = jsonschema.Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(trace), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{label}: {loc}: {err.message}")

    return errors


def _build_turn(
    turn: dict[str, Any],
    idx: int,
    strip_doc_content: bool,
    strict_ground_truth: bool,
) -> tuple[dict[str, Any], bool, bool]:
    """Return (converted_turn, used_proxy_output, used_auto_rubric)."""
    explicit_expected = isinstance(turn.get("expected_output"), str) and bool(turn.get("expected_output", "").strip())
    if strict_ground_truth and not explicit_expected:
        raise ValueError(
            f"turn {idx} missing expected_output while --strict-ground-truth is enabled"
        )

    expected_output = (turn.get("expected_output") or turn.get("assistant_output") or "").strip()
    if not expected_output:
        raise ValueError(f"turn {idx} has neither expected_output nor assistant_output")

    source = "human_label" if explicit_expected else "assistant_output_proxy"

    rubric_in = turn.get("rubric") if isinstance(turn.get("rubric"), dict) else {}
    accept_criteria = str(rubric_in.get("accept_criteria", "")).strip()
    used_auto_rubric = not bool(accept_criteria)
    if used_auto_rubric:
        if strict_ground_truth:
            raise ValueError(
                f"turn {idx} missing rubric.accept_criteria while --strict-ground-truth is enabled"
            )
        accept_criteria = "Response should match expected_output while preserving key factual details."

    docs_out: list[dict[str, Any]] = []
    docs_in = turn.get("available_documents", [])
    if not isinstance(docs_in, list):
        raise ValueError(f"turn {idx} available_documents must be an array")

    for d_idx, doc in enumerate(docs_in):
        if not isinstance(doc, dict):
            raise ValueError(f"turn {idx} document {d_idx} must be object")
        doc_id = str(doc.get("doc_id", "")).strip()
        if not doc_id:
            raise ValueError(f"turn {idx} document {d_idx} missing doc_id")

        out_doc: dict[str, Any] = {"doc_id": doc_id}
        for key in ["metadata", "redacted"]:
            if key in doc:
                out_doc[key] = doc[key]

        content = doc.get("content")
        excerpt = doc.get("excerpt")
        content_sha = doc.get("content_sha256")

        if strip_doc_content and isinstance(content, str) and content:
            content_hash = _sha256_bytes(content.encode("utf-8"))
            out_doc["content_sha256"] = f"sha256:{content_hash}"
            out_doc["excerpt"] = content[:240]
        else:
            if isinstance(content, str) and content:
                out_doc["content"] = content
            if isinstance(content_sha, str) and content_sha:
                out_doc["content_sha256"] = content_sha
            if isinstance(excerpt, str) and excerpt:
                out_doc["excerpt"] = excerpt

        has_payload = any(k in out_doc for k in ["content", "content_sha256", "excerpt"])
        if not has_payload:
            raise ValueError(
                f"turn {idx} document {d_idx} requires content/content_sha256/excerpt"
            )

        docs_out.append(out_doc)

    event_ids = turn.get("event_ids") if isinstance(turn.get("event_ids"), dict) else {}
    trace_ref = {
        "turn_ref": idx,
    }
    if isinstance(event_ids.get("user"), str):
        trace_ref["user_event_id"] = event_ids["user"]
    if isinstance(event_ids.get("assistant"), str):
        trace_ref["assistant_event_id"] = event_ids["assistant"]
    if isinstance(event_ids.get("documents"), str):
        trace_ref["document_event_id"] = event_ids["documents"]

    out_turn: dict[str, Any] = {
        "turn_id": idx,
        "user_input": str(turn.get("user_input", "")).strip(),
        "available_documents": docs_out,
        "graph_snapshot": turn.get("graph_snapshot", None),
        "expected_output": expected_output,
        "rubric": {
            "accept_criteria": accept_criteria,
            "key_entities": rubric_in.get("key_entities", []),
            "partial_credit": bool(rubric_in.get("partial_credit", True)),
            "ground_truth_source": source,
            "notes": rubric_in.get("notes") or (
                "Auto-generated rubric placeholder; replace with human rubric before publishing."
                if used_auto_rubric
                else ""
            ),
        },
        "trace_ref": trace_ref,
        "annotations": turn.get("annotations", {}),
    }

    if not out_turn["rubric"]["notes"]:
        del out_turn["rubric"]["notes"]

    return out_turn, source != "human_label", used_auto_rubric


def convert_trace_to_fixture(
    trace_path: Path,
    output_path: Path,
    fixture_id: str | None,
    complexity_tier: str,
    strict_ground_truth: bool,
    strip_doc_content: bool,
) -> dict[str, Any]:
    trace = _load_json(trace_path)
    errors = _validate_trace(trace, trace_path)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise ValueError(f"Trace validation failed with {len(errors)} error(s)")

    trace_bytes = trace_path.read_bytes()
    trace_sha = _sha256_bytes(trace_bytes)

    trace_id = str(trace.get("trace_id", "trace")).strip()
    out_fixture_id = _slug(fixture_id or trace_id)

    turns = trace.get("turns", [])
    if not isinstance(turns, list):
        raise ValueError("trace.turns must be a list")

    converted_turns: list[dict[str, Any]] = []
    any_proxy = False
    any_auto_rubric = False
    for idx, turn in enumerate(turns):
        converted_turn, used_proxy, used_auto_rubric = _build_turn(
            turn,
            idx,
            strip_doc_content=strip_doc_content,
            strict_ground_truth=strict_ground_truth,
        )
        converted_turns.append(converted_turn)
        any_proxy = any_proxy or used_proxy
        any_auto_rubric = any_auto_rubric or used_auto_rubric

    per_turn_sources = {t["rubric"]["ground_truth_source"] for t in converted_turns}
    if per_turn_sources == {"human_label"}:
        labeling_method = "human_labeled"
    elif per_turn_sources == {"assistant_output_proxy"}:
        labeling_method = "assistant_output_proxy"
    else:
        labeling_method = "mixed"

    source_in = trace.get("source", {})
    prompt_template = trace.get("prompt_template", {})
    budgets = trace.get("budgets", {})
    redaction = trace.get("redaction", {})

    fixture: dict[str, Any] = {
        "schema_version": "recorded_session_fixture.v2",
        "fixture_id": out_fixture_id,
        "source": {
            "product_version": source_in.get("product_version", "unknown"),
            "tenant_anon_id": source_in.get("tenant_anon_id"),
            "session_anon_id": source_in.get("session_anon_id"),
            "capture_date": source_in.get("capture_date"),
            "capture_timezone": source_in.get("capture_timezone"),
            "trace_id": trace_id,
            "trace_export_format": trace.get("trace_version"),
            "trace_sha256": f"sha256:{trace_sha}",
            "trace_turn_count": len(converted_turns),
            "notes": source_in.get("notes"),
        },
        "session_context": trace.get("session_context", {}),
        "turns": converted_turns,
        "ground_truth": {
            "total_turns": len(converted_turns),
            "complexity_tier": complexity_tier,
            "labeling_method": labeling_method,
            "requires_human_review": bool(any_proxy or any_auto_rubric),
            "notes": (
                "Converted from OpenClaw trace. Turn-level expected_output and rubrics should be human-reviewed before publish."
                if any_proxy or any_auto_rubric
                else "Converted from OpenClaw trace with explicit turn labels."
            ),
        },
        "held_fixed": {
            "prompt_template_hash": prompt_template.get("template_sha256"),
            "prompt_template_id": prompt_template.get("template_id"),
            "context_budget_tokens": int(budgets.get("context_budget_tokens", 0)),
            "correction_budget": int(budgets.get("correction_budget", 0)),
            "random_seed": budgets.get("random_seed"),
            "model_family": "openclaw-runtime",
        },
        "redaction": {
            "redacted": bool(redaction.get("redacted", False)),
            "strategy": redaction.get("strategy", "unspecified"),
            "pii_classes_removed": redaction.get("pii_classes_removed", []),
            "notes": redaction.get("notes", ""),
        },
        "conversion": {
            "converter": "scripts/convert_openclaw_trace_to_fixture.py",
            "converter_version": "0.2.0",
            "converted_at": _iso_now(),
            "input_trace": str(trace_path),
            "command": " ".join(sys.argv),
        },
    }

    # Remove null/empty optional fields from source and held_fixed.
    for section in ["source", "held_fixed", "redaction"]:
        obj = fixture.get(section)
        if isinstance(obj, dict):
            drop_keys = [k for k, v in obj.items() if v in (None, "")]
            for key in drop_keys:
                del obj[key]

    _write_json(output_path, fixture)
    return fixture


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert OpenClaw trace JSON into recorded-session fixture JSON.")
    parser.add_argument("--trace", required=True, help="Path to normalized OpenClaw trace JSON")
    parser.add_argument("--output", required=True, help="Output fixture path (.json)")
    parser.add_argument("--fixture-id", default=None, help="Override fixture_id (slugified)")
    parser.add_argument(
        "--complexity-tier",
        choices=["trivial", "simple", "moderate", "complex"],
        default="moderate",
        help="Fixture complexity tier",
    )
    parser.add_argument(
        "--strict-ground-truth",
        action="store_true",
        help="Require explicit expected_output and rubric.accept_criteria for every turn",
    )
    parser.add_argument(
        "--strip-doc-content",
        action="store_true",
        help="Replace document content with content_sha256 + excerpt to reduce sensitive text exposure",
    )
    args = parser.parse_args()

    trace_path = Path(args.trace)
    output_path = Path(args.output)

    if not trace_path.exists():
        print(f"Trace file not found: {trace_path}", file=sys.stderr)
        return 1

    try:
        fixture = convert_trace_to_fixture(
            trace_path=trace_path,
            output_path=output_path,
            fixture_id=args.fixture_id,
            complexity_tier=args.complexity_tier,
            strict_ground_truth=args.strict_ground_truth,
            strip_doc_content=args.strip_doc_content,
        )
    except ValueError as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1

    turns = fixture.get("turns", [])
    gt = fixture.get("ground_truth", {})
    source = fixture.get("source", {})
    print(f"Fixture written: {output_path}")
    print(f"  fixture_id:         {fixture.get('fixture_id')}")
    print(f"  trace_id:           {source.get('trace_id')}")
    print(f"  turns:              {len(turns)}")
    print(f"  labeling_method:    {gt.get('labeling_method')}")
    print(f"  requires_review:    {gt.get('requires_human_review')}")
    print("Next step:")
    print(f"  python scripts/validate_fixture.py {output_path} --check-trace-hash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
