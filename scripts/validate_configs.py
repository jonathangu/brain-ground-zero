from __future__ import annotations

import sys
from pathlib import Path

from brain_ground_zero.config import load_run_config


def _validate_family(family: Path, baselines: Path, system: Path) -> bool:
    cfg = load_run_config(family, baselines, system)
    if "name" not in cfg.family or "params" not in cfg.family:
        print(f"Family config missing required keys: {family}")
        return False
    if "baselines" not in cfg.baselines:
        print("Baseline config missing baselines list")
        return False
    return True


def main() -> int:
    families = [
        Path("configs/families/relational_drift.yaml"),
        Path("configs/families/recurring_workflows.yaml"),
        Path("configs/families/sparse_feedback.yaml"),
    ]
    baselines = Path("configs/baselines/all.yaml")
    system = Path("configs/systems/default.yaml")
    ok = True
    for family in families:
        if not family.exists():
            print(f"Missing family config: {family}")
            ok = False
            continue
        ok = _validate_family(family, baselines, system) and ok
    if ok:
        print("Config validation OK")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
