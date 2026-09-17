---
type: doc
status: active
tags: [pattern-library, pending-verification, hfpat-index, video-gen, register]
relatedTo: [video-gen, pattern-library, hfpat-index-g9-authoring]
---

# PENDING — extracted, self-verified, awaiting Chris

Chris, 2026-08-29: *"have our own file for our own blocks and patterns to register
things to so as you extract and verify yourself, add them to a markdown file so that
when I VERIFY THEM they can be ready to fold easily into our personal json file that
sits next to hfcat core file."*

**Nothing enters `hfpat-index.json` or `hfpat.js` from here without his VERIFIED.**

One block per pattern. Each block carries the exact `hfpat-index.json` row, the
`LIBRARY.md` table row, and where the draft builder + renders live. Fold with:

```
python $REPO/tools/pattern-factory/codify.py --fold <slug>
```

which moves the row into the index, appends the builder to `hfpat.js`, regenerates
the LIBRARY.md table, writes `baselines/<slug>/`, appends the LEDGER row, and marks
the block below as FOLDED with the date.

Verdict vocabulary Chris uses on the reel: **yes** / **no** / **change: <what>**.
Anything short of "yes" stays here.

---

<!-- blocks are appended below by codify.py --register; do not hand-edit rows -->

## elbowConnect — PENDING  (child: px-connect, 2026-08-29)

mechanism: Right-angle routing only, never a diagonal. The corners are ROUNDED at a fixed radius, the route is a dog-leg (leave the source horizontally, cross on a vertical leg, enter the target horizontally), each wire strokes itself on from its source, siblings are staggered, and a filled dot sits at the source terminal. One grammar in four structurally unrelated scenes.

reference: _38ybzeZ9i8 @ [[17.5, 26.9], [30.0, 35.5], [36.0, 39.0], [60.0, 63.5]]; power1.out 0.465 s, rms 1.32%

renders: `<run>/children\px-connect\renders\elbowConnect-standard.mp4` · `<run>/children\px-connect\renders\elbowConnect-mirror.mp4`

G5 final: 3.06% (rounds: 3) · G6: 0 errors 0 warnings; lint 0/0, runtime 0/0, layout 0 issues across 9 samples, motion 0/0, contrast 56/56 WCAG AA · hfcat: hand-build: no catalog item routes between two measured anchors. The closest (hw-pipeline) is the opposite aesthetic and would have to be discarded entirely.

draft: `<run>/children\px-connect\drafts\elbowConnect.js` · provenance: `<run>/children\px-connect\provenance\elbowConnect.json`

```json
{
  "slug": "elbowConnect",
  "kind": "hfpat",
  "title": "Elbow connector with rounded corners and a source terminal dot",
  "description": "Right-angle routing only, never a diagonal. The corners are ROUNDED at a fixed radius, the route is a dog-leg (leave the source horizontally, cross on a vertical leg, enter the target horizontally), each wire strokes itself on from its source, siblings are staggered, and a filled dot sits at the source terminal. One grammar in four structurally unrelated scenes.",
  "install": "HFPat.elbowConnect(tl, el, opts)",
  "writes": "",
  "source": "$REPO/pattern-library\\hfpat.js",
  "enforced": [
    "duration is derived from route length at a measured speed, so a long wire and a short one draw at the same visible pace",
    "the exit point of each route is derived and ordered by target y, so sibling wires cannot stack or cross",
    "the terminal dot is sized from the stroke (4.4x) and pushed clear of the node by its own radius, so it can never render as a semicircle",
    "elbowConnect and guardWires share ONE plan() function, so the guard can never be checking different geometry from what is drawn",
    "guardWires throws before render on: corner arcs that cannot fit the leg, sibling verticals too close with overlapping spans, a route crossing a node it does not connect, a route crossing measured type INK, and any route leaving the canvas",
    "a block whose ink cannot be measured throws rather than passing quietly",
    "guardWires asserts, given the timeline, that every terminal dot sits at its anchor at its first visible frame AND at its landing — proven by reintroducing the original bug, which makes it throw '1092px from its anchor'"
  ],
  "layouts": [
    "standard",
    "mirror"
  ],
  "provenance": "_38ybzeZ9i8 @ [[17.5, 26.9], [30.0, 35.5], [36.0, 39.0], [60.0, 63.5]]; power1.out 0.465 s, rms 1.32%",
  "convergence": "3.06% after 3 rounds",
  "approved": null
}
```

