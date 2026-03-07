from __future__ import annotations

import random
from typing import Dict, Iterable, List, Set

from brain_ground_zero.families.base import BenchmarkFamily, Step
from brain_ground_zero.models import Fact, Query


class RecurringWorkflowsFamily(BenchmarkFamily):
    def build_world(self) -> Dict[str, Fact]:
        rng = random.Random(self.seed)
        params = self.spec.params
        _validate_params(params)

        num_workflows = int(params["num_workflows"])
        steps_per_workflow = int(params["steps_per_workflow"])
        prefs_per_workflow = int(params.get("prefs_per_workflow", 0))
        action_types = list(params["action_types"])
        preference_types = list(params.get("preference_types", action_types)) or action_types
        hot_workflow_fraction = float(params.get("hot_workflow_fraction", 0.0))

        workflows = [f"W{i:03d}" for i in range(num_workflows)]
        step_slots = [f"step_{i:02d}" for i in range(steps_per_workflow)]
        pref_slots = [f"pref_{i:02d}" for i in range(prefs_per_workflow)]

        world_state: Dict[str, Fact] = {}
        history: Dict[str, List[str]] = {}

        for workflow in workflows:
            for slot in step_slots:
                relation = rng.choice(action_types)
                key = f"{workflow}::{slot}"
                fact = Fact(subject=workflow, object=slot, relation=relation, time=0, source="init")
                world_state[key] = fact
                history[key] = [relation]
            for slot in pref_slots:
                relation = rng.choice(preference_types)
                key = f"{workflow}::{slot}"
                fact = Fact(subject=workflow, object=slot, relation=relation, time=0, source="init")
                world_state[key] = fact
                history[key] = [relation]

        self._workflows = workflows
        self._step_slots = step_slots
        self._pref_slots = pref_slots
        self._action_types = action_types
        self._preference_types = preference_types
        self._history = history
        hot_count = min(len(workflows), int(round(len(workflows) * hot_workflow_fraction)))
        self._hot_workflows: Set[str] = set(rng.sample(workflows, hot_count)) if hot_count > 0 else set()
        return world_state

    def build_steps(self, world_state: Dict[str, Fact]) -> List[Step]:
        rng = random.Random(self.seed + 1)
        params = self.spec.params
        _validate_params(params)

        steps = int(params["steps"])
        workflows_per_step = int(params["workflows_per_step"])
        workflow_updates_per_step = int(params["workflow_updates_per_step"])
        step_updates_per_workflow = int(params["step_updates_per_workflow"])
        pref_updates_per_workflow = int(params.get("pref_updates_per_workflow", 0))
        query_steps_per_workflow = int(params["query_steps_per_workflow"])
        query_prefs_per_workflow = int(params.get("query_prefs_per_workflow", 0))
        recurrence_bias = float(params.get("recurrence_bias", 0.7))
        recent_window = int(params.get("recent_window", max(4, workflows_per_step * 2)))
        update_query_ratio = float(params.get("update_query_ratio", 0.6))
        contradiction_rate = float(params.get("contradiction_rate", 0.15))
        hot_workflow_bias = float(params.get("hot_workflow_bias", 0.0))
        update_recurrence_bias = float(params.get("update_recurrence_bias", recurrence_bias))
        replay_queries_per_workflow = int(params.get("replay_queries_per_workflow", 0))
        burst_update_prob = float(params.get("burst_update_prob", 0.0))
        burst_update_workflows = int(params.get("burst_update_workflows", 0))

        current = dict(world_state)
        history = {k: list(v) for k, v in self._history.items()}
        recent_workflows: List[str] = []
        last_queried_slots: Dict[str, List[str]] = {}

        steps_out: List[Step] = []
        for step_idx in range(1, steps + 1):
            updates: List[Fact] = []
            updated_slots_by_workflow: Dict[str, Dict[str, List[str]]] = {}

            update_count = min(workflow_updates_per_step, len(self._workflows))
            if burst_update_workflows > 0 and rng.random() < burst_update_prob:
                update_count = min(len(self._workflows), update_count + burst_update_workflows)
            workflows_to_update = _select_workflows(
                rng,
                self._workflows,
                recent_workflows,
                update_count,
                update_recurrence_bias,
                hot_workflows=self._hot_workflows,
                hot_bias=hot_workflow_bias,
            )

            for workflow in workflows_to_update:
                updated_slots_by_workflow.setdefault(workflow, {"steps": [], "prefs": []})

                step_count = min(step_updates_per_workflow, len(self._step_slots))
                if step_count > 0:
                    for slot in rng.sample(self._step_slots, step_count):
                        key = f"{workflow}::{slot}"
                        fact = current[key]
                        new_rel = _select_new_relation(
                            rng,
                            fact.relation,
                            history[key],
                            self._action_types,
                            contradiction_rate,
                        )
                        new_fact = Fact(
                            subject=workflow,
                            object=slot,
                            relation=new_rel,
                            time=step_idx,
                            source="update",
                        )
                        current[key] = new_fact
                        history[key].append(new_rel)
                        updates.append(new_fact)
                        updated_slots_by_workflow[workflow]["steps"].append(slot)

                pref_count = min(pref_updates_per_workflow, len(self._pref_slots))
                if pref_count > 0:
                    for slot in rng.sample(self._pref_slots, pref_count):
                        key = f"{workflow}::{slot}"
                        fact = current[key]
                        new_rel = _select_new_relation(
                            rng,
                            fact.relation,
                            history[key],
                            self._preference_types,
                            contradiction_rate,
                        )
                        new_fact = Fact(
                            subject=workflow,
                            object=slot,
                            relation=new_rel,
                            time=step_idx,
                            source="update",
                        )
                        current[key] = new_fact
                        history[key].append(new_rel)
                        updates.append(new_fact)
                        updated_slots_by_workflow[workflow]["prefs"].append(slot)

            for workflow in workflows_to_update:
                _touch_recent(recent_workflows, workflow, recent_window)

            run_count = min(workflows_per_step, len(self._workflows))
            workflows_to_run = _select_workflows(
                rng,
                self._workflows,
                recent_workflows,
                run_count,
                recurrence_bias,
                hot_workflows=self._hot_workflows,
                hot_bias=hot_workflow_bias,
            )

            for workflow in workflows_to_run:
                _touch_recent(recent_workflows, workflow, recent_window)

            queries: List[Query] = []
            answers: List[str] = []
            previous_relations: List[str | None] = []

            for workflow in workflows_to_run:
                updated = updated_slots_by_workflow.get(workflow, {"steps": [], "prefs": []})
                step_slots = _select_slots(
                    rng,
                    self._step_slots,
                    updated["steps"],
                    query_steps_per_workflow,
                    update_query_ratio,
                )
                pref_slots = _select_slots(
                    rng,
                    self._pref_slots,
                    updated["prefs"],
                    query_prefs_per_workflow,
                    update_query_ratio,
                )
                selected_slots = step_slots + pref_slots
                replay_slots = _select_replay_slots(
                    rng,
                    last_queried_slots.get(workflow, []),
                    selected_slots,
                    replay_queries_per_workflow,
                )
                for slot in selected_slots + replay_slots:
                    key = f"{workflow}::{slot}"
                    fact = current[key]
                    queries.append(Query(subject=workflow, object=slot))
                    answers.append(fact.relation)
                    prev = history[key][-2] if len(history[key]) > 1 else None
                    previous_relations.append(prev)
                last_queried_slots[workflow] = selected_slots + replay_slots

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


