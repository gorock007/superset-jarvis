# Default page size 50 for list endpoints, with a `page_size` override
worker: claude
model: sonnet
effort: medium
started: 2026-09-23 11:20 · terminal: term_b21c90

## Goal
Every list endpoint that uses `api/pagination.py` returns 50 items per page
by default (was 20) and accepts `?page_size=` up to 200. Pages are 1-based,
as today. Done: `pytest tests/api/test_pagination.py -q` green.

## Context
Only `api/pagination.py` implements paging; endpoints call `paginate(qs, request)`.
Keep the response shape `{items, page, page_size, total}` unchanged.

## Scope
- May touch: `api/pagination.py`, `tests/api/test_pagination.py`
- Must not touch: every view module
- Shared files (edit minimally, name in handoff): none

## Phases
1. Change + tests.

## Checks
`pytest tests/api/test_pagination.py -q`
