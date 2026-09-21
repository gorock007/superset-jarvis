# Ingest worker keeps running out of memory
worker: claude
model: fable
effort: xhigh
started: 2026-09-17 07:55 · terminal: term_5f00c2

## Goal
The nightly ingest worker gets OOM-killed about four hours into its run.
Nobody knows why. Find out and fix it.

## Context
It started some time in the last month; there was no single deploy anyone
can point at. Python 3.12 on Kubernetes, 8 GiB limit, pandas and pyarrow,
reads Parquet from object storage and writes to the warehouse. Memory climbs
steadily rather than in steps. Restarting it halfway through the night
"fixes" it, which is what ops currently does.

## Phases
1. Find it.
2. Fix it.

## Checks
Tell me how you convinced yourself it is fixed.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
