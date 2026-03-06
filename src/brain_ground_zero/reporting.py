from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt


def _write_summary_table(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    rows = []
    has_std = any("accuracy_std" in m for m in summary.values())
    for baseline, metrics in summary.items():
        row = {"baseline": baseline}
        for key in ["accuracy", "stale_rate", "false_rate", "unknown_rate",
                     "corrections_delivered", "context_used", "traversal_cost", "total_queries"]:
            row[key] = metrics.get(key, "")
            if has_std and f"{key}_std" in metrics:
                row[f"{key}_std"] = metrics[f"{key}_std"]
        if has_std and "num_seeds" in metrics:
            row["num_seeds"] = metrics["num_seeds"]
        rows.append(row)

    fieldnames = list(rows[0].keys())
    csv_path = artifacts_dir / "summary_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md_path = artifacts_dir / "summary_table.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(row.get(k, "")) for k in fieldnames) + " |\n")


def _write_pairwise_deltas(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    """Write a pairwise accuracy-delta and win-rate table."""
    baselines = list(summary.keys())
    n = len(baselines)
    if n < 2:
        return

    # Build delta matrix (row minus col)
    delta_rows = []
    for i, b1 in enumerate(baselines):
        row = {"baseline": b1}
        for j, b2 in enumerate(baselines):
            acc1 = summary[b1].get("accuracy", 0)
            acc2 = summary[b2].get("accuracy", 0)
            row[b2] = round(acc1 - acc2, 4)
        delta_rows.append(row)

    fieldnames = ["baseline"] + baselines
    csv_path = artifacts_dir / "pairwise_accuracy_delta.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(delta_rows)

    md_path = artifacts_dir / "pairwise_accuracy_delta.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Pairwise Accuracy Delta (row - column)\n\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in delta_rows:
            cells = []
            for k in fieldnames:
                v = row[k]
                if isinstance(v, float):
                    cells.append(f"{v:+.4f}" if v != 0 else "0.0000")
                else:
                    cells.append(str(v))
            f.write("| " + " | ".join(cells) + " |\n")


def _write_win_rate_table(
    artifacts_dir: Path,
    per_seed_summaries: Optional[List[Dict[str, Dict[str, float]]]] = None,
    summary: Optional[Dict[str, Dict[str, float]]] = None,
) -> None:
    """Write a win-rate matrix based on per-seed accuracy comparison."""
    if per_seed_summaries is None or len(per_seed_summaries) < 2:
        return

    baselines = list(per_seed_summaries[0].keys())
    n = len(baselines)
    num_seeds = len(per_seed_summaries)

    win_matrix: Dict[str, Dict[str, int]] = {b: {b2: 0 for b2 in baselines} for b in baselines}
    for seed_summary in per_seed_summaries:
        for i, b1 in enumerate(baselines):
            for j, b2 in enumerate(baselines):
                if i == j:
                    continue
                a1 = seed_summary.get(b1, {}).get("accuracy", 0)
                a2 = seed_summary.get(b2, {}).get("accuracy", 0)
                if a1 > a2:
                    win_matrix[b1][b2] += 1

    fieldnames = ["baseline"] + baselines
    rows = []
    for b1 in baselines:
        row = {"baseline": b1}
        for b2 in baselines:
            if b1 == b2:
                row[b2] = "-"
            else:
                row[b2] = f"{win_matrix[b1][b2]}/{num_seeds}"
        rows.append(row)

    csv_path = artifacts_dir / "win_rate_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md_path = artifacts_dir / "win_rate_matrix.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Win-Rate Matrix ({num_seeds} seeds)\n\n")
        f.write("Cell = number of seeds where row baseline beats column baseline on accuracy.\n\n")
        f.write("| " + " | ".join(fieldnames) + " |\n")
        f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(row[k]) for k in fieldnames) + " |\n")


