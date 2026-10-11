# Verified challenge research

Initial research: October 5, 2026. Challenge landing page and contest-specific official rules rechecked October 11, 2026 at 10:03 UTC: same deadline, required tags, seven-section template, writing-first criteria and new-project requirement. General entrant eligibility remains unverified. Historical environment notes below describe the initial research, not current implementation.

## Contest

- Theme: **Touch Grass** — open-source AI or open-weight models at the core of a project that gets people off screens and into the world.
- Window: October 5–11, 2026. Deadline: **October 11, 2026, 11:59 PM PDT**, equivalent to **October 12, 2026, 06:59 UTC**.
- Best Use of Tinker: “Use Thinking Machines' Tinker to fine-tune a model for a specific task, and show a clear improvement in performance, latency, or cost over a baseline.” Prize: $200 USD plus winner badge.
- Writing quality is weighted most heavily. Other criteria: theme relevance, creativity, technical execution, and meaningful partner use.
- Submit a DEV post using the challenge template with `devchallenge` and `hf26challenge` tags. Include what was built, demo link or video, code, how it works, why open innovation matters, and the prize category. Agent-session sharing is optional.
- Project and repository must be new within the challenge window. Note post-deadline commits in the README. Credit nontrivial prior work. English is required for prize eligibility; teams may have up to four members.
- General official rules control if they conflict with the announcement. Eligibility includes age/majority, location restrictions, and an active DEV account; entrant eligibility has not been verified here.
- The fetched pages ask entrants to show code but do not unambiguously settle private-repository judging access. Keep private now; resolve code access and license before submission without automatically changing visibility.
- Tinker promotional credits are advertised through the Hacktoberfest promos page. Amount, account eligibility, available balance, and billing requirements have not been verified.

## Existing solutions preflight

The official open-source **Tinker Cookbook** supplies training recipes, renderers and evaluation building blocks. Reuse these for SFT/LoRA and sampling; custom work should concentrate on the outdoor task, dataset, task-specific scoring and experience. Its existence and documented recipes are verified, but no dependencies have been installed or exercised here.

Tinker is a hosted training API: training loops run locally and GPU compute runs remotely. The official quickstart documents authentication, LoRA training clients, baseline sampling clients and training primitives. An open-weight base model must be selected deliberately; do not assume every available model is open-weight. Current account access, model availability, license, export compatibility and cost require a smoke check. Do not promise offline inference before demonstrating exported-model execution on the intended hardware.

## Primary sources

1. [Week 1 announcement](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-week-1-touch-grass-2450-in-prizes-across-17-4pom)
2. [Challenge page and submission template](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)
3. [Tinker category and challenge hub](https://dev.to/challenges/hf26#best-use-of-tinker)
4. [Official general rules](https://dev.to/page/official-hackathon-rules)
5. [Partner credits](https://hacktoberfest.com/my/promos)
6. [Tinker documentation](https://tinker-docs.thinkingmachines.ai/)
7. [Official Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook)
8. [SDK quickstart](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/)
