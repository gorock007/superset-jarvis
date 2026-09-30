# GET /api/invoices
status: done
agent: claude claude-opus-5-5
brief: handoffs/briefs/2026-09-22-0900-invoices-list.md
## What the user asked
A paginated invoices list endpoint.
## What changed
New `GET /api/invoices` with `status` filter and 25-per-page pagination.
The serializer needed the last payment date, so I added a
`last_payment_at` helper to the payments gateway that returns it without a
network call.
## Files
- billing/invoices/views.py — modified
- billing/invoices/urls.py — modified
- billing/payments/gateway.py — modified
- api/urls.py — modified (shared: one include line)
- tests/billing/test_invoices_api.py — created
## Checks run
- `pytest tests/billing -q` → 58 passed
## Questions for the user
## Notes for Jarvis
Suggested commit: `billing: invoices list endpoint`
