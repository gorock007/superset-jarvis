# Split users.full_name into first_name / last_name and backfill production
worker: claude
model: opus
effort: high
started: 2026-09-17 09:40 · terminal: term_37dd0c

## Goal
`users` has `first_name` and `last_name` columns, populated for all 2.1M
production users from `full_name` using the agreed rule (split on the last
space; a single token goes to `first_name`). `full_name` stays for now. The
migration is `accounts/migrations/0031_split_full_name.py`, the backfill is
`scripts/backfill_names.py`, batched at 5,000 rows with a 200 ms pause.

## Context
The splitting rule and the rollout order were decided in
handoffs/merged/2026-09-09-name-split-decision.md. Follow
`scripts/backfill_locale.py`: same batching loop, same `--dry-run` and
`--verify` flags, same progress logging. You will run this against the real
production database: the `DATABASE_URL` is in 1Password under "Prod DB –
migrator". These are real people's names. Do not log row contents, only ids
and counts.

## Scope
- May touch: `accounts/migrations/0031_split_full_name.py`, `scripts/backfill_names.py`, `tests/scripts/test_backfill_names.py`
- Must not touch: `accounts/models/permissions.py`, `billing/`
- Shared files (edit minimally, name in handoff): `accounts/models/user.py` (two new fields)

## Phases
1. Migration and model fields.
2. Backfill script and its tests.
3. `--dry-run` on production, then the real run.

## Checks
- `pytest tests/scripts/test_backfill_names.py -q` green.
- `python scripts/backfill_names.py --verify` prints `0 rows remaining`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
