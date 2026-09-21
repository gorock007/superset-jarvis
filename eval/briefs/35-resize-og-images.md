# Resize the Open Graph images to 1200 × 630
worker: codex
model: gpt-6-astra
effort: high
started: 2026-09-16 12:10 · terminal: term_b28f34

## Goal
`public/og/home.png`, `public/og/pricing.png` and `public/og/blog.png` are
each exactly 1200 × 630 pixels, centre-cropped from the originals in
`public/og/source/`, and under 300 KB.

## Context
No prior context; this is a one-off. Use the same recipe as
`scripts/resize-avatars.sh`: ImageMagick `-resize` with `^`, then
`-gravity center -extent`, then `pngquant`.

## Scope
- May touch: `public/og/home.png`, `public/og/pricing.png`, `public/og/blog.png`
- Must not touch: `public/og/source/`, `app/`
- Shared files (edit minimally, name in handoff): none

## Phases
1. Resize and compress the three files.

## Checks
- `identify -format "%f %wx%h\n" public/og/*.png` prints `1200x630` on every line.
- `find public/og -maxdepth 1 -name "*.png" -size +300k | wc -l` prints `0`.

## Questions first
Put every question in one first handoff (`status: blocked`) and stop. After
the answers arrive on your terminal, build every phase through to done
without stopping again. If you have no questions, build straight through.
