from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt


def _ordered_baselines(summary: Dict[str, Dict[str, float]]) -> List[str]:
    def sort_key(name: str) -> Tuple[int, float, str]:
        accuracy = float(summary.get(name, {}).get("accuracy", 0.0))
        if name == "oracle":
            return (0, 0.0, name)
        if name == "full_brain":
            return (1, -accuracy, name)
        return (2, -accuracy, name)

    return sorted(summary.keys(), key=sort_key)


def _is_rag_baseline(name: str) -> bool:
    return name.startswith("vector_rag")


def _best_rag_baseline(summary: Dict[str, Dict[str, float]]) -> Optional[str]:
    rag_candidates = [name for name in summary if _is_rag_baseline(name)]
    if not rag_candidates:
        return None
    return max(rag_candidates, key=lambda name: float(summary[name].get("accuracy", 0.0)))


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _format_md_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _write_table(
    csv_path: Path,
    md_path: Path,
    fieldnames: List[str],
    rows: List[Dict[str, object]],
    title: Optional[str] = None,
    preamble: Optional[str] = None,
) -> None:
    if not rows:
        return

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with md_path.open("w", encoding="utf-8") as f:
        if title:
            f.write(f"# {title}\n\n")
        if preamble:
            f.write(f"{preamble}\n\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(_format_md_value(row.get(k, "")) for k in fieldnames) + " |\n")


def _write_summary_table(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    rows: List[Dict[str, object]] = []
    has_std = any("accuracy_std" in m for m in summary.values())
    baselines = _ordered_baselines(summary)
    for baseline in baselines:
        metrics = summary[baseline]
        row: Dict[str, object] = {"baseline": baseline}
        for key in [
            "accuracy",
            "stale_rate",
            "false_rate",
            "unknown_rate",
            "corrections_delivered",
            "feedback_events",
            "feedback_rate",
            "context_used",
            "traversal_cost",
            "total_queries",
        ]:
            row[key] = metrics.get(key, "")
            if has_std and f"{key}_std" in metrics:
                row[f"{key}_std"] = metrics[f"{key}_std"]
        if has_std and "num_seeds" in metrics:
            row["num_seeds"] = metrics["num_seeds"]
        rows.append(row)

    fieldnames = list(rows[0].keys())
    _write_table(
        artifacts_dir / "summary_table.csv",
        artifacts_dir / "summary_table.md",
        fieldnames,
        rows,
    )


def _write_pairwise_deltas(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    baselines = _ordered_baselines(summary)
    if len(baselines) < 2:
        return

    delta_rows: List[Dict[str, object]] = []
    for b1 in baselines:
        row: Dict[str, object] = {"baseline": b1}
        for b2 in baselines:
            acc1 = float(summary[b1].get("accuracy", 0.0))
            acc2 = float(summary[b2].get("accuracy", 0.0))
            row[b2] = round(acc1 - acc2, 6)
        delta_rows.append(row)

    fieldnames = ["baseline"] + baselines
    _write_table(
        artifacts_dir / "pairwise_accuracy_delta.csv",
        artifacts_dir / "pairwise_accuracy_delta.md",
        fieldnames,
        delta_rows,
        title="Pairwise Accuracy Delta (row - column)",
    )


def _write_win_rate_table(
    artifacts_dir: Path,
    summary: Dict[str, Dict[str, float]],
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]] = None,
) -> None:
    if per_seed_summaries is None or len(per_seed_summaries) < 2:
        return

    baselines = _ordered_baselines(summary)
    num_seeds = len(per_seed_summaries)
    win_matrix: Dict[str, Dict[str, int]] = {b: {b2: 0 for b2 in baselines} for b in baselines}
    tie_matrix: Dict[str, Dict[str, int]] = {b: {b2: 0 for b2 in baselines} for b in baselines}

    for seed_summary in per_seed_summaries:
        for b1 in baselines:
            for b2 in baselines:
                if b1 == b2:
                    continue
                a1 = float(seed_summary.get(b1, {}).get("accuracy", 0.0))
                a2 = float(seed_summary.get(b2, {}).get("accuracy", 0.0))
                if a1 > a2:
                    win_matrix[b1][b2] += 1
                elif a1 == a2:
                    tie_matrix[b1][b2] += 1

    rows: List[Dict[str, object]] = []
    for b1 in baselines:
        row: Dict[str, object] = {"baseline": b1}
        for b2 in baselines:
            if b1 == b2:
                row[b2] = "-"
            else:
                wins = win_matrix[b1][b2]
                ties = tie_matrix[b1][b2]
                row[b2] = f"{wins}/{num_seeds}" if ties == 0 else f"{wins}/{num_seeds} (tie {ties})"
        rows.append(row)

    fieldnames = ["baseline"] + baselines
    _write_table(
        artifacts_dir / "win_rate_matrix.csv",
        artifacts_dir / "win_rate_matrix.md",
        fieldnames,
        rows,
        title=f"Win-Rate Matrix ({num_seeds} seeds)",
        preamble="Cell = number of seeds where row baseline beats column baseline on accuracy.",
    )


def _seed_labels(run_dir: Path, per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]]) -> List[str]:
    if not per_seed_summaries:
        return []
    seeds_path = run_dir / "seeds.json"
    if seeds_path.exists():
        try:
            loaded = json.loads(seeds_path.read_text(encoding="utf-8"))
            labels = [str(seed) for seed in loaded]
            if len(labels) == len(per_seed_summaries):
                return labels
        except json.JSONDecodeError:
            pass
    return [str(i + 1) for i in range(len(per_seed_summaries))]


