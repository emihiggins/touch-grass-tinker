# Training candidate review packet

All rows are AI-assisted candidates. Human review decisions are recorded below; reviewed does not mean approved. Editing this packet does not update labels or mark rows approved.

For each case check: explicit request versus UI defaults; hard/soft difficulty; lift exclusions; deadline math; clarification/unsupported codes. Record corrections in the canonical JSONL and re-run corpus audit.

**Quarantine:** candidate 009 overlaps development wording; label approved by Emi, but training eligibility remains blocked until leakage is resolved.

No held-out examples appear here. No route feasibility is labeled.

## train-candidate-001 — hard_soft_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Keep every descent blue, and give me some variety over 90 minutes.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 90,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": true,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-002 — drag_grade_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Reds are my limit. For the next 45 minutes, skip all drag lifts.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 45,
  "excluded_lift_types": [
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-003 — surface_soft_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** I prefer blue runs but can manage reds; no surface lifts, including carpets.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "magic-carpet",
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [
    "blue"
  ],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-004 — correction_budget_combo

- [x] Human reviewed
- Decision: discussion_pending
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: I think that someone who's max difficulty is blue, probably also wouldn't be experienced enough to do a t-bar lift, as those are usually pretty difficult.
- Agent response (not human approval): Recommendation: keep lift-handling comfort separate from piste difficulty. Do not infer a t-bar exclusion from blue-only; ask explicitly or add a separate user preference. Current label retained pending resolution.
- Quarantine: None

**Request:** Make it two hours—actually, 75 minutes. Nothing harder than blue.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 75,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-005 — deadline_combo

- [x] Human reviewed
- Decision: discussion_pending
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: avoid gondolas, i think should be honored, but perhaps not for the very first lift of the day as many resorts have a gondola at the base, that gives skiers access to the majority of the runs on the mountain, and given the time constraint this skier has, they might waste a lot of time initially trying to get to all the runs by avoiding the first gondola. also avoid gondolas is different from "no" gondolas
- Agent response (not human approval): Soft avoidance versus prohibition needs a distinct contract. Do not silently waive a gondola exclusion for the first lift. A future soft preference may offer a clearly disclosed access-lift tradeoff; no exception is inferred here. Current label disputed and held.
- Quarantine: None

**Request:** Give me two hours from the selected start, but I must finish by 11:20. Avoid gondolas.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 80,
  "excluded_lift_types": [
    "gondola"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-006 — deadline_no_extend_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Stay on blues and have me back by noon; keep my selected outing length.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-007 — alias_finish_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Set off from Juniper and end at Aspen after 45 minutes, on blue runs only.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 45,
  "excluded_lift_types": [],
  "finish_place_id": "ridge",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-008 — reverse_places_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Start at the ridge, finish in the valley, and avoid chairlifts.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "chairlift"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "ridge",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-009 — negative_scope_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: Cross-split near-duplicate wording with development; human label approval does not clear leakage.

**Request:** I do not need you to avoid gondolas. I do need you to avoid t-bars.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-010 — correction_grade_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Blacks would be fine—no, make red the maximum, with mostly blues.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [
    "blue"
  ],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-011 — missing_grade_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved, but curious if hard_max_difficultly should default to the hardest level on the mountain? or if null is just as sufficient.
- Agent response (not human approval): Retain null plus hard_max_difficulty clarification. Never infer the hardest permitted grade from missing ability information. Explicit approval recorded; question does not revoke approval.
- Quarantine: None

**Request:** An hour with lots of different runs, please.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": null,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "hard_max_difficulty"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": null,
  "prefer_variety": true,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-012 — unknown_finish_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Take blue runs and finish at Birch Lodge, which is not in the place list.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "finish_place_id"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": null,
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-013 — range_combo

- [x] Human reviewed
- Decision: change_requested
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: duration minutes should be 300 (5 hours to minutes conversion), but it should also cap out if its going to exceed the results close time for last lifts.
- Agent response (not human approval): Requested correction accepted as product direction: preserve 300 minutes, then evaluate actual edge operating windows separately. Schema v1 allows only 15..240; do not write invalid v1 gold or invent closing times absent from this catalog. Hold until versioned contract/planner/prompt migration.
- Quarantine: None

**Request:** Only blue descents, and make the outing five hours.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "duration_minutes"
  ],
  "duration_minutes": null,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-014 — unsupported_queue_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Avoid drag lifts and choose lifts using their live queue times.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "live_queue_times"
  ]
}
```

## train-candidate-015 — unsupported_terrain_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Give me 90 minutes with off-piste sections between lifts.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 90,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "off_piste"
  ]
}
```

