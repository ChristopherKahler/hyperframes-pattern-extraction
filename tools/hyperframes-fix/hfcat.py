"""hfcat — instant local search over the HyperFrames catalog index.

Answers "is there already a block for this?" in one command, offline, with no
model download. Returns install commands and variable counts, never prose.

    hfcat bar chart race
    hfcat --type block terminal typing
    hfcat --vars slack            # only items that expose a variable schema
    hfcat --show bar-chart-race   # full variable schema for one item

TWO SOURCES, deliberately separate:
  catalog  Documents/video-gen/hyperframes-docs/reference/catalog-index.json
           rebuilt by tools/hyperframes-fix/build-catalog-index.py
  ours     Documents/video-gen/pattern-library/hfpat-index.json
           NEVER append ours to the catalog index — that file is regenerated
           from the mirrored docs, so an append is wiped on the next re-mirror.
"""
import argparse
import json
import os
import re
import sys


# --- portable roots -------------------------------------------------------
# Repo root derives from this file's location: <root>/tools/<dir>/<file>.py
# Override with environment variables if your layout differs.
_HERE = os.path.dirname(os.path.abspath(__file__))
PEK_ROOT = os.environ.get('PEK_ROOT') or os.path.dirname(os.path.dirname(_HERE))
# The catalog indexes ship WITH this repo under catalog/reference/, so hfcat
# works straight from a clone. The full HyperFrames docs mirror (the prose
# pages each row cites) is upstream content and is NOT redistributed here -
# generate it locally with tools/hyperframes-fix/mirror-docs.ps1 and point
# HF_DOCS at it to make `--show` able to open a row's source page.
DOCS = os.environ.get('HF_DOCS') or os.path.join(PEK_ROOT, 'catalog')
INDEX = os.path.join(DOCS, 'reference', 'catalog-index.json')
MOUNTS = os.path.join(DOCS, 'reference', 'block-mount-keys.json')
HFPAT = os.path.join(
    os.environ.get('PEK_LIB') or os.path.join(PEK_ROOT, 'pattern-library'),
    'hfpat-index.json')


def source_path(item):
    """Absolute path to the source this row came from.

    Catalog rows point at their mirrored docs page. Our own patterns have no
    mirrored page and carry an explicit `source` instead.
    """
    if item.get("source"):
        return item["source"]
    if not item.get("page"):
        return "(no source recorded)"
    p = os.path.join(DOCS, item["page"].replace("/", os.sep))
    if not os.path.exists(p):
        return (item["page"] + "  (docs mirror not present - run\n"
                "    tools/hyperframes-fix/mirror-docs.ps1  and set HF_DOCS)")
    return p


def load():
    if not os.path.exists(INDEX):
        sys.exit(f"index not found: {INDEX}\n"
                 f"rebuild with tools/hyperframes-fix/build-catalog-index.py")
    items = json.load(open(INDEX, encoding="utf-8"))["items"]
    # Our own patterns live in a SEPARATE file, never appended to the catalog
    # index — that one is regenerated from the mirrored docs by
    # build-catalog-index.py, and an append would be deleted silently on the
    # next re-mirror. Two sources, independently rebuildable. (seal's spec,
    # 2026-08-27.) A missing pattern index is not an error.
    try:
        ours = json.load(open(HFPAT, encoding="utf-8")).get("items", [])
        for i in ours:
            i.setdefault("kind", "hfpat")
            i.setdefault("var_count", len(i.get("variables") or []))
            i.setdefault("writes", "")
            i.setdefault("page", "")
        items = items + ours
    except (OSError, ValueError):
        pass
    # Fold in the mount key: 44 of 154 blocks register their timeline under a
    # key that is NOT their slug, so the documented mount snippet silently
    # no-ops. Print it beside the install command so that cannot happen.
    try:
        mounts = json.load(open(MOUNTS, encoding="utf-8"))["blocks"]
        for i in items:
            m = mounts.get(i["slug"])
            if m:
                i["mount_key"] = m.get("mount_key")
                i["mount_matches_slug"] = m.get("matches_slug")
                i["install_files"] = m.get("install_files")
                i["render_time_network"] = m.get("render_time_network")
                i["needs_runtime"] = m.get("needs")
    except (OSError, ValueError, KeyError):
        pass
    return items


def tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t]


