from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigError(RuntimeError):
    pass


@dataclass
class RunConfig:
    family: Dict[str, Any]
    baselines: Dict[str, Any]
    system: Dict[str, Any]


def _load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_run_config(family_path: str | Path, baselines_path: str | Path, system_path: str | Path | None) -> RunConfig:
    family = _load_yaml(family_path)
    baselines = _load_yaml(baselines_path)
    system = _load_yaml(system_path) if system_path else {}
    return RunConfig(family=family, baselines=baselines, system=system)


def write_config_snapshot(run_dir: Path, run_config: RunConfig) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "family": run_config.family,
        "baselines": run_config.baselines,
        "system": run_config.system,
    }
    (run_dir / "config_snapshot.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )

