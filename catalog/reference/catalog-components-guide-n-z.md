---
type: reference
status: active
tags: [hyperframes, catalog, components, routing-taxonomy, video-gen, docs-mirror, motion-primitives]
relatedTo: [video-gen, hyperframes, hyperframes-docs-mirror, hyperframes-guides]
---

# Catalog components N–Z — routing taxonomy

Source: `pages/catalog/components/`, entries **108–218 of 218** alphabetically
(`native-notification-pop` → `zoom-through-transition`). **111/111 read in full.**
Companion to the a–m half held by `hf-sdk`; the halves do not overlap.

## What this file is for

`reference/catalog-index.md` already carries name, slug, description, install command,
output path, and variable schema for every item — none of that is repeated here. This
file answers the question the index cannot: **given a job, which of these do I reach for,
and how is it different from the three that sound identical?** Everything below is read
from each component's own source HTML/CSS/JS, not from its blurb.

---

# 0. Read this first — the three facts that decide everything

## 0.1 There are two incompatible integration models in this catalog

This is the single most important routing fact, and the index does not surface it.

| | **Self-driving mountable** | **Paste-snippet** |
|---|---|---|
| Count in N–Z | **71** | **40** |
| How it ships | A whole sub-composition. Registers its own paused timeline via `window.__timelines["<slug>"]` | Markup + CSS + a script that only *styles*. **No timeline is registered** |
| How you use it | Host mounts it: `data-composition-id="<slug>" data-composition-src="compositions/components/<slug>.html"` | You paste it inline and **write the GSAP tweens yourself** from the "timeline integration note" at the bottom of the file |
| How you configure it | `data-variable-values='{...}'` on the host element, read at runtime through `window.__hyperframes.getVariables()` | CSS custom properties the pasted script writes, plus editing the timeline recipe |
| Sizing | Elastic. `#root` is `position:absolute; inset:0; container-type:size`, **no `data-width`/`data-height`** — the host owns the box | Whatever you paste it into |
| Timing | Declares a formal **IN / HOLD / OUT envelope** (see §0.2) | None. Your timeline is the timing |

**If you mount a paste-snippet expecting motion, you get a static finished pose.** The
docs record this happening: `zoom-through-transition`'s own header says it "previously
shipped as a fragment whose only executable timeline lived in demo.html, so an installed
copy rendered the finished pose and never moved." It was converted to a mountable; the
other 40 were not.

**The 40 paste-snippets in N–Z:**
`number-pop-in`, `number-wheel`, `onboarding-stepper-flow`, `page-slide`, `panel-reveal`,
`parallax-unzoom`, `parallax-zoom`, `per-word-crossfade`, `perspective-marquee`,
`rgb-glitch-text`, `separator`, `settings-toggle-flow`, `shared-axis-y`, `shared-axis-z`,
`sheet-spring-up`, `shimmer-sweep`, `signup-flow`, `simulated-cursor`, `skeleton-reveal`,
`slot-machine-roll`, `soft-blur-in`, `spotlight-card`, `stagger-lattice`,
`staggered-fade-up`, `streaming-text`, `strikethrough-replace`, `success-check`,
`svg-line-draw-loader`, `tabs-slide-indicator`, `terminal-simulator`, `text-stagger`,
`text-state-swap`, `three-orbiting-cards`, `tilt-card`, `top-down-letters`, `tracking-in`,
`typewriter`, `typing-indicator`, `vignette`, `x-follow-card`.

Everything else in N–Z is a self-driving mountable. (The four `yt-*` items register a
timeline only to drive their own self-preview — see §0.3.)

## 0.2 The envelope contract, and what "elastic" actually constrains

Every self-driving mountable declares the same three-phase shape in its header comment:

```
IN_BASE  = <fixed seconds>   the authored entrance
HOLD     = max(0, D - (IN_BASE + OUT_BASE))   ELASTIC — the only stretchable phase
OUT_BASE = <fixed seconds>   the authored departure
If D < IN_BASE + OUT_BASE, IN and OUT scale down together and HOLD becomes zero.
```

Three consequences you will hit:

- **A longer host clip does not slow the motion down.** It lengthens the still hold. The
  phrase "never `gsap.timeScale()`" appears verbatim across the family. If you want the
  entrance itself slower, you need a different component or a source edit.
- **Give the host clip at least `IN_BASE + OUT_BASE`** or the entrance compresses. The
  longest IN phases in N–Z: `wordmark-tiles` **4.80s**, `whiteboard-ink` **3.55s**,
  `ticker-takeover` **3.15s**, `stop-motion-cadence` **3.0s**, `tracing-beam` **3.0s**,
  `particle-image-reveal` / `particle-text-dissolve` **2.80s**, `stitched-text-draw`
  ~**3.2s**, `stagger-cascade` **2.40s**, `pull-back-reveal` **2.40s**.
- **`exit: "none"` is the default nearly everywhere**, and it means OUT = 0s: the final
  frame holds until the clip cuts. The recurring rationale is "frame roots own
  transitions; holds end films." Set `exit` to `fade`/`up` only when the component itself
  should leave.

Many also declare **sync points** (fixed offsets inside IN, guaranteed never to drift into
the elastic HOLD) — the frame to hang a sound effect or a cut on.

## 0.3 Four `yt-*` items are helper libraries, not components

`yt-camera-move`, `yt-circle-pointer`, `yt-feather-highlight`, `yt-screen-warp` install
**global functions you call into your own timeline**, and their headers are wiring notes
rather than component descriptions. The exported API, read from source:

```
window.ytCameraMove   window.ytCameraReset   window.ytDefocusPulse
window.ytCircleOn     window.ytCircleOff     window.ytCountIn     window.ytCountdown
window.ytHighlightIn  window.ytHighlightTo   window.ytHighlightOut
window.ytScreenOn     window.ytScreenOff
```

