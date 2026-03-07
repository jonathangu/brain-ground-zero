from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from brain_ground_zero.models import Fact, Query


@dataclass
class Step:
    step: int
    updates: List[Fact]
    queries: List[Query]
    answers: List[str]
    previous_relations: List[str | None]
    feedback_mask: List[bool] | None = None


@dataclass
class FamilySpec:
    name: str
    params: Dict[str, int | float | str | bool]


class BenchmarkFamily(ABC):
    def __init__(self, spec: FamilySpec, seed: int):
        self.spec = spec
        self.seed = seed

    @abstractmethod
    def build_world(self) -> Dict[str, Fact]:
        """Return initial world state as mapping key -> Fact."""

    @abstractmethod
    def build_steps(self, world_state: Dict[str, Fact]) -> List[Step]:
        """Return ordered steps with updates and queries."""
