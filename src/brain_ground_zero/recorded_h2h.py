"""Recorded head-to-head: generate fixtures and run baselines with full trace logging."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from brain_ground_zero import reporting
from brain_ground_zero.baselines import create_baseline
from brain_ground_zero.baselines.base import BaselineSpec, BudgetSpec
from brain_ground_zero.config import RunConfig, write_config_snapshot
from brain_ground_zero.families import create_family
from brain_ground_zero.families.base import FamilySpec, Step
from brain_ground_zero.models import Correction, Fact, Query
from brain_ground_zero.runner import MetricsTracker, _aggregate_summaries


# ---------------------------------------------------------------------------
# Fixture generation
# ---------------------------------------------------------------------------


def generate_fixture(
    family_path: str | Path,
    seed: int,
    output_path: str | Path,
) -> Path:
    """Generate a deterministic fixture file from a family config.

    The fixture freezes every step, update, query, answer, and budget so that
    multiple baselines can be run against identical inputs.
    """
    family_cfg = _load_yaml(family_path)
    family_spec = FamilySpec(name=family_cfg["name"], params=family_cfg.get("params", {}))
    family = create_family(family_spec, seed)

    world_state = family.build_world()
    steps = family.build_steps(world_state)

    budgets = family_cfg.get("budgets", {})
    fixture: Dict[str, Any] = {
        "format_version": "1",
        "family": family_cfg["name"],
        "generator_seed": seed,
        "generator_params": family_cfg.get("params", {}),
        "budgets": {
            "context_budget": int(budgets.get("context_budget", 8)),
            "teacher_budget": int(budgets.get("teacher_budget", 0)),
            "teacher_delay": int(budgets.get("teacher_delay", 0)),
        },
        "steps": [],
    }

    # Serialize initial world as step 0
    init_updates = []
    for key, fact in sorted(world_state.items()):
        init_updates.append({
            "kind": "set_relation",
            "subject": fact.subject,
            "relation": fact.relation,
            "object": fact.object,
        })

    fixture["steps"].append({
        "step": 0,
        "world_updates": init_updates,
        "queries": [],
        "corrections": [],
    })

    # Serialize each generated step
    for step in steps:
        step_entry: Dict[str, Any] = {
            "step": step.step,
            "world_updates": [],
            "queries": [],
            "corrections": [],
        }
        for fact in step.updates:
            step_entry["world_updates"].append({
                "kind": "set_relation",
                "subject": fact.subject,
                "relation": fact.relation,
                "object": fact.object,
            })
        for idx, query in enumerate(step.queries):
            step_entry["queries"].append({
                "query_id": f"q_{step.step}_{idx}",
                "subject": query.subject,
                "object": query.object,
                "expected": step.answers[idx],
                "previous_relation": step.previous_relations[idx],
            })
        fixture["steps"].append(step_entry)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        yaml.dump(fixture, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Fixture written: {out}  ({_count_queries(fixture)} queries across {len(fixture['steps'])} steps)")
    return out


def _count_queries(fixture: Dict) -> int:
    return sum(len(s.get("queries", [])) for s in fixture.get("steps", []))


# ---------------------------------------------------------------------------
# Recorded head-to-head run
# ---------------------------------------------------------------------------


def run_recorded_h2h(
    fixture_path: str | Path,
    baselines_path: str | Path,
    output_dir: str | Path,
    status: str = "draft",
) -> Path:
    """Run all baselines against a fixed fixture, producing traces and scoring."""
    fixture_path = Path(fixture_path)
    output_dir = Path(output_dir)

    fixture = _load_yaml(fixture_path)
    baselines_cfg = _load_yaml(baselines_path)

    # Parse fixture into internal structures
    budget_cfg = fixture.get("budgets", {})
    budget = BudgetSpec(
        context_budget=int(budget_cfg.get("context_budget", 8)),
        teacher_budget=int(budget_cfg.get("teacher_budget", 0)),
        teacher_delay=int(budget_cfg.get("teacher_delay", 0)),
    )
    seed = int(fixture.get("generator_seed", 42))

    # Reconstruct world state from step 0 and steps from step 1+
    world_state, steps, query_map = _parse_fixture(fixture)

    # Parse baseline specs
    baseline_specs = _parse_baseline_specs(baselines_cfg)

    # Create output dirs
    traces_dir = output_dir / "traces"
    scoring_dir = output_dir / "scoring"
    verification_dir = output_dir / "verification"
    for d in [traces_dir, scoring_dir, verification_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Create baselines
    baselines = {}
    for idx, spec in enumerate(baseline_specs):
        baseline = create_baseline(spec, budget, seed + idx + 10)
        baseline.reset(world_state)
        baselines[spec.name] = baseline

    # Run and collect traces
    pending: Dict[str, List[Correction]] = {name: [] for name in baselines}
    teacher_remaining = {name: budget.teacher_budget for name in baselines}
    tracker = MetricsTracker(list(baselines.keys()))

    # Per-baseline trace files
    trace_files = {}
    for name in baselines:
        trace_files[name] = (traces_dir / f"{name}.jsonl").open("w", encoding="utf-8")

    # Per-query verdicts collector
    all_verdicts: List[Dict[str, Any]] = []
    metrics_file = (output_dir / "metrics.jsonl").open("w", encoding="utf-8")

    try:
        for step in steps:
            for name, baseline in baselines.items():
                deliveries = [c for c in pending[name] if c.deliver_at <= step.step]
                pending[name] = [c for c in pending[name] if c.deliver_at > step.step]
                if deliveries:
                    tracker.add_corrections(name, len(deliveries))
                    for c in deliveries:
                        trace_files[name].write(json.dumps({
                            "event": "correction_received",
                            "step": step.step,
                            "correction_subject": c.fact.subject,
                            "correction_object": c.fact.object,
                            "correction_relation": c.fact.relation,
                        }) + "\n")
                baseline.observe(step.step, step.updates, [c.fact for c in deliveries])

            for idx, query in enumerate(step.queries):
                truth = step.answers[idx]
                prev = step.previous_relations[idx]
                query_id = query_map.get((step.step, idx), f"q_{step.step}_{idx}")

                for name, baseline in baselines.items():
                    answer = baseline.answer(step.step, query)
                    if answer.context_used > budget.context_budget:
                        answer.context_used = budget.context_budget

                    correct = answer.relation == truth
                    stale = (not correct) and (prev is not None) and (answer.relation == prev)
                    false_ans = (not correct) and (answer.relation not in (None, prev))
                    unknown = (not correct) and (answer.relation is None)

                    verdict = "correct" if correct else ("stale" if stale else ("unknown" if unknown else "incorrect"))

                    tracker.record(
                        name,
                        step.step,
                        correct,
                        stale,
                        false_ans,
                        unknown,
                        answer.context_used,
                        answer.traversal_cost,
                        True,
                    )
                    baseline.on_feedback(step.step, query, correct, truth, answer)

                    # Teacher correction
                    if not correct and baseline.supports_teacher() and teacher_remaining[name] > 0:
                        teacher_remaining[name] -= 1
                        fact = Fact(subject=query.subject, object=query.object,
                                    relation=truth, time=step.step, source="teacher")
                        pending[name].append(Correction(fact=fact, deliver_at=step.step + budget.teacher_delay))

                    # Write trace event
                    trace_event = {
                        "event": "query_response",
                        "step": step.step,
                        "query_id": query_id,
                        "answer": answer.relation,
                        "expected": truth,
                        "verdict": verdict,
                        "context_used": answer.context_used,
                        "route_source": answer.source,
                        "traversal_cost": answer.traversal_cost,
                    }
                    trace_files[name].write(json.dumps(trace_event) + "\n")

                    # Collect verdict
                    all_verdicts.append({
                        "query_id": query_id,
                        "step": step.step,
                        "baseline": name,
                        "subject": query.subject,
                        "object": query.object,
                        "answer": answer.relation,
                        "expected": truth,
                        "verdict": verdict,
                    })
                    metrics_file.write(
                        json.dumps(
                            {
                                "baseline": name,
                                "step": step.step,
                                "subject": query.subject,
                                "object": query.object,
                                "truth": truth,
                                "answer": answer.relation,
                                "correct": correct,
                                "stale": stale,
                                "false": false_ans,
                                "unknown": unknown,
                                "context_used": answer.context_used,
                                "traversal_cost": answer.traversal_cost,
                                "route_source": answer.source,
                                "feedback_available": True,
                            }
                        )
                        + "\n"
                    )
    finally:
        for f in trace_files.values():
            f.close()
        metrics_file.close()

    # -- Scoring outputs --
    summary = tracker.summary()
    _write_scoring(scoring_dir, summary, all_verdicts)

    # -- Verification outputs --
    _write_verification(fixture_path, traces_dir, verification_dir, scoring_dir, all_verdicts, fixture)

    # -- Metadata --
    _write_metadata(output_dir, fixture_path, fixture, baseline_specs, status)

    # -- Bundle README --
    _write_bundle_readme(output_dir, fixture, summary, status)

    # -- Summary JSON (for compatibility) --
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    total_queries = _count_queries(fixture)
    print(f"Recorded head-to-head complete: {output_dir}")
    print(f"  Baselines: {len(baselines)}")
    print(f"  Total queries: {total_queries}")
    for name, metrics in summary.items():
        print(f"  {name}: accuracy={metrics['accuracy']:.4f}")

    return output_dir


def run_recorded_h2h_multiseed(
    family_path: str | Path,
    baselines_path: str | Path,
    seeds: List[int],
    run_dir: str | Path,
    status: str = "draft",
) -> Path:
    """Run recorded head-to-head across multiple seeds and aggregate report artifacts."""
    if not seeds:
        raise ValueError("At least one seed is required")

    family_path = Path(family_path)
    baselines_path = Path(baselines_path)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)

    run_config = RunConfig(
        family=_load_yaml(family_path),
        baselines=_load_yaml(baselines_path),
        system={
            "mode": "recorded_h2h_multiseed",
            "status": status,
            "seeds": seeds,
        },
    )
    write_config_snapshot(run_dir, run_config)

    per_seed_summaries: List[Dict[str, Dict[str, float]]] = []
    for seed in seeds:
        seed_dir = run_dir / f"seed_{seed}"
        fixture_path = seed_dir / "fixture.yaml"
        print(f"[seed {seed}] generate fixture")
        generate_fixture(family_path, seed, fixture_path)
        print(f"[seed {seed}] replay baselines")
        run_recorded_h2h(
            fixture_path=fixture_path,
            baselines_path=baselines_path,
            output_dir=seed_dir,
            status=status,
        )
        summary = json.loads((seed_dir / "summary.json").read_text(encoding="utf-8"))
        per_seed_summaries.append(summary)

    aggregated = _aggregate_summaries(per_seed_summaries)
    (run_dir / "summary.json").write_text(
        json.dumps(aggregated, indent=2, sort_keys=True), encoding="utf-8"
    )
    (run_dir / "per_seed_summaries.json").write_text(
        json.dumps(per_seed_summaries, indent=2, sort_keys=True), encoding="utf-8"
    )
    (run_dir / "seeds.json").write_text(json.dumps(seeds), encoding="utf-8")

    _write_seed_bundle_index(run_dir, seeds, per_seed_summaries)
    reporting.generate_report(run_dir)

    print(f"Recorded multi-seed head-to-head complete: {run_dir}")
    print(f"  Seeds: {len(seeds)} ({', '.join(str(seed) for seed in seeds)})")
    return run_dir


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _parse_fixture(fixture: Dict) -> tuple[Dict[str, Fact], List[Step], Dict[tuple, str]]:
    """Parse fixture YAML into world_state, steps, and query_id map."""
    world_state: Dict[str, Fact] = {}
    steps: List[Step] = []
    query_map: Dict[tuple, str] = {}  # (step, idx) -> query_id

    for step_entry in fixture.get("steps", []):
        step_num = step_entry["step"]

        # Build facts from updates
        updates: List[Fact] = []
        for u in step_entry.get("world_updates", []):
            fact = Fact(
                subject=u["subject"],
                object=u["object"],
                relation=u["relation"],
                time=step_num,
                source="init" if step_num == 0 else "update",
            )
            key = f"{fact.subject}::{fact.object}"
            if step_num == 0:
                world_state[key] = fact
            else:
                updates.append(fact)

        if step_num == 0:
            continue

        # Build queries
        queries: List[Query] = []
        answers: List[str] = []
        previous_relations: List[Optional[str]] = []
        for idx, q in enumerate(step_entry.get("queries", [])):
            queries.append(Query(subject=q["subject"], object=q["object"]))
            answers.append(q["expected"])
            previous_relations.append(q.get("previous_relation"))
            query_map[(step_num, idx)] = q.get("query_id", f"q_{step_num}_{idx}")

        steps.append(Step(
            step=step_num,
            updates=updates,
            queries=queries,
            answers=answers,
            previous_relations=previous_relations,
        ))

    return world_state, steps, query_map


def _parse_baseline_specs(baselines_cfg: Dict) -> List[BaselineSpec]:
    specs = []
    for entry in baselines_cfg.get("baselines", []):
        specs.append(BaselineSpec(
            name=entry["name"],
            kind=entry["kind"],
            capabilities=entry.get("capabilities", {}),
            params=entry.get("params", {}),
        ))
    return specs


def _best_rag_name(summary: Dict[str, Dict[str, float]]) -> str:
    rag_names = [name for name in summary if name.startswith("vector_rag")]
    if not rag_names:
        raise ValueError("No vector_rag baseline found in summary")
    return max(rag_names, key=lambda name: float(summary[name].get("accuracy", 0.0)))


def _write_seed_bundle_index(
    run_dir: Path,
    seeds: List[int],
    per_seed_summaries: List[Dict[str, Dict[str, float]]],
) -> None:
    rows: List[Dict[str, Any]] = []
    for seed, summary in zip(seeds, per_seed_summaries):
        best_rag = _best_rag_name(summary)
        full_acc = float(summary.get("full_brain", {}).get("accuracy", 0.0))
        rag_acc = float(summary.get(best_rag, {}).get("accuracy", 0.0))
        rows.append(
            {
                "seed": seed,
                "bundle_dir": f"seed_{seed}",
                "full_brain_accuracy_pct": round(full_acc * 100.0, 4),
                "best_rag": best_rag,
                "best_rag_accuracy_pct": round(rag_acc * 100.0, 4),
                "margin_vs_best_rag_pp": round((full_acc - rag_acc) * 100.0, 4),
                "full_brain_h2h_vs_best_rag": "1-0-0" if full_acc > rag_acc else ("0-1-0" if full_acc < rag_acc else "0-0-1"),
            }
        )

    fieldnames = list(rows[0].keys()) if rows else []
    if not fieldnames:
        return

    with (run_dir / "seed_bundle_index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with (run_dir / "seed_bundle_index.md").open("w", encoding="utf-8") as f:
        f.write("# Seed Bundle Index\n\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(row.get(name, "")) for name in fieldnames) + " |\n")


def _write_bundle_readme(
    output_dir: Path,
    fixture: Dict[str, Any],
    summary: Dict[str, Dict[str, float]],
    status: str,
) -> None:
    best_rag = _best_rag_name(summary)
    full = summary.get("full_brain", {})
    rag = summary.get(best_rag, {})
    steps = len(fixture.get("steps", []))
    queries = _count_queries(fixture)

    def pct(value: float) -> str:
        return f"{value * 100.0:.2f}%"

    lines = [
        f"# Recorded Head-to-Head Bundle: {output_dir.name}",
        "",
        f"Status: {status}",
        f"Family: {fixture.get('family', 'unknown')}",
        f"Generator seed: {fixture.get('generator_seed', 'n/a')}",
        f"Queries: {queries}",
        f"Steps: {steps}",
        "",
        "## Headline",
        "",
        f"- full_brain: {pct(float(full.get('accuracy', 0.0)))}",
        f"- best RAG ({best_rag}): {pct(float(rag.get('accuracy', 0.0)))}",
        f"- margin vs best RAG: {(float(full.get('accuracy', 0.0)) - float(rag.get('accuracy', 0.0))) * 100:+.2f} pp",
        "",
        "## Files",
        "",
        "- `fixture.yaml` -- deterministic replay fixture",
        "- `metadata.yaml` -- run metadata and baseline configuration snapshot",
        "- `metrics.jsonl` -- normalized per-query event stream for reporting",
        "- `traces/` -- raw per-baseline JSONL traces",
        "- `scoring/` -- summary/pairwise/per-query scoring tables",
        "- `verification/` -- fixture/trace hashes and reproducibility check",
    ]

    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _write_scoring(scoring_dir: Path, summary: Dict, all_verdicts: List[Dict]) -> None:
    """Write scoring tables and per-query verdicts."""
    baselines = list(summary.keys())

    # summary_table.csv / .md
    fieldnames = ["baseline", "accuracy", "stale_rate", "false_rate", "unknown_rate",
                  "corrections_delivered", "context_used", "traversal_cost", "total_queries"]
    rows = []
    for name in baselines:
        m = summary[name]
        rows.append({k: m.get(k, "") for k in fieldnames if k != "baseline"} | {"baseline": name})

    with (scoring_dir / "summary_table.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    with (scoring_dir / "summary_table.md").open("w", encoding="utf-8") as f:
        f.write("# Summary Table\n\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            cells = []
            for k in fieldnames:
                v = row.get(k, "")
                cells.append(f"{v:.4f}" if isinstance(v, float) else str(v))
            f.write("| " + " | ".join(cells) + " |\n")

    # pairwise_accuracy_delta.csv / .md
    delta_fields = ["baseline"] + baselines
    delta_rows = []
    for b1 in baselines:
        row = {"baseline": b1}
        for b2 in baselines:
            row[b2] = round(summary[b1]["accuracy"] - summary[b2]["accuracy"], 4)
        delta_rows.append(row)

    with (scoring_dir / "pairwise_accuracy_delta.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=delta_fields)
        w.writeheader()
        w.writerows(delta_rows)

    with (scoring_dir / "pairwise_accuracy_delta.md").open("w", encoding="utf-8") as f:
        f.write("# Pairwise Accuracy Delta (row - column)\n\n")
        f.write("| " + " | ".join(delta_fields) + " |\n")
        f.write("|" + "|".join(["---"] * len(delta_fields)) + "|\n")
        for row in delta_rows:
            cells = []
            for k in delta_fields:
                v = row[k]
                if isinstance(v, float):
                    cells.append(f"{v:+.4f}" if v != 0 else "0.0000")
                else:
                    cells.append(str(v))
            f.write("| " + " | ".join(cells) + " |\n")

    # per_query_verdicts.csv
    verdict_fields = ["query_id", "step", "baseline", "subject", "object", "answer", "expected", "verdict"]
    with (scoring_dir / "per_query_verdicts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=verdict_fields)
        w.writeheader()
        for v in all_verdicts:
            w.writerow({k: v.get(k, "") for k in verdict_fields})


def _write_verification(
    fixture_path: Path,
    traces_dir: Path,
    verification_dir: Path,
    scoring_dir: Path,
    all_verdicts: List[Dict],
    fixture: Dict,
) -> None:
    """Write verification hashes and reproducibility note."""
    # fixture_hash.sha256
    fixture_hash = _sha256(fixture_path)
    (verification_dir / "fixture_hash.sha256").write_text(
        f"{fixture_hash}  fixture.yaml\n", encoding="utf-8"
    )

    # trace_hashes.sha256
    trace_lines = []
    for trace_file in sorted(traces_dir.glob("*.jsonl")):
        h = _sha256(trace_file)
        trace_lines.append(f"{h}  {trace_file.name}")
    (verification_dir / "trace_hashes.sha256").write_text(
        "\n".join(trace_lines) + "\n", encoding="utf-8"
    )

    # scoring_reproducibility.txt -- verify trace-based rescoring matches
    rescore = _rescore_from_traces(traces_dir)
    original = _score_from_verdicts(all_verdicts)

    lines = [
        "Scoring Reproducibility Check",
        "=" * 40,
        f"Date: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
    ]

    match = True
    for baseline in sorted(set(list(rescore.keys()) + list(original.keys()))):
        r = rescore.get(baseline, {})
        o = original.get(baseline, {})
        bl_match = (r.get("correct", 0) == o.get("correct", 0) and
                    r.get("total", 0) == o.get("total", 0))
        status = "MATCH" if bl_match else "MISMATCH"
        if not bl_match:
            match = False
        lines.append(f"{baseline}: {status}  (traces: {r.get('correct',0)}/{r.get('total',0)}, "
                     f"original: {o.get('correct',0)}/{o.get('total',0)})")

    lines.append("")
    lines.append(f"Overall: {'PASS' if match else 'FAIL'}")

    # Query count check
    fixture_query_count = _count_queries(fixture)
    trace_query_count = sum(v.get("total", 0) for v in rescore.values())
    expected_total = fixture_query_count * len(rescore)
    lines.append(f"Fixture queries: {fixture_query_count}")
    lines.append(f"Trace query_response events (all baselines): {trace_query_count}")
    lines.append(f"Expected (queries x baselines): {expected_total}")
    count_match = trace_query_count == expected_total
    lines.append(f"Completeness: {'PASS' if count_match else 'FAIL'}")

    (verification_dir / "scoring_reproducibility.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _rescore_from_traces(traces_dir: Path) -> Dict[str, Dict[str, int]]:
    """Re-derive accuracy from trace JSONL files."""
    result: Dict[str, Dict[str, int]] = {}
    for trace_file in sorted(traces_dir.glob("*.jsonl")):
        baseline = trace_file.stem
        total = 0
        correct = 0
        for line in trace_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event") == "query_response":
                total += 1
                if event.get("verdict") == "correct":
                    correct += 1
        result[baseline] = {"total": total, "correct": correct}
    return result


def _score_from_verdicts(verdicts: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Derive accuracy from in-memory verdict list."""
    result: Dict[str, Dict[str, int]] = {}
    for v in verdicts:
        bl = v["baseline"]
        if bl not in result:
            result[bl] = {"total": 0, "correct": 0}
        result[bl]["total"] += 1
        if v["verdict"] == "correct":
            result[bl]["correct"] += 1
    return result


def _write_metadata(
    output_dir: Path,
    fixture_path: Path,
    fixture: Dict,
    baseline_specs: List[BaselineSpec],
    status: str,
) -> None:
    """Write metadata.yaml with run details."""
    git_sha = _get_git_sha()
    fixture_hash = _sha256(fixture_path)

    meta = {
        "format_version": "1",
        "status": status,
        "bundle_id": output_dir.name,
        "run_date": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_sha": git_sha,
        "harness_version": "0.1.0",
        "family": fixture.get("family", "unknown"),
        "fixture_file": "fixture.yaml",
        "fixture_sha256": fixture_hash,
        "generator_seed": fixture.get("generator_seed"),
        "generator_params": fixture.get("generator_params"),
        "budgets": fixture.get("budgets"),
        "baselines_run": [
            {
                "name": spec.name,
                "kind": spec.kind,
                "capabilities": spec.capabilities,
                "params": spec.params,
            }
            for spec in baseline_specs
        ],
    }

    with (output_dir / "metadata.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _get_git_sha() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None
