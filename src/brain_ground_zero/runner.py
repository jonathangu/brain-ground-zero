from __future__ import annotations

from pathlib import Path
from typing import Optional

from brain_ground_zero.config import RunConfig


class RunNotImplemented(RuntimeError):
    pass


def run_benchmark(run_config: RunConfig, run_id: Optional[str] = None, smoke: bool = False) -> Path:
    raise RunNotImplemented("Runner not implemented yet")

