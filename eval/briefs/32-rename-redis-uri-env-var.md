# Rename the REDIS_URI setting to REDIS_URL
worker: claude
model: haiku
effort: low
started: 2026-09-14 13:30 · terminal: term_71d4c6

## Goal
The setting is called `REDIS_URL` everywhere it is read or documented:
`config/settings.py`, `.env.example` and `docker-compose.yml`. The string
`REDIS_URI` no longer appears in the repo.

## Context
Do it the way `DB_URI` became `DATABASE_URL` in
handoffs/merged/2026-08-19-database-url-rename.md: a straight rename with no fallback
to the old name. Deployed environments are updated by ops separately.

## Scope
- May touch: `config/settings.py`, `.env.example`, `docker-compose.yml`, `README.md`
- Must not touch: `.env`, `deploy/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Rename.

## Checks
- `grep -rn REDIS_URI . --exclude-dir=.git --exclude-dir=deploy | wc -l` prints `0`.
- `python -c "from config import settings; print(bool(settings.REDIS_URL))"` prints `True` with `.env.example` loaded.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
