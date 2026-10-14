# MIPO — pricing readiness review
Date: 2026-10-14. Status: DRAFT / DO NOT MERGE OR DEPLOY.
Owner approval required: Eran. Proposed prices remain unapproved.

## Decision
Prepare $5.99 for one group game and $9.99 for two, but HOLD production approval until measured usage, contractual payment fees and the payment-to-entitlement path are verified. No live payment was made. No gameplay, AI model, question count, access rights or pilot budget was changed.

## Verified evidence
- Reviewed main commit 3a80afff5e8ee53074d740cf75b4247f1f9f35e1.
- Live GET /api/pricing returned 799 / 1299 / 299 cents, USD; trial 8, included 18, extended 30, max players 6. commerce_enabled and checkout_enabled were true. These flags only indicate configuration presence, NOT successful provider authorization.
- Live GET /health returned image_model=gpt-image-2.5-flare, ai_images=true, storage=postgres.
- Questions: kyc_ai.py calls gpt-5.6-luna, max_output_tokens=4000, SDK retries=0. One call per pack generation; creation, lobby settings and replay/freshroom can request new packs. Per-session text call budget is 3. No actual usage export was available.
- Images: kyc_visuals.py uses Images edit, n=1. Defaults low quality, 720x912; runtime quality/size overrides remain unverified. Every eligible round can generate an image, plus an eligible final poster. Round references include 1–2 people; final includes consenting eligible participants. Participant count can affect input cost; it does not multiply each round by the number of players.
- Normal completed 8/18/30-round sessions with all eligible photos, one pack, no retries or tiebreaks: 9/19/31 image requests plus one text request. These are conditional counts, not measured averages. Paid tiebreaks, repeated final attempts and settings changes can add calls.
- Image SDK automatic retries are disabled. Explicit logic allows a second attempt for selected transient errors; budget records attempts and retains estimates for unpriced failures. Persistent image jobs deduplicate work; storage retries do not regenerate images.
- kyc_budget.py records usage in budget_calls. Only Flare images with sufficient token detail get actual_micro; text calls currently remain unpriced. Cached-token discounts are not applied by its image calculation. Reconcile usage with provider billing before calling it actual expenditure.
- OpenAI standard rates checked 2026-10-14: Luna input $0.20 / cached $0.02 / output $1.20 per million tokens; Flare text input $5 / cached $1.25, image input $8 / cached $2, output $30 per million tokens.
  Sources: https://developers.openai.com/api/docs/models/gpt-5.6-luna and https://developers.openai.com/api/docs/models/gpt-image-2.5-flare
- Render logs access reached Sign In. No authenticated ledger, invoices, current launch-budget balance or fixed-service bills were retrieved.

## Cost calculation — not verified profit
Internal reserve assumptions are $0.15 per image attempt and $0.10 per text attempt. They are NOT unit prices, measured averages or guaranteed upper bounds.

Illustration only: one question-pack call, all eligible round images and one final, no retries/tiebreaks:
| Product | Proposed revenue | Provisional AI illustration | Remainder BEFORE fees, trials, taxes, other variable costs and fixed costs |
| --- | ---: | ---: | ---: |
| Trial, 8 questions | $0 | $1.45 | -$1.45 |
| One game, 18 questions | $5.99 | $2.95 | $3.04 |
| Two games, both fully played | $9.99 | $5.90 | $4.09 |
| 12 extra round images for extension | $2.99 | $1.80 incremental | $1.19 |

Extension illustration excludes any additional final/retry costs. One additional provisional trial per purchase would reduce the single/duo remainders to $1.59 / $2.64 before the other deductions. This is a sensitivity example, not an observed conversion rate.

Let C18 be measured full-game AI cost, Ctrial measured trial cost, Ntrial/Norders the allocated free-trial ratio, F(P) actual contractual payment+FX fees, V other variable costs, T taxes included in receipts:
- Single contribution = 5.99 - C18 - F(5.99) - Ctrial*Ntrial/Norders - V - T.
- Duo contribution = 9.99 - 2*C18 - F(9.99) - Ctrial*Ntrial/Norders - V - T.
Use actual redemption rates separately; do not assume unplayed second games to prove profitability.
- Operating result = total contribution minus fixed monthly infrastructure/services and other fixed expenses.
For group sizes 2, 4 and 6, compute separate means and high-percentile costs from real sessions; no numeric group-size averages can currently be supplied.

