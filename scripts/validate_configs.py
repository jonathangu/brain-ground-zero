from __future__ import annotations

import sys
from pathlib import Path

from brain_ground_zero.config import load_run_config


def main() -> int:
    family = Path("configs/families/relational_drift.yaml")
    baselines = Path("configs/baselines/all.yaml")
    system = Path("configs/systems/default.yaml")
    cfg = load_run_config(family, baselines, system)
    if "name" not in cfg.family or "params" not in cfg.family:
        print("Family config missing required keys")
        return 1
    if "baselines" not in cfg.baselines:
        print("Baseline config missing baselines list")
        return 1
    print("Config validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

