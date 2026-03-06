from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List

from brain_ground_zero.models import Answer, Fact, Query


@dataclass
class BaselineSpec:
    name: str
    kind: str
    capabilities: Dict[str, bool]
    params: Dict[str, float | int | str | bool]


@dataclass
class BudgetSpec:
    context_budget: int
    teacher_budget: int
    teacher_delay: int


class Baseline(ABC):
    def __init__(self, spec: BaselineSpec, budget: BudgetSpec, seed: int):
        self.spec = spec
        self.budget = budget
        self.seed = seed

    @abstractmethod
    def reset(self, world_state: Dict[str, Fact]) -> None:
        """Initialize internal memory from the world state."""

    @abstractmethod
    def observe(self, step: int, updates: List[Fact], corrections: List[Fact]) -> None:
        """Ingest updates and teacher corrections."""

    @abstractmethod
    def answer(self, step: int, query: Query) -> Answer:
        """Return an answer with context and traversal cost proxies."""

    def on_feedback(self, step: int, query: Query, correct: bool, truth: str, answer: Answer) -> None:
        """Optional hook for policy-gradient updates or learning signals."""
        return None

    def supports_teacher(self) -> bool:
        return bool(self.spec.capabilities.get("teacher", False))

    def supports_background_labels(self) -> bool:
        return bool(self.spec.capabilities.get("background_labels", False))

