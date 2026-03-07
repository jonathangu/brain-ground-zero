#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:-sparse_feedback_10seed}"
SEEDS="${SEEDS:-11,22,33,44,55,66,77,88,99,111}"
FAMILY="${FAMILY:-configs/families/sparse_feedback.yaml}"
BASELINES="${BASELINES:-configs/baselines/all.yaml}"
SYSTEM="${SYSTEM:-configs/systems/default.yaml}"

echo "[1/4] Running multiseed benchmark: ${RUN_ID}"
PYTHONPATH=src python3 -m brain_ground_zero.cli multiseed \
  --family "${FAMILY}" \
  --baselines "${BASELINES}" \
  --system "${SYSTEM}" \
  --seeds "${SEEDS}" \
  --run-id "${RUN_ID}"

RUN_DIR="runs/${RUN_ID}"
PROOF_DIR="proof-results/${RUN_ID}"

echo "[2/4] Syncing artifacts to ${PROOF_DIR}"
mkdir -p "${PROOF_DIR}"
cp "${RUN_DIR}/summary.json" "${PROOF_DIR}/summary.json"
cp "${RUN_DIR}/per_seed_summaries.json" "${PROOF_DIR}/per_seed_summaries.json"
cp "${RUN_DIR}/seeds.json" "${PROOF_DIR}/seeds.json"
cp "${RUN_DIR}/config_snapshot.json" "${PROOF_DIR}/config_snapshot.json"
cp "${RUN_DIR}/artifacts/"* "${PROOF_DIR}/"

echo "[3/4] Writing proof README"
RUN_ID_ENV="${RUN_ID}" python3 - <<'PY'
import csv
import json
import os
from datetime import date
from pathlib import Path

run_id_name = os.environ["RUN_ID_ENV"]
run_id = Path("runs") / run_id_name
proof_dir = Path("proof-results") / run_id_name
summary = json.loads((run_id / "summary.json").read_text(encoding="utf-8"))
seeds = json.loads((run_id / "seeds.json").read_text(encoding="utf-8"))
cfg = json.loads((run_id / "config_snapshot.json").read_text(encoding="utf-8"))
params = cfg.get("family", {}).get("params", {})


def pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


best_rag = max(
    [name for name in summary if name.startswith("vector_rag")],
    key=lambda name: float(summary[name].get("accuracy", 0.0)),
)
full = summary["full_brain"]
rag = summary[best_rag]

seed_matrix_path = run_id / "artifacts" / "per_seed_accuracy_matrix.csv"
h2h_record = "n/a"
if seed_matrix_path.exists():
    with seed_matrix_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    row_map = {row["baseline"]: row for row in rows if row.get("baseline")}
    seed_columns = [column for column in rows[0].keys() if column.startswith("seed_")] if rows else []
    if "full_brain" in row_map and best_rag in row_map and seed_columns:
        full_seed = [float(row_map["full_brain"][column]) for column in seed_columns]
        rag_seed = [float(row_map[best_rag][column]) for column in seed_columns]
        wins = sum(1 for f, r in zip(full_seed, rag_seed) if f > r)
        losses = sum(1 for f, r in zip(full_seed, rag_seed) if f < r)
        ties = sum(1 for f, r in zip(full_seed, rag_seed) if f == r)
        h2h_record = f"{wins}-{losses}-{ties}"

full_context_per_query = safe_div(float(full.get("context_used", 0.0)), float(full.get("total_queries", 0.0)))
rag_context_per_query = safe_div(float(rag.get("context_used", 0.0)), float(rag.get("total_queries", 0.0)))
context_ratio = safe_div(rag_context_per_query, full_context_per_query)
feedback_rate = float(full.get("feedback_rate", 0.0))

readme = f"""# Proof Artifacts: sparse_feedback, {len(seeds)}-seed run

Run date: {date.today().isoformat()}
Seeds: {", ".join(str(seed) for seed in seeds)}
Queries per seed: {int(full.get("total_queries", 0))}
World: {params.get("num_workflows")} workflows, {params.get("steps_per_workflow")} step slots + {params.get("prefs_per_workflow")} preference slots
Stream: {params.get("steps")} steps, {params.get("workflows_per_step")} workflows/step, explicit feedback rate {params.get("explicit_feedback_rate", 0)}, focused feedback rate {params.get("focused_feedback_rate", 0)}
Updates: {params.get("workflow_updates_per_step")} workflows/step, {params.get("step_updates_per_workflow")} step updates + {params.get("pref_updates_per_workflow")} preference updates, contradiction rate {params.get("contradiction_rate", 0)}

## Headline

- full_brain accuracy: **{pct(float(full.get("accuracy", 0.0)))} +/- {pct(float(full.get("accuracy_std", 0.0)))}**
- best RAG (`{best_rag}`) accuracy: **{pct(float(rag.get("accuracy", 0.0)))} +/- {pct(float(rag.get("accuracy_std", 0.0)))}**
- margin: **{(float(full.get("accuracy", 0.0)) - float(rag.get("accuracy", 0.0))) * 100:+.2f} pp**
- context/query: full_brain {full_context_per_query:.2f} vs {best_rag} {rag_context_per_query:.2f} ({context_ratio:.1f}x lower for full_brain)
- full_brain vs {best_rag} head-to-head: **{h2h_record}**
- measured feedback coverage: **{feedback_rate * 100:.2f}%** of queries

## What this tests

Sparse feedback simulates teacher-assisted learning where explicit correctness signals reach only a minority of queries. The full-brain method must convert sparse corrections into stronger future routing under bounded context.

## Publishable assets

- `chart_seed_h2h_full_brain_vs_best_rag.png` -- seed-by-seed dumbbell chart (full_brain vs {best_rag}) showing the head-to-head split
- `publishable_key_results_compact.md` / `.csv` -- one-row compact scorecard for site/blog/paper
- `publishable_key_results.md` / `.csv` -- full machine-readable scorecard row

## Files

- `summary_table.md` / `.csv` -- aggregate metrics for each baseline
- `leaderboard.md` / `.csv` -- ranked publication table with baseline deltas
- `pairwise_accuracy_delta.md` / `.csv` -- pairwise accuracy differences
- `win_rate_matrix.md` / `.csv` -- seed-level head-to-head wins
- `per_seed_breakdown.md` / `.csv` -- long-form per-seed metrics
- `per_seed_accuracy_matrix.md` / `.csv` -- per-seed accuracy matrix
- `proof_digest.md` -- compact narrative summary for paper/blog usage
- `worked_example_trace.md` -- representative workflow-slot trace
- `learning_curve.png` -- mean accuracy over steps with std bands
- `seeds.json` -- exact seed list

## Reproduce

```bash
./scripts/run_sparse_feedback_proof.sh
```
"""

(proof_dir / "README.md").write_text(readme, encoding="utf-8")
PY

echo "[4/4] Refreshing publishable proof pack"
python3 scripts/generate_publishable_proof_assets.py

echo "Done: ${PROOF_DIR}"
