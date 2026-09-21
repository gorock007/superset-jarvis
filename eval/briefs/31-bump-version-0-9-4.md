# Bump the version to 0.9.4
worker: claude
model: haiku
effort: low
started: 2026-09-15 18:20 · terminal: term_8e61aa

## Goal
The version is 0.9.4 in both places it is written: `pyproject.toml` and
`src/tidy/__init__.py`. Importing the package reports 0.9.4.

## Context
Part of the release plan in handoffs/merged/2026-09-15-release-0.9.4-plan.md. The
changelog and the lockfile are handled by other briefs.

## Scope
- Must not touch: `CHANGELOG.md`, `uv.lock`

## Phases
1. Change the two strings.

## Checks
`python -c "import tidy; print(tidy.__version__)"` prints `0.9.4`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
