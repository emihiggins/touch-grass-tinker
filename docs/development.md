# Development

## Runtime and layout

Python3.11+ standard library plus vanilla HTML/CSS/JavaScript and vendored MapLibre GL JS 5.6.2 for the optional Alpendorf geographic view. No npm install or Python dependencies are required for the default app. Use `python3 -m liftlap.server`; the server binds only to loopback. [As-built architecture](../technical/architecture.md).
For an extracted ZIP, launch-demo.sh (macOS/Linux) and launch-demo.bat (Windows) provide the same dependency-free startup. Both forward arguments such as --port 8768; neither installs packages or stops an existing process. --version reports the demo version without opening a port, and startup prints the exact loopback URL.

| Path | Purpose |
|---|---|
| `liftlap/` | Intent adapters, graph import/search/validation, HTTP server, budgeted research tools |
| `web/` | Browser UI, state invalidation, confirmation and print layout |
| `tests/` | Unit/integration tests; optional SDK tests skip without optional packages |
| `benchmark/` | Versioned training/development and frozen evaluation artifacts |
| `research/evidence/` | Saved outputs, reports and historical evidence |
| `demo/` | Exact-input model replay, recorded walkthrough and user instructions |
| `training/` | Pinned research dependencies, protocols and run configuration |
| `docs/` | Current user and developer guidance |
| `delivery/`, `product/`, `scratchpad/` | Planning/history; not promises of shipped production features |

## Offline checks

```bash
python3 scripts/check_release.py
node --check web/app.js
```

The release check validates local documentation links, current media/source fingerprints, upstream MapLibre/license hashes, terrain-tile hash and geographic coverage, and source/graph manifest hashes, then runs tests, reproduces13/16 from saved base outputs, builds and extracts the demo into an isolated directory, runs offline planning plus real HTTP asset/context checks there, and checks two archive hashes for determinism. It does not invoke providers. A clean Python3.11 checkout runs161 tests with22 optional skips; the optional environment previously ran all149. The pinned public-only GitHub workflow performs offline checks without secrets.

## Browser checks

Use an existing Playwright Chromium installation (not a runtime dependency), start the local server on8767, then:

```bash
PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core node scripts/browser-smoke.cjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core node scripts/browser-keyboard.cjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core node scripts/browser-stale-review.cjs
```

`browser-ai-demo.cjs` additionally re-records the walkthrough and overwrites its screenshot/PDF evidence. Run it deliberately, inspect the new artifacts, and regenerate package checks afterward. `browser-ai-live.cjs` is different: it requires an already authorized live server on8768 and makes a paid request. Do not include it in ordinary CI.

## Optional model research

The [training guide](../training/README.md) documents completed research and the pinned optional environment. The current live adapter uses an OpenClaw protected-egress setup and deliberately rejects a plaintext API key in that path. Merely installing an SDK or cloning this repository is not a working public live-AI setup.

Historical budget authorization belongs to the original experiment, not to contributors. Do not reuse it as your spending permission, reset a ledger to regain headroom, or replay ambiguous submissions. A new research run needs independently configured credentials, budget, ledger and protocol. The one-time app-demo reservation is intentionally not restartable under its original key.

## Changes and evidence

Do not modify frozen data/prompt files to improve a reported score. Add a new version and declare a new experiment instead. Keep failures in the denominator; a schema-valid output is not necessarily a correct intent. If UI code changes, regenerate the current captures/video and verify source labels, keyboard focus, stale-result rejection and printed constraints. Historical evidence must remain clearly labelled as historical.

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [evaluation](evaluation.md).

Map interaction checks: `PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/browser-map.cjs`. They require rendered geographic features, no external requests, 320px reflow and a simulated renderer-failure fallback. CSP permits same-origin workers and inline styles required by map positioning; script execution and network connections remain same-origin only. Vendored source checksums: `research/maplibre-assets.json`.

## Resort import research

[The Plose fixture](../data/terrain/plose-research/README.md) documents a bounded second-region sample and the offline import command. Regional mapping must be explicit outside the historical Austrian default. Source/derived hashes are separate, and current terrain examples remain unreviewed. No new UI resort was added.

[Source-way review packets](../research/evidence/resort-review/README.md) bind review aids to graph/source hashes. Directed-connectivity checks distinguish apparent map connectivity from possible loops; they do not certify access.

## Billing summary semantics

`liftlap.billing_check.summarize` reports `estimated_gross_usd: null` when events are missing or any event lacks a valid price. `priced_subtotal_usd` is only the sum of priced rows; it is not the total charge. Even fully priced event rows remain an account-window estimate, not a project-attributed invoice. This helper never releases ledger holds.

UI accessibility checks: `PLAYWRIGHT_MODULE=/path/to/playwright-core AXE_SCRIPT=/path/to/axe-core/axe.min.js node scripts/browser-ui.cjs`. The test uses development-only axe-core 4.11.0, injected through browser automation without weakening production CSP. It checks initial/planned states at three widths, text resizing and focus. Incomplete findings are retained for visual review; automated success is not an accessibility certification.

Request recovery checks: `PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/browser-recovery.cjs`. They inject terrain failures and hold actual API responses to verify retry recovery and stale terrain/interpretation/plan suppression. They use the offline rules adapter only.

## Browser source formatting

First-party browser files and the current browser regression scripts use Prettier **3.6.2** with the repository's `.prettierrc.json`. Formatting is development-only: Node and npm are not required to run the Python demo. Do not format or modify vendored MapLibre files; their upstream hashes are checked separately.

```sh
npx --yes --package prettier@3.6.2 prettier --check web/app.js web/index.html web/style.css scripts/browser-map.cjs scripts/browser-ai-demo.cjs scripts/browser-ui.cjs scripts/browser-recovery.cjs scripts/browser-corrections.cjs
```

Use `--write` instead of `--check` for intentional formatting changes. After any browser source change, rerun browser checks and refresh the current media evidence before updating its fingerprints.

Local-correction regression: `PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/browser-corrections.cjs`. Checks draft invalidation, integer/horizon bounds, combined correction provenance, planner payload, exported constraints and no extra interpreter call.

### Proxy-independent offline checks

Server tests and extracted-package HTTP checks use explicit direct urllib openers only for their loopback test URLs. They do not depend on NO_PROXY and do not modify machine proxy settings or provider clients. To verify isolation, run the offline release suite with HTTP_PROXY/http_proxy set to an unreachable local endpoint and NO_PROXY/no_proxy empty; all offline checks should still pass.
