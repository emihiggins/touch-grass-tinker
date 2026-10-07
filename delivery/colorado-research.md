# Colorado pass-resort research checkpoint

Winter Park (Ikon listing verified; access rules unknown) and Breckenridge (Epic candidate; automated official-page access blocked) are now bounded, unreviewed research samples. See the [dataset and adoption roadmap](../research/real-resort-expansion.md). No pass entitlement or navigation claim.

The existing review preview had three concrete defects: inline JS blocked by the loopback server CSP, a map centered at x=55 instead of450, and a disconnected toggle comparing two endpoints necessarily in the same weak component. Fixed with an allowlisted same-origin script, aspect-preserving centered projection and largest-component filtering. Sample/filter changes clear stale selection. Mobile metadata wrapping, valid definition-list markup and document language were corrected.

Verification includes four samples × three widths (390/768/1440), keyboard segment selection, actual filter counts, geometry bounds, no body overflow, no external requests, no JS errors. Phone Winter Park and desktop Breckenridge screenshots visually inspected. Axe initial/selected at390/1440 reports no A/AA violations or incomplete findings (test-only CSP bypass to inject axe; ordinary interaction test has CSP enforced). Line style legend clarifies that blue ink is not a difficulty claim.

The server change only adds the review JS route; the main planning UI is unchanged. Main recorded demo/screens/PDF refreshed against the current server. Existing model evidence remains13/16. No provider calls or new spending. Previous preview commits passed Gitleaks in this runtime, closing the scheduled runner's scanner gap.

Remaining: full-resort coverage, expert-grade contract, source direction/access/junction review, authorized fresh operator status, measured timing and field validation. No research sample was promoted into planner selection.