## train-candidate-016 — unsupported_grooming_combo

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Blue runs only, selecting the ones groomed this morning.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "live_grooming"
  ]
}
```

## train-candidate-017 — ceiling_preference

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Black is my ceiling, but favor red descents and change things up.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "black",
  "prefer_variety": true,
  "preferred_difficulties": [
    "red"
  ],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-018 — long_surface

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** For 150 minutes, use only blue pistes and skip every surface lift.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 150,
  "excluded_lift_types": [
    "magic-carpet",
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-019 — carpet_only_exclusion

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Chairlifts and drag lifts are fine; just leave out magic carpets.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "magic-carpet"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-020 — two_lift_exclusions

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Make a 35-minute outing without gondolas or cable cars.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 35,
  "excluded_lift_types": [
    "gondola",
    "cable-car"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-021 — exclusion_correction

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Skip chairs—correction, chairs are okay. Exclude gondolas instead.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "gondola"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-022 — start_alias

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Depart from Aspen Ridge and come back there after 40 minutes.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 40,
  "excluded_lift_types": [],
  "finish_place_id": "ridge",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "ridge",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-023 — destination_correction

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Finish at Aspen. Wait, finish back at Juniper Valley instead. Blue runs only.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-024 — shorter_explicit

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** The form says an hour, but I want just 20 minutes and lots of different runs.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 20,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": true,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-025 — four_hours_boundary

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** I want exactly four hours, with red as the maximum grade.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 240,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-026 — fifteen_boundary

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** A quarter of an hour on blue pistes, please.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 15,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-027 — deadline_floor

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** An hour would be nice, but I must return by 10:15 from the selected 10:00 start.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 15,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-028 — deadline_out_of_range

- [x] Human reviewed
- Decision: change_requested
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: duration minutes should be set to 10 minutes not null.
- Agent response (not human approval): Requested correction accepted as product direction: preserve 10 minutes. Schema v1 rejects values below 15; short-budget infeasibility belongs to the planner, not an invented missing-value label. Hold until versioned contract migration.
- Quarantine: None

**Request:** Set out at the selected 10:00 and be done by 10:10.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "duration_minutes"
  ],
  "duration_minutes": null,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-029 — long_deadline_cap

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Book 180 minutes, but finish no later than 12:30 from the selected start.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 150,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-030 — override_ui_grade

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Ignore the black maximum on the form; blue is my actual limit.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "black",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-031 — soft_keep_ceiling

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Prefer blue pistes while retaining my selected black maximum.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "black",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "black",
  "prefer_variety": false,
  "preferred_difficulties": [
    "blue"
  ],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-032 — two_preferences

- [x] Human reviewed
- Decision: discussion_pending
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: if theres multiple preferred difficulties, should prefer variety be true?
- Agent response (not human approval): Recommendation: retain preferred_difficulties blue/red and prefer_variety false. Equal grade preferences do not request distinct runs or less repetition; variety is a separate objective. No explicit approval inferred.
- Quarantine: None

**Request:** Favor blue and red pistes equally; black runs are permitted.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "black",
  "prefer_variety": false,
  "preferred_difficulties": [
    "blue",
    "red"
  ],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-033 — variety_no_grade

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Mix up the runs over 50 minutes. I have not selected a maximum grade.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": null,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "hard_max_difficulty"
  ],
  "duration_minutes": 50,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": null,
  "prefer_variety": true,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-034 — missing_start_place

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Take me to Aspen Ridge in 45 minutes, but my departure point is unset.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": null,
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "start_place_id"
  ],
  "duration_minutes": 45,
  "excluded_lift_types": [],
  "finish_place_id": "ridge",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": null,
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-035 — missing_finish_place

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Begin at Juniper Valley, keep it blue, and ask me where to finish.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": null,
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "finish_place_id"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": null,
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-036 — missing_time_with_exclusion

- [x] Human reviewed
- Decision: discussion_pending
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: maybe start_place_id should be null since user specified in request they have not decided where to start yet.
- Agent response (not human approval): Original request says WHEN, not WHERE: "No gondolas. I have not decided when to start." Retain selected valley and start_time null. No label change or human approval inferred from this question.
- Quarantine: None

**Request:** No gondolas. I have not decided when to start.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": null
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "start_time"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "gondola"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": null,
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-037 — missing_budget_with_grade

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** All blue, but I have not picked an outing length yet.

**UI context:**
```json
{
  "duration_minutes": null,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "duration_minutes"
  ],
  "duration_minutes": null,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-038 — two_missing_fields

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Avoid chairs; both my start time and outing duration are still undecided.

