from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.models import Answer, Fact, Query


class HeuristicStatefulBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        self.memory: Dict[str, str] = {
            f"{fact.subject}::{fact.object}": fact.relation for fact in world_state.values()
        }
        self.pending: Dict[str, Dict[str, int]] = {}
        self.threshold = int(self.spec.params.get("update_threshold", 2))

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        for fact in updates + corrections:
            key = f"{fact.subject}::{fact.object}"
            if key not in self.memory:
                self.memory[key] = fact.relation
                continue
            if self.memory[key] == fact.relation:
                continue
            pending = self.pending.setdefault(key, {})
            pending[fact.relation] = pending.get(fact.relation, 0) + 1
            if pending[fact.relation] >= self.threshold:
                self.memory[key] = fact.relation
                self.pending[key] = {fact.relation: pending[fact.relation]}

    def answer(self, step: int, query: Query) -> Answer:
        key = f"{query.subject}::{query.object}"
        relation = self.memory.get(key)
        context_used = 1 if relation else 0
        traversal_cost = 1 if relation else 1
        return Answer(
            relation=relation,
            source="heuristic_stateful",
            context_used=context_used,
            traversal_cost=traversal_cost,
        )

