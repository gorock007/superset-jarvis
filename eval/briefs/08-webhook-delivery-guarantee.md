# Decide what delivery guarantee our outgoing webhooks make
worker: claude
model: fable
effort: high
started: 2026-09-13 13:45 · terminal: term_c8e671

## Goal
`api/webhooks/deliver.py` retries a failed delivery five times with backoff.
Customers complain about duplicate events and about missed events, in about
equal numbers. We have never said what we guarantee. Decide it: at-least-once
with an idempotency key header, a dedupe window on our side, ordered or
unordered. Then make the change. Expect 20 to 40 lines of code. The size is
not the hard part; customers will build against whatever you pick.

## Context
No prior context: nothing has been decided or written down about webhook
guarantees before this brief. Around 300 customers consume webhooks; the
largest receives 40 events per second. Deliveries are rows in
`webhook_delivery` with a status and an attempt count.

## Scope
- May touch: `api/webhooks/deliver.py`, `api/webhooks/models.py`, `docs/webhooks.md`
- Must not touch: `api/billing/`, `api/webhooks/signing.py`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Write the guarantee as one sentence a customer could read.
2. Change the delivery code to match it.
3. Update the public docs page.

## Checks
The existing tests pass whichever guarantee you choose, so they prove
nothing here. State the guarantee in the handoff and list the customer
complaints it does and does not resolve.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