def _write_per_seed_breakdown(
    artifacts_dir: Path,
    run_dir: Path,
    summary: Dict[str, Dict[str, float]],
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]],
) -> None:
    if not per_seed_summaries:
        return

    baselines = _ordered_baselines(summary)
    seed_labels = _seed_labels(run_dir, per_seed_summaries)
    if not seed_labels:
        return

    long_rows: List[Dict[str, object]] = []
    for idx, seed_summary in enumerate(per_seed_summaries):
        seed_label = seed_labels[idx]
        for baseline in baselines:
            metrics = seed_summary.get(baseline, {})
            total_queries = float(metrics.get("total_queries", 0.0))
            context_used = float(metrics.get("context_used", 0.0))
            traversal_cost = float(metrics.get("traversal_cost", 0.0))
            corrections = float(metrics.get("corrections_delivered", 0.0))
            long_rows.append(
                {
                    "seed": seed_label,
                    "baseline": baseline,
                    "accuracy": metrics.get("accuracy", ""),
                    "stale_rate": metrics.get("stale_rate", ""),
                    "false_rate": metrics.get("false_rate", ""),
                    "unknown_rate": metrics.get("unknown_rate", ""),
                    "context_per_query": _safe_divide(context_used, total_queries),
                    "traversal_per_query": _safe_divide(traversal_cost, total_queries),
                    "corrections_per_1k_queries": _safe_divide(corrections * 1000.0, total_queries),
                }
            )

    _write_table(
        artifacts_dir / "per_seed_breakdown.csv",
        artifacts_dir / "per_seed_breakdown.md",
        [
            "seed",
            "baseline",
            "accuracy",
            "stale_rate",
            "false_rate",
            "unknown_rate",
            "context_per_query",
            "traversal_per_query",
            "corrections_per_1k_queries",
        ],
        long_rows,
        title="Per-Seed Breakdown",
    )

    matrix_rows: List[Dict[str, object]] = []
    for baseline in baselines:
        row: Dict[str, object] = {"baseline": baseline}
        values: List[float] = []
        for idx, seed_label in enumerate(seed_labels):
            metrics = per_seed_summaries[idx].get(baseline, {})
            value = float(metrics.get("accuracy", 0.0))
            row[f"seed_{seed_label}"] = value
            values.append(value)
        mean = sum(values) / len(values) if values else 0.0
        var = sum((v - mean) ** 2 for v in values) / len(values) if values else 0.0
        row["mean_accuracy"] = mean
        row["std_accuracy"] = var**0.5
        matrix_rows.append(row)

    fieldnames = ["baseline"] + [f"seed_{seed}" for seed in seed_labels] + ["mean_accuracy", "std_accuracy"]
    _write_table(
        artifacts_dir / "per_seed_accuracy_matrix.csv",
        artifacts_dir / "per_seed_accuracy_matrix.md",
        fieldnames,
        matrix_rows,
        title="Per-Seed Accuracy Matrix",
    )


