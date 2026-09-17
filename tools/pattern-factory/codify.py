#!/usr/bin/env python3
"""
codify.py - G9 as a tool. Two verbs:

  register   a child's delivered pattern -> one block in pattern-library/PENDING.md
             (the register Chris asked for on 2026-08-29: "add them to a markdown
             file so that when I VERIFY THEM they can be ready to fold easily into
             our personal json file that sits next to hfcat core file")
  fold       a VERIFIED slug from PENDING.md -> hfpat-index.json row, builder
             appended to hfpat.js, LIBRARY.md pattern table regenerated FROM the
             index, baselines/<slug>/ written, LEDGER row appended, block marked
             FOLDED. Only after Chris says yes. Never called by a child.

Usage:
  python codify.py register --child <child-workspace> --slug <slug> [--reference <id>]
  python codify.py fold --slug <slug> --verified-by chris [--note "..."]
  python codify.py regen-library            # LIBRARY.md table from the index, idempotent

Hard rules (fork hfpat-index-g9-authoring, approved):
  - never append to hyperframes-docs/reference/catalog-index.json (regenerated, wiped)
  - every field in the index row is produced by the pipeline (provenance.json), never typed later
  - LIBRARY.md's pattern table is GENERATED; regenerating twice yields identical bytes
  - null is an honest value
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys


# --- portable roots -------------------------------------------------------
# Repo root derives from this file's location: <root>/tools/<dir>/<file>.py
# Override with environment variables if your layout differs.
_HERE = os.path.dirname(os.path.abspath(__file__))
PEK_ROOT = os.environ.get('PEK_ROOT') or os.path.dirname(os.path.dirname(_HERE))
LIB = os.environ.get('PEK_LIB') or os.path.join(PEK_ROOT, 'pattern-library')
INDEX = os.path.join(LIB, "hfpat-index.json")
HFPAT = os.path.join(LIB, "hfpat.js")
LIBRARY = os.path.join(LIB, "LIBRARY.md")
LEDGER = os.path.join(LIB, "LEDGER.md")
PENDING = os.path.join(LIB, "PENDING.md")
BASELINES = os.path.join(LIB, "baselines")

GEN_BEGIN = "<!-- hfpat-index: generated table BEGIN - do not hand-edit; run codify.py regen-library -->"
GEN_END = "<!-- hfpat-index: generated table END -->"


def die(m):
    print("codify: " + m, file=sys.stderr)
    sys.exit(1)


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8", newline="\n").write(s)


def load_index():
    return json.load(open(INDEX, encoding="utf-8"))


def save_index(d):
    d["count"] = len(d["items"])
    d["generated"] = dt.datetime.now().isoformat(timespec="seconds")
    json.dump(d, open(INDEX, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- register

def register(child, slug, reference, draft=None):
    prov_p = os.path.join(child, "provenance", slug + ".json")
    draft_p = os.path.abspath(draft) if draft else os.path.join(child, "drafts", slug + ".js")
    if not os.path.exists(prov_p):
        die("missing " + prov_p)
    if not os.path.exists(draft_p):
        die("missing " + draft_p)
    prov = json.load(open(prov_p, encoding="utf-8"))
    std = os.path.join(child, "renders", f"{slug}-standard.mp4")
    mir = os.path.join(child, "renders", f"{slug}-mirror.mp4")
    for p in (std, mir):
        if not os.path.exists(p):
            die("missing render " + p)
    fit = prov.get("fit") or {}
    g5 = prov.get("g5") or {}
    ref = prov.get("reference") or {}
    times = ref.get("times_s") or []

    def fit_text(f):
        """One line from a fit block, whether flat {family,duration_s,rms_pct} or nested
        {travel:{...}, ripple:{...}} (packetRide shipped the nested shape)."""
        if not isinstance(f, dict):
            return "no fit recorded"
        if f.get("family") or f.get("duration_s"):
            d = f.get("duration_s"); r = f.get("rms_pct")
            return f"{f.get('family')}" + (f" {d} s" if d is not None else "") + (f", rms {r}%" if r is not None else "")
        parts = []
        for k, v in f.items():
            if isinstance(v, dict) and (v.get("family") or v.get("speed_px_per_s") or v.get("duration_s")):
                d = v.get("duration_s"); r = v.get("rms_pct"); sp = v.get("speed_px_per_s")
                parts.append(f"{k}: {v.get('family')}" + (f" {sp} px/s" if sp else "") + (f" {d} s" if d is not None else "") + (f", rms {r}%" if r is not None else ""))
        return "; ".join(parts) or "no fit recorded"
    rows = [{
        "slug": slug, "kind": "hfpat", "title": prov.get("title") or slug,
        "description": prov.get("mechanism") or "",
        "install": f"HFPat.{slug}(tl, el, opts)", "writes": "",
        "source": HFPAT.replace("/", "\\"),
        "enforced": prov.get("enforced"),
        "layouts": ["standard", "mirror"],
        "provenance": f"{ref.get('id') or reference or '?'} @ {times}; {fit_text(fit)}",
        "convergence": (f"{g5.get('final_pct')}% after {len(g5.get('rounds') or [])} rounds"
                        if g5 else None),
        "approved": None,
        "_child": child, "_draft": draft_p, "_renders": {"standard": std, "mirror": mir},
        "_provenance_file": prov_p,
        "_hfcat": (prov.get("hfcat") or {}).get("decision"),
        "_registered": dt.datetime.now().isoformat(timespec="seconds"),
    }]
    row = rows[0]
    pend = read(PENDING)
    if re.search(rf"^## {re.escape(slug)} — ", pend, re.M):
        die(f"{slug} already registered in PENDING.md")
    lib_row = f"| `{slug}` | {row['description']} | {row['provenance']}; convergence {row['convergence']} |"
    block = (
        f"\n## {slug} — PENDING  (child: {os.path.basename(child)}, {row['_registered'][:10]})\n\n"
        f"mechanism: {row['description']}\n\n"
        f"reference: {row['provenance']}\n\n"
        f"renders: `{std}` · `{mir}`\n\n"
        f"G5 final: {g5.get('final_pct')}% (rounds: {len(g5.get('rounds') or [])}) · "
        f"G6: {((prov.get('g6') or {}).get('check'))} · hfcat: {row['_hfcat']}\n\n"
        f"draft: `{draft_p}` · provenance: `{prov_p}`\n\n"
        "```json\n" + json.dumps({k: v for k, v in row.items() if not k.startswith('_')},
                                 indent=2, ensure_ascii=False) + "\n```\n\n"
        f"LIBRARY row: {lib_row}\n\n"
        f"<!-- codify:meta {json.dumps({k: v for k, v in row.items() if k.startswith('_')})} -->\n"
    )
    write(PENDING, pend.rstrip("\n") + "\n" + block)
    print(f"registered {slug} in PENDING.md (child {os.path.basename(child)})")


# --------------------------------------------------------------------------- fold

def find_block(pend, slug):
    m = re.search(rf"^## {re.escape(slug)} — (PENDING|FOLDED[^\n]*)\n(.*?)(?=^## |\Z)", pend, re.M | re.S)
    if not m:
        die(f"{slug} not in PENDING.md")
    return m


def extract_builder(draft_src, slug):
    """Take the child's draft file body (inside its IIFE if it has one) so it can be
    appended into hfpat.js's IIFE verbatim, with a provenance header."""
    body = draft_src
    m = re.search(r"\(function\s*\([^)]*\)\s*\{(.*)\}\)\s*\([^)]*\);?\s*$", draft_src, re.S)
    if m:
        body = m.group(1)
    # drop a child's own `var HFPat = global.HFPat` guard: inside hfpat.js HFPat is in scope
    body = re.sub(r"^\s*(\"use strict\";|'use strict';)\s*$", "", body, flags=re.M)
    body = re.sub(r"^\s*var HFPat = global\.HFPat;\s*$", "", body, flags=re.M)
    body = re.sub(r"^\s*if \(!HFPat\) throw new Error\([^\n]*\);\s*$", "", body, flags=re.M)
    return body.strip("\n")


