# Extraction Ledger

One row per `/pattern-extract` run. This measures the **process**, not the
output. Read it before starting a run.

`Cold rounds` is the headline number — how many child sessions it took before
one produced acceptable quality from the templates alone. It should trend to 1.

`Defects mine / Chris's` shows whether the G6 checklist catches what his eye
catches. A persistent gap means the checklist is missing an item.

| Date | Reference | Admitted | Cold rounds | Defects mine / Chris's | Root causes (child's words) | Template edits |
|---|---|---|---|---|---|---|
| 2026-08-27 | Extendly "Google Reviews on Autopilot" (truncated at 45.6s of 254s) | expDecay (measured, 1.9%); counterReel, riseIn, driftField, starPop, copyIn (authored) | **1 FAILED** (shipped with 5 workarounds) | 1 / 2 | see below | 5 fixes |
| 2026-08-27 | round 3, subject: quotes same day (89) | none new | **3 FAILED** (3 of 4 gaps were stale docs) | 0 / 0 | see below | 4 fixes |
| 2026-08-27 | round 4, no-shows recovered (1408), 4 digits | none new | **4 FAILED** (real riseIn bug) | 0 / 0 | ordering doc misdirected | 3 fixes |
| 2026-08-27 | round 5, after-hours calls (6), 1 digit | none new | **5 FAILED** (my round-4 fix was inverted) | 0 / 0 | see below | 5 fixes + enforcement |
| 2026-08-27 | round 2 vs fixed templates, subject: after-hours bookings (312) | none new | **2 FAILED** (5 refinements, 0 blockers) | 0 / 0 | see below | 5 fixes |
| 2026-08-27 | round 6, TWO briefs off one library: avg first response 4 min (restrained/editorial) + 2,140 revived (bold/high-energy) | none new | **1 PASSED** — both, first try | 1 / pending | see below | 7 logged, 1 fixed in-run |

## Gate retirement counters

Reset to zero the moment a retired gate lets a defect through to Chris.

| Gate | Criterion | Consecutive |
|---|---|---|
| G8a joint review | 5 runs where Chris finds nothing new | 0 |
| G8 cold test → single round | 5 runs passing cold first try | 1 |
| G7 per-pattern → batch approval | 10 approvals with no change requests | 0 |
| G5 convergence | never retires (automated, free) | — |
| G6 defect pass | never retires | — |


## Round 1 root causes — child's own words

Time split, measured by the child: **~60% workarounds / 40% building.**
Costliest single item: the layout checker — 6 `check` runs, 2 rejected fixes.

| # | Defect | Child's stated cause | Template fix |
|---|---|---|---|
| G1 | Documented import path `../pattern-library/` is invalid | "HyperFrames serves every composition with the **project root** as its base... parent traversal is a hard lint error" | Documented `mklink /J` junction + the fact that `init` puts `index.html` at root |
| G2 | Reel mask dissolves a **landed** number | "30%/70% against a 246px glyph in a 258px box leaves only 77.4px to 180.6px" | `tokens.css` → 13%/87%, arithmetic in the comment |
| G3 | `counterReel` + tilted stack fail `check` with 30 false positives | "`data-layout-allow-*` is **per-element, not per-subtree**" — found by grepping the CLI dist | Full section incl. the JS snippet for runtime-built strips and the contrast-coverage trap |
| G4 | `.hfp-grain` has no image | "The class supplies positioning, opacity and blend mode but no image" | Marked **Not shipped** in the pattern table |
| G5 | `starPop` unused | Not a gap — rule 1 told it what to do. Logged because the interview asked per item | none |

**The finding that mattered most** was not in the five. Asked what the library
lacked *entirely*, the child said: **a worked example.** Every selector in the
usage block referred to markup that existed nowhere, so the whole skeleton —
layer order, z-index between scrim and rail, card `top` spacing, the
`innerHTML=""` trap — was its to invent and its to get wrong.

Fix: `example/index.html` now ships as the starting point.

**Method notes worth keeping.** The child never opened `baselines/`, per the
warning. It ran the 1:1 pass on the encoded MP4 rather than browser snapshots,
and caught three defects invisible on the contact sheet. It measured PSNR
(36.55 dB) before concluding the dark ground was banding — it was fixed
RGB→yuv420p chroma cost, not bitrate. That is the standard.


