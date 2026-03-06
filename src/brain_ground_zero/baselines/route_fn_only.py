from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import SlidingVectorIndex, VectorIndex
from brain_ground_zero.models import Answer, Fact, Query
from brain_ground_zero.policy import RoutePolicy


class RouteFnOnlyBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        dim = int(self.spec.params.get("dim", 256))
        self.top_k = int(self.spec.params.get("top_k", 1))
        self.short_term_size = int(self.spec.params.get("short_term_size", 50))
        lr = float(self.spec.params.get("lr", 0.1))
        epsilon = float(self.spec.params.get("epsilon", 0.05))
        self.policy = RoutePolicy(["short_term", "long_term"], lr, epsilon, self.seed)

        self.short_term = SlidingVectorIndex(dim, self.short_term_size)
        self.long_term = VectorIndex(dim)
        self.short_term.add_many(world_state.values())
        self.long_term.add_many(world_state.values())

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        facts = updates + corrections
        for fact in facts:
            self.short_term.add(fact)
            self.long_term.add(fact)

    def answer(self, step: int, query: Query) -> Answer:
        choice, _ = self.policy.select()
        index = self.short_term if choice == "short_term" else self.long_term
        results = index.query(query, self.top_k)
        relation = results[0].relation if results else None
        context_used = min(len(results), self.top_k)
        traversal_cost = context_used
        return Answer(
            relation=relation,
            source=choice,
            context_used=context_used,
            traversal_cost=traversal_cost,
        )

    def on_feedback(self, step: int, query: Query, correct: bool, truth: str, answer: Answer) -> None:
        reward = 1.0 if correct else 0.0
        self.policy.update(answer.source, reward)