def _head_to_head_record(
    baseline: str,
    target: str,
    per_seed_summaries: List[Dict[str, Dict[str, float]]],
) -> Tuple[int, int, int]:
    wins = 0
    losses = 0
    ties = 0
    for seed_summary in per_seed_summaries:
        a1 = float(seed_summary.get(baseline, {}).get("accuracy", 0.0))
        a2 = float(seed_summary.get(target, {}).get("accuracy", 0.0))
        if a1 > a2:
            wins += 1
        elif a1 < a2:
            losses += 1
        else:
            ties += 1
    return wins, losses, ties


def _write_leaderboard(
    artifacts_dir: Path,
    summary: Dict[str, Dict[str, float]],
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]],
) -> None:
    ranked = sorted(
        summary.items(),
        key=lambda item: float(item[1].get("accuracy", 0.0)),
        reverse=True,
    )
    has_std = any("accuracy_std" in metrics for _, metrics in ranked)
    best_rag = _best_rag_baseline(summary)
    best_rag_acc = float(summary.get(best_rag, {}).get("accuracy", 0.0)) if best_rag else 0.0
    full_acc = float(summary.get("full_brain", {}).get("accuracy", 0.0))
    num_seeds = len(per_seed_summaries) if per_seed_summaries else 0

    rows: List[Dict[str, object]] = []
    for rank, (baseline, metrics) in enumerate(ranked, start=1):
        total_queries = float(metrics.get("total_queries", 0.0))
        context_used = float(metrics.get("context_used", 0.0))
        traversal_cost = float(metrics.get("traversal_cost", 0.0))
        corrections = float(metrics.get("corrections_delivered", 0.0))
        row: Dict[str, object] = {
            "rank": rank,
            "baseline": baseline,
            "accuracy_pct": float(metrics.get("accuracy", 0.0)) * 100.0,
            "delta_vs_full_brain_pp": (float(metrics.get("accuracy", 0.0)) - full_acc) * 100.0,
            "delta_vs_best_rag_pp": (float(metrics.get("accuracy", 0.0)) - best_rag_acc) * 100.0,
            "context_per_query": _safe_divide(context_used, total_queries),
            "traversal_per_query": _safe_divide(traversal_cost, total_queries),
            "corrections_per_1k_queries": _safe_divide(corrections * 1000.0, total_queries),
        }
        if has_std:
            row["accuracy_std_pct"] = float(metrics.get("accuracy_std", 0.0)) * 100.0
        if per_seed_summaries and baseline not in {"full_brain", "oracle"}:
            wins, losses, ties = _head_to_head_record("full_brain", baseline, per_seed_summaries)
            row["full_brain_h2h"] = f"{wins}-{losses}-{ties}"
            row["full_brain_h2h_rate"] = _safe_divide(wins, num_seeds)
        elif per_seed_summaries:
            row["full_brain_h2h"] = "-"
            row["full_brain_h2h_rate"] = "-"
        rows.append(row)

    fieldnames = list(rows[0].keys())
    _write_table(
        artifacts_dir / "leaderboard.csv",
        artifacts_dir / "leaderboard.md",
        fieldnames,
        rows,
        title="Leaderboard",
        preamble=(
            "Rows ranked by accuracy. `delta_vs_best_rag_pp` compares each baseline to the best vector-RAG variant."
        ),
    )


