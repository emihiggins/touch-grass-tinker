# Offline release and excluded-review fixes

The reported scheduled-run HTTP502 was not reproduced in the normal interactive environment: the complete release suite passed unchanged. But setting HTTP_PROXY/http_proxy to unreachable loopback port9 with empty NO_PROXY/no_proxy reproduced7 of8 local server tests failing. This establishes inherited proxy dependence, not proof of the exact prior proxy's502 cause.

Server tests and extracted-package checks now use local direct urllib openers. They do not change global proxy state or provider clients. The complete release passed under the deliberately invalid proxy setting; public-only Ubuntu CI now preserves this regression condition. No machine or scheduler proxy settings were changed.

The excluded-source preview was independently exercised and improved:

- Count imported `.e` shapes separately from excluded overlays in browser tests.
- Selecting imported/excluded/lift geometry clears conflicting selection; choosing an excluded list entry reveals its overlay.
- Open source lines use no fill; a filled closed area requires the actual `area=yes` tag, not just matching endpoints. Source lines no longer imply verified travel direction.
- Dogpatch shows the actual import-audit reason (`area_or_closed_way`), while Breckenridge's31 expert ways remain excluded.
- Long mobile source-review labels wrap instead of clipping. No source graph changed.

Normal-CSP browser tests cover four resorts ×390/768/1440, actual overlay counts/toggling/selection, Dogpatch area, open-line fill, keyboard, viewport bounds and zero external requests. Accessibility checks cover selected Dogpatch at390/1440; test-only axe injection bypasses CSP, regular interactions do not. Preview screenshots and hashes refreshed; main planner screenshots remain unchanged because its UI and server are unchanged.
