# Add a backfill DAG for customer_events, 2026-01-01 to 2026-06-30
worker: claude
model: opus
effort: high
started: 2026-09-15 14:00 · terminal: term_a1f6e0

## Goal
A new DAG under `dags/backfill/` with dag_id `backfill_customer_events`
reloads `customer_events` from the raw bucket into Snowflake one day per
task run, for 2026-01-01 through 2026-06-30, idempotently (delete the day's
partition, then insert). At most 4 days run in parallel. After the run, each
day's row count equals the count in the raw manifest.

## Context
The decision to backfill rather than patch is in
handoffs/merged/2026-09-09-customer-events-gap.md. Follow
`dags/daily/orders_sync.py`: same TaskFlow style, same `SnowflakeHook`
usage, same `on_failure_callback`. This runs against the production
warehouse using the `SNOWFLAKE_PROD` service credentials from the Airflow
connection store. The table holds real customer PII (emails, IP
addresses); do not export samples anywhere.

## Scope
- May touch: `dags/backfill/`, `tests/dags/`
- Must not touch: `dags/daily/`, `plugins/hooks/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. DAG with one mapped task per day.
2. Count check task at the end.
3. Dry run on one day, then the full range.

## Checks
- `airflow dags test backfill_customer_events 2026-01-01` succeeds.
- `python scripts/compare_counts.py --table customer_events --from 2026-01-01 --to 2026-06-30` prints `mismatches: 0`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
