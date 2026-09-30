# Docstrings for the public functions in billing/tax.py
worker: opencode
model: (user's picker)
effort: (none)
started: 2026-09-26 10:00 · terminal: term_2f8d6b

## Goal
Every public function in `billing/tax.py` has a one-paragraph Google-style
docstring (Args/Returns). No code changes. Done: `ruff check billing/tax.py
--select D` reports nothing, and `pytest tests/billing/test_tax.py -q` still passes.

## Context
Follow the docstrings in `billing/fx.py`.

## Scope
- May touch: `billing/tax.py`
- Must not touch: everything else
- Shared files (edit minimally, name in handoff): none

## Phases
1. Docstrings.

## Checks
`ruff check billing/tax.py --select D` and `pytest tests/billing/test_tax.py -q`
