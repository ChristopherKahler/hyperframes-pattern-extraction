"""Build an exact index of every HyperFrames catalog page from the local mirror.

Mechanical extraction only - nothing inferred. Emits:
  reference/catalog-index.md    human-readable table + per-item variable schemas
  reference/catalog-index.json  machine-readable
"""
import json
import os
import re

ROOT = r"$HF_DOCS"
PAGES = os.path.join(ROOT, "pages", "catalog")
OUT = os.path.join(ROOT, "reference")
os.makedirs(OUT, exist_ok=True)

RE_TITLE = re.compile(r"^#\s+(.+?)\s*$", re.M)
RE_DESC = re.compile(r"^#\s+.+?\n\n>\s*(.+?)\s*$", re.M)
RE_INSTALL = re.compile(r'<InstallCommand\s+command="([^"]+)"')
RE_NPX = re.compile(r"npx hyperframes add ([a-z0-9\-]+)")
# Two phrasings ship on the catalog pages, found by hf-prompt's audit 2026-08-27:
#   "That writes one file: `compositions/x.html`."          321 pages
#   "That writes `compositions/x.html`, plus 3 supporting."   51 pages
# The old regex matched only the first, then fell through to the codeblock
# filename and reported `index.html` for 9 items — wrong, and high blast radius
# (a reader would think `hyperframes add` overwrites their root index.html).
RE_WRITES = re.compile(r"writes(?:\s+one\s+file)?:?\s*`([^`]+)`")
RE_SUPPORT = re.compile(r"plus\s+(\d+)\s+supporting")
RE_CODEFILE = re.compile(r"```html\s+([A-Za-z0-9_\-.]+\.html)")
RE_VARS = re.compile(r"variables=\{(\[.*?\])\}\s*>", re.S)
# Second declaration surface, found by hf-studio 2026-08-27: a block can declare
# its schema on <html data-composition-variables='[...]'> in the source with NO
# rendered VariablesExplorer. 4 of 372 items use only this form.
RE_VARS_ATTR = re.compile(r"data-composition-variables='(\[.*?\])'", re.S)
RE_COMPSRC = re.compile(r'compositionSrc="([^"]+)"')
RE_CDN = re.compile(r'src="(https://cdn\.[^"]+)"')


def jsx_array(txt):
    """JSX object literals are JSON-compatible here (double-quoted keys)."""
    try:
        return json.loads(txt)
    except Exception:
        return None


items = []
for kind in ("blocks", "components"):
    d = os.path.join(PAGES, kind)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(d, fn)
        raw = open(path, encoding="utf-8").read()
        slug = fn[:-3]

        title = RE_TITLE.search(raw)
        desc = RE_DESC.search(raw)
        install = RE_INSTALL.search(raw)
        npx = RE_NPX.search(raw)
        # re.search takes the FIRST "writes ... `x`" on the page, which on
        # camera-shake.md matched a stray backtick long before the install
        # section and yielded "t". Take the first candidate that actually looks
        # like a declared path. (hf-prompt re-verify, 2026-08-27)
        writes = None
        for m in RE_WRITES.finditer(raw):
            v = m.group(1)
            if v.endswith(".html") or "/" in v:
                writes = m
                break
        codefile = RE_CODEFILE.search(raw)
        compsrc = RE_COMPSRC.search(raw)
        varsm = RE_VARS.search(raw)

        variables = jsx_array(varsm.group(1)) if varsm else None
        var_source = "VariablesExplorer" if variables else None
        if not variables:
            attrm = RE_VARS_ATTR.search(raw)
            if attrm:
                body = attrm.group(1)
                body = (body.replace("&quot;", '"').replace("&#39;", "'")
                            .replace("&amp;", "&").replace("&lt;", "<")
                            .replace("&gt;", ">"))
                variables = jsx_array(body)
                if variables:
                    var_source = "data-composition-variables"
        libs = sorted({m for m in RE_CDN.findall(raw)
                       if "hyperframes-player" not in m})

        items.append({
            "slug": slug,
            "kind": kind[:-1],                       # block | component
            "title": title.group(1) if title else None,
            "description": desc.group(1) if desc else None,
            "install": (install.group(1) if install
                        else (f"npx hyperframes add {npx.group(1)}" if npx else None)),
            # NEVER fall back to the codeblock filename — that is what produced
            # the bogus `index.html` values. compositionSrc is a real declared
            # path; a code-fence name is not.
            "writes": (writes.group(1) if writes
                       else (compsrc.group(1) if compsrc else None)),
            "support_files": (int(RE_SUPPORT.search(raw).group(1))
                              if RE_SUPPORT.search(raw) else 0),
            "variables": variables,
            "var_count": len(variables) if variables else 0,
            "var_source": var_source,
            "cdn_libs": libs,
            "page": f"pages/catalog/{kind}/{fn}",
            "bytes": os.path.getsize(path),
        })

