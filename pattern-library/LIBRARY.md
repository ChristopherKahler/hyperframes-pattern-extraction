---
type: reference
status: active
tags: [hyperframes, motion-graphics, pattern-library, gsap, expdecay, counter-reel, drift-field, visual-regression]
relatedTo: [video-gen]
---

# HyperFrames Pattern Library

Reusable motion-graphic patterns for Chris AI Systems. Every pattern here shipped in a render that passed a native-resolution defect pass. Nothing is added until it has.

```
pattern-library/
  hfpat.js        the patterns, as parameterized GSAP builders
  tokens.css      the palette, type scale and component styles
  baselines/      regression references — READ THE WARNING BELOW
  LIBRARY.md      this file
```

## Start here

**Copy `example/index.html` into your project and edit it.** It is a complete,
renderable composition using every class and builder here, with layer order and
checker suppressions already correct. Do not assemble one from the call list
below — those selectors refer to markup, and the markup is in the example.

## Setup

```bash
npx hyperframes init my-video --example blank --non-interactive
```

`init` puts `index.html` at the **project root**, not in `compositions/`. That one
fact decides everything about paths.

**Paths must be root-relative. Parent traversal (`../`) is a hard lint error**, not
a warning. So put the library inside the project. **The junction MUST be named `pattern-library`** - `example/index.html` references that path verbatim:

```
mklink /J "my-video\pattern-library" "$REPO/pattern-library"
```

Then in `index.html`:

```html
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800&family=Inter+Tight:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="pattern-library/tokens.css">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="pattern-library/hfpat.js"></script>
```

Read the scaffold's own `CLAUDE.md` too. The framework contract — one `class="clip"`
wrapper with `data-start` / `data-duration`, timeline paused and registered on
`window.__timelines["main"]` — lives there, not here.

## Use

```js
HFPat.eases();
const tl = gsap.timeline({ paused: true });

HFPat.counterReel(tl, "#odo", { to: 256, at: 0.45 });
HFPat.riseIn(tl, ["#c3", "#c2", "#c1"], { at: 0.45 });
HFPat.driftField(tl, "#stack", { duration: 7 });
HFPat.copyIn(tl, "#caption", "#sub", { at: 2.25 });

window.__timelines["main"] = tl;
```

## Layer order

The classes compose exactly one way, back to front:

```
.hfp-field         ground gradient     (auto)
.hfp-field-stack   drifting cards      z-index: 2
.hfp-scrim         alpha gradient      z-index: 3
.hfp-fore          type rail           z-index: 5
```

## check gates the render, and two patterns fail it out of the box

`counterReel` digit strips and the tilted `.hfp-field-stack` both trip the layout
checker with false positives — deep overflow-hidden columns and rotated bounding
boxes. Suppress with `data-layout-allow-overflow` / `-overlap` / `-occlusion`.

- **Per-element, not per-subtree.** They must go on the exact flagged node.
- The reel strips **do not exist in your HTML** — set them in JS after the call:

```js
document.querySelectorAll("#odo .hfp-strip, #odo .hfp-strip span")
  .forEach(function (el) {
    el.setAttribute("data-layout-allow-overlap", "");
    el.setAttribute("data-layout-allow-overflow", "");
    el.setAttribute("data-layout-allow-occlusion", "");   // 3+ digits need this
  });
```

**Always apply all three.** An earlier version of this doc said 2-digit reels
needed only two attributes and that `allow-occlusion` was a 3-digit concern.
That was wrong, and a cold session disproved it: a 2-digit reel showing `89`
threw 7 `text_occluded` errors. The trigger is **where the strip lands**, not
how many digits there are — `89` parks the strips at -7224px / -15222px while
`47` parks them at -6192px / -14706px, leaving different numerals sitting
inside `.hfp-scrim`'s `inset: 0` box. Target value decides it, so there is no
digit count that is safe.

`.hfp-strip` also throws `escaped_container` and `container_overflow`. Both are
cleared by `allow-overflow`.

- `allow-occlusion` also drops that element from the **contrast** gate. Put it on
  `.hfp-who` / `.hfp-mini` / `.hfp-body`, never on `.hfp-card`, or you lose contrast
  coverage on all card text.

