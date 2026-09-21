# Migrate all 38 remaining pages from pages/ to the App Router
worker: claude
model: opus
effort: high
started: 2026-09-08 09:00 · terminal: term_f3319e

## Goal
Every route listed in `docs/migration/pages-checklist.md` (38 of them) is
served from `app/` and renders the same content it does today. `pages/` is
deleted apart from `pages/api/`. `getServerSideProps` becomes an async
server component, `getStaticProps` becomes a server component with
`revalidate`, `next/head` becomes `generateMetadata`. The checklist states
the target path and data-fetching mode for every page; there is nothing
left to decide.

## Context
The pricing page was migrated first as the reference; see
handoffs/merged/2026-09-05-pricing-app-router.md. Follow
`app/(marketing)/pricing/page.tsx` for file layout, metadata, and where
client components get split out.

## Scope
- May touch: `app/`, `pages/` (deleting migrated files), `docs/migration/pages-checklist.md`
- Must not touch: `pages/api/`, `lib/db/`, `middleware.ts`
- Shared files (edit minimally, name in handoff): `next.config.js`

## Phases
1. Marketing pages (9).
2. Dashboard pages (21).
3. Settings and account pages (8).
4. Delete `pages/` leftovers and tick off the checklist.

## Checks
- `npm run build` succeeds with no `pages/` routes listed except `/api/*`.
- `npx playwright test e2e/routes.spec.ts` green (it visits all 38 routes).
- `npx tsc --noEmit` clean.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
