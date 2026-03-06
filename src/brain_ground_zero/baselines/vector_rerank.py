from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import VectorIndex
from brain_ground_zero.models import Answer, Fact, Query


class VectorRerankBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        dim = int(self.spec.params.get("dim", 256))
        self.top_k = int(self.spec.params.get("top_k", 5))
        self.rerank_k = int(self.spec.params.get("rerank_k", 3))
        self.index = VectorIndex(dim)
        self.index.add_many(world_state.values())

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        self.index.add_many(updates + corrections)

    def _rerank_score(self, fact: Fact, query: Query) -> int:
        score = 0
        if fact.subject == query.subject:
            score += 1
        if fact.object == query.object:
            score += 1
        return score

    def answer(self, step: int, query: Query) -> Answer:
        candidates = self.index.query(query, self.top_k)
        if not candidates:
            return Answer(relation=None, source="vector_rerank", context_used=0, traversal_cost=0)
        rerank_slice = candidates[: self.rerank_k]
        reranked = sorted(
            rerank_slice,
            key=lambda f: (self._rerank_score(f, query)),
            reverse=True,
        )
        relation = reranked[0].relation if reranked else candidates[0].relation
        context_used = min(len(candidates), self.top_k)
        traversal_cost = context_used + len(rerank_slice)
        return Answer(
            relation=relation,
            source="vector_rerank",
            context_used=context_used,
            traversal_cost=traversal_cost,
        )

