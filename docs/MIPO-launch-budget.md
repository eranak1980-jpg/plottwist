# MIPO launch budget

The lifetime launch ceiling remains USD 150. It is an application estimate, not a provider billing limit. Do not reset the ledger or raise CAP to create capacity.

- Each paid credit reserves the original USD 9.30 envelope (60 image attempts and 3 text attempts), including the existing 30-question extension and tiebreak allowance. No model, prompt, image quality, price or entitlement changes.
- Trials reserve USD 3.30: 8 rounds + 4 final attempts + 8 image retries, plus 3 text attempts. This is a conservative call-count allowance, not a measured cost claim.
- Completion releases unused round capacity while retaining recorded costs and capacity for up to four final attempts. Unknown/failed/in-flight calls retain their per-call allowance. Optional tiebreaks reacquire capacity before changing game state.
- Paid checkout holds all purchased credits before issuing a payment URL. Credits transfer into games atomically, including both games in a bundle. They do not compete again with trial admissions.
- Payable static links cannot safely expire locally. Holds survive declined callbacks and late approvals; refreshing the same browser/product reuses its uncompleted link. Only a confirmed refund releases unconsumed credit capacity. Abandoned payable links can therefore consume available capacity and need deliberate provider-side reconciliation.
- Migration preserves call history and counters, includes existing pending links and unused paid credits, and is idempotent across restarts. No external calls or real charges occur during migration.
- Logs flag estimated liability at 80% of the ceiling. This is a log signal, not a configured email alert.

## Checkout verification and launch gate

Always send customers to `/play-mipo` or `/checkout?product=one_game` in their browser. Raw reusable PayPlus URLs bypass creation of an order and its budget hold. Never infer a paid entitlement merely because a provider success page redirects to a playable trial.

Production audit on 2026-10-21 found five pending orders, no recorded paid orders, and a new trial session after the owner's reported successful direct-link charge. That payment must be reconciled against provider evidence; do not create another real charge or fabricate a signed callback. A production paid entitlement has not yet been verified.

## Validation

`python tests/launch_budget.py` covers migration, SQLite/Postgres concurrency, checkout holds, late/duplicate callbacks, failed callback retention, duo transfers at the ceiling, final retries, unknown/late costs, and HTTP paid/18Q enforcement. All provider/model calls are stubbed. Existing budget, commerce, static-link, game-flow and UI checks still apply.