Usage shape (from `yt-camera-move`'s own comment):

```js
ytCameraMove(tl, "#video-wrap", 5.0, { zoom: 0.11, slideY: -24 });
ytDefocusPulse(tl, "#yt-my-defocus", 5.0, 1.2);
ytCameraReset(tl, "#video-wrap", 9.0);
```

They target **any wrapper you already have** — including a `<video>` wrapper — which makes
them the only things in N–Z designed to operate on your footage rather than render their
own content. Reach for these over `push-in` / `ui-focus-zoom` when the thing being moved
is existing media rather than a component's own scene.

---

# 1. External and runtime dependencies

## 1.1 GSAP — 68 of 111 load it themselves

68 components carry `<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js">`.
**That is the only GSAP URL and the only pinned version in this half.** If you install
several components into one composition you will get duplicate GSAP tags; dedupe to one.

**No component in N–Z calls `gsap.registerPlugin`.** Several headers carry a shared
boilerplate line — *"MotionPath examples require GSAP MotionPathPlugin. Three.js examples
expose a render(progress) adapter"* — on `stagger-lattice`, `svg-line-draw-loader`, and
`three-orbiting-cards`. **For the first two that sentence is inherited boilerplate that
does not describe the file**: neither loads Three.js nor registers a plugin. Do not
provision MotionPathPlugin for them. ⚑ Verified by grepping each `## Source` block for
`registerPlugin`, `new THREE.`, and `three.module.js`. [5/5]

**Two components use no GSAP at all** — pure CSS custom properties you animate however you
like: `number-wheel`, `tracking-in`.

## 1.2 The only second CDN dependency in the whole half

`three-orbiting-cards` is alone in pulling a second library, as an ES module:

```js
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.184.0/build/three.module.js";
```

It is the only WebGL component in N–Z. It exposes a `render(progress)` adapter instead of
a free-running `requestAnimationFrame` loop, which is what makes it seekable. Budget for
a `<script type="module">` and a real GPU path before choosing it.

## 1.3 The only component that needs installed binary assets

`texture-mask-text` ships **66 texture masks as PNG files** that install to
`assets/texture-mask-text/masks/` and are referenced by project-root URL. Everything else
in N–Z is self-contained HTML/CSS/JS. If you copy this one between projects by hand, copy
the mask directory too or every class silently renders an unmasked block.

## 1.4 Canvas-2D painters — 6 components

`ordered-dither-pass`, `particle-image-reveal`, `particle-text-dissolve`,
`segmentation-flood`, `slit-scan-reveal`, `soft-blob-touch`.

All six follow one stated "canvas 2D law": a table is computed **once** at mount from a
**fixed LCG seed**, and every painted frame is a pure function of `(that table, timeline
time)` — `onUpdate` clears and redraws from scratch, with no `Math.random`, no wall clock,
no incremental state, no `requestAnimationFrame`. The named seeds are literal constants in
source: `particle-image-reveal` `0x50a71c1e`, `particle-text-dissolve` `0x9d1550f7`,
`segmentation-flood` `0x5e6f100d`, `slit-scan-reveal` `0x51175c4e`, `soft-blob-touch`
`0x50f7b10b`, `stitched-text-draw` `0x57174c3d`, `scramble-reveal` `0x27c0ffee`.

Cost: these are the expensive ones. They redraw the entire field per frame.

## 1.5 Web fonts

Only two components declare a font dependency, both for the same reason — the font *is*
the mechanic:

- `variable-axis-type` — needs a variable font exposing `wght`/`wdth`, with a font-ready gate.
- `variable-font-flex` — **pins Roboto Flex Variable** via Fontsource
  (`@fontsource-variable/roboto-flex@5.2.8`, latin standard subset). Its header explains
  the choice: *"Inter var was considered per the spec but Inter carries NO wdth axis."* It
  deliberately does **not** ride `--font-display`, because a theme font without matching
  axes would kill the effect. **Overriding the project font here breaks the component.**

## 1.6 Sound: components dispatch cues, none play audio

Ten components dispatch a bubbling `hf:sfx` `CustomEvent` carrying an id and a fixed
offset, for a scene's mix stage to catch and route. Every one states "this primitive never
plays audio." In N–Z: `native-notification-pop` (`notification-pop`),
`notification-pileup` (`notification-soft`), `pull-to-refresh` (`refresh-commit`,
`refresh-settle`), `split-tilt-cards` (`badge-pop-soft`), `stagger-cascade`,
`toggle-flip` (`click-soft`), `vector-editor-rig` (`vector-close`), `whip-pan-cut`
(`whip-cut`), `wordmark-tiles`, `oversized-cursor` (click tap).

If you want the sound, you wire a listener. Installing the component gives you the timing,
not the audio.

## 1.7 Two token systems, and they are not interchangeable

Most components paint from the **composition contract tokens**: `--brand`, `--accent`,
`--accent-2`, `--bg`, `--surface`, `--fg`, `--muted`, `--border`, `--radius`,
`--font-display`, `--font-body`, `--font-mono`, `--space-*`. In these, the near-universal
`accent` variable is a *token selector*, not a color: **green → `--brand`, blue →
`--accent`, violet → `--accent-2`.** Set the token, not the component, to rebrand.

**Eight components instead ride the `--hf-ui-*` "Operator Black" design system** — a
separate, much larger token set (`--hf-ui-surface`, `--hf-ui-text`, `--hf-ui-border`,
`--hf-ui-accent`, `--hf-ui-duration-*`, `--hf-ui-ease-*`, `--hf-ui-space-*`,
`--hf-ui-weight-*`, and a five-slot `--hf-ui-data-*` chart ramp):

`onboarding-stepper-flow`, `separator`, `settings-toggle-flow`, `sheet-spring-up`,
`signup-flow`, `simulated-cursor`, `streaming-text`, `typing-indicator`.

**They will not pick up your `--brand`/`--accent` palette.** Mixing the two families in one
frame gives you two visual systems unless you map the tokens yourself. This is the reason
those components report 35–38 distinct hex colors while contract-token components report
0–9.

---

# 2. The taxonomy — grouped by the job, not the alphabet

Legend per entry: **`M`** self-driving mountable · **`P`** paste-snippet (you write the
timeline) · **`H`** helper library · **`slot`** accepts your content · **`sfx`** dispatches
`hf:sfx` · **`canvas`** canvas-2D painter · **`3d`** CSS 3D transforms · **`ob`** Operator
Black `--hf-ui-*` tokens.

---

## 2.1 Type reveals — a line of text arrives

The most crowded shelf in the catalog. They differ by **what unit moves** and **whether
they are mountable**.

| Component | | Reach for this when |
|---|---|---|
| `per-word-rise` | M | Words (or chars, via `split`) rise blur-to-sharp and **you need per-unit landing cues**. The only one here taking a `cues` list. Default of the shelf. |
| `per-word-crossfade` | P | Same idea, calm keynote register, and you want it inline in a scene you already time. |
| `staggered-fade-up` | P | You need a **direction** (up/down/left/right), not just a rise. |
| `shared-axis-y` | P | A *swap* between two states along Y, not an entrance. Material-style shared-axis. |
| `shared-axis-z` | P | The same swap along Z (scale 0.72→1) — for focus/context depth rather than sequence. |
| `top-down-letters` | P | Per-**letter** staircase drop with **zero blur** — crisper and more mechanical than the rest of the shelf. |
| `tracking-in` | P | Letter-spacing is the reveal. **No GSAP** — you drive one CSS variable. |
| `soft-blur-in` | P | Not text-specific: add a class to **any element** for an opacity+blur+lift reveal. The generic member of this family. |

**Near-duplicate warning — `per-word-rise` vs `per-word-crossfade` vs `staggered-fade-up`
vs `text-stagger`:** all four rise words through a blur. `per-word-rise` is the only
**mountable** one (envelope + cues + `exit`); `staggered-fade-up` adds direction;
`text-stagger` adds a shimmer pass on top of the rise; `per-word-crossfade` is the plainest.
If you are mounting into a clip, take `per-word-rise`; if you are hand-timing inline, take
whichever of the other three has the extra you need.

---

## 2.2 Typing and streaming — text that writes itself

Four components, and the docs disambiguate them **in their own source**.

| Component | | Reach for this when |
|---|---|---|
| `typed-prompt` | M | A **bare prompt line** types itself. The richest: chunked human cadence, blinking caret on integer sine cycles, per-word `cues`, and a `correction` variable that types a typo, backspaces it, and retypes the real word. |
| `notes-typing` | M | The **notes-app confession as a whole scene** — bold title plus body paragraphs, caret jumping down between them. |
| `typewriter` | P | An **even, mechanical** char-by-char reveal with a caret (`line`/`block`/`none`). Deliberately not human-rhythmed. |
| `streaming-text` | P `ob` | **An AI answer, not a typewriter.** Words arrive in uneven bursts on a gap table measured from real streamed-answer footage, each landing grey and inking to full colour over 0.27s. |

`notes-typing`'s header states the routing outright: *"For a bare prompt line typing
itself, use typed-prompt; for an even mechanical reveal, use typewriter."*
`streaming-text` states its own: *"This is not a typewriter. A typewriter is even; an AI
answer arrives in bursts."*

Both `typed-prompt` and `telemetry-hud` share one stated mechanic — the **"typed-prompt
law"**: every visible frame is read from a text-at-time lookup table built synchronously
before the timeline registers, so nothing is incremental and reverse seeks are exact.

---

## 2.3 Text effects — the line is already there, something happens to it

| Component | | Reach for this when |
|---|---|---|
| `scramble-reveal` | M | Hacker-style glyph lock, left to right. Deterministic (seed `0x27c0ffee`), with an optional `terminal` frame. |
| `rgb-glitch-text` | P | Red/cyan chromatic tear on a short word. Offsets are **zero at rest**, so it only reads while the timeline runs. |
| `scan-band` | M | One **diagonal band** sweeps across a clean wordmark; the split exists only inside the band. Quieter and more deliberate than `rgb-glitch-text`. |
| `text-shimmer` | M | One specular band crosses a **fixed** headline. No entrance, no exit, no scale — the text is clean before and after. |
| `shimmer-sweep` | P | The same idea as a **reusable class** you can put on any element, configured by `--shimmer-color` / `--shimmer-width` / `--shimmer-angle`. |
| `strikethrough-replace` | P | Strike the old words, reveal the replacement. The `origin` variable only reads *while* the strike draws. |
| `text-state-swap` | P | Swap one label for another (outgoing blurs up, incoming lifts in) — no strike. The "Saving draft" → "Saved" beat. |
| `vox-annotate` | M | A keyword inside a held sentence gets a hand-drawn marker **plus** a connector drawn up to a mono callout label — one choreographed beat, not three. Four marker styles. |
| `variable-axis-type` | M | Emphasis by morphing **one** variable-font axis (`wght` or `wdth`). No position, opacity, or scale animation. |
| `variable-font-flex` | M | Per-character weight **and** width flex with optical size compensation, so ink swells while the box holds. Pins its own font. |
| `texture-mask-text` | P | Letterforms with holes cut through them by a real material texture. 66 masks; needs installed PNGs. |
| `stitched-text-draw` | M | Text drawn as **thread stitches** from a single-stroke alphabet, with a leading needle and per-letter thread-tail overshoot. |
| `wordmark-tiles` | M | A wordmark **resolves out of colour-noise tiles** through a spatially modulated wave. Broadcast/signage register. |
| `particle-text-dissolve` | M `canvas` | Text assembles **from** a particle cloud, or dissolves **to** one. Targets sampled from the rendered text bitmap at mount. |
| `slot-machine-roll` | P | Characters land by rolling a vertical reel. For a *result* (`A7K`), not prose. |
| `ticker-takeover` | M | A ticker rolls through candidate words, **locks one** with an accent flash, then promotes it to a full-frame headline. |
| `type-match-cut` | M | The headline **splits** vertically and an incoming panel grows out of the negative space and takes the frame. A transition disguised as a text effect. |

**`shimmer-sweep` vs `text-shimmer`:** same optical idea. `text-shimmer` is a mountable
that owns its own headline and timing; `shimmer-sweep` is a class you attach to something
you already have. **`scan-band` vs `rgb-glitch-text`:** both split colour channels;
`scan-band` confines the damage to a travelling diagonal band and keeps the rest clean.

---

## 2.4 Titlecards, lockups and wordmarks

| Component | | Reach for this when |
|---|---|---|
| `titlecard-lockup` | M | The full breather card: optional kicker, wordmark settling on **one** restrained move, a hairline rule drawing left to right, a mono label under it. Its stated payload is low motion — *"the stillness is the confidence."* |
| `titlecard-calm` | M | The same restraint with **only** kicker + headline. No rule, no label, no accent. Take this when `titlecard-lockup` has more furniture than you need. |
| `svg-mask-reveal` | M | The wordmark is a **window** — a soft band sweeps a token fill through the glyphs. Use a path-based sibling when exact brand outlines matter more than editable text. |
| `svg-stroke-trace` | M | An authored SVG path draws from its measured length. Closed paths get a restrained fill; open paths stay stroke-only, which keeps signatures and waves clean. |
| `outline-draw` | M | A rounded outline draws clockwise **around existing content** — a true hollow centre via two excluded masks, and it never intercepts pointer input. Mount it *over* something. |
| `store-badge-lockup` | M | The mobile end card: headline plus equal-size App Store and Google Play badges. Use when the close is an app install, not a URL. |

---

## 2.5 Numbers, data and proof

| Component | | Reach for this when |
|---|---|---|
| `number-pop-in` | P | One statistic pops in per character with blur and lift. |
| `number-wheel` | P | A **rolling odometer** reel per digit — for metrics, prices, scoreboards. **No GSAP**; you animate `--hf-number-target-y`. |
| `star-rating-fill` | M | A star row sweeps to a rating with a **fractional final star** preserved, and an optional synchronized count-up. |
| `testimonial-card` | M | A quote plus avatar/name/handle, revealed at reading pace. The plain proof beat. |
| `testimonial-proof-card` | M `slot` | The richer quote card: **per-line mask reveal**, mono byline, optional company mark, and an `emphasis` substring that gets a hand-drawn accent underline after the quote lands. Avatar is a slot for a photo. |
| `social-proof-card` | M | The whole **app-store close** as one scene: wordmark, five stars, proof line, three feature icons, CTA capsule. |
| `trust-strip` | M | A monochrome row of logo *wordmarks*, opacity-only stagger, then dead still. No boxes, no borders. |
| `telemetry-hud` | M `slot` | Mono `label: value` readouts framing a slotted subject, values **ticking to their final string** on cues, corner brackets drawing on. |

**The proof shelf disambiguates itself.** `social-proof-card`'s header: *"for an animated
star sweep use star-rating-fill; for a quote-based card use testimonial-proof-card; for a
bare CTA lockup use cta-lockup"* (the last is in the a–m half). **`testimonial-card` vs
`testimonial-proof-card`:** the plain one reveals the quote as a block and has a `rating`;
the proof one reveals it line by line through masks, drops the rating, and adds the
emphasis underline and company mark. Take `testimonial-card` for speed, the proof card
when one phrase in the quote is the point.

---

## 2.6 Pointer and gesture actors — something operates the UI

| Component | | Reach for this when |
|---|---|---|
| `oversized-cursor` | M | A deliberately oversized **macOS pointer** enters off-screen, glides to a target, clicks (the click *ignites a visible reaction on the target*), drifts aside, exits. Use to kick off a UI scene with a causal click. |
| `simulated-cursor` | P `ob` | A lightweight pointer + click pulse you **drive yourself** with x/y. Take this when you need a cursor to follow a path you are already animating, not a scripted arrival. |
| `touch-indicator` | M | The **mobile** counterpart: a translucent fingertip contact circle obeying touch physics, `tap` or `swipe`. Its law is *contact, never hover* — every appearance resolves into a touch-down. |
| `press-ripple` | M `slot` | A cursor arrives, presses a **slotted target**, releases with two ink ripple rings, then exits while the pressed state holds. The target flips `data-state="idle"` → `"pressed"` so custom slot content can style itself. |
| `pull-to-refresh` | M `sfx` | The specific native gesture: nonlinear rubber-band resistance, threshold arm, bounded loading cycles, exact snap back to rest. Skip it for generic scrolling. |
| `swipe-rail` | M | A contact circle **drags a card rail**, carries momentum after release, snaps the next card to focus. |

**`oversized-cursor` vs `simulated-cursor`:** the first is a mountable actor with its own
choreography and target; the second is a prop you animate. **`oversized-cursor` vs
`touch-indicator`:** pointer physics vs touch physics — the docs say pick by input model,
and send drawn-path gestures to a trail primitive instead.

`toggle-flip` exposes `[data-anchor="toggle-flip"]`, and both pointer actors are documented
as composing with it — that is the sanctioned way to make a pointer visibly operate a
control.

---

## 2.7 UI props and state machines — the thing being operated

| Component | | Reach for this when |
|---|---|---|
| `toggle-flip` | M `sfx` | An oversized toggle switch flipping with real physicality (thumb overshoot, track colour crossfade `--surface`→`--brand`, press-compress before release). Explicitly **the reference prop of the ui-props family** and the anchor pointer actors operate. |
| `state-chip-rail` | M | A rail of status chips advancing a **snap** state machine on a cue schedule. CSS responds to `[data-state]`; the timeline only flips attributes with `tl.set`, so every advance is exact in both seek directions. Optional badges pop beside one named state. |
| `tabs-slide-indicator` | P | A pill indicator sliding between tabs. Take this over `state-chip-rail` when the point is **navigation between two tabs**, not a multi-step machine advancing on its own. |
| `separator` | P `ob` | A 1px structural rule with a seek-safe progress reveal. Horizontal or vertical. |
| `settings-toggle-flow` | P `ob` | A composed settings screen — preference rows with toggle switches. Scaffold, **zero variables**. |
| `signup-flow` | P `ob` | A composed signup screen — social action, email, password, submit. Scaffold, **zero variables**. |
| `onboarding-stepper-flow` | P `ob` | A composed onboarding screen — milestone rail, active step card, next-action button. Scaffold, **zero variables**. |
| `skeleton-reveal` | P | A skeleton loader that pulses then cross-fades into real content. The loading→loaded beat. |
| `panel-reveal` | P | A panel opening by height with its body fading in. |
| `sheet-spring-up` | P `ob` | A bottom sheet arriving on a **real spring sampled frame-by-frame from reference footage** — overshoots its rest by 192px and settles over 0.72s. The integration note carries the full sampled table. |
| `success-check` | P | Ring pop plus tick draw. The confirmation beat. |
| `spring-pop` | M | A badge arriving with a **restrained overshoot** (`back.out`, tunable 1.1–2.0). Its header notes it exists to fill the gap left by `spring-scale-in`, whose `power3.out` never overshoots. |

The three `*-flow` scaffolds (`settings-toggle-flow`, `signup-flow`,
`onboarding-stepper-flow`) are the thinnest items in the half: ~95–106 source lines, no
header rationale beyond "Composed UI flow", **zero variables**, and Operator Black tokens.
Treat them as layout starting points to edit, not configurable components.

---

## 2.8 Notifications and chat

| Component | | Reach for this when |
|---|---|---|
| `native-notification-pop` | M `slot` `sfx` | **One** OS-faithful banner (iOS wide-centred or macOS compact top-right) drops over any scene on a closed-form underdamped spring, with backdrop blur. Its header states the split: *"Distinct from notification-stack: this is overlay chrome, faithful to the OS, one banner."* The scene behind it is a slot. |
| `notification-stack` | M | **1–5** token cards settle into a vertical stack, newest on top, then **one card resolves as the focus** while the rest dim by depth. Per-card arrival `cues`. |
| `notification-pileup` | M `sfx` | Cards arrive **faster and faster**, each pushing the pile down — the job is *anxiety*, not information. Cross-shelved as agitate. |
| `typing-indicator` | P `ob` | The three-dot chat bubble that says someone is writing. Measured from reference footage: scale 0.6→1, alpha 0.4→1 over 0.10s. |

**Three notification components, three different jobs:** one banner as overlay chrome
(`native-notification-pop`), an informative settling stack with a focus card
(`notification-stack`), and an accelerating tower whose point is overload
(`notification-pileup`). Pick by intent, not by appearance.

---

## 2.9 Camera moves

| Component | | Reach for this when |
|---|---|---|
| `push-in` | M | One slow continuous push on a centred headline, with a soft vignette. `intensity` maps to a final scale of 1.08 / 1.12 / 1.18. The simplest camera in the half. |
| `pull-back-reveal` | M | The **opposite**: start tight on one stat, hold long enough to establish it, then pull back to reveal the headline and cards that give it meaning. The chip stays the same DOM element throughout. |
| `ui-focus-zoom` | M `slot` | Establish a **whole app surface**, then zoom and pan to an anchored region on a cue and hold there. Anchor as percentages, optional focus halo. The surface is a slot. |
| `pan-stations` | M | A **lateral** pan across a row of labelled stations, settling at each. Cross-shelved: panning across features exhibits, panning across broken tools agitates. |
| `scroll-camera-story` | M `slot` | A compressed **forced-scroll** pass down a tall scene, four depth layers parallaxing at different rates, decelerating into a held final section. |
| `parallax-device-dive` | M `3d` | A phone rises into view, then the camera **pushes through its screen** and the app UI expands to fill the frame. |
| `zoom-through-transition` | M | A push that wipes the incoming scene through the outgoing one while the outgoing drifts back and blurs. |
| `parallax-zoom` | P | A focal card scales up to fill the frame while siblings parallax outward. **Zero variables — you wire classes and data attributes by hand.** |
| `parallax-unzoom` | P | The exact reverse. Its header notes the pairing: *"zoom INTO a card in scene 1, then unzoom OUT of it in scene 2."* Same manual wiring. |
| `yt-camera-move` | H | Zoom / slide / 3D tilt-pan helpers you call onto **any wrapper you already have**, including a video wrapper, plus an edge-defocus pulse. |

**`push-in` vs `ui-focus-zoom`:** `push-in` scales the whole stage on a headline;
`ui-focus-zoom` pans to an **anchor point** on a surface and clamps the pan so the scaled
world never reveals background. **`parallax-zoom` (P) vs `parallax-device-dive` (M):** the
first needs you to tag every card with `data-pz-row`/`data-pz-col`/`data-pz-focus` and
drive `--pz-progress` yourself; the second is a finished mountable scene.
**For moving *your footage* rather than a component's own content, use `yt-camera-move`.**

---

## 2.10 Transitions and scene bridges

| Component | | Reach for this when |
|---|---|---|
| `whip-pan-cut` | M `slot`×2 `sfx` | A full-frame whip pan between **your two scenes**, with capped directional motion blur peaking exactly at mid-whip. Velocity matching is structural: both scenes ride **one strip**, so the seam velocity is exact by construction. Described as *"the louder sibling of cut-the-curve."* |
| `page-slide` | P | A quiet outgoing/incoming page slide inside a rounded frame. The calm counterpart to `whip-pan-cut`. |
| `type-match-cut` | M | The headline splits and the incoming panel grows from the negative space between the word groups — a **geometric match cut**. |
| `zoom-through-transition` | M | Push through the outgoing scene into the incoming one. |
| `rubber-band-bumper` | M | The outgoing panel is **pulled against increasing resistance**, holds at visible tension, then releases past an edge with overshoot as the incoming panel settles behind it. Take this when the transition should feel loaded, not cut. |
| `physical-exit` | M | One card leaves with momentum — `toss` (arc), `drop` (gravity), `slide` (lateral stretch). Every mode carries rotation into the final offscreen pose and **never fades**. |

**`whip-pan-cut` vs `page-slide` vs `zoom-through-transition`:** lateral and violent,
lateral and calm, depth-wise. Only `whip-pan-cut` gives you two named content slots
(`before` / `after`) with token defaults.

---

## 2.11 Physics, springs and momentum

The shelf where the source is doing genuinely hard work. All of these are seek-safe by
construction, and several document *how*.

| Component | | Reach for this when |
|---|---|---|
| `spring-stack-shuffle` | M `slot`×5 | A 3–5 card stack reshuffles on cues, the back card throwing over the top. **Its signature is the interruptible spring:** a cue firing mid-flight redirects in-flight cards *preserving instantaneous velocity* — no snap, no pop. The default cue rhythm (0.9, 1.7, 1.95) fires the third cue mid-throw deliberately. |
| `soft-blob-touch` | M `canvas` | A granular soft blob deforms toward a scripted touch and recovers on a velocity-preserving spring. *"Nothing in the frame has a hard edge."* The AI-orb material beat. |
| `velocity-throw-snap` | M | A five-shot rail whips past on a fast decaying curve, then overshoots and snaps the hero shot exactly to centre. `power4.out` throw into `back.out(1.7)`. |
| `sheet-spring-up` | P `ob` | A bottom sheet on a **measured** spring table rather than an approximated ease. |
| `native-notification-pop` | M `slot` `sfx` | Its arrival is a closed-form underdamped spring sampled from a linear driver — the formula is printed in the source. |
| `rubber-band-bumper` | M | Resistance loading, then overshooting release. |
| `pull-to-refresh` | M `sfx` | Nonlinear rubber-band resistance under a scripted drag. |
| `spring-pop` | M | The small one: a single badge with a tunable overshoot. |

**How they stay deterministic** (worth knowing before you write your own): motion is
compiled at mount into per-property segment lists with explicit from/to and a pure ease
each. A redirect **cuts the covering segment analytically** — value from the ease, velocity
from a fixed finite difference — then continues on a cubic Hermite ease whose start slope
equals the cut velocity. Nothing simulates; every emitted tween is a `fromTo` with both
endpoints authored.

**`velocity-throw-snap` vs `screen-flow-carousel`:** the same motion law.
`screen-flow-carousel`'s header says so explicitly — it uses *"the velocity-throw-snap
motion law with the snap softened to the smooth register: no overshoot, no back ease."*
Take `velocity-throw-snap` for a single decisive landing on a hero; take
`screen-flow-carousel` for repeated advances that must not feel punchy.

---

## 2.12 Rails, carousels and exhibits — several things shown in order

| Component | | Reach for this when |
|---|---|---|
| `screen-flow-carousel` | M `slot`×5 | 2–5 **app screens** on a horizontal rail, one primary at centre, neighbours receded, advancing on cues with a mono caption swapping each time. Screens are slots; unslotted ones get one of four cycling skeleton variants. |
| `velocity-throw-snap` | M | Five shots, one decisive whip-and-snap to a chosen hero. Not repeatable advances. |
| `swipe-rail` | M | A rail advanced by a **visible gesture** rather than an invisible cue. |
| `spring-stack-shuffle` | M `slot`×5 | The same "several cards" idea as a **depth stack**, not a lateral rail. |
| `pan-stations` | M | The camera moves along a continuous row instead of the row moving past the camera. Use when the set should read as one environment. |
| `stagger-cascade` | M | A responsive **grid** arriving in DOM order with one evenly spaced stagger. Its evidence note: cascades appear in 13 of 18 surveyed launches, steps centring on 0.04–0.08s, with 0.14–0.18s for deliberate item-by-item reveals. |
| `stagger-lattice` | P | A grid reveal in the Anime.js-v4 stagger idiom. **Zero variables**; ignore the Three.js/MotionPath boilerplate in its header. |
| `split-tilt-cards` | M `slot`×2 `sfx` `3d` | **Two equal-weight cards** for comparison, arriving from opposite wings with mirrored `rotateY` book-open tilts under one shared perspective. Before/after with real dimension. |
| `three-orbiting-cards` | P `3d` | Three cards orbiting in **actual WebGL**. The only Three.js item in the half. |
| `scroll-feed` | M | A seamless self-scrolling feed column. `doom` or `frantic`. |
| `perspective-marquee` | P `3d` | Pill labels rolling toward a tilted horizon — a looping strip, not a sequence. |

**`stagger-cascade` vs `stagger-lattice`:** the first is a mountable with `itemCount` /
`stagger` / `direction` and a real envelope; the second is a zero-variable paste-snippet.
**`split-tilt-cards` vs a before/after wipe:** the tilt cards hold both states side by side;
`whip-pan-cut` replaces one with the other.

---

## 2.13 Product-demo scenes — a fake product doing something

| Component | | Reach for this when |
|---|---|---|
| `terminal-simulator` | P | A terminal window typing commands and streaming log output. **Zero variables** — edit the lines in the markup. |
| `vector-editor-rig` | M `sfx` | A **design-tool chrome** (tool rail, canvas, layers/properties inspector) with a live bezier pen path drawing, anchor dots, diamond handles, selection frame. Described as the design-tool twin of `terminal-run` (a–m half). |
| `sticky-mock-swap` | M | A product mock stays **pinned** while captions advance beside it, each caption threshold cross-fading the mock to the matching state. Phase length is `D / caption count`. |
| `ui-focus-zoom` | M `slot` | Your app surface plus a camera that finds the region that matters. |
| `telemetry-hud` | M `slot` | Instrument a subject with live-looking readouts. |
| `segmentation-flood` | M `canvas` `slot` | A **machine-vision read**: translucent accent masks flood over 2–4 labelled regions in quantized scanline steps, with corner brackets, mono label chips and a deterministic 2-frame HUD flicker. The AI-perception beat. |
| `tracing-beam` | M | One glowing dash follows an authored SVG path **through three UI elements**, lifting and brightening each on arrival. For showing a flow between features. |
| `offset-path-traveler` | M `slot` | A slotted traveler follows an authored path with tangent rotation. Take this over `tracing-beam` when **what travels** is your content, not a beam, and there is no three-stop story. |
| `x-follow-card` | P | A social follow card with avatar, handle, follower motion. **Zero variables.** |
| `spotlight-card` | P | A card with a scripted cursor spotlight and lit border. **Zero variables.** |
| `tilt-card` | P `3d` | A depth-layered card with hover-style parallax and a corner glow. |

**`tracing-beam` vs `offset-path-traveler`:** both follow an SVG path deterministically by
sampling it in `onUpdate` (neither needs MotionPathPlugin). `tracing-beam` fixes the story
at three labelled stops; `offset-path-traveler` gives you the path as a variable and the
traveler as a slot.

---

## 2.14 Agitation and pressure — the job is discomfort

A small, deliberately-shelved family. All mountable.

| Component | | Reach for this when |
|---|---|---|
| `overwhelm-surround` | M | Chips fly inward from every edge and crowd a **calm, still centre**. The centre never moves: pressure is spatial. 8–24 chips, tunable `intensity`. |
| `radial-surround` | M `slot` | The composed cousin: labelled chips assemble on an **elliptical ring** around a slotted subject, then optionally converge inward with an edge vignette. Positions baked once via cos/sin. The centre never moves — *"surrounded, not zoomed."* |
| `notification-pileup` | M `sfx` | Vertical, accelerating, mobile-native interruption. |
| `scroll-feed` | M | Doomscroll. Loop-friendly by default (zero-length IN and OUT keep the first and last frames matched). |
| `pan-stations` | M | Cross-shelved — panning across broken tools rather than polished features. |

**`overwhelm-surround` vs `radial-surround`:** both surround a still centre. The first is
chaotic and unlabelled (the crowd is the message); the second is ordered, labelled, and
slot-aware (the *contents* of the crowd are the message). Both explicitly guarantee the
centre never moves.

---

## 2.15 Texture, time-law and image-processing experiments

The "Wave M" experiments and canvas passes. Expensive, striking, and each demonstrates one
named law.

| Component | | Reach for this when |
|---|---|---|
| `ordered-dither-pass` | M `canvas` `slot` | Bayer-matrix ordered dithering quantizes your slotted scene: the image emerges from pure 2-tone noise to clean, or dissolves the reverse. Matrix 2/4/8, 2–6 levels. **Explicitly ordered — never error diffusion**, so it is frame-independent. |
| `particle-image-reveal` | M `canvas` `slot` | A particle field converges and settles while your **image** reveals beneath it, the trail thinning until it holds clean. `ltr` wipe or `center` iris. |
| `particle-text-dissolve` | M `canvas` | The same law applied to **text**, with targets sampled from the rendered glyph bitmap. |
| `slit-scan-reveal` | M `canvas` | The frame's **rows sample the subject at offset times** — arrival smears through time, then the offsets collapse to zero and the mark holds coherent. `rows` or `cols`. |
| `segmentation-flood` | M `canvas` `slot` | Machine-vision masks over your subject. |
| `soft-blob-touch` | M `canvas` | Granular material physics. |
| `stop-motion-cadence` | M | The **stepped-time law** as a demo: one driver quantizes time to `floor(t * fps) / fps` and feeds all motion. 8/10/12 fps, with a 2-frame edge boil seeded per step and sparkles living exactly 2–3 frames. |
| `stitched-text-draw` | M | Thread-stitch drawing, with a notable gotcha in its own header (see §3). |
| `wordmark-tiles` | M | Noise tiles resolving through a spatial wave. |
| `vignette` | P | Plain radial edge darkening. `z-index: 90` by default *so `grain-overlay` (100) reads on top* — the two are designed to stack. **Zero variables**; four CSS custom properties. |
| `yt-screen-warp` | H | Grid + scanline + vignette + sheen overlay plus a 3D warp class, so footage reads as if playing on a physical display. |
| `yt-feather-highlight` | H | Dims everything except a feathered ellipse whose position and size are CSS variables, so helpers can **glide the spotlight between targets**. |
| `yt-circle-pointer` | H | A draw-on annotation ellipse plus a countdown chip that pulses each tick. |

**`ordered-dither-pass` vs `particle-image-reveal`:** both reveal a slotted image, both
canvas. Dither quantizes colour and gives you a retro print/screen texture; particles give
you a physical assembly. **`slit-scan-reveal` vs `stop-motion-cadence`:** both are
time-law demos — the first offsets time *across space*, the second quantizes it *globally*.

**Slot mechanics for the canvas passes are unusual and easy to get wrong.** Several
(`ordered-dither-pass`, `particle-image-reveal`, `segmentation-flood`,
`screen-flow-carousel`, `scroll-camera-story`, `ui-focus-zoom`) take their content from an
inert `<template data-slot="...">` placed **at host document level**, not inside the clip —
because the runtime wipes the host clip's own children on mount. For
`ordered-dither-pass` specifically, slot content is rasterized through an SVG
`foreignObject` snapshot and so **must be self-contained**: inline styles or rules in host
`<style>` tags, **data-URI images only**, system or already-active fonts.

---

## 2.16 Whole scenes — drop one in and the beat is done

These are not primitives; each is a composed scene with several elements choreographed
together. Useful when you want a finished beat rather than a part.

| Component | | What the whole beat is |
|---|---|---|
| `notes-typing` | M | The notes-app confession: title + typed body paragraphs. |
| `social-proof-card` | M | The app-store close: wordmark, stars, proof line, three features, CTA. |
| `titlecard-lockup` | M | The breather title card, complete with rule and label. |
| `vector-editor-rig` | M `sfx` | A working design tool, chrome included. |
| `parallax-device-dive` | M `3d` | Phone → through the screen → app UI as stage. |
| `pull-back-reveal` | M | Stat → context, as one composed reveal. |
| `store-badge-lockup` | M | The mobile end card. |
| `radial-surround` | M `slot` | Subject plus its ring of pressure. |
| `scroll-camera-story` | M `slot` | A multi-section scroll film. |

---

# 3. Where the variables stop — what you cannot change without editing source

cougar asked for this explicitly. These are components whose variable surface omits
something a user would obviously want. Read from source, not from the schema.

## 3.1 The 18 components with **no variables at all**

`onboarding-stepper-flow`, `parallax-unzoom`, `parallax-zoom`, `settings-toggle-flow`,
`shimmer-sweep`, `signup-flow`, `spotlight-card`, `stagger-lattice`, `svg-line-draw-loader`,
`terminal-simulator`, `texture-mask-text`, `three-orbiting-cards`, `vignette`,
`x-follow-card`, `yt-camera-move`, `yt-circle-pointer`, `yt-feather-highlight`,
`yt-screen-warp`.

`data-variable-values` does nothing on any of them. Configuration is CSS custom properties
(`vignette`, `shimmer-sweep`, the `yt-*` set, `texture-mask-text`), manual data attributes
(`parallax-zoom` / `parallax-unzoom`), or editing the markup (`terminal-simulator`,
`x-follow-card`, the three `*-flow` scaffolds).

## 3.2 No colour control despite a strong colour identity

- **`notes-typing`** — variables are `title`, `lines`, `speed` only. **No `accent`, no
  `tone`.** Five hardcoded hex colours and no contract-token usage at all: it will not pick
  up your palette. The only scene component in the half that is entirely off-token.
- **`titlecard-calm`** — `headline` and `kicker` only. No accent. (Its sibling
  `titlecard-lockup` does expose `accent`, but only for the hairline rule.)
- **`vector-editor-rig`** — its header says this outright: *"accent is theme-owned, not a
  getVariables() knob. The path, active tool, handles, and selection frame all paint
  through `var(--brand, #0d99ff)`."* Change `--brand`, not the component.
- **`push-in`** — `text` and `intensity` only; the vignette strength is not exposed.
- **`tilt-card`** — `accent` offers `indigo | emerald | violet`, which are **literal
  colours, not contract tokens**, unlike the `green | blue | violet` mapping used by ~50
  other components. It will not follow your brand.
- **`success-check`** and **`tabs-slide-indicator`** and **`strikethrough-replace`** mix
  the two schemes: some options are literal (`red`, `amber`, `ink`) and some ride tokens
  (`blue` → `--accent`, `violet` → `--accent-2`). Read the option list before assuming.

## 3.3 Timing you cannot reach

- **No component exposes its own IN/OUT durations.** `IN_BASE` and `OUT_BASE` are source
  constants everywhere. You control *when* things happen (via `cues` / `*_at`) and how long
  the still hold is (via clip duration), never how fast the authored entrance plays.
- **`sticky-mock-swap`** derives phase length as `D / caption count` — so adding a caption
  silently speeds every phase up. There is no per-caption dwell variable.
- **`stagger-cascade`** exposes `stagger` (20–150ms) but its `IN_BASE` is fixed at 2.40s,
  so a large `itemCount` × large `stagger` gets clamped inside that budget rather than
  extending it.
- **`text-shimmer`**, **`vox-annotate`**, **`whip-pan-cut`**, **`ui-focus-zoom`**,
  **`segmentation-flood`**, **`slit-scan-reveal`**, **`press-ripple`**, **`soft-blob-touch`**
  expose a single cue (`sweep_at`, `draw_at`, `whip_at`, `zoom_at`, `flood_at`,
  `resolve_at`, `press_at`, `touch_at`) that is **clamped** so the gesture always completes
  before any exit — pushing it late does not extend the clip, it silently pulls back.

## 3.4 Content shape locked by the source

- **`tracing-beam`** — exactly **three** labels, in path order. Not a list you can grow.
- **`velocity-throw-snap`** — exactly **five** shots; `hero_index` is 0–4.
- **`native-notification-pop`** — exactly **one** body line, and long lines truncate with
  an ellipsis. Two lines needs `notification-stack`.
- **`notification-stack`** — 1–5 cards; extras past 5 are silently dropped.
- **`radial-surround`** — up to 12 chips; extras dropped.
- **`state-chip-rail`** — 2–8 states, up to 4 badges; extras dropped.
- **`telemetry-hud`** — up to 8 readouts.
- **`stitched-text-draw`** — clamped to **12 characters**, uppercased, and only A–Z 0–9 and
  space render; anything else becomes a space.
- **`wordmark-tiles`** — 12 characters.
- **`screen-flow-carousel`** 2–5 screens · **`spring-stack-shuffle`** 3–5 cards ·
  **`scroll-camera-story`** 2–4 sections · **`segmentation-flood`** 2–4 regions ·
  **`swipe-rail`** 3–5 cards · **`pan-stations`** 3–6 stations.

Silent truncation is the norm here — none of these error, they just drop the extras.

## 3.5 Slots that only exist in the installed copy

Two different slot mechanisms are in play, and the docs distinguish them:

- **Host-document templates** — you place `<template data-slot="<name>">` at host document
  level and the runtime pulls it in: `ordered-dither-pass`, `particle-image-reveal`,
  `segmentation-flood`, `screen-flow-carousel` (`screen-1`…`screen-5`),
  `scroll-camera-story`, `ui-focus-zoom`.
- **"Replace the children in your installed copy"** — the slot is an element inside the
  component file and you edit it after install: `native-notification-pop` (`scene`),
  `split-tilt-cards` (`card-a`/`card-b`), `spring-stack-shuffle` (`card-1`…`card-5`),
  `telemetry-hud` (`subject`), `whip-pan-cut` (`before`/`after`), `press-ripple` (`target`),
  `radial-surround` (`center`), `testimonial-proof-card` (`avatar`),
  `offset-path-traveler` (`traveler`), `whiteboard-ink` (`strokes`).

**The second kind cannot be filled from the host at all** — there is no variable for it.
If you need to change that content programmatically, you are editing the installed file.

---

# 4. Gotchas and constraints

Everything the sources state as a limit, a requirement, or a known failure.

## 4.1 Silent failures

1. **Mounting a paste-snippet yields a static pose.** No error. `zoom-through-transition`'s
   header documents this exact bug being fixed for that one file; the other 40 remain
   paste-only. Check §0.1 before mounting anything.
2. **Extras past a component's cap are dropped without warning** — see §3.4.
3. **`texture-mask-text` without its installed PNGs** renders unmasked text, not an error.
4. **`variable-font-flex` with the project font overridden** loses the effect entirely: it
   pins Roboto Flex deliberately because Inter has no `wdth` axis.
5. **Operator Black components in a contract-token frame** silently render in the wrong
   palette (§1.7).

## 4.2 Seek-safety traps the sources call out by name

These are stated as *"banked"* gotchas — the authors hit them and wrote them down.

- **cq-unit transform tweens blow up under seeks.** `scroll-camera-story` states it
  explicitly: nothing there tweens a cq unit; the world height is set once at mount in
  `cqh` and every tweened transform is percent-based. `spring-stack-shuffle` measures its
  stack geometry **in px** at mount for the same reason.
- **CSS `stroke-dashoffset` under-invalidates on reverse seeks in Chrome.** Both
  `stitched-text-draw` and `telemetry-hud` therefore drive the **attribute**, via
  `setAttribute`, not the CSS property. `stitched-text-draw` additionally avoids `<mask>`
  and `<clipPath>` entirely, using a double-dash trick, because *"nested SVG mask doesn't
  repaint under seek."*
- **`getTotalLength` is the sanctioned dash measurement** — *"never the `pathLength`
  attribute, never `non-scaling-stroke` on a dashed path."* Stated by `titlecard-lockup`,
  `whiteboard-ink`, `vox-annotate`, `testimonial-proof-card`, `stitched-text-draw`.
- **A root styled by class can stop matching after mount.** Composited renders scope a
  sub-composition's CSS to `[data-composition-id="<slug>"]`, so the family styles `#root`
  by **ID, never a class** (`overwhelm-surround`, `toggle-flip`, `pan-stations`,
  `vector-editor-rig` all cite "sub-compositions.md, Pitfall 3").
- **The composition id must be hardcoded in the timeline key**, because mount flattening
  strips `data-composition-id` from the live root (`FLATTENED_INNER_ROOT_STRIP_ATTRS`).
  Renaming a component means editing that literal string.
- **Variables must come from `window.__hyperframes.getVariables()`, never from parsing the
  file's own `<html>` tag** — once mounted, `document.documentElement` is the *host's*
  `<html>`.

## 4.3 Performance

- The six canvas painters (§1.4) clear and redraw the entire field every frame.
- `backdrop-filter` appears in `native-notification-pop` and `yt-camera-move`.
  `native-notification-pop` ships a **documented fallback**: *"If a host compositor
  flattens or lags the blur under seeks, remove the backdrop-filter lines; the color-mix
  surface fill underneath is opaque enough to carry the banner on its own (verified
  fallback)."*
- `whip-pan-cut` applies an SVG `feGaussianBlur` to a moving strip, capped at **16px** and
  peaking exactly at mid-whip.
- 68 components each ship their own GSAP `<script>` tag — dedupe on install.

## 4.4 Loop compatibility

Only **`scroll-feed`** is documented as loop-safe, and conditionally: *"With no cues and
exit none, zero-length IN and OUT keep the first and final frames loop-compatible and each
column moves exactly one complete card cycle. Cues or an enabled exit trade that loop
guarantee."* `perspective-marquee` lays its word list down twice so the strip reads as
continuous, but makes no loop guarantee.

## 4.5 Determinism rules the whole family obeys

Stated in nearly every header, worth internalising before authoring alongside them: no
`Math.random` at render time (seeded LCG tables computed once at mount instead), no
`Date.now` or wall clock, no CSS transitions, no free-running `requestAnimationFrame`, no
`gsap.timeScale()`, and every tween a `fromTo` with both endpoints authored so that
eventful seeks land identical frames in any order and either direction.

---

# 5. Coverage — all 111, alphabetical, with their primary shelf

| # | Component | Model | Primary shelf (§) |
|---|---|---|---|
| 1 | native-notification-pop | M slot sfx | Notifications 2.8 |
| 2 | notes-typing | M | Typing 2.2 · Scenes 2.16 |
| 3 | notification-pileup | M sfx | Notifications 2.8 · Agitation 2.14 |
| 4 | notification-stack | M | Notifications 2.8 |
| 5 | number-pop-in | P | Numbers 2.5 |
| 6 | number-wheel | P (no GSAP) | Numbers 2.5 |
| 7 | offset-path-traveler | M slot | Product demo 2.13 |
| 8 | onboarding-stepper-flow | P ob, 0 vars | UI props 2.7 |
| 9 | ordered-dither-pass | M canvas slot | Texture 2.15 |
| 10 | outline-draw | M | Lockups 2.4 |
| 11 | oversized-cursor | M sfx | Pointers 2.6 |
| 12 | overwhelm-surround | M | Agitation 2.14 |
| 13 | page-slide | P | Transitions 2.10 |
| 14 | pan-stations | M | Camera 2.9 · Rails 2.12 |
| 15 | panel-reveal | P | UI props 2.7 |
| 16 | parallax-device-dive | M 3d | Camera 2.9 · Scenes 2.16 |
| 17 | parallax-unzoom | P, 0 vars | Camera 2.9 |
| 18 | parallax-zoom | P, 0 vars | Camera 2.9 |
| 19 | particle-image-reveal | M canvas slot | Texture 2.15 |
| 20 | particle-text-dissolve | M canvas | Text effects 2.3 · Texture 2.15 |
| 21 | per-word-crossfade | P | Type reveals 2.1 |
| 22 | per-word-rise | M | Type reveals 2.1 |
| 23 | perspective-marquee | P 3d | Rails 2.12 |
| 24 | physical-exit | M | Transitions 2.10 |
| 25 | press-ripple | M slot | Pointers 2.6 |
| 26 | pull-back-reveal | M | Camera 2.9 · Scenes 2.16 |
| 27 | pull-to-refresh | M sfx | Pointers 2.6 · Physics 2.11 |
| 28 | push-in | M | Camera 2.9 |
| 29 | radial-surround | M slot | Agitation 2.14 · Scenes 2.16 |
| 30 | rgb-glitch-text | P | Text effects 2.3 |
| 31 | rubber-band-bumper | M | Transitions 2.10 · Physics 2.11 |
| 32 | scan-band | M | Text effects 2.3 |
| 33 | scramble-reveal | M | Text effects 2.3 |
| 34 | screen-flow-carousel | M slot×5 | Rails 2.12 |
| 35 | scroll-camera-story | M slot | Camera 2.9 · Scenes 2.16 |
| 36 | scroll-feed | M | Agitation 2.14 · Rails 2.12 |
| 37 | segmentation-flood | M canvas slot | Product demo 2.13 · Texture 2.15 |
| 38 | separator | P ob | UI props 2.7 |
| 39 | settings-toggle-flow | P ob, 0 vars | UI props 2.7 |
| 40 | shared-axis-y | P | Type reveals 2.1 |
| 41 | shared-axis-z | P | Type reveals 2.1 |
| 42 | sheet-spring-up | P ob | UI props 2.7 · Physics 2.11 |
| 43 | shimmer-sweep | P, 0 vars | Text effects 2.3 |
| 44 | signup-flow | P ob, 0 vars | UI props 2.7 |
| 45 | simulated-cursor | P ob | Pointers 2.6 |
| 46 | skeleton-reveal | P | UI props 2.7 |
| 47 | slit-scan-reveal | M canvas | Texture 2.15 |
| 48 | slot-machine-roll | P | Text effects 2.3 · Numbers 2.5 |
| 49 | social-proof-card | M | Proof 2.5 · Scenes 2.16 |
| 50 | soft-blob-touch | M canvas | Physics 2.11 · Texture 2.15 |
| 51 | soft-blur-in | P | Type reveals 2.1 |
| 52 | split-tilt-cards | M slot×2 sfx 3d | Rails 2.12 |
| 53 | spotlight-card | P, 0 vars | Product demo 2.13 |
| 54 | spring-pop | M | UI props 2.7 · Physics 2.11 |
| 55 | spring-stack-shuffle | M slot×5 | Physics 2.11 · Rails 2.12 |
| 56 | stagger-cascade | M | Rails 2.12 |
| 57 | stagger-lattice | P, 0 vars | Rails 2.12 |
| 58 | staggered-fade-up | P | Type reveals 2.1 |
| 59 | star-rating-fill | M | Proof 2.5 |
| 60 | state-chip-rail | M | UI props 2.7 |
| 61 | sticky-mock-swap | M | Product demo 2.13 |
| 62 | stitched-text-draw | M | Text effects 2.3 · Texture 2.15 |
| 63 | stop-motion-cadence | M | Texture 2.15 |
| 64 | store-badge-lockup | M | Lockups 2.4 · Scenes 2.16 |
| 65 | streaming-text | P ob | Typing 2.2 |
| 66 | strikethrough-replace | P | Text effects 2.3 |
| 67 | success-check | P | UI props 2.7 |
| 68 | svg-line-draw-loader | P, 0 vars | UI props 2.7 |
| 69 | svg-mask-reveal | M | Lockups 2.4 |
| 70 | svg-stroke-trace | M | Lockups 2.4 |
| 71 | swipe-rail | M | Pointers 2.6 · Rails 2.12 |
| 72 | tabs-slide-indicator | P | UI props 2.7 |
| 73 | telemetry-hud | M slot | Proof 2.5 · Product demo 2.13 |
| 74 | terminal-simulator | P, 0 vars | Product demo 2.13 |
| 75 | testimonial-card | M | Proof 2.5 |
| 76 | testimonial-proof-card | M slot | Proof 2.5 |
| 77 | text-shimmer | M | Text effects 2.3 |
| 78 | text-stagger | P | Type reveals 2.1 · Text effects 2.3 |
| 79 | text-state-swap | P | Text effects 2.3 |
| 80 | texture-mask-text | P, 0 vars, assets | Text effects 2.3 |
| 81 | three-orbiting-cards | P 3d webgl, 0 vars | Rails 2.12 |
| 82 | ticker-takeover | M | Text effects 2.3 |
| 83 | tilt-card | P 3d | Product demo 2.13 |
| 84 | titlecard-calm | M | Lockups 2.4 |
| 85 | titlecard-lockup | M | Lockups 2.4 · Scenes 2.16 |
| 86 | toggle-flip | M sfx | UI props 2.7 |
| 87 | top-down-letters | P | Type reveals 2.1 |
| 88 | touch-indicator | M | Pointers 2.6 |
| 89 | tracing-beam | M | Product demo 2.13 |
| 90 | tracking-in | P (no GSAP) | Type reveals 2.1 |
| 91 | trust-strip | M | Proof 2.5 |
| 92 | type-match-cut | M | Text effects 2.3 · Transitions 2.10 |
| 93 | typed-prompt | M | Typing 2.2 |
| 94 | typewriter | P | Typing 2.2 |
| 95 | typing-indicator | P ob | Notifications 2.8 |
| 96 | ui-focus-zoom | M slot | Camera 2.9 · Product demo 2.13 |
| 97 | variable-axis-type | M webfont | Text effects 2.3 |
| 98 | variable-font-flex | M webfont | Text effects 2.3 |
| 99 | vector-editor-rig | M sfx | Product demo 2.13 · Scenes 2.16 |
| 100 | velocity-throw-snap | M | Physics 2.11 · Rails 2.12 |
| 101 | vignette | P, 0 vars | Texture 2.15 |
| 102 | vox-annotate | M | Text effects 2.3 |
| 103 | whip-pan-cut | M slot×2 sfx | Transitions 2.10 |
| 104 | whiteboard-ink | M slot | Lockups 2.4 |
| 105 | wordmark-tiles | M sfx | Text effects 2.3 · Texture 2.15 |
| 106 | x-follow-card | P, 0 vars | Product demo 2.13 |
| 107 | yt-camera-move | H, 0 vars | Camera 2.9 |
| 108 | yt-circle-pointer | H, 0 vars | Texture 2.15 |
| 109 | yt-feather-highlight | H, 0 vars | Texture 2.15 |
| 110 | yt-screen-warp | H 3d, 0 vars | Texture 2.15 |
| 111 | zoom-through-transition | M | Transitions 2.10 |

**111/111.** Model column: `M` mountable · `P` paste-snippet · `H` helper library ·
`ob` Operator Black tokens.

---

# 6. Open questions

1. **Which of the two integration models is intended to win?** 40 paste-snippets and 71
   mountables ship side by side under one `hyperframes add` command with no signal in the
   install output. `zoom-through-transition` was converted; nothing says whether the rest
   will be.
2. **The `--hf-ui-*` Operator Black token set is never defined in the catalog pages.** Eight
   components consume ~57 of its tokens; no page in this section says where the values come
   from or how to install them. ⚑ [4/5]
3. **`spring-scale-in`, `cta-lockup`, `marker-highlight`, `cut-the-curve`, `terminal-run`,
   `before-after-wipe`** are referenced as siblings by components in this half but live in
   the a–m half (`hf-sdk`'s section). The cross-references only resolve if both halves are
   read together.
4. **"Wave" designations (Wave J2, K, K6, M, M5, M6, M8, M10) are used as authority** —
   "Wave K laws L1/L2", "the interruptible springs law" — but no page in this section
   defines what a Wave is or lists its laws.
5. **`hf:sfx` has no documented listener.** Ten components dispatch it with specific ids
   (`notification-pop`, `click-soft`, `whip-cut`, `badge-pop-soft`, `vector-close`,
   `refresh-commit`, `refresh-settle`, `notification-soft`); nothing here says what catches
   it or how ids map to the SFX library.
6. **No stated policy on multiple GSAP tags** when several components are installed into
   one composition.
7. **`data-anchor` as a composition mechanism** appears once (`toggle-flip`'s
   `[data-anchor="toggle-flip"]`, which pointer actors target) but is not documented as a
   general convention.

---

*Compiled from a complete read of `pages/catalog/components/` entries 108–218 — 111/111,
no sampling. Quoted strings are verbatim from component source headers. Integration model,
dependency, zero-variable, token-family, and flag classifications were derived by grepping
each file's `## Source` block, not its blurb. `⚑` marks an inference; `[N/5]` marks
confidence below certain.*