LIBRARY row: | `elbowConnect` | Right-angle routing only, never a diagonal. The corners are ROUNDED at a fixed radius, the route is a dog-leg (leave the source horizontally, cross on a vertical leg, enter the target horizontally), each wire strokes itself on from its source, siblings are staggered, and a filled dot sits at the source terminal. One grammar in four structurally unrelated scenes. | _38ybzeZ9i8 @ [[17.5, 26.9], [30.0, 35.5], [36.0, 39.0], [60.0, 63.5]]; power1.out 0.465 s, rms 1.32%; convergence 3.06% after 3 rounds |

<!-- codify:meta {"_child": "<run>/\children\\px-connect", "_draft": "<run>/\children\\px-connect\\drafts\\elbowConnect.js", "_renders": {"standard": "<run>/\children\\px-connect\\renders\\elbowConnect-standard.mp4", "mirror": "<run>/\children\\px-connect\\renders\\elbowConnect-mirror.mp4"}, "_provenance_file": "<run>/\children\\px-connect\\provenance\\elbowConnect.json", "_hfcat": "hand-build: no catalog item routes between two measured anchors. The closest (hw-pipeline) is the opposite aesthetic and would have to be discarded entirely.", "_registered": "2026-08-29T22:03:13"} -->

## orbitStage — PENDING  (child: px-orbit, 2026-08-29)

mechanism: A dashed ring with a hub derived from it and actors placed at measured angles. Rotation is PER ACTOR, not per assembly: some actors are pinned for whole scenes while others ride the ring, each at its own linear rate. The whole stage contracts ~1%/s continuously so the frame never freezes. Actors may sit on the ring or on the centre disc rim. The stage owns the ground light it sits in.

reference: _38ybzeZ9i8 @ [[42.0, 50.9]]; linear (riders and contraction); expDecay (entrance, authored timing) 9.0 s, rms 0.25%

renders: `<run>/children\px-orbit\renders\orbitStage-standard.mp4` · `<run>/children\px-orbit\renders\orbitStage-mirror.mp4`

G5 final: 2.36% (rounds: 3) · G6: lint 0/0, runtime 0/0, layout 0 issues across 9 samples, motion 0/0 · hfcat: hand-build: no catalog item places actors at measured angles, distinguishes pinned from riding, or carries a per-actor rate

draft: `<run>/children\px-orbit\drafts\orbitStage.js` · provenance: `<run>/children\px-orbit\provenance\orbitStage.json`

```json
{
  "slug": "orbitStage",
  "kind": "hfpat",
  "title": "Orbit stage",
  "description": "A dashed ring with a hub derived from it and actors placed at measured angles. Rotation is PER ACTOR, not per assembly: some actors are pinned for whole scenes while others ride the ring, each at its own linear rate. The whole stage contracts ~1%/s continuously so the frame never freezes. Actors may sit on the ring or on the centre disc rim. The stage owns the ground light it sits in.",
  "install": "HFPat.orbitStage(tl, el, opts)",
  "writes": "",
  "source": "$REPO/pattern-library\\hfpat.js",
  "enforced": "guardOrbit throws before rendering on: actors off-canvas or overlapping at rest, at the contracted scale AND in the RE-SOLVED arrangement; a rider crossing a pinned actor mid-sweep (closed-form on the ring, sampled for disc-rim satellites so it is not right by accident); and measured type resting on a disc at every point of every sweep and every scale, with the block rect scaled about the stage centre because the caption rides the stage. The builder DERIVES the hub diameter, actor sizes, slot positions, each slot transform-origin, the label block, and the caption position and scale from the ring radius, so the composition CSS carries no geometry to drift out of step. It asserts that a travelling ground layer is bled wider than its own travel. reDress reads the stage that orbitStage wrote off host.__hfpOrbit and throws if it is absent, and refuses to re-solve a slot that is not one of that stage actors.",
  "layouts": [
    "standard",
    "mirror"
  ],
  "provenance": "_38ybzeZ9i8 @ [[42.0, 50.9]]; linear (riders and contraction); expDecay (entrance, authored timing) 9.0 s, rms 0.25%",
  "convergence": "2.36% after 3 rounds",
  "approved": null
}
```

LIBRARY row: | `orbitStage` | A dashed ring with a hub derived from it and actors placed at measured angles. Rotation is PER ACTOR, not per assembly: some actors are pinned for whole scenes while others ride the ring, each at its own linear rate. The whole stage contracts ~1%/s continuously so the frame never freezes. Actors may sit on the ring or on the centre disc rim. The stage owns the ground light it sits in. | _38ybzeZ9i8 @ [[42.0, 50.9]]; linear (riders and contraction); expDecay (entrance, authored timing) 9.0 s, rms 0.25%; convergence 2.36% after 3 rounds |

