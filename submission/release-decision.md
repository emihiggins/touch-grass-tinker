# Release decision — ready for Emi's choice, not published

## Recommended publication scope

Publish Lift-Lap as a transparent open-AI planning experiment, **without claiming Best Use of Tinker eligibility or a fine-tuning gain**. Fine-tuning ran but regressed on the matched pilot (9/16 base vs7/16 trained). The selected base achieved13/16 on a separate frozen, human-reviewed set. These are different sets, not a9→13 improvement.

## Concrete items to approve

1. **Code visibility:** change `emihiggins/touch-grass-tinker` from private to public after final release review. A heuristic history scan checked359 blobs with no matching key/token patterns; this is not a guarantee. The repository includes human-review provenance, synthetic examples, failed experiments and generated evidence; no private run directories, credentials or provider IDs should be exposed. Alternatively provide judges private access if challenge rules accept it; this is not equivalent to public open source.
2. **Original-code license:** recommend MIT, copyright2026 Emi Higgins. The exact [proposed MIT text](proposed-LICENSE-MIT.txt) is prepared; it is not a license grant already applied. OpenStreetMap data remains separately attributed under ODbL; upstream model/SDK/Cookbook licenses remain separate.
3. **Video:** publish `demo/walkthrough.webm` with the disclosure in `demo/README.md`. It shows an exact recorded real-model response, its mistake, local correction and simulated planning; not continuous live inference. A GitHub-hosted downloadable video or external video upload needs user approval. No paid hosting/domain needed.
4. **DEV identity and publication:** confirm the DEV username that will publish, any teammate credits, and whether Emi will post or authorize agent publication. Draft: `submission/dev-post.md`. No DEV post exists yet. Resolve actual public URLs after the preceding approvals, then preview before publishing.

## Already done

-145 pre-integration tests;149 after integration, plus desktop/mobile and print generation checks.
-Real loopback browser→Tinker→confirmation→route call completed; semantic failure disclosed.
-Recorded mode requires identical request/context/catalog; otherwise refuses.
-Model output is schema-validated. Human hard-exclusion correction is local and route validation follows confirmation.
-Offline allowlisted archive built and exercised in an isolated directory; no credentials or model calls required.

## Limits that remain even after release

This is a local simulation, not production hosting or ski navigation. OSM terrain is unreviewed; no field validation, real-time lift/weather/avalanche data, or measured screen-time claim. The local server must not be exposed publicly unchanged. Live inference is opt-in and scoped to a ten-call allowance; it is not an unlimited public API. No further training is justified solely to chase the prize category.
