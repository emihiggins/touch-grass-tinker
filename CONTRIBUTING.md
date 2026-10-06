# Contributing

Start with the [developer guide](docs/development.md). The default app and offline checks require only Python3.11+; JavaScript syntax checking requires Node. No model API key is needed.

Before proposing a change, explain the user problem or reproducible failure. Keep implementation and tests focused. For UI changes, check interpretation review, correction, confirmation, stale responses, mobile/keyboard behavior and printed constraints. Preserve explicit distinctions between Rules, recorded output and live inference.

Run `python3 scripts/check_release.py` before a pull request. Optional model dependencies are not required for ordinary contributions. Never invoke paid/live test scripts without a separately configured authorized environment.

Do not alter frozen benchmark labels, prompts or saved predictions to improve results. Propose new versioned datasets/protocols instead; keep failures and provenance. Do not commit API keys, provider credentials, private run directories, user data or generated environments. Report suspected credentials privately to the repository owner rather than opening a public issue containing them.

Real-terrain additions need provenance, license/attribution and explicit review status. Graph connectivity is not proof of safe skier access. Original-code contributions are under the repository's MIT license; separately licensed data retains its own terms.
