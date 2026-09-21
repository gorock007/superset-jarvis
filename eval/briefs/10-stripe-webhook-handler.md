# Handle Stripe invoice.paid and invoice.payment_failed webhooks
worker: claude
model: opus
effort: high
started: 2026-09-16 13:10 · terminal: term_6be204

## Goal
`POST /webhooks/stripe` verifies the Stripe signature, handles `invoice.paid`
and `invoice.payment_failed`, updates `subscriptions.status`, and ignores
every other event type with a 200. A replayed event id is a no-op. The handler
is `src/webhooks/stripe.ts`, tests are `tests/webhooks/stripe.test.ts`.

## Context
No prior context: this is the first payments work in this repo. Express
with TypeScript and Prisma. Copy the structure of `src/webhooks/github.ts`:
raw-body middleware, signature check first, then a switch on the event type,
then the `processed_events` table for idempotency. Tests run against
stripe-mock with the dummy signing secret in the test fixtures; no real
Stripe keys are needed and none should be used.

## Scope
- May touch: `src/webhooks/stripe.ts`, `tests/webhooks/stripe.test.ts`, `tests/fixtures/stripe/`
- Must not touch: `prisma/schema.prisma`, `src/webhooks/github.ts`
- Shared files (edit minimally, name in handoff): `src/app.ts` (route registration)

## Phases
1. Signature verification and routing.
2. The two event handlers.
3. Idempotency and tests.

## Checks
- `npm test -- tests/webhooks/stripe.test.ts` green.
- `npx tsc --noEmit` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
