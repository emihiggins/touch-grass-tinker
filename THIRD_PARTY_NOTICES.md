# Licenses and attribution

- Original project software: [MIT](LICENSE), copyright2026 Emi Higgins.
- `data/terrain/alpendorf-source.osm` and its derived `alpendorf-lab.json`: © OpenStreetMap contributors, [ODbL1.0](data/terrain/LICENSE-ODbL.md). See [provenance and limitations](data/terrain/README.md). MIT does not replace these database terms.
- Qwen3-8B is an upstream open-weight model, accessed through Tinker, not bundled in this repository or demo archive. See its [model card](https://huggingface.co/Qwen/Qwen3-8B) and [license](https://huggingface.co/Qwen/Qwen3-8B/blob/main/LICENSE).
- Optional training/inference uses the [Tinker SDK](https://github.com/thinking-machines-lab/tinker) and [Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook). Their source and dependencies retain their own licenses; version pins are in `training/`. They are not bundled as installed packages.
- Development browser checks use Playwright/Chromium, not bundled as runtime dependencies. Screen recording is an original capture of this app, with the recorded-model limitation disclosed in `demo/README.md`.

AI coding assistance was used. Original fictional terrain and synthetic request examples are not real resort or skier data. No model weights, API keys, browser cookies, or private run directories belong in a public release.

- Bundled MapLibre GL JS 5.6.2 CSP build, worker and CSS: BSD-3-Clause and included dependency notices in [the upstream license](web/maplibre-LICENSE.txt). Download URLs and SHA256 hashes are in [the asset manifest](research/maplibre-assets.json). No upstream tiles, model weights or hosted map service are bundled.

- The repository’s `data/terrain/plose-research/` and `data/terrain/plose-expanded-research/` snapshots are also © OpenStreetMap contributors under ODbL 1.0. They are bounded research fixtures, not supported app resorts, and are not included in the local demo archive.
