---
type: spec
status: active
tags: [hfcat, pattern-library, catalog-index, hyperframes, video-gen, registry]
relatedTo: [video-gen, pattern-library]
---

# hfcat: index our own hand-rolled patterns

Spec from `seal` for `cougar`, 2026-08-27. Chris's ask: *"if we land a good hand
rolled pattern, couldn't we add to this registry for future hfcat calls?"*

Answer: yes, and there is exactly one thing that would break it.

---

## What exists, read not assumed

| Thing | Where |
|---|---|
| launcher | `hfcat` → `sh` shim, execs `C:/Python312/python.exe` |
| implementation | `$REPO/tools/hyperframes-fix/hfcat.py` |
| index | `Documents/video-gen/hyperframes-docs/reference/catalog-index.json` |

`hfcat.py:35` — `items = json.load(open(INDEX, encoding="utf-8"))["items"]`

The index top level is a dict with keys `count`, `blocks`, `components`,
`items`. 372 records. One record:

```json
{
  "slug": "ai-chat-reveal",
  "kind": "block",
  "title": "AI Chat Reveal",
  "description": "A question is typed on a rising keyboard, sent, and answered…",
  "install": "npx hyperframes add ai-chat-reveal",
  "writes": "compositions/ai-chat-reveal.html",
  "support_files": 2,
  "variables": [
    { "id": "botName", "type": "string", "role": "content",
      "label": "Assistant name", "description": "Title in the chat header.",
      "default": "Assistant" }
  ]
}
```

`hfcat.py:144` filters `pool` on `i["kind"] == a.type`, and `--type` is declared
at line 118 with `choices=["block", "component"]`.

⚑ `index-catalog.py` is referenced in hfcat's own help text as
`scratchpad/index-catalog.py` but I could not find it on disk under
`Documents/video-gen` or `C:/Users/Chris` at depth 4. Locate it before relying
on where the rebuild writes.

---

## THE THING THAT BREAKS IT

**`catalog-index.json` is REGENERATED from the mirrored docs.** hfcat's own help
says: *"Rebuild it with scratchpad/index-catalog.py after re-mirroring the
docs."*

Append our patterns to that file and the next re-mirror deletes every one of
them. Silently. Nobody finds out until `hfcat` stops returning them, and by then
the reason is three days back.

**So do not append to `catalog-index.json`.**

---

## The design

Two independent sources, concatenated at load.

| File | Owner | Rebuilt by |
|---|---|---|
| `hyperframes-docs/reference/catalog-index.json` | HyperFrames docs mirror | `index-catalog.py`, wipes and rewrites |
| `pattern-library/hfpat-index.json` | us | hand-written at G9, never auto-wiped |

`hfcat.py` `load()` reads both, concatenates, returns. A missing
`hfpat-index.json` is not an error — it returns the catalog alone, so the tool
still works on a machine that has no pattern library.

Second file, same top-level shape:

```json
{ "count": 1, "items": [ … ] }
```

## Two edits that come with it

**1. `kind` needs a third value.** `hfpat`, alongside `block` and `component`.
`hfcat.py:118` currently declares `choices=["block", "component"]`, so `--type
hfpat` is rejected today. Add it there. Without the third value our patterns
still appear in default searches (no `--type` means `pool = items`) but cannot
be filtered TO, which is the query worth having: *"what have WE built?"*

**2. `install` is a different string for ours.** Not `npx hyperframes add`.
Ours needs the junction plus the call:

```
mklink /J "<project>\pattern-library" "$REPO/pattern-library"
HFPat.orbitStage(tl, "#stage", { actors, duration })
```

`writes` should be the empty string or omitted — a pattern writes nothing, the
composition calls it.

## Fields worth adding for ours only

The catalog records carry no evidence, because a HyperFrames block does not have
any. Ours do, and it is the whole point of the library:

| Field | Value | Why |
|---|---|---|
| `provenance` | `"_38ybzeZ9i8 41.0-51.5s, circle fit rms 0.01px"` | which reference, which frames |
| `convergence` | `"0.570s vs 0.570s, within the instrument's 5.2% sd"` | G5's number |
| `approved` | `"2026-08-27"` | the date Chris said yes at G7 |
| `layouts` | `["standard", "mirror"]` | which G7b variations survived |

Print `provenance` and `convergence` in `--show`. A pattern the library cannot
account for should be visibly different from one it can.

## Where the record comes from

**Nothing new has to be written.** `/pattern-extract` G9 already produces every
field as a condition of codifying:

| G9 step | Field |
|---|---|
| `LIBRARY.md` row: name, what it is, provenance including convergence | `title`, `description`, `provenance`, `convergence` |
| `hfpat.js` builder signature and `opts` | `variables` |
| G7 approval | `approved` |
| G7b | `layouts` |

So codifying a pattern and indexing it become one action, not two. Better: make
the index the thing G9 writes, and generate the `LIBRARY.md` row FROM it, so the
two can never disagree. Today `LIBRARY.md` is prose that has already drifted
from `hfpat.js` three times in this project's ledger.

## Test it against the case that motivated it

`seal` hand-built `orbitStage` tonight without checking, and `hfcat` would have
found `radial-surround` and `locked-nucleus-orbit` in one second. After this
change, this query must return the new pattern:

```
hfcat --type hfpat re-dress stage swap contents
```

and it must survive a re-mirror of the docs. Prove the second one — re-run the
catalog rebuild and query again. A registry that has never survived a rebuild
has not been tested.
