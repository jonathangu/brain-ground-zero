from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fact:
    subject: str
    object: str
    relation: str
    time: int
    source: str


@dataclass(frozen=True)
class Query:
    subject: str
    object: str


@dataclass
class Answer:
    relation: Optional[str]
    source: str
    context_used: int
    traversal_cost: int


@dataclass
class Correction:
    fact: Fact
    deliver_at: int

