from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.baselines.base import Baseline
from brain_ground_zero.memory import GraphMemory, SlidingVectorIndex, VectorIndex
from brain_ground_zero.models import Answer, Fact, Query
from brain_ground_zero.policy import RoutePolicy


class FullBrainBaseline(Baseline):
    def reset(self, world_state: Dict[str, Fact]) -> None:
        params = self.spec.params
        dim = int(params.get("dim", 256))
        self.top_k = int(params.get("top_k", 1))
        self.short_term_size = int(params.get("short_term_size", 60))
        self.max_hops = int(params.get("max_hops", 2))
        lr = float(params.get("lr", 0.1))
        epsilon = float(params.get("epsilon", 0.05))
        self.label_per_correction = int(params.get("label_per_correction", 2))

        self.policy = RoutePolicy(["graph", "short_term", "vector"], lr, epsilon, self.seed)

        self.graph = GraphMemory(
            allow_new_edges=True,
            enable_structural=True,
            decay_rate=float(params.get("decay_rate", 0.01)),
            prune_threshold=float(params.get("prune_threshold", 0.1)),
            cofire_boost=float(params.get("cofire_boost", 0.2)),
            merge_threshold=float(params.get("merge_threshold", 0.9)),
            split_threshold=float(params.get("split_threshold", 0.3)),
        )
        self.short_term = SlidingVectorIndex(dim, self.short_term_size)
        self.long_term = VectorIndex(dim)
        self._facts_cache: List[Fact] = []
        self._latest_facts: Dict[str, Fact] = {}

        for fact in world_state.values():
            self._ingest_fact(fact)

    def _background_labels(self, step: int, corrections: List[Fact]) -> List[Fact]:
        if not corrections or self.label_per_correction <= 0:
            return []
        labels: List[Fact] = []
        for corr in corrections:
            corr_key = f"{corr.subject}::{corr.object}"
            related = [
                fact
                for key, fact in self._latest_facts.items()
                if key != corr_key and (fact.subject == corr.subject or fact.object == corr.object)
            ]
            related.sort(key=lambda f: f.time, reverse=True)
            for fact in related[: self.label_per_correction]:
                labels.append(
                    Fact(
                        subject=fact.subject,
                        object=fact.object,
                        relation=fact.relation,
                        time=step,
                        source="background",
                    )
                )
        return labels

    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        self.graph.decay()
        background = self._background_labels(step, corrections)
        all_facts = updates + corrections + background
        for fact in all_facts:
            self._ingest_fact(fact)
        self.graph.cofire(all_facts)
        self.graph.merge_prune()

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
        if choice == "short_term":
            results = self.short_term.query(query, self.top_k)
            relation = results[0].relation if results else None
            context_used = min(len(results), self.top_k)
            traversal_cost = context_used
            return Answer(
                relation=relation,
                source="short_term",
                context_used=context_used,
                traversal_cost=traversal_cost,
            )
        results = self.long_term.query(query, self.top_k)
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

    def _ingest_fact(self, fact: Fact) -> None:
        key = f"{fact.subject}::{fact.object}"
        self.graph.add_fact(fact)
        self.short_term.add(fact)
        self.long_term.add(fact)
        self._facts_cache.append(fact)
        current = self._latest_facts.get(key)
        if current is None or fact.time >= current.time:
            self._latest_facts[key] = fact