## Round 2 root causes — child's own words

Built from `example/index.html`. **`check` passed 0 errors 0 warnings on the
first run** (round 1 opened at 30 errors). No skeleton invented, no CLI dist
grepped. The class of failure dropped from blockers to refinements.

| # | Gap | Cause | Template fix |
|---|---|---|---|
| 1 | Junction name contradiction | LIBRARY.md said `lib`, `example/index.html` referenced `pattern-library/` | Doc now names `pattern-library`, stated as mandatory |
| 2 | Suppression snippet is 2-digit-only | "a 3-DIGIT reel also throws `text_occluded` on individual numerals (columns up to 23,220px)" | `allow-occlusion` added, threshold documented |
| 3 | `counterReel` timing at 3 digits | "at the example's 2.5/0.30 it ate 3.12s of a 7s piece" | Formula `duration + (digits-1) x stagger` documented |
| 4 | `riseIn` 4.4s leaves frame empty | "cards 123px low at t=2.3 because expDecay spends its tail on the last pixels — the right 45% read empty for ~1.5s" | Warned; example numbers flagged as content-tuned |
| 5 | "verify before you silence" had no method | Instruction with no procedure | Its 4-step method adopted verbatim |

**Gap 5 is the one worth keeping.** The child invented the procedure the
instruction was missing: run `check` with zero suppressions, capture 1:1 bands
of every flagged region, **record the contrast score before suppressing**
(140/140 -> 49/49 after `allow-occlusion`), then suppress and comment what was
measured. Step 3 is what makes a suppression honest rather than merely quiet.

**Method notes.** Ran the 1:1 pass on the encoded MP4; PSNR 36.11 dB, worst in
blue — same yuv420p chroma cost round 1 independently measured at 36.55, not
banding. Corrected its own eye with measurement: judged an ink gap at 5px,
measured 17px tightest / 25px median on encoded pixels. Verified `driftField`
was alive rather than frozen by comparing tail PSNR (22.33 dB, 5.5-6.9s) against
a window where copy is known to animate.

**Verdict: not a pass.** Two rounds, two failures. Blockers are gone; the
remaining class is documentation precision.

---

## Round 3 — quotes sent same day (89), 2 digits

`check` 0/0 shipped, contrast 41/41 with **116/116 recorded pre-suppression**
per the method round 2 invented. Opened at 29 errors with zero suppressions,
all traced to the two documented false-positive families. Built from the example.

**Four gaps. Three were MY stale docs**, not design gaps — fixes made in earlier
rounds that were not propagated everywhere the thing was described.

| # | Gap | Cause |
|---|---|---|
| 1 | **My round-2 fix was wrong** | I wrote "3+ digits need allow-occlusion, two suffice at 2 digits". A 2-digit reel showing `89` threw 7 `text_occluded`. Trigger is **where the strip lands**: `89` parks at -7224/-15222, `47` at -6192/-14706, putting different numerals inside `.hfp-scrim`. No digit count is safe |
| 2 | Two undocumented finding types | `escaped_container` and `container_overflow` on `.hfp-strip`; `allow-overflow` clears both |
| 3 | Dead code in `example/index.html` | Overrode the reel mask to 13/87 with a comment claiming tokens.css ships 30/70 — it has shipped 13/87 since the round-1 fix |
| 4 | `hfpat.js` header | Still documented `../pattern-library/hfpat.js`, the exact parent traversal LIBRARY.md calls a hard lint error |

All four fixed. Fix 1 now states "always apply all three" with the landing-position
evidence, so the claim cannot be re-derived wrongly from a single sample.

**Four defects it found that no checker can see:** single-word orphans on two
card bodies; a card whose timestamps (11:52 PM enquiry, 9:15 AM quote)
**contradicted the same-day headline**; a bottom row echoing the sub's own words
61px below it; and a frozen first 0.20s from `counterReel at:0.20` over an empty
frame. The contradiction is the one that would have shipped — editorial
judgement, not a template gap.

Third independent measurement of the encode constant: 36.18 dB worst in blue,
against 36.55 (R1) and 36.11 (R2). Banding ruled out by 14x contrast stretch on
both the lossless browser frame and the mp4.

**Verdict: not a pass.** Three rounds, three failures — but the class fell from
blockers, to refinements, to documentation drift.


