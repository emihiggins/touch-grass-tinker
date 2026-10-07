# Plose expanded coverage investigation

**Research only; not enabled in the app.** Original fixture and all evaluated graphs remain unchanged. © OpenStreetMap contributors, [ODbL 1.0](../LICENSE-ODbL.md).

The first sample's Schönbodenbahn boarding node lay west of its requested bbox. A single wider request (`11.700,46.677,11.734,46.694`) returned 1,869,802 bytes. The [manifest](manifest.json) records original/sanitized/graph hashes, source URL and time, and the explicitly provisional Italian grade mapping. The [sanitized source](source.osm) now preserves *all* piste types as evidence, including types not imported for routing. Contributor identity/history and relations remain omitted.

The [graph](graph.json) has 247 nodes and 251 edges (247 piste segments, four lifts). [Directed audit](structural-audit.json): zero nodes on a directed cycle, two weak components. All four lift boarding nodes have no incoming imported piste. This is still partial coverage, and broadening the box alone did not establish a lap.

## Specific lead, not a repair

The source contains four `piste:type=connection` ways. In particular, [way 50061560](https://www.openstreetmap.org/way/50061560) links nodes `635778767 → 11230733212 → 615897065` at Schönbodenbahn. Its saved tags include `piste:difficulty=easy`, but no explicit direction or access permission.

The [counterfactual report](connectivity-investigation.json) shows that adding the saved connection ways **in source order, hypothetically**, creates 20 cyclic nodes. These connections were **not** added to graph.json, and this does not establish feasible skiing, transfers, opening times or permission. The current OSM piste-type documentation describes downhill direction, but does not by itself establish travel semantics for these connection ways.

Next adoption gate: verify connection meaning/direction and boarding access using operator/domain evidence, then decide whether a separately reviewed transfer edge model is appropriate. Do not merge nearby nodes, reverse arbitrary ways or treat an unlabeled connection as open simply to obtain a loop.

## Reproduce

```sh
python3 scripts/investigate_connections.py data/terrain/plose-expanded-research
python3 scripts/audit_resort_snapshot.py --snapshot data/terrain/plose-expanded-research/graph.json --output data/terrain/plose-expanded-research/structural-audit.json
python3 -m unittest discover -s tests -p test_resort_import.py
```

The experiment copies the graph in memory and only writes a diagnostic report. No source connections enter production routing. Native source-node and way references are preserved; all timing remains assumed. See the [first fixture](../plose-research/README.md) for the earlier bounded result and import workflow.
