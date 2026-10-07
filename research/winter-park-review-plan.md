# Winter Park: first qualified routing review

This is a review queue, not an enabled resort or a ski itinerary. Use the existing
browse-only preview and source links. Do not add proximity-based connectors.

## Structural screening (October 7, 2026)

The current partial extract contains 12 imported passenger lift ways. Four have
a directed, piste-only return to their imported start node. This uses the current
unverified direction and ignores grade, access, closures, timing and queues.
It is not an assessment of safety or suitability.

| Review order | Lift/source | Return segments | Why review it |
|---|---|---:|---|
| 1 | [Discovery](https://www.openstreetmap.org/way/86248729) | 8 | Smallest structural example to qualify end to end |
| 2 | [Endeavor](https://www.openstreetmap.org/way/258676847) | 17 | Another bounded connected example |
| 3 | [Arrow](https://www.openstreetmap.org/way/17058716) | 26 | Both terminals have incident pistes; direction still unverified |
| 4 | [Prospector Express](https://www.openstreetmap.org/way/17058732) | 38 | Larger structural example after the small cases |

Counts are graph segments in the fewest-segment path, not trail counts or quality
scores. The other eight lifts have no piste-only return in this extract. This does
not establish absence of a real-world descent. In particular, the named Tubing
facility and Village Cabriolet need intended-use review before considering them
part of a downhill-ski network. Names alone are not authoritative exclusions.

The Gondola's 9.416 m proximity candidate is a closed-area source way, not a
verified connector. Keep it excluded. Do not close the gap with a straight line.

## Review record required for each candidate

1. Confirm actual boarding/alighting terminals against a dated, attributable
   source, plus local/operator review; record the specific node and way IDs.
2. Confirm every segment's permissible direction, skier access, native grade,
   and the transfer between the piste and lift. Record disagreements, not guesses.
3. Check the bounded-extract coverage against the intended user journey,
   including return to the actual access/base point, not merely the same lift.
4. Identify an authorized operating-status source and its update interval,
   expiry rules and unknown-status handling. Static OSM is not a current opening.
5. Validate timing and route behavior in the field with a qualified reviewer.
6. Keep reviewer, date, source, decision and unresolved notes bound to graph/source
   hashes. A changed graph invalidates that review. No routing promotion while
   these fields or permissions remain unresolved.

These steps require external evidence, not another model-generated label approval
from Emi. Offline analysis and preview improvements can continue independently.

## Reproduce

```sh
python scripts/review_lift_returns.py data/terrain/winter-park-research/graph.json research/evidence/resort-review/winter-park-lift-returns.json
```

The [saved report](evidence/resort-review/winter-park-lift-returns.json) records the
exact graph hash and edge IDs. The script never changes graph data. It is a
structural screen, not the route planner and not permission to navigate.
