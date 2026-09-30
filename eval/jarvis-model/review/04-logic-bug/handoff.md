# Default page size 50
status: done
agent: claude sonnet
brief: handoffs/briefs/2026-09-23-1120-page-size-50.md
## What the user asked
Bigger default pages and a page_size override.
## What changed
Default page size is 50; `page_size` is accepted and clamped to 1..200.
I tidied the offset arithmetic into one line while I was there.
## Files
- api/pagination.py — modified
- tests/api/test_pagination.py — modified
## Checks run
- `pytest tests/api/test_pagination.py -q` → 9 passed
## Questions for the user
## Notes for Jarvis
Suggested commit: `api: default page size 50, page_size override`
