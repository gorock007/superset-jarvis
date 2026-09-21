# Decide when two company records count as duplicates
worker: claude
model: fable
effort: high
started: 2026-09-12 14:05 · terminal: term_77b0e3

## Goal
`is_duplicate()` in `pipeline/dedupe/rules.py` treats two company records as
the same company when their normalised names match. Sales says it merges
too much (subsidiaries with the parent's name collapse into one account).
Support says it merges too little (obvious typos stay separate). Both are
right. Decide what the rule should be and change it. The change itself is
probably under fifty lines, but merges are irreversible downstream, so the
decision is the work.

## Context
The original rule and its reasoning are in handoffs/merged/2026-08-21-dedupe-v1.md.
Keep the structure of `pipeline/dedupe/address_rules.py`: one pure function
plus a table of worked cases next to it.
Signals available on each record: name, domain, country, VAT id (present on
about 40% of rows), parent_id (present on about 5%).

## Scope
- May touch: `pipeline/dedupe/rules.py`, `tests/dedupe/`
- Must not touch: `pipeline/dedupe/merge.py`, `warehouse/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Write down twenty realistic record pairs and what the right answer is for each.
2. Choose the rule that gets the most of them right; note the ones it still gets wrong.
3. Implement it.

## Checks
There is no labelled set, so no test can tell you the rule is right. Put the
twenty pairs and your verdicts in the handoff, and say what you would want a
human to label before this ships.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
