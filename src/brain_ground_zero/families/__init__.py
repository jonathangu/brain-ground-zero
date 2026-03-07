from __future__ import annotations

from typing import Dict, Type

from brain_ground_zero.families.base import BenchmarkFamily, FamilySpec
from brain_ground_zero.families.recurring_workflows import RecurringWorkflowsFamily
from brain_ground_zero.families.relational_drift import RelationalDriftFamily
from brain_ground_zero.families.sparse_feedback import SparseFeedbackFamily

_REGISTRY: Dict[str, Type[BenchmarkFamily]] = {
    "relational_drift": RelationalDriftFamily,
    "recurring_workflows": RecurringWorkflowsFamily,
    "sparse_feedback": SparseFeedbackFamily,
}


def create_family(spec: FamilySpec, seed: int) -> BenchmarkFamily:
    if spec.name not in _REGISTRY:
        raise ValueError(f"Unknown family: {spec.name}")
    return _REGISTRY[spec.name](spec, seed)
