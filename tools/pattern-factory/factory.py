#!/usr/bin/env python3
"""
factory.py - fan /pattern-extract out across child sessions.

One reference, one G1.json, N children (Opus, max effort) each owning one or
two candidates. Each child gets a scaffolded HyperFrames workspace, the cached
reference mp4 (so its full watch is offline), the CHILD-BRIEF contract, and a
prompt naming exactly its candidates. The orchestrator (cougar) judges every
delivery at 1:1, assembles the G7 reel, runs the batched cold test, and folds
approved rows via codify.py.

Usage:
  python factory.py spawn  --g1 <G1.json> [--only px-ink,px-count] [--dry]
  python factory.py status --g1 <G1.json>          # what each child has delivered
  python factory.py reel   --g1 <G1.json> [--out <mp4>]   # every delivered render -> one labelled reel

State: <extract-dir>/children/factory-state.json (spawn times, titles, slugs).
"""

import argparse
import datetime as dt
import glob
import json
import os
import shutil
import subprocess
import sys
import urllib.request


# --- portable roots -------------------------------------------------------
# Repo root derives from this file's location: <root>/tools/<dir>/<file>.py
# Override with environment variables if your layout differs.
_HERE = os.path.dirname(os.path.abspath(__file__))
PEK_ROOT = os.environ.get('PEK_ROOT') or os.path.dirname(os.path.dirname(_HERE))
# Optional local agent-spawn hub. Without one, run the child briefs by hand -
# see docs/AGENT-GUIDE.md, 'Running the gates without a spawn hub'.
HUB = os.environ.get('PEK_HUB') or 'http://127.0.0.1:7799/api/spawn'
BRIEF = os.path.join(_HERE, 'CHILD-BRIEF.md')
LIB = os.environ.get('PEK_LIB') or os.path.join(PEK_ROOT, 'pattern-library')
REEL = os.environ.get('PEK_REEL') or os.path.join(PEK_ROOT, 'tools', 'watch-video', 'reel.py')
# Where child sessions drop .status files. Only used by `factory.py status`.
RELAY_INBOX = os.environ.get('PEK_RELAY_INBOX') or os.path.join(
    os.path.expanduser('~'), '.pattern-extract', 'relay-inbox')
SCAFFOLD_FILES = ("hyperframes.json", "CLAUDE.md", "AGENTS.md")


def die(m):
    print("factory: " + m, file=sys.stderr)
    sys.exit(1)


def load_g1(path):
    g1 = json.load(open(path, encoding="utf-8"))
    g1["_dir"] = os.path.dirname(os.path.abspath(path))
    g1["_by_slug"] = {c["slug"]: c for c in g1["candidates"]}
    return g1


def state_path(g1):
    return os.path.join(g1["_dir"], "children", "factory-state.json")


def load_state(g1):
    try:
        return json.load(open(state_path(g1), encoding="utf-8"))
    except Exception:
        return {"children": {}}


def save_state(g1, st):
    os.makedirs(os.path.dirname(state_path(g1)), exist_ok=True)
    json.dump(st, open(state_path(g1), "w", encoding="utf-8"), indent=2)


def scaffold(g1, title):
    """A fresh HyperFrames project for one child, next to the reference's own
    build/ dir, with the live library junctioned in and the mp4 pre-cached."""
    src = os.path.join(g1["_dir"], "build")
    dst = os.path.join(g1["_dir"], "children", title)
    os.makedirs(dst, exist_ok=True)
    for f in SCAFFOLD_FILES:
        s = os.path.join(src, f)
        if os.path.exists(s) and not os.path.exists(os.path.join(dst, f)):
            shutil.copy2(s, dst)
    pj = os.path.join(dst, "package.json")
    if not os.path.exists(pj):
        base = json.load(open(os.path.join(src, "package.json"), encoding="utf-8"))
        base["name"] = title
        json.dump(base, open(pj, "w", encoding="utf-8"), indent=2)
    meta = os.path.join(dst, "meta.json")
    if not os.path.exists(meta):
        json.dump({"id": title, "name": title,
                   "createdAt": dt.datetime.now(dt.timezone.utc).isoformat()},
                  open(meta, "w", encoding="utf-8"))
    for d in ("drafts", "renders", "g2", "g5", "provenance", "pending", "scratch/dl"):
        os.makedirs(os.path.join(dst, d), exist_ok=True)
    junction = os.path.join(dst, "pattern-library")
    if not os.path.exists(junction):
        # mklink /J: same junction name the library's example references verbatim
        r = subprocess.run(["cmd", "/c", "mklink", "/J", junction.replace("/", "\\"),
                            LIB.replace("/", "\\")], capture_output=True, text=True)
        if r.returncode != 0:
            die("junction failed for " + title + ": " + r.stderr + r.stdout)
    mp4 = g1["reference"].get("cached_mp4")
    if mp4 and os.path.exists(mp4):
        tgt = os.path.join(dst, "scratch", "dl", os.path.basename(mp4))
        if not os.path.exists(tgt):
            shutil.copy2(mp4, tgt)
    # the brief travels with the workspace so it survives a hub restart
    shutil.copy2(BRIEF, os.path.join(dst, "CHILD-BRIEF.md"))
    return dst


