from __future__ import annotations

from typing import Dict, List

from brain_ground_zero.families.base import BenchmarkFamily, FamilySpec, Step
from brain_ground_zero.models import Fact


class RelationalDriftFamily(BenchmarkFamily):
    def build_world(self) -> Dict[str, Fact]:
        raise NotImplementedError("Relational drift family to be implemented")

    def build_steps(self, world_state: Dict[str, Fact]) -> List[Step]:
        raise NotImplementedError("Relational drift family to be implemented")

