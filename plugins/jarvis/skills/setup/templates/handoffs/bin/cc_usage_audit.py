#!/usr/bin/env python3
"""cc-usage-audit: see where your Claude Code usage actually goes.

Reads the session transcripts Claude Code keeps on this machine
(~/.claude/projects/**/*.jsonl), prices every request at API rates, and
reports what drove the spend: models, long context, cache reloads after idle
gaps, subagents, headless/hook sessions, what each turn was doing, and your
peak 5-hour burn.

Local only: no network calls, nothing leaves your machine. Python 3.8+, no
dependencies.

Vendored into Jarvis from https://github.com/gorock007/cc-usage-audit (MIT), with
one addition: the by_role_model aggregate that `jarvis usage` reads.
"""
import argparse, collections, datetime as dt, glob, json, os, re, statistics, sys

# USD per million tokens: input, output, cache read, cache write 5m, cache write 1h.
# Check https://docs.claude.com/en/docs/about-claude/pricing and override with
# --prices FILE (same shape, JSON) if anything here is out of date.
PRICES = {
    "claude-fable-5-1":  (10.0, 50.0, 0.25, 12.50, 20.0),
    "claude-fable-5":    (10.0, 50.0, 1.00, 12.50, 20.0),
    "claude-mythos-5":   (10.0, 50.0, 1.00, 12.50, 20.0),
    "claude-opus-5-5":   (4.0,  20.0, 0.20,  5.00,  8.0),
    "claude-opus-5":     (5.0,  25.0, 0.50,  6.25, 10.0),
    "claude-opus-4-8":   (5.0,  25.0, 0.50,  6.25, 10.0),
    "claude-opus-4-7":   (5.0,  25.0, 0.50,  6.25, 10.0),
    "claude-opus-4-6":   (5.0,  25.0, 0.50,  6.25, 10.0),
    "claude-opus-4-5":   (5.0,  25.0, 0.50,  6.25, 10.0),
    "claude-sonnet-5":   (2.0,  10.0, 0.20,  2.50,  4.0),
    "claude-sonnet-4-6": (3.0,  15.0, 0.30,  3.75,  6.0),
    "claude-sonnet-4-5": (3.0,  15.0, 0.30,  3.75,  6.0),
    "claude-haiku-4-5":  (1.0,   5.0, 0.10,  1.25,  2.0),
}
LONG_CTX = 150_000      # the threshold /usage calls out
RELOAD_TOKENS = 40_000  # a cache write this big mid-session means the context was rewritten
CACHE_TTL_MIN = 60      # subscription prompt cache TTL (5 min on API keys / usage credits)
WINDOW_H = 5

BASH_CATEGORIES = [
    ("wait/sleep loop", r"\bsleep\b|\buntil\b|while .*;\s*do|fswatch|inotifywait"),
    ("git inspect",     r"\bgit\s+(status|diff|log|show|branch)\b"),
    ("git write",       r"\bgit\s+(add|commit|push|mv|rm|merge|rebase|checkout|switch)\b"),
    ("tests/build",     r"pytest|\bnpm (test|run)|pnpm|yarn|cargo (test|build)|go test|swift (build|test)|xcodebuild|\bmake\b|tsc\b"),
    ("read/search",     r"^\s*(cat|head|tail|sed -n|less|ls|find|grep|rg|wc)\b"),
]

def model_price(model, prices):
    m = re.sub(r"-\d{8}$", "", model or "")
    for key in sorted(prices, key=len, reverse=True):
        if m.startswith(key):
            return key, prices[key]
    return m, None

def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def first_prompt(rec):
    c = rec.get("message", {}).get("content")
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    if not isinstance(c, str) or not c.strip():
        return None
    if c.startswith("<local-command") or c.startswith("<command-name>") or c.startswith("Caveat:"):
        return None
    return c

