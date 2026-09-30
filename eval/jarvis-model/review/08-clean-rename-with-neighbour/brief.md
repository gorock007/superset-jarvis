# Rename the REDIS_URI env var to REDIS_URL
worker: claude
model: haiku
effort: low
started: 2026-09-26 13:30 · terminal: term_c4a2e9

## Goal
The app reads `REDIS_URL`; `REDIS_URI` is still accepted for one release
with a deprecation warning. Done: `rg -n REDIS_URI --glob '!CHANGELOG.md'`
only shows the fallback line in `app/config.py`, and
`pytest tests/test_config.py -q` passes.

## Context
Same approach as the `DB_URI` → `DATABASE_URL` rename in
handoffs/merged/2026-07-14-database-url.md.

## Scope
- May touch: `app/config.py`, `.env.example`, `docs/deploy.md`, `tests/test_config.py`
- Must not touch: `infra/`, `web/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Rename + fallback. 2. Docs. 3. Test.

## Checks
`pytest tests/test_config.py -q` and the `rg` command above.