def _write_proof_digest(
    artifacts_dir: Path,
    summary: Dict[str, Dict[str, float]],
    family_name: str,
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]],
    seeds: List[str],
) -> None:
    non_oracle = [(name, metrics) for name, metrics in summary.items() if name != "oracle"]
    best_non_oracle_name, best_non_oracle_metrics = max(
        non_oracle,
        key=lambda item: float(item[1].get("accuracy", 0.0)),
    )
    best_rag = _best_rag_baseline(summary)
    full = summary.get("full_brain", {})
    full_acc = float(full.get("accuracy", 0.0))
    rag_acc = float(summary.get(best_rag, {}).get("accuracy", 0.0)) if best_rag else 0.0
    full_queries = float(full.get("total_queries", 0.0))
    full_ctx_per_query = _safe_divide(float(full.get("context_used", 0.0)), full_queries)

    rag_ctx_per_query = 0.0
    if best_rag:
        rag = summary[best_rag]
        rag_ctx_per_query = _safe_divide(float(rag.get("context_used", 0.0)), float(rag.get("total_queries", 0.0)))

    num_seeds = int(next(iter(summary.values())).get("num_seeds", 1))
    if per_seed_summaries:
        num_seeds = len(per_seed_summaries)

    digest_path = artifacts_dir / "proof_digest.md"
    with digest_path.open("w", encoding="utf-8") as f:
        f.write("# Proof Digest\n\n")
        f.write(f"- Family: `{family_name}`\n")
        f.write(f"- Seeds: {num_seeds}")
        if seeds:
            f.write(f" ({', '.join(seeds)})\n")
        else:
            f.write("\n")
        f.write(f"- Queries per seed: {int(full_queries) if full_queries else 'n/a'}\n")
        f.write(
            f"- Top non-oracle baseline: `{best_non_oracle_name}` "
            f"({float(best_non_oracle_metrics.get('accuracy', 0.0)) * 100:.2f}%)\n"
        )
        if best_rag:
            f.write(
                f"- Best RAG baseline: `{best_rag}` ({rag_acc * 100:.2f}%)\n"
            )
            f.write(
                f"- full_brain margin vs best RAG: {(full_acc - rag_acc) * 100:+.2f} pp\n"
            )
            if rag_ctx_per_query > 0 and full_ctx_per_query > 0:
                ratio = rag_ctx_per_query / full_ctx_per_query
                f.write(
                    f"- Context/query: full_brain {full_ctx_per_query:.2f} vs {best_rag} "
                    f"{rag_ctx_per_query:.2f} ({ratio:.2f}x lower for full_brain)\n"
                )
        if "accuracy_std" in full:
            f.write(
                f"- full_brain accuracy: {full_acc * 100:.2f}% +/- {float(full['accuracy_std']) * 100:.2f}%\n"
            )
        else:
            f.write(f"- full_brain accuracy: {full_acc * 100:.2f}%\n")

        if per_seed_summaries and best_rag:
            wins, losses, ties = _head_to_head_record("full_brain", best_rag, per_seed_summaries)
            f.write(f"- full_brain vs {best_rag} head-to-head: {wins}-{losses}-{ties}\n")

        if all(name in summary for name in ("route_fn_only", "graph_route_pg", "full_brain")):
            route_acc = float(summary["route_fn_only"].get("accuracy", 0.0)) * 100.0
            graph_acc = float(summary["graph_route_pg"].get("accuracy", 0.0)) * 100.0
            full_acc_pct = full_acc * 100.0
            f.write("- Ablation chain:\n")
            f.write(f"  - route_fn_only: {route_acc:.2f}%\n")
            f.write(f"  - graph_route_pg: {graph_acc:.2f}% ({graph_acc - route_acc:+.2f} pp vs route_fn_only)\n")
            f.write(f"  - full_brain: {full_acc_pct:.2f}% ({full_acc_pct - graph_acc:+.2f} pp vs graph_route_pg)\n")


def _baseline_accuracy_from_records(records: List[Dict], baseline: str) -> float:
    relevant = [r for r in records if r.get("baseline") == baseline]
    if not relevant:
        return 0.0
    correct = sum(1 for r in relevant if bool(r.get("correct")))
    return _safe_divide(correct, len(relevant))