**The ROTATE-NULL TEST — do this before suppressing anything.**

Suppression hides a symptom and cannot tell you whether the finding was real.
This can, mechanically, with no eyeballing:

1. Temporarily set the rotated ancestor to `rotate(0deg)`.
2. Re-run `check`.
3. **Findings that vanish were bounding-box artefacts of the rotation.**
   **Findings that persist are real geometry — fix them, do not suppress them.**
4. Restore the rotation, then suppress only what step 3 cleared.

Then record the contrast score **before** suppressing (e.g. 140/140).
`allow-occlusion` removes those elements from the contrast gate, so the score
drops (e.g. to 49/49) and the evidence is gone unless captured first.

## What `check` cannot see at all

**`check` does not test card-over-card text occlusion.** Verified by stripping
every card suppression and re-running against a known-broken ordering: 12
findings, all documented false positives, **none** naming the real overlap. The
checker is blind to it suppressed or not, so a green `check` is not evidence
here.

Two defences, use both:

- **`riseIn` autoOrder** (on by default) sorts by resting position so the
  ordering cannot be got wrong by hand. It has been got wrong by hand twice.
- **`HFPat.guardMotion(cards, opts)`** computes the minimum inter-card gap
  across the entrance closed-form off `expDecay` and throws before a frame
  renders. It catches hand-set tops, which autoOrder cannot.

```js
HFPat.guardMotion(
  [{ top: 96, height: 259 }, { top: 396, height: 259 }, { top: 696, height: 259 }],
  { travel: 940, duration: 3.4, stagger: 0.28, at: 0.45 }
);
// correct order   -> returns 41  (min gap px)
// reversed order  -> throws "card 0 is covered by card 1 by 216px at t=1.01s"
```

Run `check` **before** `guard()`. `guard()` throws inside the browser, so its failure
surfaces as a runtime error during `check`, not as a layout finding.

## The example's numbers are tuned to the example's content

`example/index.html` is a starting point, not a preset. Two values must be
re-timed when your content differs, and neither is a library bug:

- **`counterReel` total = `duration + (digits-1) * stagger`.** The example's
  2.5 / 0.30 is fine at 2 digits; at 3 digits it consumes 3.12s of a 7s piece.
  A cold session retimed to 2.10 / 0.22 and that was correct.
- **`riseIn` at 4.4s** leaves cards ~123px low at t=2.3, because `expDecay`
  spends its tail on the last few pixels. If a region of frame must read as
  filled early, shorten it - 3.4s was right for a 7s piece.

## Card overlap: one kind is real

`check` reports card overlap from rotated bounding boxes, and those are false
positives. **One overlap is not.** If `riseIn` receives its array bottom-most
first, the top card starts last and trails the one below it by ~180px against a
51px gap — its body text is genuinely underneath for about a second. No
`data-layout-allow-*` fixes it because nothing is wrong with the layout; the
timing is wrong.

**Rule: pass the array TOP-MOST ON SCREEN FIRST.** Elements rise from below, so
one still travelling sits lower than rest and encroaches on the card beneath —
which is a later DOM sibling and paints on top. So the last to arrive must be
the card with nothing below it. Order top to bottom and every card lags into
empty space.

Before dismissing any overlap as a rotated-bbox artefact, scrub the 1:1 frames
across the entrance window. A real one is visible; an artefact is not.

## Vertical rhythm is content-dependent

The example's card tops (300 / 600 / 900) are a reference for the example's
content, not a grid. **Keep card bodies to a uniform line count.** One 1-line body among 2-line
bodies produced gaps of 41px and 83px in the same stack. Change digit count or
body line count and re-derive the pitch — at 4 digits with one-line bodies those tops push the bottom card
through the canvas edge, which breaks rule 4.

Two things the library does not yet answer, both currently guesses:
- Whether a unit label may sit **under** the number rather than beside it.
  At 4 digits a sibling label is pushed into the card stack, so under is
  sometimes the only option. Treat as allowed.
- Whether `.hfp-reel { width }` is safe to change. Sharp edge 3 couples height,
  font-size and mask stops but says nothing about width. **Leave width alone**
  until someone measures it.

