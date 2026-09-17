---
description: Extraction pipeline — turn a reference video Chris likes into library patterns. Calls /watch-video to see it, measures each pattern, rebuilds it in HyperFrames, renders it for Chris to approve, and only codifies what he approves into the pattern library templates.
---

# /pattern-extract

`$ARGUMENTS` = path or URL to the reference video, plus any note about what caught his eye.

This is the **extraction pipeline**. It is not a watching tool — it *calls* one.

| Layer | Owns |
|---|---|
| `/watch-video` (`watch.py`) | seeing a video: frames, cuts, motion numbers, 1:1 defect crops |
| **`/pattern-extract`** (this) | turning what was seen into approved, codified library patterns |
| `pattern-library/` | the templates every admitted pattern must fit |

**Nothing enters the library without Chris seeing a rendered replication and saying yes.** G7 is a hard stop.

Detect patterns without asking which to look for. He wants to see what is found unprompted.

---

## Watching video — WATCH ALL OF IT

**When Chris names a video, or names a section of one, watch the whole of what
he named.** Every frame extracted, every contact sheet opened, every 1:1 defect
crop opened. Not a sample.

Never do any of these to save time or context:

- fetch a short window when he named the video
- invent a `--from/--to` range he did not ask for
- open sheet 4 of 15 and reason about the rest
- skip the native-resolution defect crops
- summarise a video from its cuts table instead of looking at it

**Token cost and context budget are NOT constraints on video digestion.** Chris
has stated this explicitly and repeatedly. Being conservative here does not save
him anything — it produces an inaccurate read, and he then spends more of his
own context and time correcting it than the full pass would ever have cost.

If a range is genuinely needed, **he names it.** Do not narrow his ask yourself.

---

## G0 — See it

Call the watching tool. Do not reimplement it.

```bash
python $REPO/tools/watch-video/watch.py "<video>" --note "reference: <name>"
```

Open every `defect_*.jpg` first, then the sheets. Verify the unique-frame count; 1-2 means the source is static or truncated — stop and say so.

## G1 — Candidate list

From `motion.csv` and the sheets, name each distinct pattern with its frame range. Expect 5-10 on a real reference.

A candidate qualifies only if it is **reusable across subjects**. "Blue gradient with a phone" is not a pattern. "Element rises and settles on an exponential ease" is.

## G2 — Measure

Numbers, not impressions.

```bash
python $REPO/tools/watch-video/motion.py <frames> --fps <F> --roi X0,Y0,X1,Y1 --stride N
```

- Entrances/exits: travel, duration, easing family, decay constant.
- Transitions: duration in **ms** from elevated-`diff` frame count, plus curve shape.
- Continuous motion: speed px/frame, direction, path class.
- Repeats: compare diff profiles frame by frame. Near-identical tails mean **one asset reused**, not two similar effects.

Below ~0.3 px/frame classification is noise. Say so instead of guessing.

## G3 — Fit to the template shape

Every library pattern is a builder with this signature:

```js
HFPat.<name>(tl, selectorOrElement, opts)   // returns HFPat, chainable
```

So the measurement has to become `opts`. Fit the curve rather than reaching for a stock ease:

```
normalized remaining at 25/50/75% → solve k → ease = (1-exp(-k*p))/(1-exp(-k))
```

Decide the parameters a future caller must control (duration, travel, count, stagger, `at`) and which are internal. Name the closest CSS/GSAP equivalent and how close it is.

## G4 — Rebuild in HyperFrames

Author it in a scratch project using `hfpat.js` + `tokens.css`, with **generic content**. Rebuild from the *numbers*. Never copy the reference's palette, copy, or subject — that is how a library becomes a clone.

Run `HFPat.guard()` before rendering. Run `npm run check`.

## G5 — Converge  ← automated gate

Render, run the same `motion.py` over rebuild and reference, diff at **matched elapsed time** (not percentiles of detected frames — different absolute times, meaningless comparison).

| Mean error | Action |
|---|---|
| ≤5% | proceed to G6 |
| 5-15% | adjust parameters, re-run |
| >15% | classification is wrong, not the parameters — back to G2 |

Record the number; it goes in the provenance row.

## G6 — Defect pass at 1:1  ← automated gate

Open every `defect_*.jpg` from the rebuild:

