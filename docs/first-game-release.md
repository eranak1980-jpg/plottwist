# MIPO first-game improvements — 26 October 2026

## Implemented
- Short default setup: name, audience, eight light rounds. Full options remain under Customize.
- On-demand rules and a clearly labeled fictional example round. The example creates no room and consumes no trial.
- Optional photos on client and server. Photo consent and individual adult-content confirmation remain enforced.
- Generated images never disable Next, replay, or tie-break controls.
- 36 curated opening questions for English/Hebrew friends, couples, and families; first two rounds only, respecting narrow advanced topics and prior question history.
- Tighter AI editorial instructions, question-length and option-length bounds; existing language/safety/deduplication filters retained.
- Leaner question screens, role labels, clearer reveal discussion prompt, optional collapsed lobby settings.
- Finished-game relationship counts derived from actual guesses, plus a locally downloadable PNG result card. No automatic social publishing.
- Landing player-count and checkout wording corrected; coherent sample question/options.
- First-party room_created, player_joined and round_completed events; no raw identifiers in analytics.
- Pricing, purchase limits, checkout validation and entitlements are unchanged.

## Verified locally
- Full HTTP games: 8/18/30 rounds, 2/4 players, no photos; all result counts verified.
- Mock payment callbacks and entitlement limits (no real charges).
- Consent, unauthorized access, stale image retries, live-job preservation.
- DOM tests: quick setup, local demo, optional photos, adult gates, image progression, summary, six UI languages.
- Existing content safety and duplicate tests, session recovery, checkout return.

## Limits
Automated tests do not establish enjoyment, willingness to pay, or CrazyGames acceptance. Opening content was edited in English and Hebrew; other languages retain their native curated packs. No paid image generation used for QA. Human group testing remains necessary.
