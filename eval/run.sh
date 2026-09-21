#!/usr/bin/env bash
# Offline evaluation of jev.sh against the labelled fixtures in this directory.
#
#   eval/run.sh                     fixtures only
#   eval/run.sh <briefs-dir>...     also replay real briefs (unlabelled; compared
#                                   with the model Jarvis chose in each header).
#                                   Real briefs stay local — never commit them here.
#
# Needs TYPESAFE_API_KEY. Go gates (decided before seeing any results):
#   lint    ≥90% agreement on every element (borderline labels excluded)
#   triage  zero non-working terminals reported as a confident `working`,
#           and ≥60% of the lines read kept out of Jarvis's context
#   routing no gate — shadow only
set -u
dirs=("$@")
here=$(cd "$(dirname "$0")" && pwd)
jev="$here/../plugins/jarvis/skills/setup/templates/handoffs/bin/jev.sh"
labels="$here/labels.json"
[ -n "${TYPESAFE_API_KEY:-}" ] || { echo "set TYPESAFE_API_KEY first"; exit 2; }

out=$(mktemp -d "${TMPDIR:-/tmp}/jev-eval.XXXXXX")
export JEV_LOG_DIR="$out/fixtures"
cd "$here" || exit 2

echo "briefs…"
for f in briefs/*.md; do "$jev" brief "$f" >/dev/null; done
echo "terminals…"
set --
for f in terminals/*.txt; do
  set -- "$@" --file "$f"
  [ $# -ge 20 ] && { "$jev" triage "$@" >/dev/null; set --; }
done
[ $# -gt 0 ] && "$jev" triage "$@" >/dev/null

[ -s "$JEV_LOG_DIR/log.jsonl" ] || { echo "nothing logged — is the key valid?"; exit 1; }

jq -rs --slurpfile L "$labels" --argjson floor "${JEV_CONFIDENCE_FLOOR:-0.6}" '
  def pct(n; d): if d == 0 then "n/a" else "\(n * 100 / d | round)% (\(n)/\(d))" end;
  def tally(f): group_by(f) | map("\(.[0] | f) ×\(length)") | join(", ");
  $L[0] as $lab
  | (map(select(.kind == "brief")) | map(. + {name: (.brief | split("/")[-1])})
     | map(select($lab.briefs[.name])) | map(. + {want: $lab.briefs[.name]})) as $b
  | (map(select(.kind == "triage")) | map(select($lab.terminals[.terminal]))
     | map(. + {want: $lab.terminals[.terminal]})) as $t
  | "== Brief lint (gate: ≥90% per element) — \($b | length) of \($lab.briefs | length) briefs answered",
    (("files", "pattern", "done", "fence", "prior") as $e
     | ($b | map(select((.want.borderline // []) | index($e) | not))) as $clear
     | "  \($e): \(pct($clear | map(select((.lint[$e] >= 0.5) == .want.lint[$e])) | length; $clear | length))"
       + ($clear | map(select((.lint[$e] >= 0.5) != .want.lint[$e]) | "\(.name) \(.lint[$e] * 100 | round / 100)")
          | if length > 0 then "   wrong: " + join(" · ") else "" end)),
    "",
    "== Shadow routing (no gate)",
    "  tier exact: \(pct($b | map(select(.jev_tier == .want.tier)) | length; $b | length))",
    "  label → jev: \($b | map(select(.jev_tier != .want.tier)) | tally("\(.want.tier) → \(.jev_tier)"))",
    (("media_asset", "computer_use", "security", "touches_secrets") as $k
     | ({media_asset: "media"}[$k] // $k) as $lk
     | "  \($k): \(pct($b | map(select((.route[$k] >= 0.5) == (.want[$lk] // false))) | length; $b | length))"),
    "  mean \($b | map(.seconds) | add / ([length, 1] | max) * 1000 | round) ms · \($b | map(.input_tokens) | add / ([length, 1] | max) | round) input tokens per brief",
    "",
    "== Terminal triage — \($t | length) of \($lab.terminals | length) terminals answered",
    "  state exact: \(pct($t | map(select(.state == .want.state)) | length; $t | length))",
    "  hard cases exact: \(pct($t | map(select(.want.hard and .state == .want.state)) | length; $t | map(select(.want.hard)) | length))",
    "  label → got: \($t | map(select(.state != .want.state)) | tally("\(.want.state) → \(.state)"))",
    ($t | map(select(.want.state != "working" and .state == "working" and .confidence >= $floor)) as $missed
     | "  GATE missed non-working (hidden from Jarvis): \($missed | length)"
       + (if ($missed | length) > 0 then "   " + ($missed | map("\(.terminal) \(.confidence * 100 | round / 100)") | join(" · ")) else "" end)),
    "  GATE lines kept out of context: \(pct(($t | map(.lines_read) | add) - ($t | map(.lines_shown) | add); $t | map(.lines_read) | add))  (need ≥60%)"
' "$JEV_LOG_DIR/log.jsonl"

for d in ${dirs[@]+"${dirs[@]}"}; do
  [ -d "$d" ] || continue
  export JEV_LOG_DIR="$out/real"
  for f in "$d"/*.md; do
    case "$f" in */TEMPLATE.md) continue ;; esac
    "$jev" brief "$f" >/dev/null
  done
done
[ -s "$out/real/log.jsonl" ] && { echo; echo "== Real briefs (Jev vs the model Jarvis chose)"; JEV_LOG_DIR="$out/real" "$jev" report; }
echo; echo "raw logs: $out"