<!-- codify:meta {"_child": "<run>/\children\\px-orbit", "_draft": "<run>/\children\\px-orbit\\drafts\\orbitStage.js", "_renders": {"standard": "<run>/\children\\px-orbit\\renders\\orbitStage-standard.mp4", "mirror": "<run>/\children\\px-orbit\\renders\\orbitStage-mirror.mp4"}, "_provenance_file": "<run>/\children\\px-orbit\\provenance\\orbitStage.json", "_hfcat": "hand-build: no catalog item places actors at measured angles, distinguishes pinned from riding, or carries a per-actor rate", "_registered": "2026-08-29T22:03:15"} -->

## reDress — PENDING  (child: px-orbit, 2026-08-29)

mechanism: Change the subject without clearing the frame. NOT a cross-fade: the outgoing dressing TRANSLATES UP and is clipped away by its own container, the frame holds bare for one frame, and the incoming dressing RISES IN from below - while the stage re-solves underneath it (uniform x1.092 scale on expo.inOut, slots snapping from irregular angles to cardinal, disc-rim satellites leaving on their own faster window, the ground light stepping back to the stage centre). Two entirely different topics share one geometry and no transition is spent.

reference: _38ybzeZ9i8 @ [[45.5, 46.5]]; power4.in exit + power1.inOut entrance (was: power1.inOut cross-fade) 0.576 s, rms 3.92%

renders: `<run>/children\px-orbit\renders\reDress-standard.mp4` · `<run>/children\px-orbit\renders\reDress-mirror.mp4`

G5 final: 6.62% (rounds: 6) · G6: lint 0/0, runtime 0/0, layout 0 issues across 9 samples, motion 0/0 · hfcat: hand-build: every catalog hit is a transition, and this pattern value is that it is not one

draft: `<run>/children\px-orbit\drafts\orbitStage.js` · provenance: `<run>/children\px-orbit\provenance\reDress.json`

```json
{
  "slug": "reDress",
  "kind": "hfpat",
  "title": "Re-dressed stage",
  "description": "Change the subject without clearing the frame. NOT a cross-fade: the outgoing dressing TRANSLATES UP and is clipped away by its own container, the frame holds bare for one frame, and the incoming dressing RISES IN from below - while the stage re-solves underneath it (uniform x1.092 scale on expo.inOut, slots snapping from irregular angles to cardinal, disc-rim satellites leaving on their own faster window, the ground light stepping back to the stage centre). Two entirely different topics share one geometry and no transition is spent.",
  "install": "HFPat.reDress(tl, el, opts)",
  "writes": "",
  "source": "$REPO/pattern-library\\hfpat.js",
  "enforced": "The travel a dressing needs is DERIVED from the box that clips it - the builder walks up to the nearest ancestor whose overflow is not visible, measures the INK with a Range rather than the element rect, and moves the dressing exactly far enough to clear it. A dressing with no clipping ancestor gets a short rise and a fade instead, detected rather than declared. The stage re-solve start is computed from the transition own midpoint, so the two cannot be lined up wrongly. The re-solve reads host.__hfpOrbit and throws if orbitStage has not run, and throws if resolve.angles names an element that is not one of that stage actors. Nothing is ever parked outside its clip - immediateRender:false on the incoming set, and the outgoing set returns to y=0 at opacity 0 the instant it clears - which is a check finding converted rather than suppressed.",
  "layouts": [
    "standard",
    "mirror"
  ],
  "provenance": "_38ybzeZ9i8 @ [[45.5, 46.5]]; power4.in exit + power1.inOut entrance (was: power1.inOut cross-fade) 0.576 s, rms 3.92%",
  "convergence": "6.62% after 6 rounds",
  "approved": null
}
```

LIBRARY row: | `reDress` | Change the subject without clearing the frame. NOT a cross-fade: the outgoing dressing TRANSLATES UP and is clipped away by its own container, the frame holds bare for one frame, and the incoming dressing RISES IN from below - while the stage re-solves underneath it (uniform x1.092 scale on expo.inOut, slots snapping from irregular angles to cardinal, disc-rim satellites leaving on their own faster window, the ground light stepping back to the stage centre). Two entirely different topics share one geometry and no transition is spent. | _38ybzeZ9i8 @ [[45.5, 46.5]]; power4.in exit + power1.inOut entrance (was: power1.inOut cross-fade) 0.576 s, rms 3.92%; convergence 6.62% after 6 rounds |

