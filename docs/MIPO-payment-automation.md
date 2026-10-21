# Payment-to-access repair — 2026-10-21

## Changes

- Normalize PayPlus's official transaction callback shape: `transaction.uid`, `transaction.payment_page_request_uid`, amount, currency, status code, order metadata. Do not read card/3DS statuses as the charge result.
- Accept completed Charge callbacks only when a transaction type is present; Refund, Approval, Check and Token never grant credits. Legacy flat callbacks remain supported.
- Preserve signature, exact USD price, order/request binding and unique transaction protections. No redirect can grant credit.
- Save the pending order before leaving MIPO. If PayPlus omits order metadata on the return URL, poll that saved order with the same browser identity. Cross-browser ownership is still enforced by the server.
- Log callback outcome/error category only, without payment/customer payloads or credentials.

Schema source: the official PayPlus WooCommerce gateway `includes/wc_payplus_gateway.php`, `set_arrangement_callback`:
https://github.com/PayPlus-Gateway/payplus-payment-gateway

## Verification and remaining provider dependency

Local tests use signed synthetic callbacks only, never production credentials. They cover nested callbacks, one/two games, declines then approval, request mismatch, transaction reuse, wrong price/currency, no authorization/refund credit, missing return order, and no access from a return URL alone. Existing commerce/static-link/budget tests also pass. These are application tests, not proof of live provider delivery.

Production read-only IPN lookup for the previously verified purchase returned HTTP 403 on October 21. The API key, secret and payment-page UID were present. Response was JSON, not a browser challenge. This does not by itself establish whether the cause is API activation, credentials or another access restriction.

Live mode remains `static_link`. Appending `more_info` to a reusable link is an existing implementation assumption; official docs describe order metadata for GenerateLink API requests. End-to-end propagation by the reusable-link route has not been verified. Do not claim that a successful raw-link charge or a manually reconciled entitlement verifies the automatic flow.

The existing paid purchase was reconciled separately to room EDN8V without another charge. It is not a callback test. No additional real charge is authorized by this repair.

To close live verification, either obtain confirmation of supported reusable-link order metadata and a genuine matching callback, or restore server API access and use order-specific GenerateLink URLs. Any real purchase test needs Eran's approval; confirm one entitlement for one transaction and paid 18-question access, including a duplicate callback without another credit.
