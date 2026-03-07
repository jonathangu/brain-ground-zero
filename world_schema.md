# World Schema

The world is a time-evolving set of entities and typed relations.

## Entities
Each entity is identified by a string ID and optional attributes.

```json
{
  "id": "E42",
  "type": "person",
  "attrs": {"name": "Avery"}
}
```

## Relations
Relations are directed, typed edges between entities and may change over time.

```json
{
  "subject": "E42",
  "object": "E07",
  "relation": "manages",
  "time": 12,
  "source": "update"
}
```

## Drift events
Drift is defined as a change to an existing relation for a subject-object pair.

```json
{
  "subject": "E42",
  "object": "E07",
  "old_relation": "manages",
  "new_relation": "reports_to",
  "time": 12
}
```

## World parameters
- `num_entities`
- `relation_types`
- `initial_density`
- `drift_rate`
- `contradiction_rate`
- `explicit_feedback_rate` (family-dependent, for sparse supervision)
- `seed`