## Three sharp edges

- **Any leading digit** inks right of the rail, because every tabular figure
  centres in the 172px cell. Measured ~25px for `1` and ~24.7px for `6` — it is
  not digit-specific. Measure your value and nudge, or accept it; it is optical,
  not a bug.
- `counterReel` calls `host.innerHTML = ""`. A unit label ("SECONDS") cannot live
  inside `.hfp-counter` — make it a sibling in a flex row.
- `copyIn` and `riseIn` animate `transform`. Never position their targets with
  `transform: translateY()`; use `padding` or `top`, or GSAP overwrites you.
- `.hfp-reel { height }`, `.hfp-strip span { font-size }` and the mask stops are one
  coupled set. Change one, re-check the others at 1:1 with the number **landed**,
  not mid-roll.

## Patterns

| Pattern | What it is | Provenance |
|---|---|---|
| `eases()` → **expDecay** | Exponential-decay ease, k=0.9/s | Measured off a studio-produced reference, frames 452-557 @25fps. Rebuild converged to **1.9% mean error** over a 249px travel |
| `counterReel` | Mechanical odometer, digits roll at different rates | Authored. Lower digits spin more — that is what makes it read as a drum, not a number swap |
| `riseIn` | Entrance from below, settles on expDecay, optional alternating tilt | Same measurement as expDecay |
| `driftField` | Slow linear background drift across the full duration | Fixes dead-still backgrounds, which read as broken in short pieces |
| `starPop` | Rating row, staggered with overshoot. Inline SVG, no network dep | Authored |
| `copyIn` | Headline then sub. Spacing only, no rule or underline | Authored |
| `guard` | Pre-render collision check on absolutely-positioned text | Built after a caption crushed its own subline by 29px |

## Rules the library encodes

These are not style preferences. Each one is a defect that shipped and was caught at 1:1.

1. **No borders, rules, underlines or hairlines.** Separate with space, scale and weight. Chris's standing preference, and the practical reason is stronger than the aesthetic one: three of the four defects in this library's history came from decoration nobody asked for.
2. **Mask with alpha, never with an opaque colour scrim.** A flat scrim over a gradient backdrop shows as rectangular seams. Use `mask-image`.
3. **Run `HFPat.guard()` before rendering.** Text collisions are geometry. `npm run check` does not catch them because they sit within tolerance.
4. **Never end an element flush to the canvas edge.** It reads as unfinished.
5. **Nothing static for more than ~2s** in a short piece.
6. **Determinism:** no `Date.now`, no `Math.random`, no fetch. HyperFrames renders by seeking a paused timeline.

## Adding a pattern

A pattern is admitted only after it has shipped in a render that passed the 1:1 defect pass. Then:

1. Add the builder to `hfpat.js` with a comment recording *where the numbers came from*. Measured beats invented; if it was authored, say so.
2. Add any component styles to `tokens.css`.
3. Add a row to the table above.
4. Capture a baseline (below).

## baselines/ — read this before using them

Baselines exist for **one purpose: catching silent visual regression.** Fonts load from a CDN, Chrome's rasterizer changes between versions, and `tokens.css` gets edited. In all three cases the code is unchanged, `check` passes, and the output quietly degrades. A stored frame is the only mechanism that catches that.

**They are deliberately NOT creative reference.** Do not open `baselines/` to decide what a new video should look like. The steelman against storing them is real and it is this: a pinned frame anchors every downstream session to one palette, one layout and one subject, and that anchoring is invisible because it looks like helpful context. The library's value is its *parameters*, which transfer to any subject. The baseline's value is a pixel comparison, which transfers to nothing.

So:

- **Machine comparison:** yes. Diff a new render of the same composition against its baseline.
- **"What should this look like?":** no. Design from the brief and the tokens.
- **Staleness:** a baseline that no longer matches intentional changes is worse than none, because it gets believed. Regenerate it in the same commit as the change that invalidated it, and record the date.

Each baseline directory holds a hero frame, the four 1:1 defect bands, and `BASELINE.md` naming the version, date, and what was verified.