**UI context:**
```json
{
  "duration_minutes": null,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": null
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "start_time",
    "duration_minutes"
  ],
  "duration_minutes": null,
  "excluded_lift_types": [
    "chairlift"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": null,
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-039 — conflicting_budget

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** It must last exactly 45 minutes and exactly 90 minutes. Neither is a correction.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "duration_minutes"
  ],
  "duration_minutes": null,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-040 — conflicting_finish

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** End at both Juniper Valley and Aspen Ridge as the single finish point.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "finish_place_id"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": null,
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-041 — unknown_start

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Begin at Fox Hollow, not one of the listed places, and end at Juniper.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "start_place_id"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": null,
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-042 — unknown_both_places

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Start at Otter Lodge and finish at Elk Hut; neither appears in the catalog.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [
    "start_place_id",
    "finish_place_id"
  ],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": null,
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": null,
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "clarify",
  "unsupported_preferences": []
}
```

## train-candidate-043 — crowding_and_budget

- [x] Human reviewed
- Decision: discussion_pending
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: 'red or easier' I think implies they are open to variety easier than red as well as red.
- Agent response (not human approval): Recommendation: red-or-easier is a hard ceiling permitting blue/red; it does not request distinct runs or grade mixing. Keep prefer_variety false. Crowding remains unsupported. No explicit approval inferred.
- Quarantine: None

**Request:** Ninety minutes on red or easier pistes, selecting only uncrowded runs.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 90,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "crowding"
  ]
}
```

## train-candidate-044 — two_live_features

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Use current queue times and today’s grooming reports to choose my laps.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "live_queue_times",
    "live_grooming"
  ]
}
```

## train-candidate-045 — offpiste_and_variety

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** For 45 minutes, mix marked runs with off-piste descents for variety.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 45,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": true,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "unsupported",
  "unsupported_preferences": [
    "off_piste"
  ]
}
```

## train-candidate-046 — negated_live_request

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** I do not need live queue information. Use my selected settings and avoid rope tows.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 60,
  "excluded_lift_types": [
    "rope-tow"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-047 — negated_offpiste

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** No off-piste skiing: keep me on marked blue runs for 55 minutes.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 55,
  "excluded_lift_types": [],
  "finish_place_id": "valley",
  "hard_max_difficulty": "blue",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```

## train-candidate-048 — grade_correction_with_drag

- [x] Human reviewed
- Decision: approved
- Reviewer: Emi Higgins
- Reviewed at: 2026-10-06T20:21:27Z
- Human note: approved
- Agent response (not human approval): None
- Quarantine: None

**Request:** Use black runs—actually, nothing above red. Avoid drag lifts for 80 minutes.

**UI context:**
```json
{
  "duration_minutes": 60,
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00"
}
```

**Catalog:** valley: Juniper Valley (aliases: Juniper, the valley); ridge: Aspen Ridge (aliases: Aspen, the ridge)

**Proposed label:**
```json
{
  "clarification_fields": [],
  "duration_minutes": 80,
  "excluded_lift_types": [
    "platter",
    "rope-tow",
    "t-bar"
  ],
  "finish_place_id": "valley",
  "hard_max_difficulty": "red",
  "prefer_variety": false,
  "preferred_difficulties": [],
  "schema_version": 1,
  "start_place_id": "valley",
  "start_time": "2027-01-15T10:00:00+01:00",
  "status": "ready",
  "unsupported_preferences": []
}
```