def fold(slug, verified_by, note):
    pend = read(PENDING)
    m = find_block(pend, slug)
    if m.group(1).startswith("FOLDED"):
        die(f"{slug} already folded")
    meta_m = re.search(r"<!-- codify:meta (.*?) -->", m.group(2), re.S)
    row_m = re.search(r"```json\n(.*?)\n```", m.group(2), re.S)
    if not meta_m or not row_m:
        die("block is missing its meta/row; was it hand-edited?")
    meta = json.loads(meta_m.group(1))
    row = json.loads(row_m.group(1))
    row["approved"] = {"by": verified_by, "date": dt.datetime.now().isoformat(timespec="seconds"),
                       "note": note}

    # 1. index row (our file, never the catalog's)
    idx = load_index()
    if any(i["slug"] == slug for i in idx["items"]):
        die(f"{slug} already in hfpat-index.json")
    idx["items"].append(row)
    idx["g9_fields_pending"] = [i["slug"] for i in idx["items"] if i.get("provenance") is None]
    save_index(idx)

    # 2. builder into hfpat.js, before the IIFE's closing line
    src = read(HFPAT)
    tail_m = re.search(r"\n\}\)\(typeof window !== \"undefined\" \? window : this\);\s*$", src)
    if not tail_m:
        die("hfpat.js closing line not found; refuse to append blind")
    if re.search(rf"HFPat\.{re.escape(slug)}\s*=", src):
        die(f"HFPat.{slug} already defined in hfpat.js")
    already = f"draft: {meta['_draft']}" in src
    builder = "" if already else extract_builder(read(meta["_draft"]), slug)
    header = ("" if already else f"\n  /* =====================================================================\n"
              f"     {slug} — folded {row['approved']['date'][:10]} by codify.py, verified by {verified_by}\n"
              f"     provenance: {row['provenance']}\n"
              f"     convergence: {row['convergence']}\n"
              f"     draft: {meta['_draft']}\n"
              f"     ===================================================================== */\n")
    src = src[:tail_m.start()] + header + builder + "\n" + src[tail_m.start():]
    shutil.copy2(HFPAT, HFPAT + ".BAK-pre-" + slug)
    write(HFPAT, src)

    # 3. baselines from the child's watch ring (hero = sheet_01, four defect bands)
    bdir = os.path.join(BASELINES, slug)
    os.makedirs(bdir, exist_ok=True)
    ring = meta["_renders"]["standard"][:-4] + ".watch"
    copied = []
    if os.path.isdir(ring):
        vers = sorted(d for d in os.listdir(ring) if d.startswith("v"))
        if vers:
            vdir = os.path.join(ring, vers[-1])
            for f in os.listdir(vdir):
                if f.startswith("defect_") or f == "sheet_01.jpg":
                    shutil.copy2(os.path.join(vdir, f), os.path.join(bdir, "hero.jpg" if f == "sheet_01.jpg" else f))
                    copied.append(f)
    write(os.path.join(bdir, "BASELINE.md"),
          f"# Baseline — {slug}\n\n| | |\n|---|---|\n| Captured | {row['approved']['date'][:10]} |\n"
          f"| From | {meta['_child']} |\n| Render | {meta['_renders']['standard']} |\n"
          f"| Provenance | {row['provenance']} |\n| Convergence | {row['convergence']} |\n"
          f"| Verified by | {verified_by} |\n\n## Files copied from the child's G6 ring\n\n"
          + "".join(f"- {c}\n" for c in copied)
          + "\n## Regression use only\n\nDiff a re-render against these. Never creative reference (LIBRARY.md warning).\n")

    # 4. ledger row
    led = read(LEDGER)
    led_row = (f"| {row['approved']['date'][:10]} | {row['provenance'].split(' @')[0]} (factory) | {slug} | "
               f"pending cold test | - / - | see child REPORT.md | fold via codify.py |")
    led = re.sub(r"(\| 2026-08-27 \| round 6[^\n]*\n)", r"\1" + led_row + "\n", led, count=1) \
        if "| round 6" in led else led.rstrip("\n") + "\n" + led_row + "\n"
    write(LEDGER, led)

    # 5. mark the block, regenerate LIBRARY table
    pend = pend.replace(f"## {slug} — PENDING", f"## {slug} — FOLDED {row['approved']['date'][:10]} by {verified_by}", 1)
    write(PENDING, pend)
    regen_library()
    print(f"folded {slug}: index row, hfpat.js builder, baselines/{slug}, LEDGER row, LIBRARY.md table")