def build_prompt(g1, asg, cwd):
    ref = g1["reference"]
    rows = []
    for s in asg["slugs"]:
        c = g1["_by_slug"][s]
        rows.append(f"  - {s}  (candidate #{c['n']})  ref {c['ref_s']} s\n"
                    f"      mechanism: {c['mechanism']}\n"
                    f"      library gap: {c['gap']}")
    return (
        f"EXTRACTION CHILD for /pattern-extract. Parent: cougar. Reference: {ref['name']} "
        f"({ref['id']}, {ref['url']}), {ref['duration_s']} s @ {ref['fps']} fps.\n\n"
        f"YOUR CANDIDATES (both, each through every gate):\n" + "\n".join(rows) + "\n\n"
        f"Why these two together: {asg['why']}.\n\n"
        f"Your workspace is {cwd} (already scaffolded; the reference mp4 is cached at "
        f"scratch/dl/{ref['id']}.mp4 so watch.py runs offline; the library is junctioned at "
        f"pattern-library/ and is READ-ONLY for you).\n\n"
        f"READ {cwd}/CHILD-BRIEF.md FIRST and follow it exactly: the eight files to read, "
        f"G0 FULL WATCH (every sheet, every defect crop, no --from/--to), G2 with ROI + "
        f"fit-ease.py on every transition, G2b hfcat, G3, G4 both layouts from one file, "
        f"G5 mechanically with fit-ease --compare (<=5%), G6 at 1:1 on both renders, then the "
        f"exact deliverable paths and the provenance/pending schemas. Token spend and runtime are "
        f"not constraints; do the full pass, double-verify, and measure rather than describe.\n\n"
        f"Report stage changes to cougar only (base relay ping --to cougar). Never ping chris. "
        f"When both patterns are DELIVERED, ping cougar with every deliverable path, set your "
        f".status to 'idle: delivered', and stay alive for the interview."
    )


def spawn(g1, only, dry):
    st = load_state(g1)
    for asg in g1["assignments"]:
        title = asg["child"]
        if only and title not in only:
            continue
        if title in st["children"] and not dry:
            print(f"skip {title}: already spawned {st['children'][title]['spawned_at']}")
            continue
        cwd = scaffold(g1, title)
        prompt = build_prompt(g1, asg, cwd)
        payload = {"side": "win", "cwd": cwd, "title": title, "project": "video-gen",
                   "parent": "cougar", "model": "opus", "effort": "max",
                   "prompt": prompt, "report_boot": True}
        if dry:
            print(f"--- {title} -> {cwd}\n{prompt}\n")
            continue
        req = urllib.request.Request(HUB, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
        except Exception as e:
            die(f"spawn {title} failed: {e}")
        st["children"][title] = {"slugs": asg["slugs"], "cwd": cwd,
                                 "spawned_at": dt.datetime.now().isoformat(timespec="seconds"),
                                 "hub": body[:300]}
        save_state(g1, st)
        print(f"spawned {title}  slugs={asg['slugs']}  hub={body[:120]}")


def status(g1):
    st = load_state(g1)
    for title, ch in st["children"].items():
        cwd = ch["cwd"]
        inbox = os.path.join(RELAY_INBOX, title)
        try:
            stat = open(os.path.join(inbox, ".status"), encoding="utf-8").read().strip()
        except Exception:
            stat = "(no .status)"
        print(f"== {title}  spawned {ch['spawned_at']}  status: {stat}")
        for s in ch["slugs"]:
            have = {
                "draft": os.path.exists(os.path.join(cwd, "drafts", s + ".js")),
                "std": os.path.exists(os.path.join(cwd, "renders", f"{s}-standard.mp4")),
                "mirror": os.path.exists(os.path.join(cwd, "renders", f"{s}-mirror.mp4")),
                "prov": os.path.exists(os.path.join(cwd, "provenance", s + ".json")),
                "pending": os.path.exists(os.path.join(cwd, "pending", s + ".md")),
            }
            print(f"   {s:<14} " + "  ".join(f"{k}:{'Y' if v else '-'}" for k, v in have.items()))
        rep = os.path.join(cwd, "REPORT.md")
        print(f"   REPORT.md: {'Y' if os.path.exists(rep) else '-'}")


def reel(g1, out):
    st = load_state(g1)
    clips = []
    for title, ch in st["children"].items():
        for s in ch["slugs"]:
            for lay in ("standard", "mirror"):
                p = os.path.join(ch["cwd"], "renders", f"{s}-{lay}.mp4")
                if os.path.exists(p):
                    clips.append({"label": f"{s} / {lay}", "file": p})
    # approved orbit pair rides along so the reel is the whole reference in one file
    for lay in ("standard", "mirror"):
        p = os.path.join(g1["_dir"], "build", "renders", f"orbit-{lay}.mp4")
        if os.path.exists(p):
            clips.insert(0 if lay == "mirror" else 0, {"label": f"orbitStage+reDress / {lay}", "file": p})
    if not clips:
        die("no renders delivered yet")
    out = out or os.path.join(g1["_dir"], "reel", f"{g1['reference']['id']}-G7-reel.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    man = out[:-4] + ".clips.json"
    json.dump(clips, open(man, "w", encoding="utf-8"), indent=2)
    subprocess.run([sys.executable, REEL, out, "--manifest", man,
                    "--title", f"{g1['reference']['name']} — pattern reel"], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["spawn", "status", "reel"])
    ap.add_argument("--g1", required=True)
    ap.add_argument("--only", default=None, help="comma-separated child titles")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    g1 = load_g1(a.g1)
    only = set(a.only.split(",")) if a.only else None
    if a.cmd == "spawn":
        spawn(g1, only, a.dry)
    elif a.cmd == "status":
        status(g1)
    else:
        reel(g1, a.out)


if __name__ == "__main__":
    main()
