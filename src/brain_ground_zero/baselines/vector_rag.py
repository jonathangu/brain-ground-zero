from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import VectorIndex
from brain_ground_zero.models import Answer, Fact, Query


class VectorRagBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        dim = int(self.spec.params.get("dim", 256))
        self.top_k = int(self.spec.params.get("top_k", 1))
        self.index = VectorIndex(dim)
        self.index.add_many(world_state.values())

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        self.index.add_many(updates + corrections)

    def answer(self, step: int, query: Query) -> Answer:
        results = self.index.query(query, self.top_k)
        relation = results[0].relation if results else None
        context_used = min(len(results), self.top_k)
        traversal_cost = context_used
        return Answer(relation=relation, source="vector", context_used=context_used, traversal_cost=traversal_cost)

