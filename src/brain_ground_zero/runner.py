from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from brain_ground_zero.baselines import create_baseline
from brain_ground_zero.baselines.base import BaselineSpec, BudgetSpec
from brain_ground_zero.config import RunConfig, write_config_snapshot
from brain_ground_zero.families import create_family
from brain_ground_zero.families.base import FamilySpec, Step
from brain_ground_zero.models import Answer, Correction, Fact, Query


@dataclass
class MetricsBucket:
    total: int = 0
    correct: int = 0
    stale: int = 0
    false: int = 0
    unknown: int = 0
    context_used: int = 0
    traversal_cost: int = 0
    corrections_delivered: int = 0
    step_correct: Dict[int, int] = field(default_factory=dict)
    step_total: Dict[int, int] = field(default_factory=dict)


class MetricsTracker:
    def __init__(self, baselines: List[str]) -> None:
        self.data = {name: MetricsBucket() for name in baselines}

    def record(
        self,
        baseline: str,
        step: int,
        correct: bool,
        stale: bool,
        false: bool,
        unknown: bool,
        context_used: int,
        traversal_cost: int,
    ) -> None:
        bucket = self.data[baseline]
        bucket.total += 1
        bucket.correct += 1 if correct else 0
        bucket.stale += 1 if stale else 0
        bucket.false += 1 if false else 0
        bucket.unknown += 1 if unknown else 0
        bucket.context_used += context_used
        bucket.traversal_cost += traversal_cost
        bucket.step_total[step] = bucket.step_total.get(step, 0) + 1
        bucket.step_correct[step] = bucket.step_correct.get(step, 0) + (1 if correct else 0)

    def add_corrections(self, baseline: str, count: int) -> None:
        self.data[baseline].corrections_delivered += count

    def summary(self) -> Dict[str, Dict[str, float]]:
        out: Dict[str, Dict[str, float]] = {}
        for name, bucket in self.data.items():
            incorrect = bucket.total - bucket.correct
            stale_rate = bucket.stale / incorrect if incorrect else 0.0
            false_rate = bucket.false / incorrect if incorrect else 0.0
            accuracy = bucket.correct / bucket.total if bucket.total else 0.0
            learning_curve = []
            for step in sorted(bucket.step_total.keys()):
                total = bucket.step_total[step]
                correct = bucket.step_correct.get(step, 0)
                learning_curve.append({"step": step, "accuracy": correct / total if total else 0.0})
            out[name] = {
                "accuracy": accuracy,
                "stale_rate": stale_rate,
                "false_rate": false_rate,
                "unknown_rate": bucket.unknown / incorrect if incorrect else 0.0,
                "corrections_delivered": bucket.corrections_delivered,
                "context_used": bucket.context_used,
                "traversal_cost": bucket.traversal_cost,
                "total_queries": bucket.total,
                "learning_curve": learning_curve,
            }
        return out


def _parse_family_spec(family_cfg: Dict) -> FamilySpec:
    return FamilySpec(name=family_cfg["name"], params=family_cfg.get("params", {}))


def _parse_baseline_specs(baselines_cfg: Dict) -> List[BaselineSpec]:
    specs = []
    for entry in baselines_cfg.get("baselines", []):
        specs.append(
            BaselineSpec(
                name=entry["name"],
                kind=entry["kind"],
                capabilities=entry.get("capabilities", {}),
                params=entry.get("params", {}),
            )
        )
    return specs


def _build_budget(family_cfg: Dict) -> BudgetSpec:
    budgets = family_cfg.get("budgets", {})
    return BudgetSpec(
        context_budget=int(budgets.get("context_budget", 8)),
        teacher_budget=int(budgets.get("teacher_budget", 0)),
        teacher_delay=int(budgets.get("teacher_delay", 0)),
    )


def _shrink_steps(steps: List[Step]) -> List[Step]:
    out: List[Step] = []
    for step in steps[:5]:
        out.append(
            Step(
                step=step.step,
                updates=step.updates[:2],
                queries=step.queries[:5],
                answers=step.answers[:5],
                previous_relations=step.previous_relations[:5],
            )
        )
    return out


