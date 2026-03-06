from __future__ import annotations

import random
from typing import Dict, List, Tuple

from brain_ground_zero.families.base import BenchmarkFamily, Step
from brain_ground_zero.models import Fact, Query


class RelationalDriftFamily(BenchmarkFamily):
    def build_world(self) -> Dict[str, Fact]:
        rng = random.Random(self.seed)
        params = self.spec.params
        num_entities = int(params["num_entities"])
        relation_types = list(params["relation_types"])
        initial_density = float(params["initial_density"])

        entities = [f"E{i:03d}" for i in range(num_entities)]
        all_pairs: List[Tuple[str, str]] = [
            (s, o) for s in entities for o in entities if s != o
        ]
        rng.shuffle(all_pairs)
        target_edges = max(1, int(len(all_pairs) * initial_density))

        world_state: Dict[str, Fact] = {}
        self._history: Dict[str, List[str]] = {}

        for s, o in all_pairs[:target_edges]:
            relation = rng.choice(relation_types)
            key = f"{s}::{o}"
            fact = Fact(subject=s, object=o, relation=relation, time=0, source="init")
            world_state[key] = fact
            self._history[key] = [relation]

        self._entities = entities
        self._relation_types = relation_types
        return world_state

    def build_steps(self, world_state: Dict[str, Fact]) -> List[Step]:
        rng = random.Random(self.seed + 1)
        params = self.spec.params
        steps = int(params["steps"])
        updates_per_step = int(params["updates_per_step"])
        queries_per_step = int(params["queries_per_step"])
        drift_rate = float(params["drift_rate"])
        contradiction_rate = float(params["contradiction_rate"])

        history = {k: list(v) for k, v in self._history.items()}
        current = dict(world_state)
        all_pairs = [(s, o) for s in self._entities for o in self._entities if s != o]
        pair_pool = set(f"{s}::{o}" for s, o in all_pairs)

        steps_out: List[Step] = []
        for step_idx in range(1, steps + 1):
            updates: List[Fact] = []

            for _ in range(updates_per_step):
                use_drift = rng.random() < drift_rate and len(current) > 0
                if use_drift:
                    key = rng.choice(list(current.keys()))
                    fact = current[key]
                    prev_rel = fact.relation
                    if rng.random() < contradiction_rate and len(history[key]) > 1:
                        candidates = [r for r in history[key] if r != prev_rel]
                        new_rel = rng.choice(candidates) if candidates else prev_rel
                    else:
                        choices = [r for r in self._relation_types if r != prev_rel]
                        new_rel = rng.choice(choices) if choices else prev_rel
                    new_fact = Fact(
                        subject=fact.subject,
                        object=fact.object,
                        relation=new_rel,
                        time=step_idx,
                        source="update",
                    )
                    current[key] = new_fact
                    history[key].append(new_rel)
                    updates.append(new_fact)
                else:
                    available = list(pair_pool - set(current.keys()))
                    if not available:
                        key = rng.choice(list(current.keys()))
                        fact = current[key]
                        new_rel = rng.choice(self._relation_types)
                        new_fact = Fact(
                            subject=fact.subject,
                            object=fact.object,
                            relation=new_rel,
                            time=step_idx,
                            source="update",
                        )
                        current[key] = new_fact
                        history[key].append(new_rel)
                        updates.append(new_fact)
                        continue

                    key = rng.choice(available)
                    subject, object_ = key.split("::")
                    relation = rng.choice(self._relation_types)
                    new_fact = Fact(
                        subject=subject,
                        object=object_,
                        relation=relation,
                        time=step_idx,
                        source="update",
                    )
                    current[key] = new_fact
                    history[key] = [relation]
                    updates.append(new_fact)

            queries: List[Query] = []
            answers: List[str] = []
            previous_relations: List[str | None] = []

            update_keys = [f"{f.subject}::{f.object}" for f in updates]
            for _ in range(queries_per_step):
                if update_keys and rng.random() < 0.5:
                    key = rng.choice(update_keys)
                else:
                    key = rng.choice(list(current.keys()))
                subject, object_ = key.split("::")
                queries.append(Query(subject=subject, object=object_))
                answers.append(current[key].relation)
                prev = history[key][-2] if len(history[key]) > 1 else None
                previous_relations.append(prev)

            steps_out.append(
                Step(
                    step=step_idx,
                    updates=updates,
                    queries=queries,
                    answers=answers,
                    previous_relations=previous_relations,
                )
            )

        self._history = history
        return steps_out