- [ ] `guard()` clean, nothing flush to a canvas edge
- [ ] no borders, rules, underlines, hairlines
- [ ] masks are alpha, never opaque colour scrims over a gradient
- [ ] no glyph clipping, no rotated corners off-canvas
- [ ] nothing static beyond ~2s
- [ ] `check` contrast passes

Any failure: fix, re-render, re-check. Never present a render with a known defect.

## G7 — Chris approves  ← HARD STOP, human gate

Send him the rendered replication:

```
SendUserFile: <scratch>/.watch/vNNN/render.mp4
```

State in the message: what the pattern is, the measured parameters, the G5 convergence number, and anything known-open.

Then **stop**. Do not write to `pattern-library/`. Do not partially admit. Do not treat silence, a topic change, or a general compliment about the session as approval.

| He says | Do |
|---|---|
| "this looks great" / "make it into the library" / explicit yes | proceed to G8 |
| any change request | apply it, re-render, return to G6, present again |
| nothing yet | hold — the pattern stays out of the library |

If several patterns came out of one reference, present them one at a time and get a verdict on each. Approval of one is not approval of the batch.

## G8 — Cold-session reproduction  ← GATE, and the one that matters most

Chris approving *this* session's render only proves this session can do it. The
library is worthless if the next session cannot reproduce the quality from the
templates alone. So before codifying, prove it.

Spawn a child with **no hints beyond what Chris would naturally say**:

```python
payload = {"side": "win", "cwd": "<scratch dir>", "title": "coldtest",
           "project": "video-gen", "parent": "<your codename>",
           "prompt": "Build a short motion graphic using the pattern library at "
                     "$REPO/pattern-library. Read "
                     "LIBRARY.md first and follow it. Subject: <adjacent topic>. "
                     "Render it, check the output, fix anything wrong, then send "
                     "me the mp4 with SendUserFile. Ping <codename> when done "
                     "with anything in the library that was unclear."}
# POST http://127.0.0.1:7799/api/spawn
```

**Who judges.** You do — and your standing comes from G7. Chris approved *your*
render, so your eye is calibrated to the bar he accepted. That calibration is
the whole reason this gate sits in the extracting session rather than anywhere
else. A session whose output he never signed off on has no business grading a
child's.

Rules for the cold test:

- **Different subject, same patterns.** If the child needs the reference's
  content to succeed, the pattern is not a pattern.
- **No coaching mid-run.** Do not send it the answer. Every question it has to
  ask is a hole in the templates.
- **Judge its render at 1:1**, same defect pass as your own.

## G7b — LAYOUT VARIATIONS  <- new stage, Chris 2026-08-27

Before a pattern is codified, produce **two layouts of it: `standard` and `mirror`.**

Chris's call, 2026-08-27: *"maybe we just get consistency on standard and mirror. Those
seem pretty much the easier ones to really get consistent. And we get two variations per
pattern, that's enough to not just come across as pure template."*

Two, not one to three. The vertical axis was built, rendered and cut: `invert` broke and
`mirrorInvert` was rejected on sight. Consistency across two beats coverage across four.
Chris adds variation alts himself over time as the library grows.

**Why this gate exists.** Two cold sessions given deliberately opposite creative briefs
produced the SAME SLIDE: left rail 141px in both, number top-left, cards right, identical
tilt. The library was portable and had no variety. A motion-feel axis was built first and
Chris killed it on sight: *"The slight speed adjustments are NOT noticeable by a human.
A true variation is a design variation of the same concept."*

**A variation moves the design, not the timing.** Same content, same concept, different
arrangement. His examples: a horizontal flip; a reversed build with the number bottom-left
and the cards entering from the top.

### The rule that makes mirroring work

**Swap positions, never flip pixels.** `transform: scaleX(-1)` mirrors the type and every
word reads backwards. The rail moves to the opposite edge, the field moves across, the
tilt inverts its sign, and the type is never transformed.

Vertical follows the same discipline: nothing rotates. The anchor changes and entrance
travel changes sign, so a rise becomes a fall with every glyph upright.

### What must move with the layout

A composition is **not** "a rail and a field". Measured failures from the first build:

| Failure | Cause |
|---|---|
| Mirrored cards went ghost | The scrim is a one-sided gradient. Move the cards and they land under the dark half. **The mask must follow the layout.** |
| Inverted number collided with the headline | The rail moved to the bottom, straight through the copy. **Anchors must be re-solved, not just re-assigned.** |
| Only the number mirrored | Headline and sub were separate elements outside the named rail. **Every placed element must be enumerated.** |

