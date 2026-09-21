# Harden the session cookie and rotate the session id on login
worker: codex
model: gpt-5.6-sol
effort: high
started: 2026-09-16 09:45 · terminal: term_2e40b6

## Goal
In `server/auth/session.ts`: the session cookie is set with `HttpOnly`,
`Secure` and `SameSite=Lax`; the session id is regenerated on every
successful login and on privilege change; sessions expire absolutely after
12 hours and after 30 minutes idle; logout deletes the server-side session
row, not just the cookie.

## Context
Follow `server/auth/csrf.ts` for how options come from config and how the
tests are laid out (`server/auth/csrf.test.ts`): supertest against the app
factory, one describe block per behaviour.

## Scope
- May touch: `server/auth/session.ts`, `server/auth/session.test.ts`, `server/config/auth.ts`
- Must not touch: `server/auth/oauth/`, `server/db/schema.ts`
- Shared files (edit minimally, name in handoff): `server/app.ts`

## Phases
1. Cookie flags and expiry.
2. Id rotation on login and privilege change.
3. Server-side logout.
4. Tests for each.

## Checks
- `npm test -- server/auth/session.test.ts` green.
- `curl -si -X POST localhost:3000/login -d 'email=dev@example.test&password=dev' | grep -i '^set-cookie'` shows `HttpOnly; Secure; SameSite=Lax`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
