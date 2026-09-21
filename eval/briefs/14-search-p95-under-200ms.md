# Get /search p95 under 200 ms on the 1M-row seed
worker: claude
model: opus
effort: high
started: 2026-09-13 09:50 · terminal: term_0e5c77

## Goal
`GET /search?q=` has a p95 of about 900 ms on the 1M-row seed database. Done
is p95 below 200 ms on the same seed, with identical results for the 50
queries in the benchmark. Changes go in `search/queries.py` and a new
migration `search/migrations/0019_search_indexes.py`.

## Context
The profile is already done and is in handoffs/merged/2026-09-11-search-profile.md:
82% of the time is one sequential scan caused by `ILIKE '%term%'`. Take the
same approach we took for the orders query last quarter.

## Scope
- May touch: `search/queries.py`, `search/migrations/0019_search_indexes.py`, `bench/`
- Must not touch: `search/api.py` (the response shape stays), `orders/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Index migration.
2. Rewrite the query to use it.
3. Benchmark and compare result sets.

## Checks
- `python bench/search_bench.py --rows 1000000 --p95-max 200` exits 0.
- `pytest tests/search -q` green.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
