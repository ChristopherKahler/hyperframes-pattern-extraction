#!/usr/bin/env python3
"""hfcat-nudge - every time a session touches HyperFrames, remind it to query
the FULL catalog with hfcat first, and say whether it has done so this session.

Chris, 2026-08-29: "anytime you are ever touching a hyperframes command you
need to get a message reminding you to call hfcat and double check what's
available from the FULL catalog."

Measured before this existed: the `hyperframes-catalog` base domain fires on
prompt keywords and on Write/Edit under Documents/video-gen. It does NOT fire
on a Bash/PowerShell command such as `npx hyperframes render` from any other
directory - verified 2026-08-29 by running exactly that from C:/Users/Chris
and receiving no injection. A fresh session would never have heard of hfcat.

What this hook does (PreToolUse, exit 0 always - it never blocks):

  1. Bash/PowerShell command mentioning hyperframes  -> reminder + session state
  2. Write/Edit of an .html/.js/.css file inside a HyperFrames project
     (a hyperframes.json in any ancestor directory)        -> same reminder
  3. Bash/PowerShell command running hfcat               -> RECORDS the query
     to a per-session marker, so (1) and (2) can report "last hfcat query:
     ..." instead of "NOT yet called this session". That record is the
     measurement the catalog-query-enforcement-gate fork needs before it can
     decide whether blocking is warranted.

Wiring (settings.json, PreToolUse):

    {"matcher": "Bash|PowerShell|Write|Edit|MultiEdit",
     "hooks": [{"type": "command",
                "command": "C:/Python312/python.exe $HOME/.claude/hooks/hfcat-nudge.py",
                "timeout": 5}]}

Output contract: JSON on stdout with hookSpecificOutput.additionalContext.
Anything unexpected -> exit 0 silently. A nudge must never break a tool call.
"""

import json
import os
import re
import sys
import time

MARK_DIR = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or ".",
                        "hfcat-nudge")
HF_RE = re.compile(r"(?<![\w-])(hyperframes|hf)(?![\w-])", re.I)
HFCAT_RE = re.compile(r"(?<![\w-])hfcat(?:\.py)?\b(.*)$", re.I | re.M)
SKIP_RE = re.compile(r"hfcat-nudge|hyperframes-docs|--version\b", re.I)


def session_id(payload):
    sid = (payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID")
           or os.environ.get("CLAUDE_CODE_SESSION_ID") or "")
    return re.sub(r"[^\w-]", "", str(sid))[:64] or "unknown"


def marker_path(sid):
    os.makedirs(MARK_DIR, exist_ok=True)
    return os.path.join(MARK_DIR, sid + ".json")


def load_marker(sid):
    try:
        return json.load(open(marker_path(sid), encoding="utf-8"))
    except Exception:
        return {"queries": []}


def save_marker(sid, m):
    try:
        json.dump(m, open(marker_path(sid), "w", encoding="utf-8"))
    except Exception:
        pass


def in_hf_project(path):
    """True if hyperframes.json sits in the file's directory or any ancestor."""
    try:
        d = os.path.dirname(os.path.abspath(path))
    except Exception:
        return False
    for _ in range(12):
        if os.path.exists(os.path.join(d, "hyperframes.json")):
            return True
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return False


def emit(text):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "additionalContext": text}}))
    sys.stdout.flush()


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    tool = payload.get("tool_name") or ""
    inp = payload.get("tool_input") or {}
    sid = session_id(payload)

    if tool in ("Bash", "PowerShell"):
        cmd = str(inp.get("command") or "")
        if SKIP_RE.search(cmd) and not HFCAT_RE.search(cmd):
            return
        m = HFCAT_RE.search(cmd)
        if m:
            mk = load_marker(sid)
            q = (m.group(1) or "").strip()[:160]
            mk.setdefault("queries", []).append({"t": time.time(), "q": q})
            mk["queries"] = mk["queries"][-50:]
            save_marker(sid, mk)
            return
        if not HF_RE.search(cmd):
            return
        what = "command: " + cmd.strip().splitlines()[0][:120]
    elif tool in ("Write", "Edit", "MultiEdit"):
        fp = str(inp.get("file_path") or "")
        if not fp or not re.search(r"\.(html?|js|mjs|css)$", fp, re.I):
            return
        if not in_hf_project(fp):
            return
        what = "file: " + fp
    else:
        return

    mk = load_marker(sid)
    qs = mk.get("queries") or []
    if qs:
        last = qs[-1]
        age = int(time.time() - last["t"])
        state = (f"hfcat HAS been queried this session ({len(qs)}x; last {age}s ago: "
                 f"`hfcat {last['q']}`). If this beat is a different need, query again.")
    else:
        state = ("hfcat has NOT been called in this session yet. Do it before "
                 "hand-writing any composition markup, animation CSS or motion code.")

    emit(
        "[hfcat] HyperFrames touched (" + what + "). " + state + " "
        "The catalog is 372 finished, parameterised blocks/components plus our own "
        "patterns - hand-building duplicates them. Run `hfcat <what the beat needs>` "
        "(flags: --type block|component|hfpat, --vars, -n N, --json, --show <slug> "
        "for the variable schema + the CORRECT mount key - 44 of 154 blocks mount "
        "under a key that is not their slug). Then `hyperframes add <slug>` or, on "
        "`no catalog match`, hand-build with the miss on record. Every result prints "
        "the absolute source path; open it for the full implementation."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
