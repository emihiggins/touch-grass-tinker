> All 16 cases approved by Emi on 2026-10-06 at22:42:57UTC (message2415). Cases and graphs are now hash-bound and frozen. The original review instructions below are retained for provenance.

# Fresh evaluation review —16 cases

These are new fictional scenarios, not a repeat review. No model predictions have been run on them. Reply with case numbers and approve/correct/uncertain; no commands required. Review the intended meaning first, then open the proposed label.

This compact set replaces the originally proposed100–200case protocol for this submission iteration: lower review burden, but weak generalization evidence. It is authored by the same project agent and needs your independent review; it is not frozen yet. No model/prompt changes may be selected using its eventual predictions.
## Scenario: access

All edges directed; queues0; lifts and pistes are fictional. Open09:00–16:00local unless a case overrides closure. Green < blue < red < black here; not a universal resort mapping.
- access: Fern Gate → Birch Shelf · gondola · 4min
- upper: Birch Shelf → Cloud Point · chairlift · 4min
- blue-ridge: Cloud Point → Brook Bend · blue · 5min
- green-connector: Brook Bend → Fern Gate · green · 3min
- green-home: Birch Shelf → Fern Gate · green · 6min
- red-direct: Cloud Point → Fern Gate · red · 4min
## Scenario: surface

All edges directed; queues0; lifts and pistes are fictional. Open09:00–16:00local unless a case overrides closure. Green < blue < red < black here; not a universal resort mapping.
- chair: Fern Gate → Stone Hut · chairlift · 3min
- carpet: Stone Hut → North Crest · magic-carpet · 2min
- blue-home: North Crest → Fern Gate · blue · 5min
- red-home: Stone Hut → Fern Gate · red · 4min
## Scenario: closing

All edges directed; queues0; lifts and pistes are fictional. Open09:00–13:00local unless a case overrides closure. Green < blue < red < black here; not a universal resort mapping.
- chair: Fern Gate → North Crest · chairlift · 3min
- blue-home: North Crest → Fern Gate · blue · 4min
- gondola: Fern Gate → Sun Ridge · gondola · 5min
- green-home: Sun Ridge → Fern Gate · green · 4min
## Scenario: village

All edges directed; queues0; lifts and pistes are fictional. Open09:00–16:00local unless a case overrides closure. Green < blue < red < black here; not a universal resort mapping.
- chair: Fern Gate → Cloud Point · chairlift · 5min
- village-run: Cloud Point → Elm Village · blue · 4min
- home-run: Cloud Point → Fern Gate · green · 6min
- carpet: Fern Gate → Learning Bench · magic-carpet · 1min
- practice: Learning Bench → Fern Gate · green · 1min

## final-review-001

Scenario: **access**

> For this session my limit is green. Leave the other selections as they are.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "green",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: access, green-home, access, green-home

</details>

Decision: approved by Emi (message 2415)

## final-review-002

Scenario: **access**

> Blue pistes are my preference; green connecting descents are fine. Keep the blue ceiling.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [
    "blue"
  ],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: access, upper, blue-ridge, green-connector, access, upper, blue-ridge, green-connector

</details>

Decision: approved by Emi (message 2415)

## final-review-003

Scenario: **access**

> Gondolas are a firm no for me, even if that prevents an outing.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [
    "gondola"
  ],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **no_route**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-004

Scenario: **access**

> Try to avoid gondolas, but that is a preference rather than a ban.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [
    "gondola"
  ],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: access, upper, blue-ridge, green-connector

</details>

Decision: approved by Emi (message 2415)

## final-review-005

Scenario: **surface**

> Exclude surface lifts, carpets included; my blue maximum is unchanged.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [
    "magic-carpet",
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **no_route**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-006

Scenario: **surface**

> I would prefer red runs, but do not raise my selected blue safety limit.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [
    "red"
  ],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: chair, carpet, blue-home, chair, carpet, blue-home

</details>

Decision: approved by Emi (message 2415)

## final-review-007

Scenario: **surface**

> There are only two minutes available for the entire loop.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 2,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **no_route**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-008

Scenario: **surface**

> My destination is Far Meadow, not Fern Gate. Retain the remaining settings.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "remote",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **no_route**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-009

Scenario: **closing**

> Make my requested duration five hours. The operating windows still apply.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 300,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: chair, blue-home

</details>

Decision: approved by Emi (message 2415)

## final-review-010

Scenario: **closing**

> I have eight minutes in total, starting at the selected time.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 8,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: chair, blue-home

</details>

Decision: approved by Emi (message 2415)

## final-review-011

Scenario: **closing**

> Use the shortest live lift queues to choose this outing.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "unsupported",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": [
    "live_queue_times"
  ]
}
```
Expected planner result: **unsupported**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-012

Scenario: **closing**

> I cannot give a time budget yet; ask me for it before planning.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T12:50:00+01:00",
  "duration_minutes": null,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [
    "duration_minutes"
  ],
  "unsupported_preferences": []
}
```
Expected planner result: **clarify**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-013

Scenario: **village**

> My departure point has not been decided. The finishing point stays selected.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": null,
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [
    "start_place_id"
  ],
  "unsupported_preferences": []
}
```
Expected planner result: **clarify**

Example route: None

</details>

Decision: approved by Emi (message 2415)

## final-review-014

Scenario: **village**

> Prefer blue and red pistes, without gondolas. Repeating a piste is fine.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [
    "gondola"
  ],
  "avoided_lift_types": [],
  "preferred_difficulties": [
    "blue",
    "red"
  ],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: carpet, practice, carpet, practice, chair, home-run, chair, home-run

</details>

Decision: approved by Emi (message 2415)

## final-review-015

Scenario: **village**

> End at Elm Village instead of returning to Fern Gate.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "village",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **ok**

Example route: carpet, practice, carpet, practice, chair, home-run, chair, village-run

</details>

Decision: approved by Emi (message 2415)

## final-review-016

Scenario: **village**

> Keep the selected blue limit and give me a one-hour loop.

Selected settings:
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 45,
  "hard_max_difficulty": "blue"
}
```
**All lifts are closed in this case.**

<details><summary>Proposed answer—open after deciding</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-03-15T10:00:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```
Expected planner result: **no_route**

Example route: None

</details>

Decision: approved by Emi (message 2415)
