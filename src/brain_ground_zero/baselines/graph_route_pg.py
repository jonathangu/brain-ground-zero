from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import GraphMemory, VectorIndex
from brain_ground_zero.models import Answer, Fact, Query
from brain_ground_zero.policy import RoutePolicy


class GraphRoutePGBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        dim = int(self.spec.params.get("dim", 256))
        self.top_k = int(self.spec.params.get("top_k", 1))
        self.max_hops = int(self.spec.params.get("max_hops", 2))
        lr = float(self.spec.params.get("lr", 0.1))
        epsilon = float(self.spec.params.get("epsilon", 0.05))
        self.policy = RoutePolicy(["graph", "vector"], lr, epsilon, self.seed)

        self.graph = GraphMemory(
            allow_new_edges=False,
            enable_structural=False,
        )
        self.vector = VectorIndex(dim)
        for fact in world_state.values():
            self.graph.add_fact(fact)
            self.vector.add(fact)

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        for fact in updates + corrections:
            self.graph.add_fact(fact)
            self.vector.add(fact)

    def answer(self, step: int, query: Query) -> Answer:
        choice, _ = self.policy.select()
        if choice == "graph":
            relation, traversal = self.graph.get_relation(query.subject, query.object)
            context_used = 1 if relation else 0
            traversal_cost = traversal if relation else self.max_hops
            return Answer(
                relation=relation,
                source="graph",
                context_used=context_used,
                traversal_cost=traversal_cost,
            )
        results = self.vector.query(query, self.top_k)
        relation = results[0].relation if results else None
        context_used = min(len(results), self.top_k)
        traversal_cost = context_used
        return Answer(
            relation=relation,
            source="vector",
            context_used=context_used,
            traversal_cost=traversal_cost,
        )

    def on_feedback(self, step: int, query: Query, correct: bool, truth: str, answer: Answer) -> None:
        reward = 1.0 if correct else 0.0
        self.policy.update(answer.source, reward)

