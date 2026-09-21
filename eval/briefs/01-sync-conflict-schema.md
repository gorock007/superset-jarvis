# Decide how offline edit conflicts are stored and resolved (Trailnotes mobile)
worker: claude
model: fable
effort: xhigh
started: 2026-09-14 09:12 · terminal: term_4c1e9a

## Goal
Trailnotes lets people edit notes offline on several devices. When two
devices change one note before either syncs, the server currently keeps
whichever push arrives last and silently drops the other. We need a data
model and a resolution rule for these conflicts, and nobody has decided what
that should be: last-write-wins per field, a CRDT for the note body, or a
conflicts table the user resolves by hand are all on the table. Choose one,
justify it, and write down the schema that supports it.

## Context
The mobile client is React Native with SQLite; the server is Node with
Postgres. Note bodies are Markdown, typically under 5 KB. About 4% of users
have more than one active device. Product has said "never lose text" but
also "never show the user a merge dialog", and those two may not both be
achievable; say so if they are not.

## Scope
- May touch: `docs/design/sync-conflicts.md` (create it), `server/migrations/0042_sync_conflicts.sql` (draft only)
- Must not touch: `mobile/src/db/`, `server/src/sync/push.ts`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Write up the three candidate models with the failure cases each one has.
2. Pick one; write the schema and the resolution rule into the design doc.
3. Draft the migration. Do not wire it into the sync code.

## Checks
No test can tell you the design is right. In the handoff, list the conflict
scenarios you walked through by hand and what the chosen model does in each.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
