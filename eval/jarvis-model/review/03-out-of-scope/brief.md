# Invoices list endpoint: GET /api/invoices
worker: claude
model: claude-opus-5-5
effort: high
started: 2026-09-22 09:00 · terminal: term_0d93aa

## Goal
`GET /api/invoices?status=open&page=2` returns the signed-in account's
invoices, newest first, 25 per page, with `{items, page, total}`. Done:
`pytest tests/billing/test_invoices_api.py -q` green.

## Context
Follow `billing/credits/views.py` (same pagination helper, same permission
class). Invoices are read from `billing.invoices.models.Invoice`; nothing
about payments changes.

## Scope
- May touch: `billing/invoices/views.py`, `billing/invoices/urls.py`, `tests/billing/test_invoices_api.py`
- Must not touch: `billing/payments/`, `billing/migrations/`
- Shared files (edit minimally, name in handoff): `api/urls.py`

## Phases
1. View + route. 2. Tests.

## Checks
`pytest tests/billing -q 2>&1 | tail -5`