def _resolve_worked_example_source(
    run_dir: Path,
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]],
) -> Tuple[Optional[Path], Optional[str]]:
    direct_metrics = run_dir / "metrics.jsonl"
    if direct_metrics.exists():
        return direct_metrics, None

    sub_dirs = sorted(p for p in run_dir.iterdir() if p.is_dir() and p.name.startswith("seed_"))
    if not sub_dirs:
        return None, None

    if not per_seed_summaries:
        metrics_path = sub_dirs[0] / "metrics.jsonl"
        return (metrics_path if metrics_path.exists() else None), sub_dirs[0].name.removeprefix("seed_")

    best_rag_per_seed: List[float] = []
    for seed_summary in per_seed_summaries:
        full_acc = float(seed_summary.get("full_brain", {}).get("accuracy", 0.0))
        rag_names = [name for name in seed_summary if _is_rag_baseline(name)]
        rag_acc = max(float(seed_summary[name].get("accuracy", 0.0)) for name in rag_names) if rag_names else 0.0
        best_rag_per_seed.append(full_acc - rag_acc)

    if not best_rag_per_seed:
        metrics_path = sub_dirs[0] / "metrics.jsonl"
        return (metrics_path if metrics_path.exists() else None), sub_dirs[0].name.removeprefix("seed_")

    target_gap = sum(best_rag_per_seed) / len(best_rag_per_seed)
    best_index = min(
        range(len(best_rag_per_seed)),
        key=lambda idx: abs(best_rag_per_seed[idx] - target_gap),
    )
    if best_index >= len(sub_dirs):
        best_index = 0
    chosen_dir = sub_dirs[best_index]
    metrics_path = chosen_dir / "metrics.jsonl"
    seed_label = chosen_dir.name.removeprefix("seed_")
    return (metrics_path if metrics_path.exists() else None), seed_label


def _write_worked_example(
    artifacts_dir: Path,
    run_dir: Path,
    family_name: str,
    summary: Dict[str, Dict[str, float]],
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]] = None,
) -> None:
    metrics_path, seed_label = _resolve_worked_example_source(run_dir, per_seed_summaries)
    if metrics_path is None or not metrics_path.exists():
        return

    records = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        return

    best_rag = _best_rag_baseline(summary)
    pair_steps: Dict[str, List[Dict]] = {}
    for record in records:
        key = f"{record['subject']}::{record['object']}"
        pair_steps.setdefault(key, []).append(record)

    best_key = None
    best_score = float("-inf")
    for key, recs in pair_steps.items():
        steps = sorted(set(int(r["step"]) for r in recs))
        step_truth = {}
        for step in steps:
            step_records = [r for r in recs if int(r["step"]) == step]
            if step_records:
                step_truth[step] = str(step_records[0]["truth"])
        truth_sequence = [step_truth[s] for s in steps if s in step_truth]
        drift_events = sum(
            1 for idx in range(1, len(truth_sequence)) if truth_sequence[idx] != truth_sequence[idx - 1]
        )
        has_error = any(not bool(r.get("correct")) for r in recs)
        full_acc = _baseline_accuracy_from_records(recs, "full_brain")
        rag_acc = _baseline_accuracy_from_records(recs, best_rag) if best_rag else 0.0

        score = (
            len(steps)
            + (drift_events * 4)
            + ((full_acc - rag_acc) * 8)
            + (2 if has_error else 0)
        )
        if score > best_score:
            best_score = score
            best_key = key

    if best_key is None:
        return

    example_records = pair_steps[best_key]
    baseline_acc_summary: Dict[str, Dict[str, float]] = {}
    for baseline in sorted(set(r["baseline"] for r in example_records)):
        baseline_acc_summary[baseline] = {"accuracy": _baseline_accuracy_from_records(example_records, baseline)}
    baselines_in_example = _ordered_baselines(baseline_acc_summary)
    steps_in_example = sorted(set(int(r["step"]) for r in example_records))
    has_feedback_flag = any("feedback_available" in r for r in example_records)

    subject, object_ = best_key.split("::")
    md_path = artifacts_dir / "worked_example_trace.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Worked Example: {subject} -> {object_}\n\n")
        if seed_label:
            f.write(f"Representative seed: `{seed_label}`\n\n")
        f.write("How each baseline answers the same query as the ground-truth relation changes over time.\n\n")
        header = ["step", "truth"]
        if has_feedback_flag:
            header.append("explicit_feedback")
        header += baselines_in_example
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "|".join(["---"] * len(header)) + "|\n")

        for step in steps_in_example:
            step_recs = {r["baseline"]: r for r in example_records if int(r["step"]) == step}
            if not step_recs:
                continue
            truth = str(next(iter(step_recs.values()))["truth"])
            cells = [str(step), truth]
            if has_feedback_flag:
                feedback = any(bool(r.get("feedback_available")) for r in step_recs.values())
                cells.append("yes" if feedback else "no")
            for baseline in baselines_in_example:
                record = step_recs.get(baseline)
                if record is None:
                    cells.append("?")
                    continue
                answer = record["answer"] or "null"
                if bool(record["correct"]):
                    mark = "ok"
                elif bool(record["stale"]):
                    mark = "STALE"
                else:
                    mark = "WRONG"
                cells.append(f"{answer} ({mark})")
            f.write("| " + " | ".join(cells) + " |\n")

        f.write(f"\n*Source: `{metrics_path.name}`, family `{family_name}`, query pair `{best_key}`*\n")