def load_file(path, since, prices):
    """Return (meta, requests) for one transcript. Requests are deduped by requestId (last record wins:
    streamed messages repeat the same usage block per content chunk)."""
    reqs, meta = {}, {"path": path, "entrypoint": None, "prompt": "", "tool_text": []}
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return meta, []
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            meta["entrypoint"] = meta["entrypoint"] or d.get("entrypoint")
            t = d.get("type")
            if t == "user" and not meta["prompt"] and not d.get("isMeta"):
                meta["prompt"] = first_prompt(d) or ""
            if t != "assistant":
                continue
            m = d.get("message") or {}
            u = m.get("usage")
            if not u or m.get("model") in (None, "<synthetic>") or not d.get("timestamp"):
                continue
            rid = d.get("requestId") or m.get("id")
            tools = []
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    inp = c.get("input") or {}
                    tools.append((c.get("name"), inp.get("command", "") if c.get("name") == "Bash" else ""))
                    meta["tool_text"].append(json.dumps(inp)[:2000])
            prev = reqs.get(rid)
            if prev:
                tools = prev["tools"] + tools
            reqs[rid] = {"t": ts(d["timestamp"]), "model": m.get("model"), "u": u, "tools": tools,
                         "sidechain": bool(d.get("isSidechain"))}
    out = []
    for r in sorted(reqs.values(), key=lambda r: r["t"]):
        u = r["u"]
        cc = u.get("cache_creation") or {}
        w5, w1 = cc.get("ephemeral_5m_input_tokens", 0), cc.get("ephemeral_1h_input_tokens", 0)
        if not cc:
            w1 = u.get("cache_creation_input_tokens", 0) or 0
        inp, outp, cr = u.get("input_tokens", 0) or 0, u.get("output_tokens", 0) or 0, u.get("cache_read_input_tokens", 0) or 0
        key, p = model_price(r["model"], prices)
        cost = {"in": 0, "out": 0, "read": 0, "write": 0}
        if p:
            cost = {"in": inp * p[0] / 1e6, "out": outp * p[1] / 1e6, "read": cr * p[2] / 1e6,
                    "write": (w5 * p[3] + w1 * p[4]) / 1e6}
        r.update(model_key=key, priced=bool(p), ctx=inp + cr + w5 + w1, write_tokens=w5 + w1,
                 cost=cost, usd=sum(cost.values()))
        out.append(r)
    # mark reloads before filtering by date so the gap before the first in-range request is known
    prev = None
    for i, r in enumerate(out):
        gap = (r["t"] - prev).total_seconds() / 60 if prev else None
        r["gap_min"] = gap
        if i == 0:
            r["reload"] = None
        elif r["write_tokens"] >= RELOAD_TOKENS:
            r["reload"] = "after idle" if gap is not None and gap > CACHE_TTL_MIN else "other"
        else:
            r["reload"] = None
        prev = r["t"]
    out = [r for r in out if r["t"] >= since]
    return meta, out

def bash_category(cmd, extra):
    for name, rx in extra + BASH_CATEGORIES:
        if re.search(rx, cmd, re.M):
            return name
    return "bash: other"

def turn_category(r, extra):
    if not r["tools"]:
        return "reply / end of turn"
    name, cmd = r["tools"][0]
    if name == "Bash":
        return bash_category(cmd, extra)
    if name in ("Agent", "Task"):
        return "launch subagent"
    if name and name.startswith("mcp__"):
        return "mcp: " + name.split("__")[1]
    return name or "?"

def parse_kv(items, what):
    out = []
    for s in items or []:
        if "=" not in s:
            sys.exit(f"{what} expects NAME=REGEX, got {s!r}")
        k, v = s.split("=", 1)
        out.append((k, v))
    return out

def fmt_usd(x):
    return f"${x:,.2f}"

def pct(a, b):
    return f"{(a / b * 100 if b else 0):.0f}%"

