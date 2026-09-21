# Summarise the changes since v2.3.0 into the changelog
worker: claude
model: sonnet
effort: medium
started: 2026-09-17 15:10 · terminal: term_64a2f8

## Goal
`CHANGELOG.md` gets a "2.4.0" section at the top that summarises everything
merged since the v2.3.0 tag, grouped under Added, Changed and Fixed, written
for users rather than for us: what they will notice, not which files moved.

## Context
What is and is not in 2.4.0 was agreed in handoffs/merged/2026-09-12-v2.4-scope.md.
Match the existing 2.3.0 entry in `CHANGELOG.md`: one line per change,
present tense, PR number in parentheses at the end, no author names.

## Scope
- May touch: `CHANGELOG.md`
- Must not touch: `package.json` (the version bump is a separate brief), `docs/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Read the merged PR titles and descriptions since the tag.
2. Drop internal-only changes; group the rest.
3. Write the section.

## Checks
Read it back once as a user who has never seen the repo.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
