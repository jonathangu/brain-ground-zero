from __future__ import annotations

import random
from typing import Dict, List

from brain_ground_zero.families.base import BenchmarkFamily, Step
from brain_ground_zero.models import Fact, Query


class SparseFeedbackFamily(BenchmarkFamily):
    """Recurring workflows with sparse explicit feedback availability."""

    def build_world(self) -> Dict[str, Fact]:
        rng = random.Random(self.seed)
        params = self.spec.params

        num_workflows = int(params["num_workflows"])
        steps_per_workflow = int(params["steps_per_workflow"])
        prefs_per_workflow = int(params.get("prefs_per_workflow", 0))
        action_types = list(params["action_types"])
        preference_types = list(params.get("preference_types", action_types)) or action_types

        workflows = [f"S{i:03d}" for i in range(num_workflows)]
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
        return world_state

    def build_steps(self, world_state: Dict[str, Fact]) -> List[Step]:
        rng = random.Random(self.seed + 1)
        params = self.spec.params

        steps = int(params["steps"])
        workflows_per_step = int(params["workflows_per_step"])
        workflow_updates_per_step = int(params["workflow_updates_per_step"])
        step_updates_per_workflow = int(params["step_updates_per_workflow"])
        pref_updates_per_workflow = int(params.get("pref_updates_per_workflow", 0))
        query_steps_per_workflow = int(params["query_steps_per_workflow"])
        query_prefs_per_workflow = int(params.get("query_prefs_per_workflow", 0))
        recurrence_bias = float(params.get("recurrence_bias", 0.8))
        recent_window = int(params.get("recent_window", max(4, workflows_per_step * 2)))
        update_query_ratio = float(params.get("update_query_ratio", 0.7))
        contradiction_rate = float(params.get("contradiction_rate", 0.2))

        revision_burst_rate = float(params.get("revision_burst_rate", 0.35))
        burst_extra_step_updates = int(params.get("burst_extra_step_updates", 1))
        burst_extra_pref_updates = int(params.get("burst_extra_pref_updates", 1))

        explicit_feedback_rate = float(params.get("explicit_feedback_rate", 0.08))
        focused_feedback_rate = float(params.get("focused_feedback_rate", 0.4))
        feedback_focus_recent_steps = int(params.get("feedback_focus_recent_steps", 2))
        min_feedback_per_step = int(params.get("min_feedback_per_step", 0))

        current = dict(world_state)
        history = {k: list(v) for k, v in self._history.items()}
        last_changed = {key: 0 for key in current}
        recent_workflows: List[str] = []

        steps_out: List[Step] = []
        for step_idx in range(1, steps + 1):
            updates: List[Fact] = []
            updated_slots_by_workflow: Dict[str, Dict[str, List[str]]] = {}

            update_count = min(workflow_updates_per_step, len(self._workflows))
            workflows_to_update = rng.sample(self._workflows, update_count) if update_count > 0 else []

            for workflow in workflows_to_update:
                updated_slots_by_workflow.setdefault(workflow, {"steps": [], "prefs": []})
                burst = rng.random() < revision_burst_rate

                step_count = step_updates_per_workflow + (burst_extra_step_updates if burst else 0)
                step_count = min(step_count, len(self._step_slots))
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
                        last_changed[key] = step_idx
                        updates.append(new_fact)
                        updated_slots_by_workflow[workflow]["steps"].append(slot)

                pref_count = pref_updates_per_workflow + (burst_extra_pref_updates if burst else 0)
                pref_count = min(pref_count, len(self._pref_slots))
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
                        last_changed[key] = step_idx
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
            )
            for workflow in workflows_to_run:
                _touch_recent(recent_workflows, workflow, recent_window)

            queries: List[Query] = []
            answers: List[str] = []
            previous_relations: List[str | None] = []
            query_keys: List[str] = []

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

                for slot in step_slots + pref_slots:
                    key = f"{workflow}::{slot}"
                    fact = current[key]
                    queries.append(Query(subject=workflow, object=slot))
                    answers.append(fact.relation)
                    prev = history[key][-2] if len(history[key]) > 1 else None
                    previous_relations.append(prev)
                    query_keys.append(key)

            feedback_mask = _build_feedback_mask(
                rng=rng,
                step=step_idx,
                query_keys=query_keys,
                last_changed=last_changed,
                explicit_feedback_rate=explicit_feedback_rate,
                focused_feedback_rate=focused_feedback_rate,
                feedback_focus_recent_steps=feedback_focus_recent_steps,
                min_feedback_per_step=min_feedback_per_step,
            )

            steps_out.append(
                Step(
                    step=step_idx,
                    updates=updates,
                    queries=queries,
                    answers=answers,
                    previous_relations=previous_relations,
                    feedback_mask=feedback_mask,
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
) -> List[str]:
    if count <= 0:
        return []
    available = set(workflows)
    chosen: List[str] = []
    attempts = 0
    while len(chosen) < count and available and attempts < count * 10:
        attempts += 1
        if recent and rng.random() < recurrence_bias:
            candidate = rng.choice(recent)
        else:
            candidate = rng.choice(workflows)
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


def _build_feedback_mask(
    rng: random.Random,
    step: int,
    query_keys: List[str],
    last_changed: Dict[str, int],
    explicit_feedback_rate: float,
    focused_feedback_rate: float,
    feedback_focus_recent_steps: int,
    min_feedback_per_step: int,
) -> List[bool]:
    if not query_keys:
        return []

    mask: List[bool] = []
    focused_indices: List[int] = []
    for idx, key in enumerate(query_keys):
        changed_at = last_changed.get(key, -10**9)
        is_focused = (step - changed_at) <= feedback_focus_recent_steps
        if is_focused:
            focused_indices.append(idx)
        p = focused_feedback_rate if is_focused else explicit_feedback_rate
        mask.append(rng.random() < p)

    required = min(min_feedback_per_step, len(query_keys))
    shortfall = required - sum(1 for m in mask if m)
    if shortfall > 0:
        candidates = [i for i in focused_indices if not mask[i]]
        if len(candidates) < shortfall:
            candidates.extend(i for i, m in enumerate(mask) if not m and i not in candidates)
        rng.shuffle(candidates)
        for idx in candidates[:shortfall]:
            mask[idx] = True

    return mask