### Verdicts on record

Rendered from one file, one line differing:

| Variation | Chris's verdict |
|---|---|
| standard | good |
| mirror | good |
| invert | **broken** |
| mirrorInvert | **awkward, rejected** |

Two of four survived. That ratio is normal and it is why the gate caps at three: a
variation that does not survive his eye is not a variation.

### The gate

- Produce BOTH layouts per admitted pattern: standard and mirror
- Render each from ONE file with a single differing line, so any difference is the
  variation and nothing else
- Show Chris a still grid before clips
- **Only variations he approves are codified.** A rejected one is deleted, not tuned

**Target: 5-10 patterns x 2 layouts.** That is enough to fill a full video without it
reading as one template.

---

### G8a — Joint review

Judge it, then hand it to Chris and let him judge it too. Two passes catch
different things: yours is systematic against the checklist, his is instant and
catches what reads wrong. Neither alone has been sufficient in practice.

Send the child's render, state the defects you found, and ask what he sees that
you did not. **Merge both lists before the interview** — the interview questions
are built from the combined list, not yours alone.

**ONE cold run, not rounds.** The cold session is a **gap finder**, not a
scoreboard. Do not re-spawn children chasing a clean pass — five rounds on the
first library produced five distinct failure classes and never a pass, because
each fresh session probes somewhere new. That is the instrument working, not a
signal to keep rolling.

Harvest every gap from the one run, then iterate here:

| Outcome | Action |
|---|---|
| Any gap, of any severity | take it to G8b, then **convert it to code** (below) |
| Clean render with zero gaps | proceed to G9 |
| Cannot produce a render at all | the pattern is not portable; do not codify |

### G8c — Convert every gap to code  ← STANDING REQUIREMENT

**When a session misreads a rule, make the rule impossible to get wrong. Never
just reword it.** Rewording is the same failure with better prose, and it will
fail again. Chris made this a requirement on 2026-08-27, after four of five
cold failures turned out to be misread or stale documentation rather than
design gaps.

For each gap, ask: **can this be computed, derived, measured, or asserted
instead of read?**

| Gap shape | Conversion |
|---|---|
| A formula in prose | a parameter the builder derives from (`opts.budget`) |
| "always remember to apply X" | the builder applies X to nodes it creates |
| A value someone must measure | measure it at runtime |
| An ordering someone must respect | derive the order, ignore what was passed |
| Hand-tuned numbers that break on new content | measure and distribute |
| A class no gate can catch | a `guard*` that throws before rendering |

If it genuinely cannot be enforced, say why in one line beside the prose. **A
rule that survives only because someone read carefully is a rule waiting to
fail.**

Then iterate: convert, re-verify with the reviewer, convert the next. The loop
runs over the gap list, not over fresh children.

### G8d — Fallback: measured iteration, for what cannot be enforced

Some rules resist one-shot enforcement. `opticalAlign` failed three times
because every available API measures the advance box, not the ink, and no
canvas API exposes `font-variant-numeric` — so a correct runtime computation
does not exist. When that happens, do **not** ship a fourth guess and do not
demote the rule back to prose. Run a measured loop.

**The protocol:**

1. **Land in the ballpark** with whatever the code can do honestly.
2. **Measure the result** against the real artefact — rendered pixels, not
   intent. An eyeball here turns the loop into repeated guessing.
3. **State the tolerance and the instrument's resolution** before starting.
   Hand pixel reads carry roughly plus or minus 3px; you cannot converge below
   your instrument.
4. **Adjust, re-measure, repeat** until inside tolerance or the delta stops
   moving.
5. **Record the landed value with its provenance** — what was measured, with
   what, and the error bars. A measured constant with provenance is a first-
   class result; `expDecay` is one, at 1.9% convergence.
6. **Stop condition is mandatory.** Inside tolerance, or two passes with no
   improvement. Without one this loop runs forever and looks like progress.

**When the loop itself can be automated, automate the loop rather than the
rule.** The correct fix for `opticalAlign` is a one-off script that renders
each digit and alpha-scans the leftmost inked column — that is exactly the
manual measuring process, run once, emitted as a table.

**If neither is possible**, remove the code, write the three things a future
attempt needs — what was tried, what it measured, why it was the wrong box —
and give the reference values with error bars. Silence invites a fourth guess.

