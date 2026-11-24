# MIPO free portal release — 24 November 2026

Public game: https://plottwist-b1du.onrender.com/
Portal entry: https://plottwist-b1du.onrender.com/?cg=1
Marketing page: https://plottwist-b1du.onrender.com/play-mipo

## Submission update

MIPO is a free social guessing game for two or more friends. One player answers a question privately, the others predict the answer, and the reveal awards points. Players can continue with the same group.

Compared with the October submission:
- No payment, card, browser trial limit or paid replay in the free release; 8/18/30-question lengths.
- Bundled MIPO artwork replaces live image generation. No metered image or question generation on free rooms.
- Faster setup and automatic private lobby creation in the portal edition.
- CrazyGames v3 room updates, launch invites, live join listener and platform invite links.
- Platform locale and username support; gameplay start/stop separate from lobby/reveal screens; SDK mute settings take priority over in-game audio.
- Portal edition uses curated questions, has no 18+ settings, custom question text, photo uploads or free-text chat. Display names have a basic profanity filter.
- SDK midgame ad opportunity only when a finished match's host chooses replay. No-fill/ad error continues to replay. Revenue depends on platform approval, launch stage and ad availability.
- Existing gender, reconnection, first-round reopen and question deduplication behavior retained.

## QA performed

Free HTTP contract includes a full 18-question match, replay, another free room, 30-question limit and six portal languages with generation providers configured as assertion failures. Zero image jobs and zero checkout orders were created.
Existing HTTP, checkout/entitlement, content, continuity/gender, repeat-purchase recovery, invite capacity and affected DOM regressions passed in legacy mode. New SDK contract covers invites, locale/username, room status, audio settings and ad-error continuation. Local browser verified free room creation and automatic portal lobby with SDK-provided demo username.

Not established by local checks: acceptance by CrazyGames, actual ad delivery/revenue, live portal iframe latency on every device, or the platform's own QA declarations. Complete the portal preview against the deployed URL before checking submission declarations. Do not claim mobile testing or third-party testing that has not occurred.

## Operations

`MIPO_FREE_PLAY` defaults to `1` and overrides `MIPO_COMMERCE_ENABLED`. It disables new checkout, trial enforcement, paid generation admission, generation recovery and live image settings. Historical orders/callbacks remain for prior transactions. Existing entitlements are not deleted or spent by free play. `MIPO_FREE_PLAY=0` restores legacy server behavior for regression checks; the public marketing copy represents the new free release.

Production runs on the existing Render service. Earlier `plottwist-cg-staging` points to an older branch; use the public portal entry above when resubmitting, not that outdated staging URL.

Official requirements consulted:
- https://docs.crazygames.com/requirements/gameplay/
- https://docs.crazygames.com/requirements/technical/
- https://docs.crazygames.com/requirements/multiplayer/
- https://docs.crazygames.com/sdk/game/
- https://docs.crazygames.com/sdk/user/
- https://docs.crazygames.com/sdk/video-ads/