def _plot_learning_curve(
    artifacts_dir: Path,
    summary: Dict[str, Dict[str, float]],
    family_name: str,
) -> None:
    has_std = any(
        "accuracy_std" in point
        for metrics in summary.values()
        for point in metrics.get("learning_curve", [])
    )

    plt.figure(figsize=(10, 6))
    for baseline in _ordered_baselines(summary):
        metrics = summary[baseline]
        curve = metrics.get("learning_curve", [])
        if not curve:
            continue
        xs = [point["step"] for point in curve]
        ys = [point["accuracy"] for point in curve]
        (line,) = plt.plot(xs, ys, label=baseline)
        if has_std:
            stds = [point.get("accuracy_std", 0) for point in curve]
            lo = [y - s for y, s in zip(ys, stds)]
            hi = [y + s for y, s in zip(ys, stds)]
            plt.fill_between(xs, lo, hi, alpha=0.15, color=line.get_color())

    plt.xlabel("Step")
    plt.ylabel("Accuracy")
    title = f"Learning Curve ({_pretty_family_name(family_name)})"
    if has_std:
        num_seeds = next(iter(summary.values())).get("num_seeds", "?")
        title += f" [{num_seeds} seeds, mean +/- 1 std]"
    plt.title(title)
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    out_path = artifacts_dir / "learning_curve.png"
    plt.savefig(out_path, dpi=150)
    plt.close()


def _resolve_family_name(run_dir: Path) -> str:
    config_path = run_dir / "config_snapshot.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            family = config.get("family", {})
            name = family.get("name")
            if name:
                return str(name)
        except json.JSONDecodeError:
            pass
    return "benchmark"


def _pretty_family_name(name: str) -> str:
    return name.replace("_", " ").title()


def generate_report(run_dir: Path) -> None:
    run_dir = Path(run_dir)
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing summary.json in {run_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    per_seed_path = run_dir / "per_seed_summaries.json"
    per_seed_summaries = None
    if per_seed_path.exists():
        per_seed_summaries = json.loads(per_seed_path.read_text(encoding="utf-8"))

    family_name = _resolve_family_name(run_dir)
    seed_labels = _seed_labels(run_dir, per_seed_summaries)

    _write_summary_table(artifacts_dir, summary)
    _write_leaderboard(artifacts_dir, summary, per_seed_summaries)
    _write_pairwise_deltas(artifacts_dir, summary)
    _write_win_rate_table(artifacts_dir, summary, per_seed_summaries=per_seed_summaries)
    _write_per_seed_breakdown(artifacts_dir, run_dir, summary, per_seed_summaries)
    _write_worked_example(
        artifacts_dir,
        run_dir,
        family_name,
        summary=summary,
        per_seed_summaries=per_seed_summaries,
    )
    _write_proof_digest(
        artifacts_dir,
        summary,
        family_name,
        per_seed_summaries=per_seed_summaries,
        seeds=seed_labels,
    )
    _plot_learning_curve(artifacts_dir, summary, family_name)

    print(f"Report artifacts written to {artifacts_dir}")
