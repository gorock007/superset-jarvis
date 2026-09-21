#!/usr/bin/env bash
# Offline self-test of jev.sh: fail-open paths, request shape, secret masking.
# No API key, no network, no cost — run it after any change to jev.sh.
#
#   eval/selftest.sh
set -u
here=$(cd "$(dirname "$0")" && pwd)
jev="$here/../plugins/jarvis/skills/setup/templates/handoffs/bin/jev.sh"
brief="$here/briefs/$(ls "$here/briefs" | head -n 1)"
term="$here/terminals/$(ls "$here/terminals" | head -n 1)"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/jev-selftest.XXXXXX")
export JEV_LOG_DIR="$tmp/log"
fails=0
ok() { echo "  ok    $1"; }
bad() { echo "  FAIL  $1"; fails=$((fails + 1)); }
check() { if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi; }

echo "fail-open"
out=$(env -u TYPESAFE_API_KEY "$jev" brief "$brief" 2>&1); rc=$?
[ $rc = 0 ] && printf '%s' "$out" | grep -q '^jev: skipped'; check "brief without a key skips, exit 0" $?
out=$(env -u TYPESAFE_API_KEY "$jev" triage --file "$term" 2>&1); rc=$?
[ $rc = 0 ] && [ -n "$out" ]; check "triage without a key falls back to the raw tail, exit 0" $?
start=$(date +%s)
out=$(TYPESAFE_API_KEY=selftest TYPESAFE_API_URL=http://127.0.0.1:9/ "$jev" brief "$brief" 2>&1); rc=$?
[ $rc = 0 ] && printf '%s' "$out" | grep -q '^jev: skipped'; check "brief with the API unreachable skips, exit 0" $?
[ $(( $(date +%s) - start )) -le 20 ]; check "…and gives up within 20s" $?
out=$(env -u TYPESAFE_API_KEY "$jev" outcome "$brief" clean 2>&1); check "outcome needs no key" $?
[ ! -e "$JEV_LOG_DIR/log.jsonl" ] || ! grep -q '"kind":"brief"' "$JEV_LOG_DIR/log.jsonl"; check "skipped calls log no verdict" $?

if command -v jq >/dev/null 2>&1; then
  echo "request shape (--dry-run)"
  p=$(env -u TYPESAFE_API_KEY "$jev" --dry-run brief "$brief" 2>/dev/null)
  printf '%s' "$p" | jq -e '(.questions | length) == 13 and (.state | type) == "string" and .model != null' >/dev/null; check "brief: 13 questions, string state, a model" $?
  printf '%s' "$p" | jq -e '.state | test("(^|\n)(worker|model|effort):") | not' >/dev/null; check "brief: Jarvis's model choice is stripped from the state" $?
  printf '%s' "$p" | jq -e '[.questions[] | .type] | unique - ["noul","score","choice"] == []' >/dev/null; check "brief: only noul/score/choice questions" $?
  p=$(env -u TYPESAFE_API_KEY "$jev" --dry-run triage --file "$term" 2>/dev/null)
  printf '%s' "$p" | jq -es '.[0].questions | has("state") and has("repeating")' >/dev/null; check "triage: state + repeating questions" $?
else
  echo "request shape: skipped (jq not installed)"
fi

echo "masking"
# Token shapes are split with "" and joined at run time, so no token-shaped
# literal sits in the repo.
eval "$(awk '/^clean\(\) \{/{p=1} p{print} p&&/^}/{exit}' "$jev")"
export SELFTEST_DEPLOY_TOKEN="literal-env-value-xyz123"
masked=$(sed 's/""//g' <<EOT | clean
DATABASE_URL=postgres://app:hunter2secret@db.internal:5432/notes
password: "correct horse battery"
  "api_key": "abcd1234efgh",
clientSecret=qqqq1111wwww
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1234
-----END RSA PRIVATE KEY-----
gh""p_FAKE1234567890abcdefgh github""_pat_11ABCDEFG0123456789abcdefgh
AI""zaSyA1234567890abcdefghijklmnopqrstuv s""k_live_FAKE1234567890abcdef
h""f_FAKEabcdefghijklmnopqrstuv s""k-ant-FAKE-abcdefghijklmnop
Authorization: Bearer abcdefghijklmnop123456
Set-Cookie: sid=s3ss10nvalue123; Path=/
echo literal-env-value-xyz123
Keybindings: src/keys.ts and tokenizer: fast-bpe-v2
Tests: 12 passed, 0 failed
EOT
)
for leak in hunter2secret "correct horse" abcd1234efgh qqqq1111wwww MIIEow FAKE AIzaSy abcdefghijklmnop123456 s3ss10nvalue123 literal-env-value; do
  printf '%s' "$masked" | grep -q -- "$leak"; [ $? != 0 ]; check "masks $leak" $?
done
for keep in "src/keys.ts" "fast-bpe-v2" "12 passed" "db.internal:5432/notes"; do
  printf '%s' "$masked" | grep -q -- "$keep"; check "keeps $keep" $?
done

rm -rf "$tmp"
echo; [ "$fails" = 0 ] && echo "selftest: all passed" || { echo "selftest: $fails failed"; exit 1; }
