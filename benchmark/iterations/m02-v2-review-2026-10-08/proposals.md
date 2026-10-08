# Proposed interpretations — open after blind review

All proposals are unapproved. Reject or edit freely; discrepancies stay unresolved until adjudicated. Hashes bind the current complete row, not an automatic approval.

## m02-v2-review-001

All four surface subtypes are hard exclusions; blue overrides the UI maximum.

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [
    "t-bar",
    "platter",
    "rope-tow",
    "magic-carpet"
  ],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

Current approval hash: `229fe774f6e1ebfd60857902776d93d85d4d08a7c919911ba2639c0fcaa184a6`

## m02-v2-review-002

Same family as 001: soft avoidance, not prohibition.

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "blue",
  "excluded_lift_types": [],
  "avoided_lift_types": [
    "t-bar",
    "platter",
    "rope-tow",
    "magic-carpet"
  ],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

Current approval hash: `b00c4116ce55f29a805916b972cb39d16dba71afb1d0ebb225f4ad882dc0d361`

## m02-v2-review-003

Eight minutes is valid extraction, not proof a route is feasible.

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 8,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

Current approval hash: `d202c89eb38831105f723f2ee0e516678dc266f69b8f3cd46e5e42256844f6ec`

## m02-v2-review-004

Explicit unknown clears the default hour; planning remains blocked.

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": null,
  "hard_max_difficulty": "red",
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

Current approval hash: `a12b668d8f9bb66dd377e3da22aa61b55ac577fcbc2b2148c436b676c485174e`

## m02-v2-review-005

Green is supported in v2; explicit maximum replaces red.

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "green",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": []
}
```

Current approval hash: `f18d96e51e9584fa32065458d35d2b7831078f0924aa21661c842ff67a27c73d`

## m02-v2-review-006

Multiple grade preferences do not imply variety. Context maximum remains red.

```json
{
  "schema_version": 2,
  "status": "ready",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
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

Current approval hash: `5e68cd9be1ca5b8917051d2158bd2d45975cc857d77f059c2a46f105df523ffe`

## m02-v2-review-007

Moon Observatory is absent from the catalog; do not invent its ID.

```json
{
  "schema_version": 2,
  "status": "clarify",
  "start_place_id": null,
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "red",
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

Current approval hash: `548377e59806a4f0016c29dd273244c89460768311624961e1573b33a4343a34`

## m02-v2-review-008

Booking transport is unsupported; wording of the unsupported tag needs human adjudication.

```json
{
  "schema_version": 2,
  "status": "unsupported",
  "start_place_id": "meadow",
  "finish_place_id": "meadow",
  "start_time": "2027-02-03T09:30:00+01:00",
  "duration_minutes": 60,
  "hard_max_difficulty": "red",
  "excluded_lift_types": [],
  "avoided_lift_types": [],
  "preferred_difficulties": [],
  "prefer_variety": false,
  "clarification_fields": [],
  "unsupported_preferences": [
    "helicopter booking"
  ]
}
```

Current approval hash: `5dcf582646ebc42f0af2c5fbd6f6955c20a1d2573abb9ec653b989815606f1a7`
