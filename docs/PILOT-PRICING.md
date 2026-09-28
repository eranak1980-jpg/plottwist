# Launch pilot — September 28, 2026

Accepted pricing: USD 7.99 / one game, USD 12.99 / two games, up to 18 questions each; 0.49 per extra question for the extended game. Quotes are server-calculated and restricted to 8–30 questions, 1–2 games. Six players maximum. Checkout is deliberately disabled until a payment provider and verified entitlements exist. `/pricing` is a preview, not a purchase flow. The site's name is unchanged pending final naming decision.

## Budget and measurement

The live pilot has a persistent USD 150 **estimated reservation envelope**, maximum 100 AI sessions, and no automatic reset or top-up. Each session currently reserves USD 9.30: 60 image attempts at provisional USD 0.15 + three text calls at provisional USD 0.10. This conservative reservation means at most 16 new sessions initially, less than the 100-session ceiling. Reservations are not automatically released; this prevents abandonment, restarts and unknown-billing timeouts from silently restoring spending capacity. Existing admitted games use their own remaining quota. Replay creates a new reservation. Local no-key test runs consume none.

Each round has at most three image attempts; the final poster permits four to accommodate the three tie-break cycles. SDK text retries are disabled; each image retry gets its own persistent call record. Calls are logged before contacting the provider; errors/timeouts remain unpriced reservations. Usage is stored without photos, names or prompts. Image costs are calculated for gpt-image-2.5-flare at standard $5 text-input, $8 image-input and $30 output per million tokens. Alternate model rates and text pricing are not guessed. Host-only `/api/costs/CODE?host=TOKEN` reports measured cost separately from unpriced calls and an estimated total. Never share the host URL/token. The finish screen provides this report to the authenticated host.

This is **not a guaranteed provider-dollar hard cap**: actual token usage is known after a request, unpriced calls and rates/taxes may differ, and already in-flight requests can finish. Measured overruns increase the global reservation and stop subsequent calls when the envelope is exhausted. Cost samples must be reconciled with provider billing before public launch. Hosting, payment fees, taxes and ads are not included in the per-game AI report.

## Before paid/public launch

Connect payment provider with signed webhooks and idempotent game entitlements. Add verified host identity and one-trial-per-host rules; the current pilot is globally bounded, not an identity-verified public free offer. Free launch mode must enforce eight questions server-side; pilot testers may currently use 6–30. Measure real costs across 2–6 players, final/tied posters, 8/18/30 rounds and errors. Do not publish an unlimited free offer. No provider billing settings or paid subscriptions were changed in this update.