def _write_worked_example(artifacts_dir: Path, run_dir: Path, family_name: str) -> None:
    """Extract a single query pair traced across all baselines/steps as a worked example."""
    metrics_path = run_dir / "metrics.jsonl"
    if not metrics_path.exists():
        # For multi-seed, use the first sub-run
        sub_dirs = sorted(p for p in run_dir.iterdir() if p.is_dir() and p.name.startswith("seed_"))
        if sub_dirs:
            metrics_path = sub_dirs[0] / "metrics.jsonl"
        if not metrics_path.exists():
            return

    records = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        return

    # Find a query pair that appears in multiple steps (drifted)
    pair_steps: Dict[str, List[Dict]] = {}
    for r in records:
        key = f"{r['subject']}::{r['object']}"
        pair_steps.setdefault(key, []).append(r)

    # Pick the pair with the most steps and at least one incorrect answer
    best_key = None
    best_score = 0
    for key, recs in pair_steps.items():
        steps_seen = len(set(r["step"] for r in recs))
        has_error = any(not r["correct"] for r in recs)
        score = steps_seen * 2 + (10 if has_error else 0)
        if score > best_score:
            best_score = score
            best_key = key

    if best_key is None:
        return

    example_records = pair_steps[best_key]
    baselines_in_example = sorted(set(r["baseline"] for r in example_records))
    steps_in_example = sorted(set(r["step"] for r in example_records))

    subject, object_ = best_key.split("::")

    md_path = artifacts_dir / "worked_example_trace.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Worked Example: {subject} -> {object_}\n\n")
        f.write(
            "How each baseline answers the same query as the ground-truth relation changes over time.\n\n"
        )

        # Header
        header = ["step", "truth"] + baselines_in_example
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "|".join(["---"] * len(header)) + "|\n")

        for step in steps_in_example:
            step_recs = {r["baseline"]: r for r in example_records if r["step"] == step}
            if not step_recs:
                continue
            truth = next(iter(step_recs.values()))["truth"]
            cells = [str(step), truth]
            for bl in baselines_in_example:
                r = step_recs.get(bl)
                if r is None:
                    cells.append("?")
                else:
                    ans = r["answer"] or "null"
                    mark = "ok" if r["correct"] else ("STALE" if r["stale"] else "WRONG")
                    cells.append(f"{ans} ({mark})")
            f.write("| " + " | ".join(cells) + " |\n")

        f.write(f"\n*Source: metrics.jsonl, family `{family_name}`, query pair `{best_key}`*\n")


def _plot_learning_curve(
    artifacts_dir: Path, summary: Dict[str, Dict[str, float]], family_name: str
) -> None:
    has_std = any(
        "accuracy_std" in pt
        for m in summary.values()
        for pt in m.get("learning_curve", [])
    )

    plt.figure(figsize=(10, 6))
    for baseline, metrics in summary.items():
        curve = metrics.get("learning_curve", [])
        if not curve:
            continue
        xs = [point["step"] for point in curve]
        ys = [point["accuracy"] for point in curve]
        line, = plt.plot(xs, ys, label=baseline)
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


def generate_report(run_dir: Path) -> None:
    run_dir = Path(run_dir)
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing summary.json in {run_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    # Load per-seed summaries if they exist (multi-seed run)
    per_seed_path = run_dir / "per_seed_summaries.json"
    per_seed_summaries = None
    if per_seed_path.exists():
        per_seed_summaries = json.loads(per_seed_path.read_text(encoding="utf-8"))

    _write_summary_table(artifacts_dir, summary)
    _write_pairwise_deltas(artifacts_dir, summary)
    _write_win_rate_table(artifacts_dir, per_seed_summaries=per_seed_summaries, summary=summary)
    family_name = _resolve_family_name(run_dir)
    _write_worked_example(artifacts_dir, run_dir, family_name)
    _plot_learning_curve(artifacts_dir, summary, family_name)

    print(f"Report artifacts written to {artifacts_dir}")


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
