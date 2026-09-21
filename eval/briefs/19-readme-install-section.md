# Rewrite the Install section of the README
worker: claude
model: sonnet
effort: medium
started: 2026-09-16 11:45 · terminal: term_5e0b92

## Goal
The Install section of `README.md` covers the three supported methods
(Homebrew, `pipx`, from source) in that order, each with a copy-pasteable
command and a one-line check that it worked. The long version moves to a
new `docs/install.md`, linked from the README.

## Context
No prior context; nothing earlier touches the docs. Match the tone and
structure of `docs/upgrade.md`: short imperative sentences, one code block
per step, no screenshots.

## Scope
- May touch: `README.md`, `docs/install.md`
- Must not touch: `docs/upgrade.md`, `src/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Write `docs/install.md`.
2. Cut the README section down to the three commands plus the link.

## Checks
- `npx markdownlint README.md docs/install.md` clean.
- `npx markdown-link-check README.md` reports no dead links.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