blocks = [i for i in items if i["kind"] == "block"]
comps = [i for i in items if i["kind"] == "component"]

with open(os.path.join(OUT, "catalog-index.json"), "w", encoding="utf-8") as f:
    json.dump({"count": len(items), "blocks": len(blocks),
               "components": len(comps), "items": items}, f, indent=2)


def vartable(v):
    lines = ["| id | type | default | range |", "|---|---|---|---|"]
    for x in v:
        rng = ""
        if "min" in x or "max" in x:
            rng = f"{x.get('min','')}–{x.get('max','')}"
            if "step" in x:
                rng += f" step {x['step']}"
        default = x.get("default", "")
        if isinstance(default, str):
            default = default.replace("\n", " / ").replace("|", "\\|")
            if len(default) > 60:
                default = default[:57] + "..."
        lines.append(f"| `{x.get('id','')}` | {x.get('type','')} | "
                     f"{default} | {rng} |")
    return "\n".join(lines)


L = []
L.append("---")
L.append("type: reference")
L.append("status: active")
L.append("tags: [hyperframes, catalog, blocks, components, "
         "install-commands, variable-schemas, video-gen]")
L.append("relatedTo: [video-gen, hyperframes, hyperframes-registry]")
L.append("---")
L.append("")
L.append("# HyperFrames catalog — complete index")
L.append("")
L.append(f"Extracted mechanically from the local mirror on 2026-08-27. "
         f"**{len(items)} items: {len(blocks)} blocks, {len(comps)} components.** "
         f"Nothing here is summarised — every field is lifted verbatim from the page.")
L.append("")
L.append("`blocks` are whole sub-compositions with a declared variable schema. "
         "`components` are snippets you paste into a composition. "
         "Machine-readable twin: `catalog-index.json`.")
L.append("")

for label, group in (("Blocks", blocks), ("Components", comps)):
    L.append(f"## {label} ({len(group)})")
    L.append("")
    L.append("| Item | Slug | Vars | Writes | Description |")
    L.append("|---|---|---|---|---|")
    for i in group:
        d = (i["description"] or "").replace("|", "\\|")
        if len(d) > 130:
            d = d[:127] + "..."
        L.append(f"| {i['title'] or ''} | `{i['slug']}` | {i['var_count'] or ''} | "
                 f"`{i['writes'] or ''}` | {d} |")
    L.append("")

withvars = [i for i in items if i["var_count"]]
L.append(f"## Variable schemas ({len(withvars)} items expose one)")
L.append("")
L.append("These are the tunable parameters each item declares. Defaults are the "
         "shipped values.")
L.append("")
for i in sorted(withvars, key=lambda x: (x["kind"], x["slug"])):
    L.append(f"### `{i['slug']}` — {i['title']} ({i['kind']})")
    L.append("")
    L.append(f"`{i['install'] or ''}` → `{i['writes'] or ''}`")
    L.append("")
    L.append(vartable(i["variables"]))
    L.append("")

libcount = {}
for i in items:
    for lib in i["cdn_libs"]:
        libcount[lib] = libcount.get(lib, 0) + 1
if libcount:
    L.append("## External CDN dependencies used by catalog source")
    L.append("")
    L.append("| Uses | Library URL |")
    L.append("|---|---|")
    for lib, n in sorted(libcount.items(), key=lambda kv: -kv[1]):
        L.append(f"| {n} | `{lib}` |")
    L.append("")

missing = [i for i in items if not i["title"] or not i["writes"]]
L.append("## Extraction audit")
L.append("")
L.append(f"- Pages parsed: **{len(items)}**")
L.append(f"- With a title: **{sum(1 for i in items if i['title'])}**")
L.append(f"- With a description: **{sum(1 for i in items if i['description'])}**")
L.append(f"- With an install command: **{sum(1 for i in items if i['install'])}**")
L.append(f"- With a declared output file: **{sum(1 for i in items if i['writes'])}**")
L.append(f"- With a variable schema: **{len(withvars)}** "
         f"({sum(1 for i in withvars if i.get('var_source') == 'VariablesExplorer')} "
         f"via the rendered VariablesExplorer, "
         f"{sum(1 for i in withvars if i.get('var_source') == 'data-composition-variables')} "
         f"declared ONLY on `<html data-composition-variables>` in source — "
         f"invisible on the rendered docs page)")
if missing:
    L.append(f"- ⚑ Incomplete extraction on **{len(missing)}**: "
             + ", ".join(f"`{i['slug']}`" for i in missing[:40]))
L.append("")

open(os.path.join(OUT, "catalog-index.md"), "w", encoding="utf-8").write("\n".join(L))

print(f"items={len(items)} blocks={len(blocks)} components={len(comps)} "
      f"with_vars={len(withvars)} incomplete={len(missing)}")