def run_benchmark(run_config: RunConfig, run_id: Optional[str] = None, smoke: bool = False) -> Path:
    family_cfg = run_config.family
    system_cfg = run_config.system or {}

    seed = int(family_cfg.get("seed", system_cfg.get("random_seed", 0)))
    family_spec = _parse_family_spec(family_cfg)
    family = create_family(family_spec, seed)

    world_state = family.build_world()
    steps = family.build_steps(world_state)
    if smoke:
        steps = _shrink_steps(steps)

    budget = _build_budget(family_cfg)
    baseline_specs = _parse_baseline_specs(run_config.baselines)

    if run_id is None:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        run_id = f"{family_spec.name}_{stamp}"

    output_dir = Path(system_cfg.get("output_dir", "runs"))
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    write_config_snapshot(run_dir, run_config)

    baselines = {}
    for idx, spec in enumerate(baseline_specs):
        baseline = create_baseline(spec, budget, seed + idx + 10)
        baseline.reset(world_state)
        baselines[spec.name] = baseline

    pending: Dict[str, List[Correction]] = {name: [] for name in baselines}
    teacher_remaining = {name: budget.teacher_budget for name in baselines}
    tracker = MetricsTracker(list(baselines.keys()))

    metrics_path = run_dir / "metrics.jsonl"
    with metrics_path.open("w", encoding="utf-8") as f:
        for step in steps:
            for name, baseline in baselines.items():
                deliveries = [c for c in pending[name] if c.deliver_at <= step.step]
                pending[name] = [c for c in pending[name] if c.deliver_at > step.step]
                if deliveries:
                    tracker.add_corrections(name, len(deliveries))
                baseline.observe(step.step, step.updates, [c.fact for c in deliveries])

            for idx, query in enumerate(step.queries):
                truth = step.answers[idx]
                prev = step.previous_relations[idx]
                for name, baseline in baselines.items():
                    answer = baseline.answer(step.step, query)
                    if answer.context_used > budget.context_budget:
                        answer.context_used = budget.context_budget
                    correct = answer.relation == truth
                    stale = (not correct) and (prev is not None) and (answer.relation == prev)
                    false = (not correct) and (answer.relation not in (None, prev))
                    unknown = (not correct) and (answer.relation is None)

                    tracker.record(
                        name,
                        step.step,
                        correct,
                        stale,
                        false,
                        unknown,
                        answer.context_used,
                        answer.traversal_cost,
                    )

                    baseline.on_feedback(step.step, query, correct, truth, answer)

                    if (
                        (not correct)
                        and baseline.supports_teacher()
                        and teacher_remaining[name] > 0
                    ):
                        teacher_remaining[name] -= 1
                        fact = Fact(
                            subject=query.subject,
                            object=query.object,
                            relation=truth,
                            time=step.step,
                            source="teacher",
                        )
                        pending[name].append(
                            Correction(fact=fact, deliver_at=step.step + budget.teacher_delay)
                        )

                    record = {
                        "baseline": name,
                        "step": step.step,
                        "subject": query.subject,
                        "object": query.object,
                        "truth": truth,
                        "answer": answer.relation,
                        "correct": correct,
                        "stale": stale,
                        "false": false,
                        "unknown": unknown,
                        "context_used": answer.context_used,
                        "traversal_cost": answer.traversal_cost,
                        "route_source": answer.source,
                    }
                    f.write(json.dumps(record) + "\n")

    summary = tracker.summary()
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    latest = output_dir / "latest"
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(run_dir, target_is_directory=True)
    except OSError:
        pass

    return run_dir


def run_multi_seed(
    run_config: RunConfig,
    seeds: List[int],
    run_id: Optional[str] = None,
    smoke: bool = False,
) -> Path:
    """Run the benchmark across multiple seeds and aggregate results."""
    family_cfg = run_config.family
    system_cfg = run_config.system or {}

    if run_id is None:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        run_id = f"{family_cfg.get('name', 'bench')}_multiseed_{stamp}"

    output_dir = Path(system_cfg.get("output_dir", "runs"))
    agg_dir = output_dir / run_id
    agg_dir.mkdir(parents=True, exist_ok=True)
    (agg_dir / "artifacts").mkdir(exist_ok=True)
    write_config_snapshot(agg_dir, run_config)

    per_seed_summaries: List[Dict[str, Dict[str, float]]] = []

    for seed in seeds:
        seed_config = RunConfig(
            family={**family_cfg, "seed": seed},
            baselines=run_config.baselines,
            system=run_config.system,
        )
        sub_id = f"{run_id}/seed_{seed}"
        sub_dir = run_benchmark(seed_config, run_id=sub_id, smoke=smoke)
        summary = json.loads((sub_dir / "summary.json").read_text(encoding="utf-8"))
        per_seed_summaries.append(summary)

    aggregated = _aggregate_summaries(per_seed_summaries)
    (agg_dir / "summary.json").write_text(
        json.dumps(aggregated, indent=2, sort_keys=True), encoding="utf-8"
    )
    (agg_dir / "per_seed_summaries.json").write_text(
        json.dumps(per_seed_summaries, indent=2, sort_keys=True), encoding="utf-8"
    )
    (agg_dir / "seeds.json").write_text(json.dumps(seeds), encoding="utf-8")

    latest = output_dir / "latest"
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(agg_dir, target_is_directory=True)
    except OSError:
        pass

    return agg_dir


def _aggregate_summaries(
    summaries: List[Dict[str, Dict[str, float]]],
) -> Dict[str, Dict[str, float]]:
    """Compute mean and std across seeds for each baseline metric."""
    import math

    baselines = list(summaries[0].keys())
    scalar_keys = [
        "accuracy", "stale_rate", "false_rate", "unknown_rate",
        "corrections_delivered", "context_used", "traversal_cost", "total_queries",
    ]
    out: Dict[str, Dict[str, float]] = {}
    for name in baselines:
        agg: Dict[str, float] = {}
        for key in scalar_keys:
            vals = [s[name][key] for s in summaries if name in s]
            mean = sum(vals) / len(vals)
            std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 0.0
            agg[key] = round(mean, 6)
            agg[f"{key}_std"] = round(std, 6)
        agg["num_seeds"] = len(summaries)

        # Aggregate learning curves by step
        curves: Dict[int, List[float]] = {}
        for s in summaries:
            if name not in s:
                continue
            for point in s[name].get("learning_curve", []):
                step = point["step"]
                curves.setdefault(step, []).append(point["accuracy"])
        agg_curve = []
        for step in sorted(curves.keys()):
            vals = curves[step]
            mean = sum(vals) / len(vals)
            std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 0.0
            agg_curve.append({"step": step, "accuracy": round(mean, 6), "accuracy_std": round(std, 6)})
        agg["learning_curve"] = agg_curve
        out[name] = agg
    return out