## Rounds 4-5 — and the end of the cold-test phase

**Round 4 (1408, 4 digits)** found a REAL bug: `riseIn`'s documented ordering
made the last card to arrive the one painted on top, so its body text sat
genuinely under its neighbour for ~1s. Three cold sessions had built with that
pattern and never hit it.

**Round 5 (6, 1 digit)** found that my round-4 FIX had inverted the rule. I had
originally written "top-most first", coldtest4 reframed it as z-paint-order, I
adopted the reframing because it sounded more rigorous, and it was wrong. Round
5 caught it in one round. **The library was correct before I "fixed" it.**

### The finding that changed the approach

`check` **does not test card-over-card text occlusion at all.** Proven by
stripping every card suppression and re-running against the known-broken
ordering: 12 findings, all documented false positives, none naming the real
overlap. Suppressed or not, the checker is blind. A green `check` is not
evidence for this class.

That means no gate can catch a regression here, which raised ordering from a
convenience to load-bearing — and prompted the switch from documenting rules to
**enforcing them in code**.

### Rules converted from prose to code

| Was documented | Now enforced |
|---|---|
| `duration + (n-1) x stagger` eats the budget | `counterReel` derives timing from `opts.budget` |
| "always apply all three suppressions" | `counterReel` sets them on every strip and span it builds |
| "any leading digit inks right of the rail" | `opticalAlign` (opt-in) measures the real landing glyph via Range rect |
| "order top-most first" | `riseIn` autoOrder sorts by resting position |
| "300/600/900 is content-tuned" | `HFPat.cardPitch` measures heights and distributes |
| nothing — this class was undetectable | `HFPat.guardMotion` computes min inter-card gap closed-form and throws |
| "suppress the false positives" | **ROTATE-NULL TEST**: set the ancestor to `rotate(0deg)`, re-run `check`; findings that vanish were artefacts, findings that persist are real |

`guardMotion` verified: correct order returns min gap 41px; reversed throws
"card 0 is covered by card 1 by 216px at t=1.01s".

### Reviewer mode

Chris's call after round 5: stop spawning cold children, keep one seasoned
session as standing reviewer. It is burned for portability testing but has
found **four** of my errors — the ordering inversion plus three separate
defects in `opticalAlign`, including that I probed span index 0, which is
always the glyph `0` and never the digit that lands.

**Five rounds, five failures, five distinct classes, no repeats.** The blockers
went first, then the refinements, then my own stale docs, then a real pattern
bug, then my own bad fix.

---

## Round 6 — the first pass, and what it did not prove

Two children, spawned blind and simultaneously off the **enforced** library,
given deliberately different creative directions:

| Child | Subject | Brief | Result |
|---|---|---|---|
| `heron` | average first response cut to 4 minutes | restrained, editorial, negative space | clean — I found nothing it missed |
| `coldtest6b` | 2,140 dead leads revived in 30 days | bold, high-energy, dense | one hero-number defect |

**Both shipped a publishable 7s render in one round with zero blockers.** Five
previous rounds produced five failures. This is the first pass.

### The three gaps BOTH found, independently

Two blind sessions converging on the same gap is the strongest signal this
project has produced. Neither could see the other's work.

| # | Gap | Why it survived five rounds |
|---|---|---|
| 1 | `cardPitch`'s box argument is **stack-space, not canvas-space** | `height` defaults to 1080 (the canvas) but cards live in `.hfp-field-stack` — 1700px tall at `top:-180`. Defaults write tops into the mask fade. The **enforced** path has no worked example; `example/index.html` never calls `cardPitch` |
| 2 | **ROTATE-NULL TEST misclassifies the scrim family** | The test separates *rotation* artefacts from everything else, not artefacts from real defects. The `.hfp-scrim` `text_occluded` findings persist at `rotate(0)`, and step 3 says persisting findings are real geometry — so read literally it forbids the suppression the example itself ships, and sends the reader hunting a defect that is not there |
| 3 | The example's stated **reason** for that suppression is wrong | It claims the gradient hits zero alpha at 1113px so nothing is painted over cards at x=1060 — but 1060 < 1113, so the conclusion contradicts its own numbers. `coldtest6b` measured it properly: the 95deg gradient line is 2006.8px, zero alpha at 1164px along it, leaving card 1 under 9.0% alpha and card 2 under 2.3%. **The suppression is correct; the justification is not.** The honest one is the 96/96 contrast pass recorded pre-suppression |

