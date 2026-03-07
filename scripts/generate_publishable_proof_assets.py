#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import yaml


FOCUS_BUNDLES = (
    {
        "bundle_id": "recorded_h2h_relational_drift_10seed",
        "family": "relational_drift",
        "label": "Recorded H2H",
        "kind": "multiseed",
    },
    {
        "bundle_id": "sparse_feedback_10seed",
        "family": "sparse_feedback",
        "label": "Sparse Feedback",
        "kind": "multiseed",
    },
    {
        "bundle_id": "recurring_workflows_10seed",
        "family": "recurring_workflows",
        "label": "Recurring Workflows",
        "kind": "multiseed",
    },
)


@dataclass
class BundleMetrics:
    bundle_id: str
    bundle_dir: Path
    family: str
    label: str
    kind: str
    seeds: int
    queries_per_seed: int
    steps: int
    baseline_count: int
    full_brain_accuracy: float
    full_brain_accuracy_std: Optional[float]
    best_rag: str
    best_rag_accuracy: float
    best_rag_accuracy_std: Optional[float]
    margin_vs_best_rag_pp: float
    h2h_record_vs_best_rag: str
    context_per_query_full_brain: float
    context_per_query_best_rag: float
    context_ratio_best_rag_over_full_brain: float
    route_fn_only_accuracy: float
    graph_route_pg_accuracy: float
    full_minus_graph_pp: float
    graph_minus_route_fn_pp: float
    seed_labels: List[str]
    seed_full_brain_accuracies: List[float]
    seed_best_rag_accuracies: List[float]
    summary_rows: List[Dict[str, str]]


def _parse_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _best_rag_name(summary_by_baseline: Dict[str, Dict[str, str]]) -> str:
    rag_names = [name for name in summary_by_baseline if name.startswith("vector_rag")]
    if not rag_names:
        raise ValueError("No vector_rag baseline found in summary table")
    return max(rag_names, key=lambda name: _parse_float(summary_by_baseline[name].get("accuracy")))


def _context_per_query(metrics: Dict[str, str]) -> float:
    return _safe_div(
        _parse_float(metrics.get("context_used")),
        _parse_float(metrics.get("total_queries")),
    )


