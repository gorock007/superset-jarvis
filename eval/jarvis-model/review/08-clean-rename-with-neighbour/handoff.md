# REDIS_URI → REDIS_URL
status: done
agent: claude haiku
brief: handoffs/briefs/2026-09-26-1330-redis-url.md
## What the user asked
Rename the Redis env var.
## What changed
Config reads `REDIS_URL`, falling back to `REDIS_URI` with a
DeprecationWarning. `.env.example` and the deploy doc use the new name.
## Files
- app/config.py — modified
- .env.example — modified
- docs/deploy.md — modified
- tests/test_config.py — modified
## Checks run
- `pytest tests/test_config.py -q` → 11 passed
- `rg -n REDIS_URI --glob '!CHANGELOG.md'` → app/config.py:18-20 (the fallback) only
## Questions for the user
## Notes for Jarvis
Suggested commit: `config: rename REDIS_URI to REDIS_URL (URI still accepted)`