`heron` ranked gap 2 as the costlier of the three: a literal reading of the rotate-null test sends you hunting a defect that does not exist, where gap 3 only costs you the derivation.

Fix 2 needs a second null test — set `.hfp-scrim{background:none}` and re-run;
findings that clear were scrim artefacts, findings that persist have a real
card-over-card component underneath. Call it SCRIM-NULL.

### The defect at 1:1

`coldtest6b`'s hero number. Ink runs measured on the delivered mp4 at t=6.8:

    2  [gap 20]  ,  [gap 3]  1  [46]  4  [47]  0

The comma sits 20px off the `2` and 3px off the `1`, jammed into the 1's foot
serif. It reads as `2 ,1 4 0`. `check` was green — no gate sees comma spacing.

**Fixed and verified.** The child re-measured over the full glyph height,
found its own error, and refixed: margins now sum to -24 rather than -40, split
-8/-16. I re-measured the re-delivered encode independently — comma ink moved
from `20px / 3px` to `21px / 18px`. The collision is gone; `check` still 0/0,
contrast 57/57.

**Gap 7, from that exchange:** LIBRARY.md must say **measure ink over the FULL
glyph height.** A cap-height band silently drops foot serifs and descenders, and
it is invisible because the numbers that come back look plausible. Bricolage's
`1` carries a foot serif 122px wide against a 71px stem — a band chosen to
exclude the comma excluded the widest part of the very digit being spaced
against. `hfpat.js` records this same failure three times for `opticalAlign`:
**measuring a box that is not the ink.**

Two of the child's own numbers did **not** reproduce against the file it
shipped: it reported the comma at 21/20px, and reported a 101px ink hole from a
narrow `1`. Measured, the inter-digit gaps are a uniform 46/47px and the `1`
inks 122px wide — it has a foot serif in this face. **A child's measurement is
evidence, not a fact.** Re-measure on the delivered artefact before recording.

**Three instances of one bug shape in a single round**, all "threshold catches
the background too": my type-to-edge probe measured the full-bleed gradient
ground; `coldtest6b`'s cap-height band dropped the foot serif it was spacing
against; and its number-to-card clearance probe scanned from x=900 at green>58
where the field gradient itself reaches g=69, so it returned the scan boundary
rather than a card edge. The real clearance is analytic — number ink ends at
825, card 1's rotated top-left corner is at 996, so 171px.

**A probe against a gradient needs a threshold the gradient cannot reach, or it
is measuring its own scan window.** Self-audit numbers from the same run that
DID hold: rail alignment 140/141/142/141/141/140, card gaps 30/30/31.

### What the pass did NOT prove

Both renders came out as **the same slide**: eyebrow top-left, giant number
beneath it, headline, cards stacked right at the same -7deg tilt, same palette,
same type pairing. The left rail measured **141px in both, at every timestamp
sampled**.

The only real variance was energy — `coldtest6b` ran 2.4x the frame-to-frame
change (diff mean 2.595 vs 1.063) with 3 cards against 2. That is content
volume, not creative direction.

**Portability is solved. Variety is not.** A library that produces one
composition regardless of brief cannot fill five minutes without reading as one
template, and no gate in this pipeline measures that. Cold tests ask *can a
fresh session reproduce the quality* — they have never asked *can two sessions
produce different work*. Running two briefs at once is what surfaced it, and it
should be how every future cold test runs.

### Method note

The first attempt to measure type-to-edge thresholded on "differs from the
corner colour" and reported OFF-CANVAS on every frame of both renders. It was
measuring the full-bleed gradient ground, which covers the whole canvas by
design — **a convenient proxy instead of the real quantity**, the same bug shape
`marlin` flagged in REVIEW.md. Thresholding on luminance instead (type is bone
at luma 240, ground is 25) made the ground drop out regardless of the gradient.

`coldtest6b` diagnosed its own discrepancy without prompting: its digit runs came from a cap-height band (y195-300) chosen to exclude the comma, which misses the `1`'s foot serif — the glyph's widest feature. Both its 71px `1` and its 101px hole were artefacts of that band. **Choosing a measurement window to exclude one thing silently excludes others.** Measure over the full glyph height, then mask what you meant to drop.

