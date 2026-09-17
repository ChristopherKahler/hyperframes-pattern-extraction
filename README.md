# HyperFrames Pattern Extraction Kit

Turn a video you admire into **reusable, parameterised motion patterns** you can
build new videos out of — without the result reading as a clone of the original.

You point the pipeline at a reference video. It watches the whole thing at a
resolution where defects are actually visible, measures the motion numerically,
fits each movement to a curve, rebuilds it in HyperFrames from the *numbers*
(never the reference's content), proves the rebuild converges on the original
within a stated error, and only then asks a human to approve it. Approved
patterns get codified into a library that other sessions build from.

The point is the **measurement**, not the imitation. A pattern enters the library
as `expDecay(k=0.9/s)`, not as "that cool bouncy thing PayCloud does".

---

## What's in here

```
commands/           The pipeline itself, as agent playbooks (slash commands)
  pattern-extract.md    the 12-gate extraction pipeline — the main event
  watch-video.md        how to actually SEE a video (frames, cuts, 1:1 crops)
  breakdown-reel.md     decode a swiped social video's editing style
  wordsrt.md            word-level timestamps for frame-accurate anchoring

tools/
  watch-video/        watch.py, motion.py, fit-ease.py, reel.py
  pattern-factory/    factory.py, codify.py + the child-session briefs
  hyperframes-fix/    hfcat.py (catalog search), docs mirror, Windows fixes

catalog/reference/  The HyperFrames catalog indexes hfcat queries
                    372 items (154 blocks + 218 components) + guides

pattern-library/    The output of all of the above
  hfpat.js            7 codified GSAP builders
  tokens.css          palette, type scale, component styles
  LIBRARY.md          how to consume it — READ THIS FIRST when building
  LEDGER.md           every extraction run and what it cost
  PENDING.md          patterns awaiting human approval
  baselines/          stored frames for catching silent visual regression

bin/                hfcat launchers (put this dir on PATH)
hooks/              hfcat-nudge.py — makes an agent remember the catalog exists
docs/               PLAYBOOK.md, FFMPEG-LEVERS.md, catalog/index spec
```

## Start here

1. **[SETUP.md](SETUP.md)** — install every tool. Written so an AI agent can
   execute it top to bottom on a fresh machine.
2. **[AGENT-GUIDE.md](AGENT-GUIDE.md)** — what to tell your AI. Every tool, what
   it is for, and which one to reach for when.
3. **[pattern-library/LIBRARY.md](pattern-library/LIBRARY.md)** — read before
   building anything with the library.

## The one-line version

```bash
# see a video properly
python tools/watch-video/watch.py "<video or URL>" --note "what I'm looking at"

# search 379 ready-made blocks/components/patterns before hand-building anything
hfcat "counter"

# run the full extraction pipeline (in an AI session, with commands/ installed)
/pattern-extract <video> "the thing that caught my eye"
```

## The rules that make it work

These are not style preferences. Each one is on the record because skipping it
produced a measured failure.

- **A contact sheet is not looking at the video.** A 470px cell is a 24%
  thumbnail of a 1920px frame; a 29px caption collision is invisible there and
  glaring at 1:1. Every run opens every native-resolution `defect_*.jpg` first.
- **Watch all of what was named.** Never narrow a request to a shorter window to
  save time or tokens. An inaccurate read costs more to correct than the full
  pass ever costs to run.
- **The reference's subject never enters the library.** Only parameters transfer.
  Copy the palette, the copy or the concept and you have built a clone.
- **Nothing is codified without an explicit human yes** (gate G7) **and a cold
  session reproducing it from the templates alone** (gate G8). This session
  succeeding proves nothing about whether the pattern is portable.
- **When a session misreads a rule, make the rule impossible to get wrong.**
  Rewording is the same failure with better prose. Convert it to a derived
  parameter, a runtime assertion, or a guard that throws.
- **Every timing claim cites a frame number or a CSV row.** No prose timings.

## Status

7 patterns codified, all from a single reference. 4 more sit in `PENDING.md`
awaiting approval. `LEDGER.md` records what each run cost, including the root
causes from the cold-session interviews — read it before a run rather than
rediscovering the same tedium.

The highest-transfer asset in the library is **`expDecay`**: an exponential-decay
ease, k=0.9/s, measured off a reference at 25fps and rebuilt to **1.9% mean error
over a 249px travel**. Stock GSAP power/expo eases do not match it, and the
difference is visible.

## Licence and provenance

The pipeline, the tooling and `hfpat.js` are original work. The
`catalog/reference/` indexes describe the upstream
[HyperFrames](https://www.npmjs.com/package/hyperframes) catalog and are
included so `hfcat` works from a clone; the full HyperFrames documentation
mirror is **not** redistributed here — generate it locally with
`tools/hyperframes-fix/mirror-docs.ps1`.
