#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:-recorded_h2h_relational_drift_10seed}"
SEEDS="${SEEDS:-11,22,33,44,55,66,77,88,99,111}"
FAMILY="${FAMILY:-configs/families/relational_drift.yaml}"
BASELINES="${BASELINES:-configs/baselines/all.yaml}"
OUTPUT_ROOT="${OUTPUT_ROOT:-runs}"

RUN_DIR="${OUTPUT_ROOT}/${RUN_ID}"
PROOF_DIR="proof-results/${RUN_ID}"

echo "[1/6] Running recorded_h2h multi-seed replay: ${RUN_ID}"
PYTHONPATH=src python3 -m brain_ground_zero.cli recorded_h2h_multiseed \
  --family "${FAMILY}" \
  --baselines "${BASELINES}" \
  --seeds "${SEEDS}" \
  --run-id "${RUN_ID}" \
  --output-dir "${OUTPUT_ROOT}" \
  --status publishable

echo "[2/6] Syncing artifacts to ${PROOF_DIR}"
RUN_DIR_ENV="${RUN_DIR}" PROOF_DIR_ENV="${PROOF_DIR}" python3 - <<'PY'
import os
import shutil
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ENV"])
proof_dir = Path(os.environ["PROOF_DIR_ENV"])
proof_dir.mkdir(parents=True, exist_ok=True)

root_files = [
    "summary.json",
    "per_seed_summaries.json",
    "seeds.json",
    "config_snapshot.json",
    "seed_bundle_index.csv",
    "seed_bundle_index.md",
]
for rel in root_files:
    src = run_dir / rel
    if src.exists():
        shutil.copy2(src, proof_dir / rel)

artifacts_dir = run_dir / "artifacts"
if artifacts_dir.exists():
    for src in artifacts_dir.iterdir():
        if src.is_file():
            shutil.copy2(src, proof_dir / src.name)

for seed_dir in sorted(path for path in run_dir.iterdir() if path.is_dir() and path.name.startswith("seed_")):
    target = proof_dir / seed_dir.name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(seed_dir, target)
PY

echo "[3/6] Validating per-seed recorded bundles"
python3 scripts/validate_recorded_h2h.py "${PROOF_DIR}"/seed_*/ | tee "${PROOF_DIR}/seed_bundle_validation.txt"

echo "[4/6] Validating multiseed aggregate bundle"
python3 scripts/validate_recorded_h2h_multiseed.py "${PROOF_DIR}" | tee "${PROOF_DIR}/multiseed_validation.txt"

echo "[5/6] Writing proof README"
RUN_ID_ENV="${RUN_ID}" PROOF_DIR_ENV="${PROOF_DIR}" python3 - <<'PY'
import json
import os
from datetime import date
from pathlib import Path

run_id = os.environ["RUN_ID_ENV"]
proof_dir = Path(os.environ["PROOF_DIR_ENV"])
summary = json.loads((proof_dir / "summary.json").read_text(encoding="utf-8"))
seeds = json.loads((proof_dir / "seeds.json").read_text(encoding="utf-8"))
cfg = json.loads((proof_dir / "config_snapshot.json").read_text(encoding="utf-8"))
params = cfg.get("family", {}).get("params", {})


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"

best_rag = max(
    [name for name in summary if name.startswith("vector_rag")],
    key=lambda name: float(summary[name].get("accuracy", 0.0)),
)
full = summary["full_brain"]
rag = summary[best_rag]

readme = f"""# Proof Artifacts: recorded_h2h relational_drift, {len(seeds)}-seed run

Run date: {date.today().isoformat()}
Seeds: {", ".join(str(seed) for seed in seeds)}
Queries per seed: {int(full.get("total_queries", 0))}
Steps per seed: {params.get("steps", "n/a")} (+ fixture step 0)
Updates/query stream: {params.get("updates_per_step", "n/a")} updates/step, {params.get("queries_per_step", "n/a")} queries/step

## Headline

- full_brain accuracy: **{pct(float(full.get("accuracy", 0.0)))} +/- {pct(float(full.get("accuracy_std", 0.0)))}**
- best RAG (`{best_rag}`) accuracy: **{pct(float(rag.get("accuracy", 0.0)))} +/- {pct(float(rag.get("accuracy_std", 0.0)))}**
- margin: **{(float(full.get("accuracy", 0.0)) - float(rag.get("accuracy", 0.0))) * 100:+.2f} pp**

## Files

- `summary_table.md` / `.csv` -- aggregate metrics for each baseline
- `leaderboard.md` / `.csv` -- ranked publication table with baseline deltas
- `pairwise_accuracy_delta.md` / `.csv` -- pairwise accuracy differences
- `win_rate_matrix.md` / `.csv` -- seed-level head-to-head wins
- `per_seed_breakdown.md` / `.csv` -- long-form per-seed metrics
- `per_seed_accuracy_matrix.md` / `.csv` -- per-seed accuracy matrix
- `proof_digest.md` -- compact narrative summary for paper/blog usage
- `worked_example_trace.md` -- representative relation trace from a recorded seed
- `learning_curve.png` -- mean per-step accuracy over seeds with std bands
- `seed_bundle_index.md` / `.csv` -- index linking each seed to its deterministic replay bundle
- `seed_bundle_validation.txt` -- per-seed validator output
- `multiseed_validation.txt` -- aggregate validator output
- `seed_<N>/` -- full recorded bundle for each seed (fixture, traces, scoring, verification)

## Reproduce

```bash
./scripts/run_recorded_h2h_proof.sh
```
"""

(proof_dir / "README.md").write_text(readme, encoding="utf-8")
PY

echo "[6/6] Refreshing publishable proof pack"
python3 scripts/generate_publishable_proof_assets.py

echo "Done: ${PROOF_DIR}"