<!-- codify:meta {"_child": "<run>/\children\\px-orbit", "_draft": "<run>/\children\\px-orbit\\drafts\\orbitStage.js", "_renders": {"standard": "<run>/\children\\px-orbit\\renders\\reDress-standard.mp4", "mirror": "<run>/\children\\px-orbit\\renders\\reDress-mirror.mp4"}, "_provenance_file": "<run>/\children\\px-orbit\\provenance\\reDress.json", "_hfcat": "hand-build: every catalog hit is a transition, and this pattern value is that it is not one", "_registered": "2026-08-29T22:03:16"} -->

## packetRide — PENDING  (child: px-connect, 2026-08-29)

mechanism: An arc ripple fires at the source node about half a second early; a payload disc carrying a line-art glyph spawns at the node's edge, travels the connector at a CONSTANT speed, and the wire flashes to the accent colour behind it and relaxes back to its resting colour once the packet is ~100px past.

reference: _38ybzeZ9i8 @ [[21.0, 22.0], [60.0, 63.5]]; travel: none (linear) 360 px/s, rms 0.14%; ripple: expDecay(k=4.12) 0.266 s, rms 1.0%

renders: `<run>/children\px-connect\renders\packetRide-standard.mp4` · `<run>/children\px-connect\renders\packetRide-mirror.mp4`

G5 final: 2.57% (rounds: 2) · G6: 0 errors 0 warnings; lint 0/0, runtime 0/0, layout 0 issues across 9 samples, motion 0/0, contrast 56/56 WCAG AA · hfcat: hand-build: no catalog item carries a payload along a caller-derived route, and none lights the route behind it. The miss is on record.

draft: `<run>/children\px-connect\drafts\packetRide.js` · provenance: `<run>/children\px-connect\provenance\packetRide.json`

```json
{
  "slug": "packetRide",
  "kind": "hfpat",
  "title": "Payload rides a connector, lighting the wire behind it",
  "description": "An arc ripple fires at the source node about half a second early; a payload disc carrying a line-art glyph spawns at the node's edge, travels the connector at a CONSTANT speed, and the wire flashes to the accent colour behind it and relaxes back to its resting colour once the packet is ~100px past.",
  "install": "HFPat.packetRide(tl, el, opts)",
  "writes": "",
  "source": "$REPO/pattern-library\\hfpat.js",
  "enforced": [
    "packetRide refuses to run if elbowConnect has not built a wire on that host, rather than inventing a path — one owner for the geometry",
    "travel duration is derived from the real path length via getTotalLength at the measured speed, never hand-set",
    "the lit trail's tween duration is derived as dur*(1+trail/L) so its leading edge tracks the packet by construction rather than by a tuned number",
    "the trail's dash pattern hides itself at both ends, so no opacity keyframes are needed and there is nothing whose result depends on which side of a `set` you seek to",
    "the payload is positioned off getPointAtLength — pure geometry, no layout reads at render time, so any seek lands identically",
    "the ripple grows by the `r` attribute rather than by scale, so no transform-origin can displace it"
  ],
  "layouts": [
    "standard",
    "mirror"
  ],
  "provenance": "_38ybzeZ9i8 @ [[21.0, 22.0], [60.0, 63.5]]; travel: none (linear) 360 px/s, rms 0.14%; ripple: expDecay(k=4.12) 0.266 s, rms 1.0%",
  "convergence": "2.57% after 2 rounds",
  "approved": null
}
```

LIBRARY row: | `packetRide` | An arc ripple fires at the source node about half a second early; a payload disc carrying a line-art glyph spawns at the node's edge, travels the connector at a CONSTANT speed, and the wire flashes to the accent colour behind it and relaxes back to its resting colour once the packet is ~100px past. | _38ybzeZ9i8 @ [[21.0, 22.0], [60.0, 63.5]]; travel: none (linear) 360 px/s, rms 0.14%; ripple: expDecay(k=4.12) 0.266 s, rms 1.0%; convergence 2.57% after 2 rounds |

<!-- codify:meta {"_child": "<run>/\children\\px-connect", "_draft": "<run>/\children\\px-connect\\drafts\\packetRide.js", "_renders": {"standard": "<run>/\children\\px-connect\\renders\\packetRide-standard.mp4", "mirror": "<run>/\children\\px-connect\\renders\\packetRide-mirror.mp4"}, "_provenance_file": "<run>/\children\\px-connect\\provenance\\packetRide.json", "_hfcat": "hand-build: no catalog item carries a payload along a caller-derived route, and none lights the route behind it. The miss is on record.", "_registered": "2026-08-29T22:04:44"} -->
