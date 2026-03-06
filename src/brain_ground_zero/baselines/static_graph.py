from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import GraphMemory
from brain_ground_zero.models import Answer, Fact, Query


class StaticGraphBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        self.max_hops = int(self.spec.params.get("max_hops", 2))
        self.graph = GraphMemory(
            allow_new_edges=False,
            enable_structural=False,
        )
        for fact in world_state.values():
            self.graph.add_fact(fact)

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        # Static graph does not update after init
        return None

    def answer(self, step: int, query: Query) -> Answer:
        relation, traversal = self.graph.get_relation(query.subject, query.object)
        context_used = 1 if relation else 0
        traversal_cost = traversal if relation else self.max_hops
        return Answer(
            relation=relation,
            source="static_graph",
            context_used=context_used,
            traversal_cost=traversal_cost,
        )

