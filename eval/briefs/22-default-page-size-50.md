# Raise the default API page size from 20 to 50
worker: claude
model: sonnet
effort: medium
started: 2026-09-16 09:20 · terminal: term_f09c1e

## Goal
List endpoints return 50 items when the caller sends no `limit`. That means
`DEFAULT_PAGE_SIZE` in `api/pagination.py` is 50, the tests in
`tests/test_pagination.py` expect 50, and the number in `docs/api/pagination.md`
says 50.

## Context
Do it the way `MAX_PAGE_SIZE` was raised in
handoffs/merged/2026-08-28-max-page-size.md: constant, test expectation, docs line,
nothing else. No endpoint overrides the default, so nothing else changes.

## Scope
- May touch: `api/pagination.py`, `tests/test_pagination.py`, `docs/api/pagination.md`
- Must not touch: `api/views/`, `api/serializers/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Constant, test, docs.

## Checks
- `pytest tests/test_pagination.py -q` green.
- `grep -n "DEFAULT_PAGE_SIZE = 50" api/pagination.py` prints one line.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