def score(item, terms):
    """Field-weighted term overlap. Slug and title beat description."""
    slug = tokens(item["slug"])
    title = tokens(item["title"])
    desc = tokens(item["description"])
    n = 0
    for t in terms:
        if t in slug:
            n += 10
        elif any(s.startswith(t) for s in slug):
            n += 6
        if t in title:
            n += 6
        elif any(s.startswith(t) for s in title):
            n += 3
        if t in desc:
            n += 2
    # a query whose every term lands somewhere beats a partial match
    if terms and all(t in slug + title + desc for t in terms):
        n += 8
    return n


def show(item):
    print(f"\n{item['title']}  ({item['kind']})")
    print(f"  {item['install']}")
    print(f"  writes:  {item['writes']}"
          + (f"  (+{item['support_files']} supporting)"
             if item.get("support_files") else ""))
    if item.get("mount_key") and item.get("mount_matches_slug") is False:
        print(f"  MOUNT:   data-composition-id=\"{item['mount_key']}\"  "
              f"<- NOT the slug. Using the slug here silently does nothing.")
    elif item.get("mount_key"):
        print(f"  mount:   data-composition-id=\"{item['mount_key']}\"")
    print(f"  source:  {source_path(item)}")
    print(f"  {item['description']}")
    if item.get("render_time_network"):
        print("  WARNING: fetches over the network at RENDER time — "
              "fails on an offline render host.")
    if item.get("cdn_libs"):
        print(f"  needs: {', '.join(item['cdn_libs'])}")
    v = item.get("variables") or []
    if not v:
        print("  no declared variables")
        return
    print(f"  {len(v)} variables (declared via {item.get('var_source')}):")
    for x in v:
        rng = ""
        if "min" in x or "max" in x:
            rng = f"  [{x.get('min','')}..{x.get('max','')}]"
        d = str(x.get("default", ""))
        if len(d) > 50:
            d = d[:47] + "..."
        print(f"    {x.get('id',''):<22} {x.get('type',''):<8} = {d}{rng}")


def main():
    ap = argparse.ArgumentParser(prog="hfcat", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*", help="what the beat needs")
    ap.add_argument("--type", choices=["block", "component", "hfpat"],
                help="filter by kind (hfpat = our own pattern library)")
    ap.add_argument("--vars", action="store_true",
                    help="only items exposing a variable schema")
    ap.add_argument("--show", metavar="SLUG", help="full schema for one item")
    ap.add_argument("-n", type=int, default=8, help="how many results (default 8)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    items = load()

    if a.show:
        m = [i for i in items if i["slug"] == a.show]
        if not m:
            sys.exit(f"no catalog item with slug '{a.show}'")
        if a.json:
            print(json.dumps(m[0], indent=2))
        else:
            show(m[0])
        return

    if not a.query:
        ap.print_help()
        return

    pool = items
    if a.type:
        pool = [i for i in pool if i["kind"] == a.type]
    if a.vars:
        pool = [i for i in pool if i["var_count"]]

    terms = tokens(" ".join(a.query))
    ranked = sorted(((score(i, terms), i) for i in pool),
                    key=lambda p: -p[0])
    hits = [i for s, i in ranked if s > 0][:a.n]

    if a.json:
        print(json.dumps(hits, indent=2))
        return

    if not hits:
        print(f"no catalog match for {' '.join(a.query)!r} "
              f"among {len(pool)} items — hand-building is justified")
        return

    print(f"{len(hits)} of {len(pool)} catalog items match {' '.join(a.query)!r}:\n")
    for i in hits:
        v = f"{i['var_count']} vars" if i["var_count"] else "no vars"
        d = (i["description"] or "")
        if len(d) > 88:
            d = d[:85] + "..."
        flags = []
        if i.get("mount_matches_slug") is False:
            flags.append(f'mount id="{i["mount_key"]}"')
        if i.get("render_time_network"):
            flags.append("render-time network")
        print(f"  {i['slug']:<38} {i['kind']:<10} {v:<9} {d}")
        print(f"  {'':<38} source: {source_path(i)}")
        if flags:
            print(f"  {'':<38} ! {' · '.join(flags)}")
    print(f"\n  hfcat --show <slug>        full variable schema + mount key")
    if any(i["kind"] != "hfpat" for i in hits):
        print("  hyperframes add <slug>     install a catalog block/component")
    if any(i["kind"] == "hfpat" for i in hits):
        print("  HFPat.<slug>(el, opts)     call one of OUR patterns")
    print("  every source path above is the full file — read it for the complete implementation")


if __name__ == "__main__":
    main()
