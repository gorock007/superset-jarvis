# Build the transactions CSV export from the PM spec
worker: claude
model: fable
effort: high
started: 2026-09-11 16:20 · terminal: term_0b6f7c

## Goal
Add a transactions export at `app/api/export/route.ts`. The PM spec, quoted
in full:

> 1. The export must stream, so accounts with 2M+ rows do not time out.
> 2. The first row after the header is a totals row summing every amount in the file.
> 3. The file must open in Excel with no warnings and with umlauts intact.
> 4. Encoding: UTF-8 without BOM.
> 5. Rows are sorted by amount, largest first.

Points 1 and 2 conflict, 1 and 5 conflict, and 3 and 4 conflict. The PM is
away until October. Work out what the export should actually do and build
that.

## Context
Next.js 15 on Vercel, Postgres through Drizzle. Function timeout is 60 s.
The largest account today has 2.4M transactions. Finance opens these files
in Excel on Windows; the data team reads them with pandas.

## Phases
1. Write down each contradiction and the options for resolving it.
2. Decide. Record the decisions where the PM will see them.
3. Implement.

## Checks
Use your judgement. Say in the handoff which spec points you dropped or
bent, and why.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