def _select_new_relation(
    rng: random.Random,
    current: str,
    history: List[str],
    candidates: List[str],
    contradiction_rate: float,
) -> str:
    if rng.random() < contradiction_rate:
        prior = [rel for rel in history if rel != current]
        if prior:
            return rng.choice(prior)
    choices = [rel for rel in candidates if rel != current]
    return rng.choice(choices) if choices else current


def _touch_recent(recent: List[str], workflow: str, max_len: int) -> None:
    if workflow in recent:
        recent.remove(workflow)
    recent.append(workflow)
    if len(recent) > max_len:
        del recent[:-max_len]


def _select_workflows(
    rng: random.Random,
    workflows: List[str],
    recent: List[str],
    count: int,
    recurrence_bias: float,
    hot_workflows: Set[str] | None = None,
    hot_bias: float = 0.0,
) -> List[str]:
    if count <= 0:
        return []
    available = set(workflows)
    hot = hot_workflows or set()
    hot_weight = max(0.0, 1.0 + hot_bias)
    chosen: List[str] = []
    attempts = 0
    while len(chosen) < count and available and attempts < count * 10:
        attempts += 1
        if recent and rng.random() < recurrence_bias:
            candidate = _weighted_choice(rng, recent, hot, hot_weight)
        else:
            candidate = _weighted_choice(rng, workflows, hot, hot_weight)
        if candidate in available:
            chosen.append(candidate)
            available.remove(candidate)
    if len(chosen) < count and available:
        remaining = list(available)
        rng.shuffle(remaining)
        chosen.extend(remaining[: count - len(chosen)])
    return chosen


