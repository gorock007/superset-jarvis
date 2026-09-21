# Read the log level from LOG_LEVEL
worker: claude
model: sonnet
effort: medium
started: 2026-09-17 11:30 · terminal: term_40fe6a

## Goal
`server/config/logging.ts` takes the level from the `LOG_LEVEL` environment
variable (`debug`, `info`, `warn`, `error`), defaults to `info`, and throws
at startup on any other value. Starting with `LOG_LEVEL=debug` produces
debug lines; starting without it produces none.

## Context
The config loader this plugs into was built in
handoffs/merged/2026-09-14-config-loader.md. Follow `server/config/port.ts`: read
through `env()`, validate with the zod schema, export a frozen object.

## Scope
- May touch: `server/config/logging.ts`, `server/config/logging.test.ts`
- Must not touch: anything else

## Phases
1. Config and validation.
2. Tests for the default, each valid level, and an invalid value.

## Checks
- `npm test -- server/config/logging.test.ts` green.
- `LOG_LEVEL=debug npm run start:once | grep -c '"level":"debug"'` prints a number above 0.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
