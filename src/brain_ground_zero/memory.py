from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

from brain_ground_zero.models import Fact, Query


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _hash_token(token: str, dim: int) -> int:
    digest = hashlib.md5(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "little") % dim


def embed(text: str, dim: int) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return vec
    for token in tokens:
        idx = _hash_token(token, dim)
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


class VectorIndex:
    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._vectors: List[np.ndarray] = []
        self._facts: List[Fact] = []

    def add(self, fact: Fact) -> None:
        text = f"{fact.subject} {fact.object}"
        self._vectors.append(embed(text, self.dim))
        self._facts.append(fact)

    def add_many(self, facts: Iterable[Fact]) -> None:
        for fact in facts:
            self.add(fact)

    def query(self, query: Query, top_k: int) -> List[Fact]:
        if not self._facts:
            return []
        q_vec = embed(f"{query.subject} {query.object}", self.dim)
        mat = np.vstack(self._vectors)
        scores = mat @ q_vec
        if top_k <= 0:
            return []
        idx = np.argsort(scores)[-top_k:][::-1]
        return [self._facts[i] for i in idx]

    def __len__(self) -> int:
        return len(self._facts)


class SlidingVectorIndex(VectorIndex):
    def __init__(self, dim: int, max_items: int) -> None:
        super().__init__(dim)
        self.max_items = max_items

    def add(self, fact: Fact) -> None:
        super().add(fact)
        if len(self._facts) > self.max_items:
            self._facts = self._facts[-self.max_items :]
            self._vectors = self._vectors[-self.max_items :]


@dataclass
class GraphEdge:
    relation: str
    weight: float
    last_updated: int
    history: List[str] = field(default_factory=list)


class GraphMemory:
    def __init__(
        self,
        allow_new_edges: bool,
        enable_structural: bool,
        decay_rate: float = 0.0,
        prune_threshold: float = 0.0,
        cofire_boost: float = 0.0,
        merge_threshold: float = 1.0,
        split_threshold: float = 1.0,
    ) -> None:
        self.allow_new_edges = allow_new_edges
        self.enable_structural = enable_structural
        self.decay_rate = decay_rate
        self.prune_threshold = prune_threshold
        self.cofire_boost = cofire_boost
        self.merge_threshold = merge_threshold
        self.split_threshold = split_threshold
        self.edges: Dict[str, Dict[str, GraphEdge]] = {}

    def add_fact(self, fact: Fact) -> None:
        key = f"{fact.subject}::{fact.object}"
        if key not in self.edges:
            if not self.allow_new_edges:
                return
            self.edges[key] = {}
        variants = self.edges[key]

        if not self.enable_structural:
            variants.clear()
            variants[fact.relation] = GraphEdge(
                relation=fact.relation,
                weight=1.0,
                last_updated=fact.time,
                history=[fact.relation],
            )
            return

        if fact.relation in variants:
            edge = variants[fact.relation]
            edge.weight += 1.0
            edge.last_updated = fact.time
            edge.history.append(fact.relation)
            return

        if variants:
            weights = [edge.weight for edge in variants.values()]
            total = sum(weights) if weights else 0.0
            dominant = max(weights) if weights else 0.0
            dominant_ratio = dominant / total if total > 0 else 0.0
            conflict = 1.0 - dominant_ratio
            if conflict < self.split_threshold:
                variants.clear()
        variants[fact.relation] = GraphEdge(
            relation=fact.relation,
            weight=1.0,
            last_updated=fact.time,
            history=[fact.relation],
        )

    def get_relation(self, subject: str, object_: str) -> Tuple[Optional[str], int]:
        key = f"{subject}::{object_}"
        variants = self.edges.get(key)
        if not variants:
            return None, 2
        best = max(variants.values(), key=lambda e: (e.weight, e.last_updated))
        return best.relation, 1

    def decay(self) -> None:
        if self.decay_rate <= 0:
            return
        for variants in self.edges.values():
            for edge in variants.values():
                edge.weight *= max(0.0, 1.0 - self.decay_rate)

    def cofire(self, facts: List[Fact]) -> None:
        if self.cofire_boost <= 0:
            return
        for fact in facts:
            key = f"{fact.subject}::{fact.object}"
            variants = self.edges.get(key)
            if not variants:
                continue
            if fact.relation in variants:
                variants[fact.relation].weight += self.cofire_boost

    def merge_prune(self) -> None:
        if not self.enable_structural:
            return
        for key in list(self.edges.keys()):
            variants = self.edges[key]
            if not variants:
                del self.edges[key]
                continue
            total = sum(edge.weight for edge in variants.values())
            if total > 0:
                dominant = max(variants.values(), key=lambda e: e.weight)
                if dominant.weight / total >= self.merge_threshold:
                    self.edges[key] = {dominant.relation: dominant}
                    variants = self.edges[key]
            for rel in list(variants.keys()):
                if variants[rel].weight < self.prune_threshold:
                    del variants[rel]
            if not variants:
                del self.edges[key]