def table(rows, headers, right=()):
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h)) for i, h in enumerate(headers)]
    def line(vals):
        return "  ".join(str(v).rjust(widths[i]) if i in right else str(v).ljust(widths[i]) for i, v in enumerate(vals))
    print("  " + line(headers))
    print("  " + "  ".join("-" * w for w in widths))
    for r in rows:
        print("  " + line(r))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"), help="transcript root (default ~/.claude/projects)")
    ap.add_argument("--days", type=float, default=7, help="look back this many days (default 7)")
    ap.add_argument("--since", help="ISO date/time to start from; overrides --days")
    ap.add_argument("--until", help="ISO date/time to stop at")
    ap.add_argument("--project", action="append", help="only projects whose folder name contains this (repeatable)")
    ap.add_argument("--role", action="append", metavar="NAME=REGEX",
                    help="label sessions whose first prompt matches REGEX (repeatable, first match wins)")
    ap.add_argument("--role-tool", action="append", metavar="NAME=REGEX",
                    help="label sessions where any tool call input matches REGEX, e.g. orchestrator='agents create'")
    ap.add_argument("--bash-category", action="append", metavar="NAME=REGEX",
                    help="extra category for Bash turns, checked before the built-in ones")
    ap.add_argument("--prices", help="JSON file of {model_prefix: [in, out, cache_read, write_5m, write_1h]} to merge in")
    ap.add_argument("--redact", action="store_true", help="hide project names and prompt text (for screenshots)")
    ap.add_argument("--top", type=int, default=10, help="rows in top-N tables (default 10)")
    ap.add_argument("--json", action="store_true", help="print the aggregates as JSON instead of text")
    a = ap.parse_args()

    prices = dict(PRICES)
    if a.prices:
        prices.update({k: tuple(v) for k, v in json.load(open(a.prices)).items()})
    now = dt.datetime.now(dt.timezone.utc)
    since = ts(a.since) if a.since else now - dt.timedelta(days=a.days)
    if since.tzinfo is None:
        since = since.replace(tzinfo=dt.timezone.utc)
    until = ts(a.until) if a.until else now
    if until.tzinfo is None:
        until = until.replace(tzinfo=dt.timezone.utc)
    roles = parse_kv(a.role, "--role")
    role_tools = parse_kv(a.role_tool, "--role-tool")
    bash_extra = parse_kv(a.bash_category, "--bash-category")

    if not os.path.isdir(a.root):
        sys.exit(f"No transcripts at {a.root}")

    sessions, reqs = [], []
    cutoff = since.timestamp() - 3600
    proj_alias = {}
    for proj in sorted(os.listdir(a.root)):
        pdir = os.path.join(a.root, proj)
        if not os.path.isdir(pdir) or (a.project and not any(p.lower() in proj.lower() for p in a.project)):
            continue
        pname = proj_alias.setdefault(proj, f"project-{len(proj_alias) + 1}") if a.redact else re.sub(r"^-Users-[^-]+-?", "", proj) or proj
        for f in glob.glob(os.path.join(pdir, "*.jsonl")):
            if os.path.getmtime(f) < cutoff:
                continue
            sid = os.path.basename(f)[:-6]
            meta, rs = load_file(f, since, prices)
            rs = [r for r in rs if r["t"] <= until]
            subs = []
            for sf in glob.glob(os.path.join(pdir, sid, "subagents", "*.jsonl")):
                agent_type = "?"
                try:
                    agent_type = json.load(open(sf[:-6] + ".meta.json")).get("agentType", "?")
                except (OSError, ValueError):
                    pass
                _, srs = load_file(sf, since, prices)
                for r in srs:
                    if r["t"] <= until:
                        r["agent_type"] = agent_type
                        subs.append(r)
            if not rs and not subs:
                continue
            ep = meta["entrypoint"] or "?"
            headless = ep.startswith("sdk")
            role = None
            for name, rx in roles:
                if re.search(rx, meta["prompt"]):
                    role = name
                    break
            if role is None:
                for name, rx in role_tools:
                    if any(re.search(rx, t) for t in meta["tool_text"]):
                        role = name
                        break
            if role is None:
                role = "headless (sdk / -p / hooks)" if headless else "interactive"
            s = {"id": sid, "project": pname, "entrypoint": ep, "role": role,
                 "prompt": "" if a.redact else re.sub(r"\s+", " ", meta["prompt"])[:80],
                 "raw_prompt": re.sub(r"\s+", " ", meta["prompt"])}
            for r in rs:
                r["session"] = s
                r["kind"] = "subagent" if r["sidechain"] else "main"
                r["agent_type"] = "(inline)" if r["sidechain"] else None
            for r in subs:
                r["session"] = s
                r["kind"] = "subagent"
            s["reqs"] = rs + subs
            sessions.append(s)
            reqs.extend(s["reqs"])

    if not reqs:
        sys.exit("No requests in that period.")
    reqs.sort(key=lambda r: r["t"])
    total = sum(r["usd"] for r in reqs)
    unpriced = collections.Counter(r["model"] for r in reqs if not r["priced"])
    R = {}

    # 1. by model and cost component
    bymodel = collections.defaultdict(lambda: collections.Counter())
    comp = collections.Counter()
    for r in reqs:
        b = bymodel[r["model_key"]]
        b["usd"] += r["usd"]; b["turns"] += 1
        for k, v in r["cost"].items():
            comp[k] += v
    long_usd = sum(r["usd"] for r in reqs if r["ctx"] > LONG_CTX)
    R["total_usd"] = total
    R["by_model"] = {k: dict(v) for k, v in bymodel.items()}
    R["components"] = dict(comp)
    R["long_context_share"] = long_usd / total if total else 0

    # 2. by role / kind
    byrole = collections.defaultdict(lambda: collections.Counter())
    for r in reqs:
        key = r["session"]["role"] + (" > subagents" if r["kind"] == "subagent" else "")
        b = byrole[key]
        b["usd"] += r["usd"]; b["turns"] += 1; b["ctx"] += r["ctx"]
        b["sessions_" + r["session"]["id"]] = 1
        for k, v in r["cost"].items():
            b[k] += v
    brm = collections.defaultdict(lambda: collections.Counter())
    for r in reqs:
        if r["kind"] == "main":
            b = brm[(r["session"]["role"], r["model_key"])]
            b["usd"] += r["usd"]; b["turns"] += 1; b["ctx"] += r["ctx"]
    R["by_role_model"] = [{"role": k[0], "model": k[1], **v} for k, v in brm.items()]
    R["by_role"] = {k: {"usd": v["usd"], "turns": v["turns"], "sessions": sum(1 for x in v if x.startswith("sessions_")),
                        "avg_ctx": v["ctx"] / v["turns"], "write_share": v["write"] / v["usd"] if v["usd"] else 0,
                        "read_share": v["read"] / v["usd"] if v["usd"] else 0,
                        "out_share": v["out"] / v["usd"] if v["usd"] else 0} for k, v in byrole.items()}

    # 3. cache reloads
    rel = collections.defaultdict(lambda: [0, 0.0])
    for r in reqs:
        if r["reload"]:
            key = (r["session"]["role"] + (" > subagents" if r["kind"] == "subagent" else ""), r["reload"])
            rel[key][0] += 1
            rel[key][1] += r["usd"]
    R["reloads"] = [{"role": k[0], "cause": k[1], "turns": v[0], "usd": v[1]} for k, v in rel.items()]

    # 4. subagents
    sa = collections.defaultdict(lambda: collections.Counter())
    for r in reqs:
        if r["kind"] == "subagent":
            b = sa[(r["agent_type"], r["model_key"])]
            b["usd"] += r["usd"]; b["turns"] += 1
    R["subagents"] = [{"agent": k[0], "model": k[1], **v} for k, v in sa.items()]

    # 5. headless sessions grouped by prompt start (finds hooks and scripts calling claude)
    hl = collections.defaultdict(lambda: collections.Counter())
    for s in sessions:
        if s["entrypoint"].startswith("sdk"):
            key = (s["entrypoint"], s["raw_prompt"][:48])
            hl[key]["runs"] += 1
            hl[key]["usd"] += sum(r["usd"] for r in s["reqs"])
            hl[key]["turns"] += len(s["reqs"])
    R["headless"] = [{"entrypoint": k[0], "prompt_start": f"(prompt {i + 1})" if a.redact else k[1], **v}
                     for i, (k, v) in enumerate(sorted(hl.items(), key=lambda kv: -kv[1]["usd"]))]

    # 6. what turns were doing (main-session turns only)
    tc = collections.defaultdict(lambda: collections.Counter())
    for r in reqs:
        if r["kind"] == "main":
            b = tc[(r["session"]["role"], turn_category(r, bash_extra))]
            b["usd"] += r["usd"]; b["turns"] += 1
    R["turns"] = [{"role": k[0], "doing": k[1], **v} for k, v in tc.items()]

    # 7. burn rate: worst rolling 5-hour window, concurrency
    best, j, run, best_span = 0.0, 0, 0.0, None
    for i, r in enumerate(reqs):
        run += r["usd"]
        while reqs[j]["t"] < r["t"] - dt.timedelta(hours=WINDOW_H):
            run -= reqs[j]["usd"]; j += 1
        if run > best:
            best, best_span = run, (reqs[j]["t"], r["t"])
    buckets = collections.defaultdict(set)
    for r in reqs:
        buckets[r["t"].replace(minute=r["t"].minute // 10 * 10, second=0, microsecond=0)].add(r["session"]["id"] + (r.get("agent_type") or ""))
    peak_conc = max(len(v) for v in buckets.values())
    R["peak_window_usd"] = best
    R["peak_window"] = [best_span[0].isoformat(), best_span[1].isoformat()] if best_span else None
    R["peak_concurrent_sessions_10min"] = peak_conc

    # 8. startup weight
    starts = [s["reqs"][0]["ctx"] for s in sessions if s["reqs"] and s["reqs"][0]["kind"] == "main" and s["entrypoint"] == "cli"]
    R["median_startup_ctx"] = statistics.median(starts) if starts else None

    # 9. top sessions
    top = sorted(sessions, key=lambda s: -sum(r["usd"] for r in s["reqs"]))[: a.top]
    R["top_sessions"] = [{"project": s["project"], "session": s["id"][:8], "role": s["role"],
                          "usd": sum(r["usd"] for r in s["reqs"]), "turns": len(s["reqs"]),
                          "max_ctx": max(r["ctx"] for r in s["reqs"]), "prompt": s["prompt"]} for s in top]
    R["unpriced_models"] = dict(unpriced)
    R["period"] = [since.isoformat(), until.isoformat()]

    if a.json:
        print(json.dumps(R, indent=2, default=str))
        return
    report(R, reqs, sessions, a)

def report(R, reqs, sessions, a):
    total = R["total_usd"]
    loc = lambda s: ts(s).astimezone().strftime("%a %d %b %H:%M")
    print(f"\ncc-usage-audit  ·  {loc(R['period'][0])} → {loc(R['period'][1])}")
    print(f"{len(sessions)} sessions, {len(reqs):,} requests, {fmt_usd(total)} at API prices "
          f"(a proxy for plan usage, not a bill)\n")

    print("WHERE IT GOES")
    c = R["components"]
    print(f"  output (incl. thinking) {pct(c.get('out', 0), total):>4}   cache writes {pct(c.get('write', 0), total):>4}   "
          f"cache reads {pct(c.get('read', 0), total):>4}   uncached input {pct(c.get('in', 0), total):>4}")
    print(f"  spent at >{LONG_CTX // 1000}k context: {R['long_context_share']:.0%}\n")
    rows = sorted(R["by_model"].items(), key=lambda kv: -kv[1]["usd"])
    table([(k, fmt_usd(v["usd"]), pct(v["usd"], total), f"{v['turns']:,}", f"${v['usd'] / v['turns']:.3f}") for k, v in rows],
          ("model", "cost", "share", "turns", "$/turn"), right=(1, 2, 3, 4))

    print("\nBY SESSION TYPE")
    rows = sorted(R["by_role"].items(), key=lambda kv: -kv[1]["usd"])
    table([(k, v["sessions"], fmt_usd(v["usd"]), pct(v["usd"], total), f"${v['usd'] / v['turns']:.3f}",
            f"{v['avg_ctx'] / 1000:.0f}k", f"{v['write_share']:.0%}", f"{v['read_share']:.0%}", f"{v['out_share']:.0%}")
           for k, v in rows],
          ("type", "sessions", "cost", "share", "$/turn", "avg ctx", "writes", "reads", "output"), right=tuple(range(1, 9)))

    print("\nCACHE RELOADS  (a mid-session cache write of 40k+ tokens: the whole context written again)")
    if R["reloads"]:
        rows = sorted(R["reloads"], key=lambda x: -x["usd"])
        table([(x["role"], x["cause"], x["turns"], fmt_usd(x["usd"]), pct(x["usd"], total)) for x in rows],
              ("type", "cause", "turns", "cost", "of total"), right=(2, 3, 4))
        print(f"  'after idle' = more than {CACHE_TTL_MIN} min since the previous turn, so the cache had expired.")
        print("  'other' = compaction, a /model switch, or anything else that changed the cached prefix.")
    else:
        print("  none")

    print("\nSUBAGENTS")
    if R["subagents"]:
        rows = sorted(R["subagents"], key=lambda x: -x["usd"])[: a.top]
        table([(x["agent"], x["model"], x["turns"], fmt_usd(x["usd"]), pct(x["usd"], total)) for x in rows],
              ("agent", "model", "turns", "cost", "share"), right=(2, 3, 4))
    else:
        print("  none")

    print("\nHEADLESS SESSIONS  (Agent SDK, claude -p, plugin hooks; grouped by how the prompt starts)")
    if R["headless"]:
        rows = sorted(R["headless"], key=lambda x: -x["usd"])[: a.top]
        table([(x["entrypoint"], x["prompt_start"], x["runs"], fmt_usd(x["usd"]), pct(x["usd"], total)) for x in rows],
              ("entry", "prompt starts with", "runs", "cost", "share"), right=(2, 3, 4))
    else:
        print("  none")

    print("\nWHAT MAIN-SESSION TURNS WERE DOING  (cost of the turn that made the call)")
    roles = sorted({x["role"] for x in R["turns"]}, key=lambda k: -sum(y["usd"] for y in R["turns"] if y["role"] == k))
    for role in roles[:4]:
        rows = sorted([x for x in R["turns"] if x["role"] == role], key=lambda x: -x["usd"])
        sub = sum(x["usd"] for x in rows)
        print(f"  [{role}]  {fmt_usd(sub)}")
        table([(x["doing"], x["turns"], fmt_usd(x["usd"]), pct(x["usd"], sub), f"${x['usd'] / x['turns']:.3f}") for x in rows[:8]],
              ("doing", "turns", "cost", "share", "$/turn"), right=(1, 2, 3, 4))

    print("\nBURN RATE")
    if R["peak_window"]:
        print(f"  worst {WINDOW_H}-hour window: {fmt_usd(R['peak_window_usd'])} ({loc(R['peak_window'][0])} → {loc(R['peak_window'][1])})")
    print(f"  most sessions active in one 10-minute slot: {R['peak_concurrent_sessions_10min']}")
    if R["median_startup_ctx"]:
        print(f"  median context before the first reply (system prompt, tools, skills, CLAUDE.md): {R['median_startup_ctx'] / 1000:.0f}k tokens")

    print("\nTOP SESSIONS")
    table([(x["project"][:28], x["session"], x["role"][:20], fmt_usd(x["usd"]), x["turns"], f"{x['max_ctx'] / 1000:.0f}k", x["prompt"][:40])
           for x in R["top_sessions"]],
          ("project", "session", "type", "cost", "turns", "max ctx", "first prompt"), right=(3, 4, 5))

    if R["unpriced_models"]:
        print(f"\nNot priced (add them with --prices): {dict(R['unpriced_models'])}")
    print()

if __name__ == "__main__":
    main()