def _select_slots(
    rng: random.Random,
    slots: List[str],
    updated_slots: List[str],
    count: int,
    update_query_ratio: float,
) -> List[str]:
    if count <= 0 or not slots:
        return []
    count = min(count, len(slots))
    remaining = list(slots)
    updated = [s for s in updated_slots if s in remaining]
    chosen: List[str] = []
    for _ in range(count):
        use_updated = updated and rng.random() < update_query_ratio
        if use_updated:
            slot = rng.choice(updated)
        else:
            slot = rng.choice(remaining)
        if slot in remaining:
            remaining.remove(slot)
        if slot in updated:
            updated.remove(slot)
        chosen.append(slot)
    return chosen


def _select_replay_slots(
    rng: random.Random,
    previous_slots: List[str],
    selected_slots: List[str],
    count: int,
) -> List[str]:
    if count <= 0 or not previous_slots:
        return []
    candidates = [slot for slot in previous_slots if slot not in selected_slots]
    if not candidates:
        return []
    rng.shuffle(candidates)
    return candidates[:count]


def _weighted_choice(
    rng: random.Random,
    items: Iterable[str],
    hot_items: Set[str],
    hot_weight: float,
) -> str:
    pool = list(items)
    if not pool:
        raise ValueError("Cannot sample from empty pool")
    weights = [hot_weight if item in hot_items else 1.0 for item in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def _validate_params(params: Dict) -> None:
    _require_positive_int(params, "num_workflows")
    _require_positive_int(params, "steps_per_workflow")
    _require_non_negative_int(params, "prefs_per_workflow")
    _require_positive_int(params, "steps")
    _require_positive_int(params, "workflows_per_step")
    _require_non_negative_int(params, "query_steps_per_workflow")
    _require_non_negative_int(params, "query_prefs_per_workflow")
    _require_non_negative_int(params, "workflow_updates_per_step")
    _require_non_negative_int(params, "step_updates_per_workflow")
    _require_non_negative_int(params, "pref_updates_per_workflow")
    _require_non_negative_int(params, "recent_window")
    _require_non_negative_int(params, "replay_queries_per_workflow")
    _require_non_negative_int(params, "burst_update_workflows")

    action_types = list(params.get("action_types", []))
    if not action_types:
        raise ValueError("recurring_workflows requires a non-empty action_types list")
    preference_types = list(params.get("preference_types", action_types)) or action_types
    if not preference_types:
        raise ValueError("recurring_workflows requires a non-empty preference_types list")

    _require_probability(params, "recurrence_bias")
    _require_probability(params, "update_query_ratio")
    _require_probability(params, "contradiction_rate")
    _require_probability(params, "hot_workflow_fraction")
    _require_probability(params, "burst_update_prob")

    update_recurrence_bias = float(params.get("update_recurrence_bias", params.get("recurrence_bias", 0.7)))
    if not 0.0 <= update_recurrence_bias <= 1.0:
        raise ValueError("update_recurrence_bias must be in [0, 1]")


def _require_positive_int(params: Dict, key: str) -> None:
    if key not in params:
        raise ValueError(f"Missing required recurring_workflows param: {key}")
    value = int(params[key])
    if value <= 0:
        raise ValueError(f"recurring_workflows param `{key}` must be > 0 (got {value})")


def _require_non_negative_int(params: Dict, key: str) -> None:
    value = int(params.get(key, 0))
    if value < 0:
        raise ValueError(f"recurring_workflows param `{key}` must be >= 0 (got {value})")


def _require_probability(params: Dict, key: str) -> None:
    value = float(params.get(key, 0.0))
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"recurring_workflows param `{key}` must be in [0, 1] (got {value})")
