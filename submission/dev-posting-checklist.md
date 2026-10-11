# Final posting checklist — Emi

**Submit by October11, 2026 at11:59 PM PDT (October12 at06:59 UTC).**
Verified against the [official contest rules](https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules)
and [challenge/template page](https://dev.to/challenges/hacktoberfest-week1-2026-10-05) on October11.

The agent has prepared files only. Per [release ownership](release-decision.md),
repository visibility and DEV publication remain yours. No new labels or training
are required to submit the completed project.

## 1. Make the code and demo accessible

- Review [the article](dev-post.md) and [dated verification](verification.json).
- Change **emihiggins/touch-grass-tinker** to public in GitHub → Settings → General → Danger Zone → Change repository visibility.
- In a signed-out/incognito window, check all three:
  - [Repository](https://github.com/emihiggins/touch-grass-tinker)
  - [Demo WebM](https://github.com/emihiggins/touch-grass-tinker/raw/refs/heads/main/demo/walkthrough.webm)
  - [Article screenshot](https://raw.githubusercontent.com/emihiggins/touch-grass-tinker/main/research/evidence/app-integration/recorded-corrected-desktop.png)
- Play the video, not just its GitHub file page. It is a silent download/playback link, not an embedded hosted app. If DEV does not display the screenshot reliably, upload that image using DEV's editor and replace its URL.
- Public-only CI has intentionally skipped while private. After changing visibility, use **Actions → Offline checks → Run workflow**. Do not claim hosted Linux/Windows CI passed until its runs actually finish.

## 2. Prepare the DEV post

- Open the submission template from the challenge page while signed into your DEV account.
- Title: **Lift-Lap Planner: let the model read the request, not invent the mountain**
- Tags: **devchallenge**, **hf26challenge**
- Paste [dev-post-body.md](dev-post-body.md) into the body editor. It has no YAML or internal comments. The canonical [dev-post.md](dev-post.md) includes `published: false` as repository metadata, not text to paste into the body.
- Preview the seven sections, image, video link, code links and results table. Do not replace the video label with “live demo.”
- Confirm eligibility under the official rules. If you had human teammates, add their DEV handles; one post per team. AI coding assistance is already disclosed.
- Best Use of Tinker is listed for consideration. Keep the explicit results and the caveat: no demonstrated aggregate task-success, latency or cost improvement. Category qualification and judging are the organizers’ decision.

## 3. Publish and record the entry

- Publish before the deadline. Confirm the article is publicly readable while signed out and has both required tags.
- Keep the published URL for your records. Publication status in this repository remains pending until actually verified.
- Record the submitted commit and article URL. Any later code changes must be identified in the root README as post-deadline changes; retain the contest-time evidence.

## Optional, not blocking today's entry

The local `dist/liftlap-local-demo.zip` is generated and verified. The GitHub source
ZIP and documented Python quick start are sufficient to obtain the app after public
access is enabled; no release-asset upload or hosted deployment is required here.
The agent session is optional and intentionally not shared. Future dataset review
and billing reconciliation remain research/maintenance tasks, not reasons to delay
an otherwise accurate submission.
