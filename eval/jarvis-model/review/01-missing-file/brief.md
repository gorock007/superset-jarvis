# Add --since to `backlog export`
worker: claude
model: claude-opus-5-5
effort: high
started: 2026-09-20 10:05 · terminal: term_4c1e02

## Goal
`backlog export --since 2026-09-01` exports only saves created on or after
that date. Without `--since` the output is unchanged. Done:
`pytest tests/test_export.py -q` green, and
`backlog export --since 2026-09-01 --format csv | wc -l` prints fewer lines
than the unfiltered export on the fixture DB.

## Context
Follow the way `--tag` is implemented in `cli/export.py` (option parsed in
`export_cmd`, filter applied in `_query_saves`). Dates are parsed with
`datetime.date.fromisoformat`; reject anything else with a click error.

## Scope
- May touch: `cli/export.py`, `cli/_dates.py` (new, if you want a helper), `tests/test_export.py`
- Must not touch: `backlog/db/`, `backlog/models.py`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Option + filter. 2. Tests.

## Checks
`pytest tests/test_export.py -q 2>&1 | tail -5` and `ruff check cli tests`
