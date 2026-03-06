from __future__ import annotations

from typing import Dict, Type

from brain_ground_zero.baselines.base import Baseline, BaselineSpec, BudgetSpec
from brain_ground_zero.baselines.oracle import OracleBaseline
from brain_ground_zero.baselines.vector_rag import VectorRagBaseline
from brain_ground_zero.baselines.vector_rerank import VectorRerankBaseline
from brain_ground_zero.baselines.heuristic_stateful import HeuristicStatefulBaseline
from brain_ground_zero.baselines.static_graph import StaticGraphBaseline
from brain_ground_zero.baselines.route_fn_only import RouteFnOnlyBaseline
from brain_ground_zero.baselines.graph_route_pg import GraphRoutePGBaseline
from brain_ground_zero.baselines.full_brain import FullBrainBaseline

_REGISTRY: Dict[str, Type[Baseline]] = {
    "oracle": OracleBaseline,
    "vector_rag": VectorRagBaseline,
    "vector_rag_rerank": VectorRerankBaseline,
    "heuristic_stateful": HeuristicStatefulBaseline,
    "static_graph": StaticGraphBaseline,
    "route_fn_only": RouteFnOnlyBaseline,
    "graph_route_pg": GraphRoutePGBaseline,
    "full_brain": FullBrainBaseline,
}


def create_baseline(spec: BaselineSpec, budget: BudgetSpec, seed: int) -> Baseline:
    if spec.kind not in _REGISTRY:
        raise ValueError(f"Unknown baseline kind: {spec.kind}")
    return _REGISTRY[spec.kind](spec, budget, seed)

