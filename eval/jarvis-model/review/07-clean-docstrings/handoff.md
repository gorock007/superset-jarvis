# Docstrings for billing/tax.py
status: done
agent: opencode
brief: handoffs/briefs/2026-09-26-1000-tax-docstrings.md
## What the user asked
Document the tax helpers.
## What changed
Added docstrings to `vat_rate` and `apply_vat`; no code changed.
## Files
- billing/tax.py — modified
## Checks run
- `ruff check billing/tax.py --select D` → All checks passed!
- `pytest tests/billing/test_tax.py -q` → 7 passed
## Questions for the user
## Notes for Jarvis
Suggested commit: `billing: docstrings for tax helpers`
