from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def _write_summary_table(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    rows = []
    for baseline, metrics in summary.items():
        rows.append(
            {
                "baseline": baseline,
                "accuracy": metrics["accuracy"],
                "stale_rate": metrics["stale_rate"],
                "false_rate": metrics["false_rate"],
                "unknown_rate": metrics["unknown_rate"],
                "corrections_delivered": metrics["corrections_delivered"],
                "context_used": metrics["context_used"],
                "traversal_cost": metrics["traversal_cost"],
                "total_queries": metrics["total_queries"],
            }
        )

    csv_path = artifacts_dir / "summary_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = artifacts_dir / "summary_table.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("| " + " | ".join(rows[0].keys()) + " |\n")
        f.write("|" + "|".join(["---"] * len(rows[0])) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(row[k]) for k in row.keys()) + " |\n")


def _plot_learning_curve(artifacts_dir: Path, summary: Dict[str, Dict[str, float]]) -> None:
    plt.figure(figsize=(10, 6))
    for baseline, metrics in summary.items():
        curve = metrics.get("learning_curve", [])
        if not curve:
            continue
        xs = [point["step"] for point in curve]
        ys = [point["accuracy"] for point in curve]
        plt.plot(xs, ys, label=baseline)
    plt.xlabel("Step")
    plt.ylabel("Accuracy")
    plt.title("Learning Curve (Relational Drift)")
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

    _write_summary_table(artifacts_dir, summary)
    _plot_learning_curve(artifacts_dir, summary)

    print(f"Report artifacts written to {artifacts_dir}")