# --------------------------------------------------------------------------- regen

def regen_library():
    idx = load_index()
    lines = ["| Pattern | What it is | Provenance |", "|---|---|---|"]
    for i in idx["items"]:
        prov = i.get("provenance") or "pending G9 back-fill (LEDGER)"
        conv = i.get("convergence")
        enf = i.get("enforced")
        cell = prov + (f"; convergence {conv}" if conv else "") + (f". Enforced: {enf}" if enf else "")
        appr = i.get("approved")
        if isinstance(appr, dict):
            cell += f". Verified {appr.get('date', '')[:10]} by {appr.get('by')}"
        lines.append(f"| `{i['slug']}` | {i.get('description', '')} | {cell} |")
    table = GEN_BEGIN + "\n" + "\n".join(lines) + "\n" + GEN_END
    lib = read(LIBRARY)
    if GEN_BEGIN in lib:
        lib = re.sub(re.escape(GEN_BEGIN) + r".*?" + re.escape(GEN_END), lambda _: table, lib, flags=re.S)
    else:
        # first run: replace the hand-written table under "## Patterns"
        m = re.search(r"(## Patterns\n\n)(\| Pattern.*?)(?=\n\n## |\Z)", lib, re.S)
        if not m:
            die("LIBRARY.md '## Patterns' table not found")
        lib = lib[:m.start(2)] + table + lib[m.end(2):]
    write(LIBRARY, lib)
    print(f"LIBRARY.md pattern table regenerated from hfpat-index.json ({len(idx['items'])} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["register", "fold", "regen-library"])
    ap.add_argument("--child")
    ap.add_argument("--slug")
    ap.add_argument("--reference", default=None)
    ap.add_argument("--draft", default=None, help="register: draft file when two slugs share one (default drafts/<slug>.js)")
    ap.add_argument("--verified-by", default=None)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    if a.cmd == "register":
        if not (a.child and a.slug):
            die("register needs --child and --slug")
        register(os.path.abspath(a.child), a.slug, a.reference, a.draft)
    elif a.cmd == "fold":
        if not (a.slug and a.verified_by):
            die("fold needs --slug and --verified-by (Chris's yes, on record)")
        fold(a.slug, a.verified_by, a.note)
    else:
        regen_library()


if __name__ == "__main__":
    main()
