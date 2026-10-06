# As-built architecture

The current application uses **Python’s standard library HTTP server and graph planner, plus vanilla browser HTML/CSS/JavaScript and an optional bundled MapLibre geographic renderer**. It does not use FastAPI, NetworkX, React or Vite. Those were proposed in the [original architecture](architecture-proposal.md), not implemented.

## Request flow

1. `GET /api/context` supplies a server-owned graph, place catalog, fixed demo context and available interpretation modes.
2. `POST /api/interpret` chooses Rules, an exact-input recorded response, or an explicitly enabled live base-model adapter.
3. The browser displays the original request/settings and parsed constraints. Local hard-exclusion edits remove overlapping soft preferences; they do not invoke a model.
4. Explicit confirmation sends an intent to `POST /api/plan`. Schema/catalog/time checks run before graph planning.
5. `compact.py` contracts eligible piste chains. `core.py` searches the compact graph within bounds; expansion and independent validation check the source-level route.
6. The browser displays the simulated route and approved constraints. Changing inputs invalidates confirmation and rejects stale asynchronous responses. Print retains intent provenance and corrections.

## Components

- `rules.py`: narrow deterministic interpreter with clarification/unsupported outcomes.
- `app_model.py`: exact-input replay and opt-in live Qwen3-8B adapter. Live calls reuse the pinned renderer/SDK, strict output validation and shared budget ledger.
- `server.py`: loopback-only allowlisted assets/API, host/origin checks and bounded request size. Not a production authenticated service.
- `core.py`: directed graph, operation-window checks, hard restrictions, soft-preference scoring, bounded search and route validation.
- `compact.py`: reversible source-edge contraction/expansion.
- `import_osm.py`: OSM extract processing with provenance and unreviewed-terrain boundaries.
- `sample_runner.py`, `training_transport.py`, `experiment.py`, `final_evaluation.py`: research execution and evaluation, separate from default app startup.
- `spend.py`: atomic SQLite reservations. Ambiguous provider outcomes retain their reservation; the ledger is not a provider-enforced spending cap or invoice.

## Contracts and state

See [intent v2](intent-v2.md). The app has no accounts, persisted user profiles, database-backed route history, public authentication or live resort feed. Graphs and fixed scenarios are local files. Private model run records and spending ledgers live under ignored `runs/`; credentials are not delivered to the browser.

The recorded example is a real saved output and includes a semantic mistake. Its request hash binds text, selected context and place catalog. It refuses unmatched input. It is not a model emulator.

## Boundaries

The UI’s supported normalized grade order does not establish universal resort grading. OSM connectivity and illustrative timing do not establish permission or safe access. The route validator checks a supplied intent, not the correctness of language interpretation. Explicit human review remains important.

No hosted app, permanent fine-tuned model deployment, unrestricted paid endpoint, or real-world terrain validation is claimed. [Current guides](../docs/README.md) describe the supported installation and checks.
