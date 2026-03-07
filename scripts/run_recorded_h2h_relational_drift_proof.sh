#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:-recorded_h2h_relational_drift_001}"
FAMILY="${FAMILY:-configs/families/relational_drift.yaml}"
SEED="${SEED:-42}"
BASELINES="${BASELINES:-configs/baselines/all.yaml}"
PROOF_DIR="proof-results/${RUN_ID}"

echo "[1/4] Generating deterministic fixture (family=${FAMILY}, seed=${SEED})"
mkdir -p "${PROOF_DIR}"
PYTHONPATH=src python3 -m brain_ground_zero.cli generate_fixture \
  --family "${FAMILY}" \
  --seed "${SEED}" \
  --output "${PROOF_DIR}/fixture.yaml"

echo "[2/4] Running recorded head-to-head bundle: ${RUN_ID}"
PYTHONPATH=src python3 -m brain_ground_zero.cli recorded_h2h \
  --fixture "${PROOF_DIR}/fixture.yaml" \
  --baselines "${BASELINES}" \
  --output "${PROOF_DIR}"

echo "[3/4] Validating recorded bundle"
python3 scripts/validate_recorded_h2h.py "${PROOF_DIR}"

echo "[4/4] Refreshing publishable proof pack"
python3 scripts/generate_publishable_proof_assets.py

echo "Done: ${PROOF_DIR}"
