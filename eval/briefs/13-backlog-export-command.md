# Add `backlog export --format json|csv`
worker: claude
model: opus
effort: high
started: 2026-09-12 10:15 · terminal: term_be4410

## Goal
`backlog export --format json` writes every save as a JSON array to stdout;
`--format csv` writes a header plus one row per save; `--out PATH` writes to
a file instead; `--since YYYY-MM-DD` filters. An unknown format exits 2 with
a usage message. Code goes in `backlog/commands/export.py`, tests in
`tests/test_export.py`.

## Context
The command layout was settled in handoffs/merged/2026-09-01-backlog-cli-layout.md.
Follow `backlog/commands/import_.py`: same Click group registration, same
`open_store()` context manager, same error-to-exit-code mapping.

## Scope
- May touch: `backlog/commands/export.py`, `tests/test_export.py`
- Must not touch: `backlog/store/`, `backlog/schema.sql`
- Shared files (edit minimally, name in handoff): `backlog/cli.py` (register the command)

## Phases
1. JSON writer and `--since`.
2. CSV writer and `--out`.
3. Tests.

## Checks
- `pytest tests/test_export.py -q` green.
- `backlog export --format csv | head -1` prints `id,url,title,label,saved_at`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
