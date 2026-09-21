# Move every hard-coded UI string in the app into i18n keys
worker: claude
model: opus
effort: high
started: 2026-09-07 09:05 · terminal: term_8c72b1

## Goal
All 140 components under `src/screens/` and `src/components/` render their
text through `t()`; no user-visible literal is left in JSX. Keys live in
`src/i18n/en.json`, named `<screen>.<element>` in camelCase. Plurals use the
`_one` / `_other` suffixes. Interpolation uses `{{name}}`. English output is
pixel-identical to today's. This is large, but every rule is fixed.

## Context
The Login screen was done as the pilot; the conventions were agreed in
handoffs/merged/2026-09-03-i18n-login-pilot.md. Follow
`src/screens/Login/LoginScreen.tsx` exactly: `useTranslation()` at the top,
no string concatenation, `accessibilityLabel` values translated too.

## Scope
- May touch: `src/screens/`, `src/components/`, `src/i18n/en.json`
- Must not touch: `src/i18n/de.json` (translators own it), `ios/`, `android/`
- Shared files (edit minimally, name in handoff): `src/i18n/index.ts`

## Phases
1. `src/components/` (52 files).
2. `src/screens/` A–M (47 files).
3. `src/screens/` N–Z (41 files).
4. Sort `en.json`, remove unused keys.

## Checks
- `npm run i18n:lint` reports `0 hard-coded strings`.
- `npm test` green (snapshot tests must not change).
- `npx tsc --noEmit` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