def _row_lookup(rows: Sequence[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {row["baseline"]: row for row in rows if row.get("baseline")}


def _parse_per_seed_matrix(path: Path, baseline: str) -> Tuple[List[str], List[float]]:
    rows = _read_csv_rows(path)
    if not rows:
        return [], []
    seed_columns = [column for column in rows[0].keys() if column.startswith("seed_")]
    row_map = _row_lookup(rows)
    selected = row_map.get(baseline)
    if selected is None:
        return [], []
    labels = [column.removeprefix("seed_") for column in seed_columns]
    values = [_parse_float(selected.get(column)) for column in seed_columns]
    return labels, values


def _h2h_record(seed_full: Sequence[float], seed_rag: Sequence[float]) -> str:
    if not seed_full or not seed_rag or len(seed_full) != len(seed_rag):
        return "n/a"
    wins = 0
    losses = 0
    ties = 0
    for full, rag in zip(seed_full, seed_rag):
        if full > rag:
            wins += 1
        elif full < rag:
            losses += 1
        else:
            ties += 1
    return f"{wins}-{losses}-{ties}"


def _markdown_table(fieldnames: Sequence[str], rows: Sequence[Dict[str, object]]) -> str:
    if not rows:
        return ""
    lines = ["| " + " | ".join(fieldnames) + " |", "|" + "|".join(["---"] * len(fieldnames)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(name, "")) for name in fieldnames) + " |")
    return "\n".join(lines) + "\n"


def _write_table(csv_path: Path, md_path: Path, rows: List[Dict[str, object]], title: str) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(_markdown_table(fieldnames, rows))


def _bundle_row(bundle: BundleMetrics) -> Dict[str, object]:
    return {
        "bundle": bundle.bundle_id,
        "family": bundle.family,
        "seeds": bundle.seeds,
        "queries_per_seed": bundle.queries_per_seed,
        "steps": bundle.steps,
        "baselines": bundle.baseline_count,
        "full_brain_accuracy_pct": round(bundle.full_brain_accuracy * 100.0, 4),
        "full_brain_accuracy_std_pct": "n/a"
        if bundle.full_brain_accuracy_std is None
        else round(bundle.full_brain_accuracy_std * 100.0, 4),
        "best_rag": bundle.best_rag,
        "best_rag_accuracy_pct": round(bundle.best_rag_accuracy * 100.0, 4),
        "best_rag_accuracy_std_pct": "n/a"
        if bundle.best_rag_accuracy_std is None
        else round(bundle.best_rag_accuracy_std * 100.0, 4),
        "margin_vs_best_rag_pp": round(bundle.margin_vs_best_rag_pp, 4),
        "full_brain_h2h_vs_best_rag": bundle.h2h_record_vs_best_rag,
        "full_brain_context_per_query": round(bundle.context_per_query_full_brain, 4),
        "best_rag_context_per_query": round(bundle.context_per_query_best_rag, 4),
        "context_ratio_best_rag_over_full_brain": round(bundle.context_ratio_best_rag_over_full_brain, 4),
        "route_fn_only_accuracy_pct": round(bundle.route_fn_only_accuracy * 100.0, 4),
        "graph_route_pg_accuracy_pct": round(bundle.graph_route_pg_accuracy * 100.0, 4),
        "graph_minus_route_fn_pp": round(bundle.graph_minus_route_fn_pp, 4),
        "full_minus_graph_pp": round(bundle.full_minus_graph_pp, 4),
    }


def _proof_rung(bundle: BundleMetrics) -> str:
    if bundle.kind == "recorded":
        return "Recorded H2H (first artifact, single fixture)"
    return f"Simulation proof ({bundle.seeds}-seed)"


def _format_pct(value: float, digits: int = 1) -> str:
    return f"{value * 100.0:.{digits}f}%"


def _format_pct_with_std(value: float, std: Optional[float]) -> str:
    if std is None:
        return _format_pct(value)
    return f"{_format_pct(value)} +/- {_format_pct(std)}"


def _bundle_compact_row(bundle: BundleMetrics) -> Dict[str, object]:
    return {
        "focus": bundle.label,
        "bundle": bundle.bundle_id,
        "proof_rung": _proof_rung(bundle),
        "seeds": bundle.seeds,
        "queries_per_seed": bundle.queries_per_seed,
        "full_brain_accuracy": _format_pct_with_std(bundle.full_brain_accuracy, bundle.full_brain_accuracy_std),
        "best_rag": bundle.best_rag,
        "best_rag_accuracy": _format_pct_with_std(bundle.best_rag_accuracy, bundle.best_rag_accuracy_std),
        "margin_vs_best_rag_pp": f"{bundle.margin_vs_best_rag_pp:+.1f}",
        "h2h_vs_best_rag": bundle.h2h_record_vs_best_rag,
        "context_ratio_best_rag_over_full_brain": f"{bundle.context_ratio_best_rag_over_full_brain:.1f}x",
        "ablation_full_minus_graph_pp": f"{bundle.full_minus_graph_pp:+.1f}",
    }


def _bundle_claim_line(bundle: BundleMetrics) -> str:
    base = (
        f"{bundle.label}: full_brain {_format_pct_with_std(bundle.full_brain_accuracy, bundle.full_brain_accuracy_std)} "
        f"vs {bundle.best_rag} {_format_pct_with_std(bundle.best_rag_accuracy, bundle.best_rag_accuracy_std)} "
        f"({bundle.margin_vs_best_rag_pp:+.1f} pp), context {bundle.context_ratio_best_rag_over_full_brain:.1f}x lower for full_brain"
    )
    if bundle.kind == "recorded":
        return f"- {base}. First scored fixed-session artifact (single seeded fixture; not yet proof-scale)."
    return f"- {base}, head-to-head {bundle.h2h_record_vs_best_rag}."


def _load_multiseed_bundle(bundle_dir: Path, descriptor: Dict[str, str]) -> BundleMetrics:
    summary_rows = _read_csv_rows(bundle_dir / "summary_table.csv")
    summary_by_baseline = _row_lookup(summary_rows)

    best_rag = _best_rag_name(summary_by_baseline)
    full = summary_by_baseline["full_brain"]
    rag = summary_by_baseline[best_rag]
    route_fn = summary_by_baseline["route_fn_only"]
    graph_pg = summary_by_baseline["graph_route_pg"]

    seeds = json.loads((bundle_dir / "seeds.json").read_text(encoding="utf-8"))
    config = json.loads((bundle_dir / "config_snapshot.json").read_text(encoding="utf-8"))
    steps = int(config.get("family", {}).get("params", {}).get("steps", 0))

    seed_labels, seed_full = _parse_per_seed_matrix(bundle_dir / "per_seed_accuracy_matrix.csv", "full_brain")
    rag_seed_labels, seed_rag = _parse_per_seed_matrix(bundle_dir / "per_seed_accuracy_matrix.csv", best_rag)
    if rag_seed_labels and rag_seed_labels != seed_labels:
        raise ValueError(f"Seed columns mismatch in {bundle_dir}")

    h2h_record = _h2h_record(seed_full, seed_rag)

    return BundleMetrics(
        bundle_id=descriptor["bundle_id"],
        bundle_dir=bundle_dir,
        family=descriptor["family"],
        label=descriptor["label"],
        kind=descriptor["kind"],
        seeds=len(seeds),
        queries_per_seed=int(round(_parse_float(full.get("total_queries")))),
        steps=steps,
        baseline_count=len(summary_rows),
        full_brain_accuracy=_parse_float(full.get("accuracy")),
        full_brain_accuracy_std=_parse_float(full.get("accuracy_std")),
        best_rag=best_rag,
        best_rag_accuracy=_parse_float(rag.get("accuracy")),
        best_rag_accuracy_std=_parse_float(rag.get("accuracy_std")),
        margin_vs_best_rag_pp=(_parse_float(full.get("accuracy")) - _parse_float(rag.get("accuracy"))) * 100.0,
        h2h_record_vs_best_rag=h2h_record,
        context_per_query_full_brain=_context_per_query(full),
        context_per_query_best_rag=_context_per_query(rag),
        context_ratio_best_rag_over_full_brain=_safe_div(_context_per_query(rag), _context_per_query(full)),
        route_fn_only_accuracy=_parse_float(route_fn.get("accuracy")),
        graph_route_pg_accuracy=_parse_float(graph_pg.get("accuracy")),
        full_minus_graph_pp=(_parse_float(full.get("accuracy")) - _parse_float(graph_pg.get("accuracy"))) * 100.0,
        graph_minus_route_fn_pp=(_parse_float(graph_pg.get("accuracy")) - _parse_float(route_fn.get("accuracy"))) * 100.0,
        seed_labels=seed_labels,
        seed_full_brain_accuracies=seed_full,
        seed_best_rag_accuracies=seed_rag,
        summary_rows=summary_rows,
    )


def _load_recorded_bundle(bundle_dir: Path, descriptor: Dict[str, str]) -> BundleMetrics:
    summary_rows = _read_csv_rows(bundle_dir / "scoring" / "summary_table.csv")
    summary_by_baseline = _row_lookup(summary_rows)

    best_rag = _best_rag_name(summary_by_baseline)
    full = summary_by_baseline["full_brain"]
    rag = summary_by_baseline[best_rag]
    route_fn = summary_by_baseline["route_fn_only"]
    graph_pg = summary_by_baseline["graph_route_pg"]

    fixture = yaml.safe_load((bundle_dir / "fixture.yaml").read_text(encoding="utf-8"))
    steps = len(fixture.get("steps", []))

    return BundleMetrics(
        bundle_id=descriptor["bundle_id"],
        bundle_dir=bundle_dir,
        family=descriptor["family"],
        label=descriptor["label"],
        kind=descriptor["kind"],
        seeds=1,
        queries_per_seed=int(round(_parse_float(full.get("total_queries")))),
        steps=steps,
        baseline_count=len(summary_rows),
        full_brain_accuracy=_parse_float(full.get("accuracy")),
        full_brain_accuracy_std=None,
        best_rag=best_rag,
        best_rag_accuracy=_parse_float(rag.get("accuracy")),
        best_rag_accuracy_std=None,
        margin_vs_best_rag_pp=(_parse_float(full.get("accuracy")) - _parse_float(rag.get("accuracy"))) * 100.0,
        h2h_record_vs_best_rag="n/a (single seed)",
        context_per_query_full_brain=_context_per_query(full),
        context_per_query_best_rag=_context_per_query(rag),
        context_ratio_best_rag_over_full_brain=_safe_div(_context_per_query(rag), _context_per_query(full)),
        route_fn_only_accuracy=_parse_float(route_fn.get("accuracy")),
        graph_route_pg_accuracy=_parse_float(graph_pg.get("accuracy")),
        full_minus_graph_pp=(_parse_float(full.get("accuracy")) - _parse_float(graph_pg.get("accuracy"))) * 100.0,
        graph_minus_route_fn_pp=(_parse_float(graph_pg.get("accuracy")) - _parse_float(route_fn.get("accuracy"))) * 100.0,
        seed_labels=[],
        seed_full_brain_accuracies=[],
        seed_best_rag_accuracies=[],
        summary_rows=summary_rows,
    )


def _load_bundle(bundle_dir: Path, descriptor: Dict[str, str]) -> BundleMetrics:
    if descriptor["kind"] == "recorded":
        return _load_recorded_bundle(bundle_dir, descriptor)
    return _load_multiseed_bundle(bundle_dir, descriptor)


def _plot_recorded_accuracy_context(bundle: BundleMetrics) -> None:
    rows = _row_lookup(bundle.summary_rows)
    points: List[Tuple[str, float, float]] = []
    for baseline, metrics in rows.items():
        accuracy = _parse_float(metrics.get("accuracy")) * 100.0
        context_per_query = _context_per_query(metrics)
        points.append((baseline, context_per_query, accuracy))

    points.sort(key=lambda item: item[2], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    for baseline, context_per_query, accuracy in points:
        if baseline == "full_brain":
            color = "#0b8a5f"
            size = 120
            zorder = 4
        elif baseline == bundle.best_rag:
            color = "#e67e22"
            size = 110
            zorder = 3
        elif baseline == "oracle":
            color = "#555555"
            size = 90
            zorder = 2
        else:
            color = "#2d6aa6"
            size = 80
            zorder = 2
        ax.scatter(context_per_query, accuracy, s=size, color=color, edgecolor="black", linewidth=0.6, zorder=zorder)
        ax.text(context_per_query + 0.06, accuracy + 0.2, baseline, fontsize=8)

    ax.set_xlabel("Context per query")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(
        "Recorded H2H: Accuracy vs Context Per Query\n"
        f"full_brain {bundle.full_brain_accuracy * 100:.2f}% vs {bundle.best_rag} {bundle.best_rag_accuracy * 100:.2f}%"
    )
    ax.grid(alpha=0.25)
    ax.set_xlim(-0.2, max(point[1] for point in points) + 0.8)
    ax.set_ylim(-2, 103)

    out_path = bundle.bundle_dir / "chart_accuracy_context_tradeoff.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_seed_dumbbell(bundle: BundleMetrics) -> None:
    if not bundle.seed_labels or not bundle.seed_full_brain_accuracies or not bundle.seed_best_rag_accuracies:
        return

    fig, ax = plt.subplots(figsize=(10.5, 6))
    y_positions = list(range(len(bundle.seed_labels)))

    full_pct = [value * 100.0 for value in bundle.seed_full_brain_accuracies]
    rag_pct = [value * 100.0 for value in bundle.seed_best_rag_accuracies]

    for y, seed, full, rag in zip(y_positions, bundle.seed_labels, full_pct, rag_pct):
        color = "#0b8a5f" if full >= rag else "#b23a48"
        ax.plot([rag, full], [y, y], color=color, linewidth=2.2, alpha=0.85)
        margin = full - rag
        ax.text(max(full, rag) + 0.7, y, f"{margin:+.1f} pp", va="center", fontsize=8)

    ax.scatter(rag_pct, y_positions, color="#e67e22", s=55, label=bundle.best_rag, zorder=3)
    ax.scatter(full_pct, y_positions, color="#0b8a5f", s=55, label="full_brain", zorder=4)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(bundle.seed_labels)
    ax.set_xlabel("Accuracy (%)")
    ax.set_ylabel("Seed")
    ax.set_title(
        f"{bundle.label}: full_brain vs {bundle.best_rag} by Seed\n"
        f"Head-to-head: {bundle.h2h_record_vs_best_rag}"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")

    min_x = min(min(full_pct), min(rag_pct))
    max_x = max(max(full_pct), max(rag_pct))
    ax.set_xlim(max(0.0, min_x - 10.0), min(103.0, max_x + 12.0))

    out_path = bundle.bundle_dir / "chart_seed_h2h_full_brain_vs_best_rag.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def _plot_cross_margin_context(bundles: Sequence[BundleMetrics], output_path: Path) -> None:
    labels = [bundle.label for bundle in bundles]
    margins = [bundle.margin_vs_best_rag_pp for bundle in bundles]
    context_ratios = [bundle.context_ratio_best_rag_over_full_brain for bundle in bundles]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.5))
    margin_colors = ["#2d6aa6", "#0b8a5f", "#0b8a5f"]

    bars_margin = axes[0].bar(labels, margins, color=margin_colors, edgecolor="black", linewidth=0.5)
    axes[0].set_title("full_brain Margin vs Best RAG")
    axes[0].set_ylabel("Accuracy Delta (pp)")
    axes[0].grid(axis="y", alpha=0.25)
    for bar, value in zip(bars_margin, margins):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{value:+.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    bars_ratio = axes[1].bar(labels, context_ratios, color="#e67e22", edgecolor="black", linewidth=0.5)
    axes[1].set_title("Best-RAG Context Cost vs full_brain")
    axes[1].set_ylabel("Context Ratio (x)")
    axes[1].grid(axis="y", alpha=0.25)
    for bar, value in zip(bars_ratio, context_ratios):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.07,
            f"{value:.1f}x",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.suptitle("Focus Evidence: Recorded H2H + Sparse Feedback + Recurring Workflows", fontsize=13)
    fig.tight_layout(rect=(0, 0.0, 1, 0.93))
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _plot_ablation_ladder(bundles: Sequence[BundleMetrics], output_path: Path) -> None:
    x_labels = ["route_fn_only", "graph_route_pg", "full_brain"]
    xs = [0, 1, 2]
    palette = {
        "Recorded H2H": "#2d6aa6",
        "Sparse Feedback": "#0b8a5f",
        "Recurring Workflows": "#8c5a2b",
    }

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    for bundle in bundles:
        ys = [
            bundle.route_fn_only_accuracy * 100.0,
            bundle.graph_route_pg_accuracy * 100.0,
            bundle.full_brain_accuracy * 100.0,
        ]
        ax.plot(
            xs,
            ys,
            marker="o",
            linewidth=2.2,
            markersize=7,
            color=palette.get(bundle.label, "#333333"),
            label=bundle.label,
        )
        ax.text(
            xs[-1] + 0.04,
            ys[-1],
            f"+{bundle.full_minus_graph_pp:.1f} pp",
            va="center",
            fontsize=8,
            color=palette.get(bundle.label, "#333333"),
        )

    ax.set_xticks(xs)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Ablation Ladder Across Focus Bundles")
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(0, 103)
    ax.legend(loc="lower right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _write_publishable_bundle_files(bundles: Sequence[BundleMetrics], output_dir: Path) -> None:
    tables_dir = output_dir / "tables"
    charts_dir = output_dir / "charts"
    tables_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    focus_rows = [_bundle_row(bundle) for bundle in bundles]
    compact_focus_rows = [_bundle_compact_row(bundle) for bundle in bundles]
    _write_table(
        tables_dir / "focus_evidence_table.csv",
        tables_dir / "focus_evidence_table.md",
        focus_rows,
        "Focus Evidence Table",
    )
    _write_table(
        tables_dir / "focus_evidence_table_compact.csv",
        tables_dir / "focus_evidence_table_compact.md",
        compact_focus_rows,
        "Focus Evidence Table (Compact)",
    )

    _plot_cross_margin_context(bundles, charts_dir / "focus_margin_context.png")
    _plot_ablation_ladder(bundles, charts_dir / "focus_ablation_ladder.png")

    bundle_map = {bundle.bundle_id: bundle for bundle in bundles}
    recurring = bundle_map.get("recurring_workflows_10seed")
    sparse = bundle_map.get("sparse_feedback_10seed")
    recorded = bundle_map.get("recorded_h2h_relational_drift_001")

    with (output_dir / "site_blog_paper_starter.md").open("w", encoding="utf-8") as f:
        f.write("# Site/Blog/Paper Starter Pack\n\n")
        f.write("Generated from tracked proof bundles.\n\n")
        f.write("## Use this first\n\n")
        f.write("1. `tables/focus_evidence_table_compact.md`\n")
        f.write("2. `charts/focus_margin_context.png`\n")
        f.write("3. `charts/focus_ablation_ladder.png`\n")
        f.write("4. `../recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`\n")
        f.write("5. `../sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`\n")
        f.write("6. `../recorded_h2h_relational_drift_001/chart_accuracy_context_tradeoff.png`\n\n")
        f.write("## Canonical topline claims\n\n")
        for bundle in bundles:
            f.write(_bundle_claim_line(bundle) + "\n")
        f.write("\n## Recommended asset order\n\n")
        f.write("### Site\n\n")
        if recurring is not None:
            f.write("- recurring_workflows scorecard: `../recurring_workflows_10seed/publishable_key_results_compact.md`\n")
        if sparse is not None:
            f.write("- sparse_feedback scorecard: `../sparse_feedback_10seed/publishable_key_results_compact.md`\n")
        f.write("- cross-bundle quick table: `tables/focus_evidence_table_compact.md`\n")
        f.write("- cross-bundle chart: `charts/focus_margin_context.png`\n\n")
        f.write("### Blog\n\n")
        if recurring is not None:
            f.write("- recurring_workflows seed head-to-head chart: `../recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`\n")
        if sparse is not None:
            f.write("- sparse_feedback seed head-to-head chart: `../sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`\n")
        if recorded is not None:
            f.write("- recorded_h2h tradeoff chart: `../recorded_h2h_relational_drift_001/chart_accuracy_context_tradeoff.png`\n")
        f.write("- ablation support chart: `charts/focus_ablation_ladder.png`\n\n")
        f.write("### Paper\n\n")
        f.write("- compact numeric table: `tables/focus_evidence_table_compact.csv`\n")
        f.write("- full numeric table: `tables/focus_evidence_table.csv`\n")
        f.write("- ablation figure: `charts/focus_ablation_ladder.png`\n")
        f.write("- margin/context figure: `charts/focus_margin_context.png`\n")

    with (output_dir / "README.md").open("w", encoding="utf-8") as f:
        f.write("# Publishable Proof Pack\n\n")
        f.write("High-signal assets for site/blog/paper use, generated from tracked proof bundles.\n\n")
        f.write("## Start Here\n\n")
        f.write("- [site_blog_paper_starter.md](site_blog_paper_starter.md)\n")
        f.write("- [focus_evidence_table_compact.md](tables/focus_evidence_table_compact.md)\n")
        f.write("- [focus_margin_context.png](charts/focus_margin_context.png)\n")
        f.write("- [focus_ablation_ladder.png](charts/focus_ablation_ladder.png)\n\n")
        f.write("## Tables\n\n")
        f.write("- [focus_evidence_table_compact.md](tables/focus_evidence_table_compact.md)\n")
        f.write("- [focus_evidence_table_compact.csv](tables/focus_evidence_table_compact.csv)\n")
        f.write("- [focus_evidence_table.md](tables/focus_evidence_table.md)\n")
        f.write("- [focus_evidence_table.csv](tables/focus_evidence_table.csv)\n\n")
        f.write("## Charts\n\n")
        f.write("- [focus_margin_context.png](charts/focus_margin_context.png)\n")
        f.write("- [focus_ablation_ladder.png](charts/focus_ablation_ladder.png)\n")
        f.write("- [recorded_h2h_seed_h2h.png](../recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)\n")
        f.write("- [sparse_feedback_seed_h2h.png](../sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)\n")
        f.write("- [recurring_workflows_seed_h2h.png](../recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)\n")


def _write_per_bundle_scorecards(bundles: Sequence[BundleMetrics]) -> None:
    for bundle in bundles:
        row = _bundle_row(bundle)
        compact_row = _bundle_compact_row(bundle)
        _write_table(
            bundle.bundle_dir / "publishable_key_results.csv",
            bundle.bundle_dir / "publishable_key_results.md",
            [row],
            f"Publishable Key Results: {bundle.bundle_id}",
        )
        _write_table(
            bundle.bundle_dir / "publishable_key_results_compact.csv",
            bundle.bundle_dir / "publishable_key_results_compact.md",
            [compact_row],
            f"Publishable Key Results (Compact): {bundle.bundle_id}",
        )


def _build_focus_bundles(proof_root: Path) -> List[BundleMetrics]:
    bundles: List[BundleMetrics] = []
    for descriptor in FOCUS_BUNDLES:
        bundle_dir = proof_root / descriptor["bundle_id"]
        if not bundle_dir.exists():
            print(f"[skip] Missing bundle: {bundle_dir}")
            continue
        bundle = _load_bundle(bundle_dir, descriptor)
        bundles.append(bundle)
    return bundles


def _render_per_bundle_charts(bundles: Sequence[BundleMetrics]) -> None:
    for bundle in bundles:
        if bundle.kind == "recorded":
            _plot_recorded_accuracy_context(bundle)
        else:
            _plot_seed_dumbbell(bundle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate publishable proof charts and tables.")
    parser.add_argument(
        "--proof-root",
        type=Path,
        default=Path("proof-results"),
        help="Root folder that contains tracked proof bundles.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("proof-results") / "publishable",
        help="Directory where cross-bundle publishable artifacts are written.",
    )
    args = parser.parse_args()

    proof_root = args.proof_root
    output_dir = args.output_dir

    bundles = _build_focus_bundles(proof_root)
    if not bundles:
        raise SystemExit("No focus bundles found. Nothing to do.")

    _render_per_bundle_charts(bundles)
    _write_per_bundle_scorecards(bundles)
    _write_publishable_bundle_files(bundles, output_dir)

    print("Generated publishable artifacts:")
    for bundle in bundles:
        print(f"- {bundle.bundle_id}")
    print(f"- {output_dir}")


if __name__ == "__main__":
    main()
