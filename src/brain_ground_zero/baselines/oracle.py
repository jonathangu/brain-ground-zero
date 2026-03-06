from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.models import Answer, Fact, Query


class OracleBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        self._world_state = dict(world_state)

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        for fact in updates + corrections:
            key = f"{fact.subject}::{fact.object}"
            self._world_state[key] = fact

    def answer(self, step: int, query: Query) -> Answer:
        key = f"{query.subject}::{query.object}"
        fact = self._world_state.get(key)
        relation = fact.relation if fact else None
        return Answer(relation=relation, source="oracle", context_used=1, traversal_cost=1)

