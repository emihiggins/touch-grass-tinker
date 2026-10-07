# Emi's final publication steps

Implementation and release preparation are complete locally. **The agent will not change repository visibility or publish to DEV.** MIT was approved in message2437 and is applied in `LICENSE`. No additional model training or label review is required.

1. Review the [article](dev-post.md), [demo guide](../demo/README.md), [recorded video](../demo/walkthrough.webm), and [license/notices](../THIRD_PARTY_NOTICES.md).
2. When ready, change **emihiggins/touch-grass-tinker** to public yourself in GitHub Settings → General → Danger Zone → Change repository visibility. No command or automated release hook performs this switch.
3. Open a signed-out/incognito window and verify:
   - https://github.com/emihiggins/touch-grass-tinker
   - https://github.com/emihiggins/touch-grass-tinker/raw/refs/heads/main/demo/walkthrough.webm
   - The README local-demo instructions and MIT/ODbL notices.
4. The public-only offline GitHub workflow skips while private. After switching public, run **Actions → Offline checks → Run workflow**, or let a subsequent public commit trigger it. Local checks are already verified; hosted CI is not yet claimed.
5. Open the challenge submission template in your own DEV account. Copy the body of `dev-post.md` from the italic challenge line onward. The file's YAML front matter (`title`, `published:false`, `tags`) is repository metadata, not text to paste into DEV's rich editor. Use its title and tags in DEV's fields. Remove the internal publishing comment if it appears in the editor.
6. Preview all seven requested sections. Confirm the video link works signed out. A download link is intentional; if you prefer an embedded player, upload the video yourself to a supported host and replace that link. Do not imply this is a live hosted app or a fine-tuned success.
7. The challenge page was rechecked October 7: deadline October 11, 2026 at 11:59 PM PDT (October 12 at 06:59 UTC). Check current challenge eligibility/deadline in the linked official challenge page, add teammate credits if applicable, and publish yourself. No DEV username, credentials or account connection needs to be sent to the agent.

## Honest claims retained

- Matched pilot: base9/16, fine-tuned7/16. No fine-tuning gain or Best Use of Tinker claim.
- Different fresh frozen set: base13/16; small fictional set, not statistical/field validation.
- Video is an exact replay of one real app response, including an interpretation error and manual correction. It is not continuous live inference.
- OpenStreetMap lab is unreviewed. No live lift/weather/avalanche information or on-mountain navigation claim.

Billing reconciliation was attempted at01:07UTC but charges remain unverified; this is independent of editorial review. Current$1.75 holds are budget reservations, not a bill. No top-up is enabled by this project.