Missing inputs:
1. Authenticated export of budget_calls joined to budget_sessions and game metadata, including rounds, access type, participant counts, retries, tiebreaks and unfinished sessions. The current host cost endpoint only covers the active session; use all historical sessions for aggregate totals. Historical participant counts may need logs if not retained.
2. OpenAI usage/billing reconciliation, including unknown failed requests and token caching.
3. PayPlus/Max contract: percentage and fixed fees, USD/cross-border/FX fees, settlement currency, refund/chargeback costs and applicable fee taxes.
4. Actual Render compute, Postgres, storage, traffic and other recurring bills, separated from usage-based costs.
5. Trial completion/conversion and paid-game redemption observations.

## Critical launch blockers
1. Current one-game checkout redirects to a fixed $7.99 PayPlus link before creating an order in MIPO. That route bypasses order ownership, checkout_started tracking and the existing callback matching flow. A successful payment on that link alone does not establish automatic entitlement.
2. Draft restores the existing server checkout path for one_game, matching two_games and extension. This REQUIRES working PayPlus API access and verified callbacks. Prior API refusal is unresolved; no claim that this draft fixes provider permissions. If PayPlus only supports static links on this account, agree and implement a verified order-matching solution separately before release. Do not simply change a static link price and deploy.
3. Latest merchant-status evidence is Eran's report that support diagnosed a nonexistent merchant number. Subsequent legal-name form preparation is not evidence the merchant/USD permissions were fixed. Require provider confirmation and an explicitly authorized Israeli-card USD test.
4. Pilot budget reserves $9.30 per admission and never releases unused reservations. With a $150 cap, at most 16 admissions fit from an empty ledger, potentially fewer after overages. Current remaining balance unknown. This can block free and paid games; require a separate reviewed decision before launch. No limits were changed.
5. Analytics purchase_completed is recorded on repeated paid callbacks; reports must deduplicate by order ID. checkout_started currently occurs only after provider link creation, excluding failed checkout attempts. Visitor/client/owner identifiers differ across stages; validate joins before reporting a funnel or conversion improvement. No new tracking feature added in this pricing draft.

## Prepared changes and surface map
- mipo_commerce.py: proposed prices 599/999/299; pricing payload and quote derive from PRODUCTS; rights/counts unchanged.
- static/landing.html: proposed prices, group-wide one-payment message, accurate 6-total-player example, two-game saving $1.99.
- static/pricing.html: proposed prices and EN/HE value copy; same question limits and extension rules.
- static/checkout.html: group/no-subscription copy and package summary from server prices; one-game restored to existing order-based checkout; pending confirmation copy no longer claims payment was received before verification.
- Trial-end screen in static/experience.js links to landing pricing; extension copy remains $2.99. static/kyc.html and kyc_locales.py contained no searched old price literals. Recheck all deployed/localized assets before release.
- PayPlus hosted checkout, terminal USD settings, emails/receipts: NOT changed; mandatory provider-side verification remains.
- Old orders keep their stored amount; callbacks compare against each order, not the new current price.
- No expiry countdown, forced urgency, split-pay mechanism, new package, subscription or per-player charge.

## Validation
Passed locally with SQLite and a fake provider, no external charges:
- Quotes 599/999 plus unchanged 299 extension.
- Provider payloads in USD with correct amount and item price.
- Signed mismatched amounts rejected.
- Signed successful callbacks grant 1 or 2 game credits as appropriate.
- Repeated callback does not duplicate entitlement.
- Extension sets existing paid game to 30.
- Trial configuration remains 8.
- JavaScript syntax for changed HTML passes node --check.

Not yet completed: browser/mobile visual QA, full free-trial gameplay and trial enforcement, spent-credit rejection, concurrent requests/callbacks, actual provider callbacks/receipts, Israeli-card USD payment, refund behavior, live deployment consistency. Local idempotent callback tests do not prove prevention of duplicate user-submitted charges.

## Release gate
1. Reconnect Render to read existing usage/bills and close the missing cost inputs.
2. Confirm merchant/USD/API permissions and chosen payment integration; resolve pilot-budget blocker.
3. Recalculate contribution for both prices, including trial allocation and measured retries.
4. Present final figures and request Eran's explicit approval of $5.99/$9.99 and deployment.
5. Run sandbox end-to-end and mobile/desktop QA; real charge only with separate explicit authorization.
6. Coordinate server, assets and PayPlus release; stop if any displayed/requested/charged amount differs. Preserve correct amounts for existing orders.
7. Measure visitors → trial started → trial completed → checkout started → payment completed using deduplicated, joinable events; revenue and variable costs by product. Do not claim improved conversion without data.

Final approval request: RESERVED until evidence above is complete. This draft is reviewable now, but is not recommended for production publication yet.
