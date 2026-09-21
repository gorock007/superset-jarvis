# Prettier pass over the web package
worker: codex
model: gpt-5.6-luna
effort: low
started: 2026-09-15 12:00 · terminal: term_6f2a0b

## Goal
Run Prettier over `packages/web/`.

## Context
The repo's Prettier config is already in place at the root.

## Scope
- May touch: `packages/web/`
- Must not touch: `packages/web/public/`, `packages/api/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Format.

## Checks
`npx prettier --check packages/web`

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
