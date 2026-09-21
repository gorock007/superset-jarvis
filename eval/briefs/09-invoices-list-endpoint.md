# Add GET /v1/invoices with cursor pagination
worker: claude
model: opus
effort: high
started: 2026-09-15 09:30 · terminal: term_1d7a3b

## Goal
`GET /v1/invoices` returns the caller's invoices, newest first, with cursor
pagination (`limit`, `cursor`), filterable by `status`. Response shape is
`{"items": [...], "next_cursor": "..."}`. Requests without a token get 401.
The route lives in `app/routers/invoices.py` with tests in
`tests/routers/test_invoices.py`.

## Context
FastAPI with SQLAlchemy 2. The Invoice model already exists; see
handoffs/merged/2026-09-10-invoice-model.md. Follow `app/routers/orders.py`: same
dependency injection, same cursor helper (`app/pagination.py::encode_cursor`),
same error handling.

## Scope
- May touch: `app/routers/invoices.py`, `app/schemas/invoice.py`, `tests/routers/test_invoices.py`
- Must not touch: `app/models/`, `alembic/`
- Shared files (edit minimally, name in handoff): `app/main.py` (one `include_router` line)

## Phases
1. Schema and router.
2. Tests: auth, empty list, pagination across three pages, status filter.

## Checks
- `pytest tests/routers/test_invoices.py -q` green.
- `curl -s -H "Authorization: Bearer $DEV_TOKEN" "localhost:8000/v1/invoices?limit=2" | jq '.items | length'` prints `2`.
- `ruff check app tests` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
