# Find and fix the intermittent 500 on POST /api/checkout/confirm
worker: claude
model: fable
effort: high
started: 2026-09-15 08:40 · terminal: term_a90f2d

## Goal
Since the 2026-09-08 deploy, `POST /api/checkout/confirm` returns a 500 for
roughly 0.7% of production requests. The cause is unknown and nobody has
reproduced it locally; the tracebacks point at three different lines on
different days. Done means: the root cause is named in the handoff with the
evidence that convinced you, a regression test at
`tests/checkout/test_confirm_race.py` fails on the current code and passes
with your fix, and the replay script reports zero errors.

## Context
Django 5 API, Postgres, Celery. The only change in that deploy is described
in handoffs/merged/2026-09-08-checkout-idempotency.md. Read it first. You will need
production evidence: a read-only Datadog API key and the DSN of the
production read replica are in Vault at `kv/checkout/debug`. Those logs and
rows contain real customer emails, addresses and order contents. Do not
paste any of it into the handoff or into test fixtures.
Write the regression test the way `tests/checkout/test_refund_race.py` does
it: threaded test client, a `threading.Barrier`, assert on row counts.

## Scope
- May touch: `checkout/services/confirm.py`, `checkout/models.py`, `tests/checkout/`
- Must not touch: `payments/gateway/`, `checkout/migrations/`
- Shared files (edit minimally, name in handoff): `checkout/locks.py`

## Phases
1. Pull a week of failing requests from Datadog; group them by traceback.
2. Form a hypothesis, reproduce it in a test, confirm the test fails.
3. Fix it. Re-run the replay against a local server.

## Checks
- `pytest tests/checkout -q` is green.
- `python scripts/replay_confirm.py --n 500 --concurrency 20` prints `errors: 0`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
