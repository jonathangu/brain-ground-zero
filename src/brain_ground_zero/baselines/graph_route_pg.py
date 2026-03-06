from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.models import Answer, Fact, Query


class GraphRoutePGBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        self._world_state = dict(world_state)

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        return None

    def answer(self, step: int, query: Query) -> Answer:
        raise NotImplementedError("Graph route PG baseline to be implemented")