### G8b — Interview the child before touching the template

When its render has defects, **do not diagnose the template yourself.** You
would be inferring which instruction was ambiguous. The child is the only thing
in the loop with the causal answer: it read the template and produced the
defect. Ask it.

Keep it alive and ping directed questions, one round, tied to the specific
defects you found:

```
base relay ping --to coldtest --from <codename> --msg "Judged your render. Found: <defect list>.
Not asking you to fix it. Tell me, per defect:
 1. which line of LIBRARY.md or hfpat.js did you act on
 2. what did you take it to mean
 3. what did you have to decide with no guidance at all
 4. what did you look for and not find"
```

Then rewrite the template so the answer to (3) and (4) is stated outright, and
so (2) can only be read one way. Quote the child's own wording in the fix where
it is clearer than yours — it is the evidence of how the text actually reads to
someone with no context.

Rules:

- **Ask before editing.** A template fix that skips the interview is a guess.
- **One interview per cold run.** Do not turn it into a coaching channel.
- **The next cold test uses a fresh child**, never the interviewed one — it now
  knows things the template does not say.
- Log each fix as: defect → child's stated cause → template change.

## G9 — Codify into the templates

Only after an explicit yes AND a passing cold test. Follow the library's shapes exactly:

1. **`hfpat.js`** — add the builder. Comment must record where the numbers came from and the G5 error. Measured beats invented; if authored, say so. Obey determinism: no `Date.now`, no `Math.random`, no fetch, pure `fromTo`.
2. **`tokens.css`** — add component styles under the `.hfp-` prefix, using the existing custom properties. No borders.
3. **`LIBRARY.md`** — one row in the pattern table: name, what it is, provenance including convergence.
4. **`baselines/<pattern>/`** — hero frame, four 1:1 defect bands, and `BASELINE.md` naming version, date, renderer and font versions, what was verified, what is known-open.

## G10 — Report

One table: pattern, measured parameters, convergence %, verdict. Name anything detected but not admitted and why. Held patterns stay listed so they can be revisited.

## G11 — Log the run so the process can improve

The library gets better because patterns accumulate. **The process only gets
better if it is measured**, and a render is not a measurement of the process.

Append one row to `pattern-library/LEDGER.md` per extraction:

| Date | Reference | Patterns admitted | Cold rounds to pass | Defects: mine / Chris's | Root causes | Template edits |
|---|---|---|---|---|---|---|

- **Cold rounds to pass** is the headline number. It is how tedious this was.
- **Defects mine / Chris's** shows whether the checklist is catching what his eye
  catches. A persistent gap means the checklist is missing an item — add it.
- **Root causes** come from the G8b interview, in the child's words.

### Retiring gates on evidence

Gates come off when the data says so, never because the process feels mature.

| Retire | Only after |
|---|---|
| G8a joint review | 5 consecutive runs where Chris finds nothing you missed |
| G8 cold test to one round | 5 consecutive runs passing cold on the first try |
| G7 per-pattern approval → batch approval | 10 consecutive approvals with no change requests |
| G5 convergence check | never — it is automated and costs nothing |
| G6 defect pass | never — it is the reason quality holds |

If a retired gate is followed by a defect reaching Chris, it goes straight back
on and the counter resets to zero.

### Watch for these, they are the tedium

The ledger exists to surface them, so read it before each run rather than
re-discovering them:

- The same root cause appearing twice means the template edit did not take.
  Rewrite it differently; do not add a second sentence beside the first.
- A pattern re-measured from a new reference that already exists in the library
  under another name — merge instead of admitting a duplicate.
- Anything Chris requests in G7 that was already stated in `LIBRARY.md` — that
  is a discoverability problem, not a content one. Move it, do not restate it.

---

## Standing rules

- **`/watch-video` is a called tool.** This pipeline never reimplements seeing.
- **G7 is not optional and cannot be inferred.** Only an explicit yes from Chris admits a pattern.
- **Detect, don't ask** which patterns to pull.
- **Every timing claim cites a frame number or CSV row.** No prose timings.
- **The reference's subject never enters the library.** Only parameters transfer.
- **Baselines are regression references, never creative reference** — see the warning in `LIBRARY.md`.
- **A pattern is portable or it is not.** Cold-session reproduction is the proof; this session succeeding is not.
- **Admitted or not.** No provisional entries; a library nobody trusts is worse than a small one.
