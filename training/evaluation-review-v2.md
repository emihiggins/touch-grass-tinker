# Independent evaluation review — 16-case pilot

These are new fictional scenarios and graph topologies, authored by the same project agent and pending your independent review. This is not a frozen or statistically representative test set. No model predictions have been generated.

For each case, read the request/context first. Open the proposed answer after deciding what it means. Reply with the case number and approve/correct/uncertain. No commands needed. Route outcomes are simulation-only; the supplied topology is the entire available network.

Soft avoidance is a preference, not a prohibition. Distinct grades do not imply variety. Durations remain literal; infeasible routes are separate from missing information.

## Graph key

### fork

All edges are directed. All are open 08:00–16:00 local, with no queues; durations are assumptions.

- gate: Moss Landing → Kite Hub, gondola, 3 minutes.
- chair: Moss Landing → Kite Hub, chairlift, 5 minutes.
- left: Kite Hub → Reed Corner, blue, 3 minutes.
- right: Kite Hub → Larch Landing, red, 2 minutes.
- return-west: Reed Corner → Moss Landing, blue, 2 minutes.
- return-east: Larch Landing → Moss Landing, blue, 1 minutes.
### transfer

All edges are directed. All are open 08:00–16:00 local, with no queues; durations are assumptions.

- entry: Moss Landing → Aster Middle, gondola, 2 minutes.
- connector: Aster Middle → Fern Foot, blue, 1 minutes.
- upper: Fern Foot → Slate Peak, t-bar, 2 minutes.
- return: Slate Peak → Moss Landing, red, 3 minutes.
### oneway

All edges are directed. All are open 08:00–16:00 local, with no queues; durations are assumptions.

- ascend: Moss Landing → Slate Peak, chairlift, 2 minutes.
- lower: Slate Peak → Brook Hollow, blue, 3 minutes.
- restore: Brook Hollow → Moss Landing, platter, 2 minutes.
- shortcut: Slate Peak → Moss Landing, black, 1 minutes.
### islands

All edges are directed. All are open 08:00–16:00 local, with no queues; durations are assumptions.

- west-up: Moss Landing → Moss Crest, chairlift, 1 minutes.
- west-down: Moss Crest → Moss Landing, blue, 1 minutes.
- east-up: Larch Landing → Larch Crest, gondola, 1 minutes.
- east-down: Larch Crest → Larch Landing, red, 1 minutes.

## eval-review-001

**Request:** Please steer clear of gondolas if there is another way; I still need to return to Moss Landing.

**Graph:** fork

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
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

**Expected outcome:** ok
**Example route:** ['chair', 'left', 'return-west']

</details>

- Decision: pending
- Corrections:

## eval-review-002

**Request:** I cannot take a gondola or a chairlift. Keep every other setting.

**Graph:** fork

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [
    "chairlift",
    "gondola"
  ],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** no_route
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-003

**Request:** My window is five hours; I am happy with the selected terrain limit.

**Graph:** fork

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 300,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** ok
**Example route:** ['chair', 'left', 'return-west']

</details>

- Decision: pending
- Corrections:

## eval-review-004

**Request:** Keep everything selected except the return point: meet me at the unlisted Stone Shelter.

**Graph:** fork

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": "base",
  "finish_place_id": null,
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [
    "finish_place_id"
  ],
  "unsupported_preferences": []
}
```

**Expected outcome:** clarify
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-005

**Request:** Gondolas are a last preference, not forbidden. A red descent is fine.

**Graph:** transfer

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
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

**Expected outcome:** ok
**Example route:** ['entry', 'connector', 'upper', 'return']

</details>

- Decision: pending
- Corrections:

## eval-review-006

**Request:** Definitely no gondola boarding, even if it is the only access lift.

**Graph:** transfer

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
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

**Expected outcome:** no_route
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-007

**Request:** Make the whole loop fit in ten minutes; do not change my grade limit.

**Graph:** transfer

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 10,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** ok
**Example route:** ['entry', 'connector', 'upper', 'return']

</details>

- Decision: pending
- Corrections:

## eval-review-008

**Request:** Pick the route with the lightest crowds this morning.

**Graph:** transfer

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "unsupported",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": [
    "crowding"
  ]
}
```

**Expected outcome:** unsupported
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-009

**Request:** Stay on blue descents. I am comfortable with the platter return lift.

**Graph:** oneway

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** ok
**Example route:** ['ascend', 'lower', 'restore']

</details>

- Decision: pending
- Corrections:

## eval-review-010

**Request:** Keep it blue and rule out every surface lift, including carpets.

**Graph:** oneway

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
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

**Expected outcome:** no_route
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-011

**Request:** I can do two minutes before my meeting; leave the remaining choices alone.

**Graph:** oneway

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 2,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** no_route
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-012

**Request:** I know my departure station, but I cannot choose a departure time yet.

**Graph:** oneway

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": null,
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [
    "start_time"
  ],
  "unsupported_preferences": []
}
```

**Expected outcome:** clarify
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-013

**Request:** Return here after skiing; aim for some different runs, all within my chosen limit.

**Graph:** islands

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": true,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** ok
**Example route:** ['west-up', 'west-down']

</details>

- Decision: pending
- Corrections:

## eval-review-014

**Request:** Travel from Moss Landing to Larch Landing using the mapped lifts and pistes.

**Graph:** islands

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "base",
  "finish_place_id": "east",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

**Expected outcome:** no_route
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-015

**Request:** Use my settings and only runs reported as freshly groomed today.

**Graph:** islands

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "unsupported",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": [
    "live_grooming"
  ]
}
```

**Expected outcome:** unsupported
**Example route:** None

</details>

- Decision: pending
- Corrections:

## eval-review-016

**Request:** I have not chosen my maximum slope grade. Please do not assume one.

**Graph:** islands

**UI context:**
```json
{
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": "red"
}
```

<details><summary>Proposed answer — open after your own interpretation</summary>

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": "base",
  "finish_place_id": "base",
  "start_time": "2027-02-20T09:00:00+01:00",
  "duration_minutes": 50,
  "hard_max_difficulty": null,
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [
    "hard_max_difficulty"
  ],
  "unsupported_preferences": []
}
```

**Expected outcome:** clarify
**Example route:** None

</details>

- Decision: pending
- Corrections:
