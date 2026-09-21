# Add docstrings to the public functions in the billing package
worker: claude
model: sonnet
effort: medium
started: 2026-09-14 10:40 · terminal: term_9d31b7

## Goal
Every public function and class in the billing package has a docstring.
Private helpers (leading underscore) are left alone. No behaviour changes.

## Context
No prior context; there is no earlier handoff about documentation in this
package. Write them the way `compute_tax()` is documented: a one-line
summary, a blank line, then Args, Returns and Raises sections in Google
style, with units stated for every money value (cents, never floats).

## Scope
- May touch: `billing/` (docstrings only)
- Must not touch: `billing/migrations/`, `tests/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Module by module, alphabetical.

## Checks
Nothing changes at runtime, so there is nothing to run. Re-read your diff
and confirm it contains docstrings and nothing else.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
