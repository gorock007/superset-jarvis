# Write the table-driven test suite for the lexer
worker: codex
model: gpt-5.6-sol (red band; opus-tier task)
effort: high
started: 2026-09-14 15:25 · terminal: term_2a88d5

## Goal
`crates/parser/src/lexer.rs` has line coverage above 90%, from a new test
file `crates/parser/tests/lexer_cases.rs` holding at least 60 cases: every
token kind, string escapes, nested comments, numeric literal edge cases,
and each `LexError` variant.

## Context
Follow `crates/parser/tests/ast_cases.rs`: a `CASES` table of
`(name, input)` pairs, one loop, insta snapshots under
`crates/parser/tests/snapshots/`. Do not change lexer behaviour. If a case
exposes a bug, mark the case `#[ignore]` and name it in the handoff.

## Scope
- May touch: `crates/parser/tests/lexer_cases.rs`, `crates/parser/tests/snapshots/`
- Must not touch: `crates/parser/src/`, `crates/cli/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Token kinds and literals.
2. Comments and whitespace.
3. Error variants.

## Checks
- `cargo test -p parser` green.
- `cargo llvm-cov -p parser --fail-under-lines 90` exits 0.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
