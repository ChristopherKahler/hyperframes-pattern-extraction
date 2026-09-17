---
type: reference
status: active
tags:
  [
    hyperframes,
    catalog,
    components,
    routing-taxonomy,
    motion-primitives,
    video-gen,
  ]
relatedTo: [catalog-index, sdk-and-packages, catalog-blocks-guide, video-gen]
---

# HyperFrames catalog components A–M — routing guide

## What this section covers

The 107 components in `pages/catalog/components/` whose slug sorts from
`animated-bar-chart` through `multiplayer-cursors` — every file read in full,
source HTML/CSS/JS as the truth rather than the prose around it. It answers the
question the catalog index cannot: **given a job, which of these do I reach for,
and what will it cost me to install.** Name, slug, description, install command,
output path and variable schema are deliberately absent — those live in
`reference/catalog-index.md`.

## How to use this file

Two axes decide every choice, and they are orthogonal:

- **Mount class** (§1) — how the thing installs and what it demands of the host.
  Get this wrong and nothing renders, regardless of taste.
- **Job group** (§3) — what it is actually for. Sixteen groups, derived from
  reading the source, not from the tag lists.

Then §4 (near-duplicates), §5 (runtime requirements), §6 (variables that lie).

Coverage is mechanical: the group assignment in §2 was diffed against the 107
`##########` markers in the corpus — 107 assigned, zero unassigned, zero
duplicates.

---

## 1. The four mount classes

This is the primary routing split and the index does not express it. It was
derived per file from three markers: presence of `<!doctype html>`, presence of
a `<template>` wrapper, presence of `data-composition-variables`.

| Class | What it is                       | Count | How it installs                                                        | What it costs you                                                          |
| ----- | -------------------------------- | ----- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **A** | Mountable sub-composition        | 55    | `data-composition-src` + `data-variable-values` on a host element       | Nothing. Drop-in, themed, retimed, seek-safe.                              |
| **B** | Standalone document              | 24    | Paste the whole file, or open it as its own composition                 | Fixed `data-width`/`data-height`; you own placement and often the timeline. |
| **C** | Variable-aware paste fragment    | 18    | Paste markup + CSS + script; **you write the GSAP**                     | The file animates nothing on its own.                                      |
| **D** | Plain paste snippet              | 10    | Paste markup + CSS; **you write the GSAP**                              | No variables at all. Editing means editing HTML.                           |

### Class A — mountable sub-composition (55)

The modern shape. `<html data-composition-variables='[…]'>` wraps a `<template>`;
the runtime clones only the template contents. Inside, `#root` is
`position:absolute; inset:0; container-type:size` with **no** `data-width`/
`data-height`, every measurement in `cqw`/`cqh`/`cqmin`, every colour from a
contract token, one paused timeline registered under a **literal** string key
(mount flattening strips `data-composition-id` off the inner root, so the key
cannot be read from the DOM). Variables arrive through
`window.__hyperframes.getVariables()`, which merges declared defaults with host
`data-variable-values`.

Reach for class A unless you have a specific reason not to. It is the only class
that themes, retimes and composes without you touching its internals.

### Class B — standalone document (24)

`<!doctype html>` with its own `<head>`, its own reset, fixed pixel dimensions,
and a timeline it registers itself. Three sub-families, and they behave very
differently:

- **`caption-*` burn-ins (15)** — `data-timeline-locked`, 1920×1080, canvas
  pipeline, Google-Fonts `<link>`. Whole-frame subtitle renderers, not
  primitives. See §3.1.
- **`hw-*` and `mk-*` helper libraries (7)** — the file's own timeline is a
  *self-preview* explicitly marked "not part of the snippet you copy". What you
  actually take is the exported `window.hw*` / `window.mk*` functions.
- **`camera-shake` and `morph-text` (2)** — one is a helper
  (`window.cameraShake`), one is a locked 15-second scene.

### Class C — variable-aware paste fragment (18)

No doctype, no template: a bare `<div class="hf-transition-…">` carrying its own
`data-composition-variables`. The script reads
`window.__hyperframes.getVariables()`, clamps every value, and writes the result
out as CSS custom properties — then stops. **No GSAP is loaded and no timeline is
created.** Every one of the 18 ships a "Timeline integration" comment block at
the bottom that is the recipe you are expected to copy into your own timeline.

These are the transitions.dev ports. They are the cheapest things in the catalog
to restyle and the most work to actually animate.

### Class D — plain paste snippet (10)

Markup plus CSS, no variables, no timeline. Nine of the ten carry a timeline
integration example; `grain-overlay` carries none because it is pure CSS. Three
(`confetti`, `mesh-gradient-bg`, `motion-blur`) reference `gsap` in their
integration block **without loading it** — the host must already have GSAP on the
page.

---

## 2. Page index — routing map

Slug → mount class → job group → runtime demands. Deliberately not a re-list of
the index: no names, no descriptions, no install commands, no variable schemas.

Job-group codes are expanded in §3. Flags: `gsap` = ships its own GSAP 3.14.2
CDN tag; `canvas` = uses a 2D canvas pipeline; `webfont` = external Google Fonts
stylesheet; `sfx` = dispatches `hf:sfx`; `slot` = accepts caller content through
`data-slot` or a host `<template data-slot>`.

| Slug | Group | Class | Requires |
| ---- | ----- | ----- | -------- |
| `animated-bar-chart` | D | DATA | — |
| `arc-motion-path` | D | UTIL | — |
| `ascii-render-pass` | A | PASS | gsap canvas slot |
| `ascii-trail-reveal` | A | TYPE | gsap |
| `aurora-drift` | A | PASS | gsap |
| `avatar-cloud` | A | PROOF | gsap sfx |
| `avatar-group-hover` | C | PROOF | — |
| `badge-pop` | C | UIM | — |
| `beat-accent` | A | BEAT | gsap sfx |
| `beat-pulse-background` | A | PASS | gsap |
| `beat-timeline` | A | BEAT | gsap sfx |
| `before-after-wipe` | A | CMP | gsap sfx slot |
| `blur-in` | C | UIM | — |
| `blur-out-up` | C | UIM | — |
| `bottom-up-letters` | C | TYPE | — |
| `browser-device-stage` | A | DEV | gsap slot |
| `camera-rig-depth-stack` | D | CAM | — |
| `camera-scan-gate` | A | CAM | gsap sfx |
| `camera-shake` | B | CAM | gsap |
| `caption-blend-difference` | D | CAP | — |
| `caption-camera-follow` | A | CAP | gsap |
| `caption-clip-wipe` | B | CAP | gsap canvas webfont |
| `caption-editorial-emphasis` | B | CAP | gsap canvas webfont |
| `caption-emoji-pop` | B | CAP | gsap canvas webfont |
| `caption-glitch-rgb` | B | CAP | gsap canvas webfont |
| `caption-gradient-fill` | B | CAP | gsap canvas webfont |
| `caption-highlight` | B | CAP | gsap canvas webfont |
| `caption-kinetic-slam` | B | CAP | gsap canvas webfont |
| `caption-matrix-decode` | B | CAP | gsap canvas webfont |
| `caption-neon-accent` | B | CAP | gsap canvas webfont |
| `caption-neon-glow` | B | CAP | gsap canvas webfont |
| `caption-parallax-layers` | B | CAP | gsap canvas webfont |
| `caption-particle-burst` | B | CAP | gsap canvas webfont |
| `caption-pill-karaoke` | B | CAP | gsap canvas webfont |
| `caption-texture` | B | CAP | gsap canvas webfont |
| `caption-weight-shift` | B | CAP | gsap canvas webfont |
| `card-resize` | C | UIM | — |
| `char-slam-explode` | A | TYPE | gsap |
| `chart-story` | A | DATA | gsap |
| `chat-message` | A | UIM | gsap |
| `chat-thread` | A | UIM | gsap |
| `chromatic-aberration-wipe` | C | TRAN | — |
| `code-terminal-run` | A | STRUCT | gsap slot |
| `comparison-split` | A | CMP | gsap sfx |
| `confetti` | D | PASS | — |
| `conic-progress-ring` | A | DATA | gsap |
| `constellation-hub` | A | STRUCT | gsap |
| `count-up` | A | DATA | gsap |
| `cta-close` | A | PROOF | gsap |
| `cta-lockup` | A | PROOF | gsap |
| `cursor-glyph-trail` | A | PTR | gsap slot |
| `cut-the-curve` | A | DATA | gsap sfx |
| `decline-chart` | A | DATA | gsap |
| `device-frame-stage` | A | DEV | gsap sfx |
| `directional-wipe` | C | TRAN | — |
| `drift-hold` | A | CAM | gsap |
| `dynamic-grid` | C | UIM | — |
| `echo-trail` | A | UTIL | gsap slot |
| `facet-morph` | A | TRAN | gsap sfx |
| `fade-through` | C | TRAN | — |
| `focus-blur-resolve` | C | CAM | — |
| `focus-rack` | A | CAM | gsap |
| `focus-swap` | A | CAM | gsap |
| `gesture-tap` | A | PTR | gsap |
| `gloss-sweep` | A | PASS | gsap |
| `grade-split-reveal` | A | CMP | gsap |
| `grain-field` | A | PASS | gsap |
| `grain-overlay` | D | PASS | — |
| `grid-card-assemble` | A | STRUCT | gsap slot |
| `grid-pixelate-wipe` | D | TRAN | — |
| `halftone-dissolve` | A | TRAN | gsap canvas slot |
| `headline-slam` | A | TYPE | gsap |
| `hw-arrow` | B | HAND | gsap |
| `hw-boil` | B | HAND | gsap |
| `hw-box-label` | B | HAND | gsap |
| `hw-callout-circle` | B | HAND | gsap |
| `hw-underline` | B | HAND | gsap |
| `icon-morph-beat` | A | BEAT | gsap |
| `icon-swap` | C | UIM | — |
| `ink-bleed-reveal` | A | TRAN | gsap canvas slot |
| `inline-highlight` | C | EMPH | — |
| `input-feedback` | C | UIM | — |
| `iris-reveal` | A | TRAN | gsap sfx slot |
| `keyframe-scrub-stack` | D | STRUCT | — |
| `kinetic-type-swap` | A | TYPE | gsap |
| `light-sweep-pass` | A | PASS | gsap sfx slot |
| `line-by-line-slide` | C | TYPE | — |
| `line-swap` | A | TYPE | gsap |
| `locked-nucleus-orbit` | A | STRUCT | gsap |
| `logo-brand-close` | A | PROOF | gsap |
| `logo-sting` | A | PROOF | gsap |
| `logo-wall` | A | PROOF | gsap sfx |
| `marker-checklist-card` | A | HAND | gsap |
| `marker-highlight` | A | EMPH | gsap |
| `match-cut` | A | TRAN | gsap |
| `matrix-decode` | C | TYPE | — |
| `menu-morph` | C | UIM | — |
| `mesh-gradient-bg` | D | PASS | — |
| `micro-transitions` | C | UIM | — |
| `mk-emphasis-type` | B | EMPH | gsap |
| `mk-usage-arc` | B | DATA | gsap |
| `modal-morph` | A | UIM | gsap slot |
| `morph-swap` | A | TRAN | gsap sfx slot |
| `morph-text` | B | TYPE | gsap webfont |
| `motion-blur` | D | UTIL | — |
| `multi-device-splay` | A | DEV | gsap |
| `multiplayer-cursors` | A | PTR | gsap sfx |

**Group legend** (expanded in §3):

| Code    | Job                                    | n   | Code     | Job                                 | n   |
| ------- | -------------------------------------- | --- | -------- | ----------------------------------- | --- |
| `CAP`   | Caption / subtitle burn-in             | 17  | `DATA`   | Numbers and charts                  | 7   |
| `UIM`   | Product-UI micro-interactions          | 12  | `PROOF`  | Credibility lockups, brand closes   | 7   |
| `TRAN`  | Shot-to-shot transitions               | 10  | `HAND`   | Hand-drawn annotation               | 6   |
| `TYPE`  | Headline and word-block reveals        | 9   | `STRUCT` | Structure, diagrams, assembly       | 5   |
| `PASS`  | Full-frame passes, grounds, particles  | 9   | `CMP`    | Two states held against each other  | 3   |
| `CAM`   | Camera moves and focus                 | 7   | `PTR`    | Cursors, gestures, presence         | 3   |
| `EMPH`  | Mark a word inside running text        | 3   | `DEV`    | Device and browser mockups          | 3   |
| `BEAT`  | Music and rhythm sync                  | 3   | `UTIL`   | Motion helper libraries             | 3   |

---

## 3. Job groups

Sixteen groups, assigned by what the source does, not by tag list or alphabet.
Each entry is one line: **when you reach for this one instead of its
neighbours.**

### 3.1 CAP — caption / subtitle burn-in (17)

Not primitives. Fifteen of them are whole-frame renderers: class B,
`data-timeline-locked`, hardcoded 1920×1080, `data-duration="8"`,
`data-fps="30"`, a 2D canvas pipeline, and a Google-Fonts `<link>`. **The
transcript is baked into the file as a JS array.** You do not vary a caption
component; you edit its array and re-render. Pick the look first, then accept
its whole frame.

Three transcript idioms, and they are not interchangeable when you script
generation:

- `var TRANSCRIPT = […]` normalised through `normalizeWords()` — `caption-emoji-pop`,
  `caption-glitch-rgb`, `caption-neon-accent`, `caption-pill-karaoke`,
  `caption-weight-shift`. The structured form; carries per-word metadata.
- `var WORDS = […]` flat — `caption-camera-follow`, `caption-clip-wipe`,
  `caption-gradient-fill`, `caption-highlight`, `caption-kinetic-slam`,
  `caption-matrix-decode`, `caption-neon-glow`, `caption-particle-burst`,
  `caption-texture`.
- `var W = […]` plus a `BLOCKS` grouping array — `caption-editorial-emphasis`,
  `caption-parallax-layers`. Words are addressed by index from `BLOCKS`, so
  editing the text means editing two arrays in step.

Routing within the group:

- `caption-highlight` — the default TikTok karaoke: solid block sweeps behind the
  active word. Take this unless you have a reason not to; everything else in the
  group is this plus a cost.
- `caption-pill-karaoke` — same job as `caption-highlight` but the highlight is a
  rounded pill container; reach for it when the block edge reads too hard.
- `caption-clip-wipe` — reveal by clip-path edge instead of by highlight; the one
  to use when the background is busy and a coloured block would fight it.
- `caption-kinetic-slam` — one word per screen at display size with alternating
  entrance directions; the only member that abandons the caption band entirely.
- `caption-weight-shift` — transitions between *lines*, not words, by animating
  font weight; reach for it when the copy is two calm statements, not a
  word-by-word read.
- `caption-editorial-emphasis` — dual-font with dramatic size contrast; the only
  one that changes typeface treatment rather than adding decoration around it.
- `caption-neon-accent` vs `caption-neon-glow` — see §4.1.
- `caption-glitch-rgb` — RGB channel split plus a CRT scanline overlay; the
  scanline is the differentiator, not the aberration (for aberration alone on a
  transition, use `chromatic-aberration-wipe`).
- `caption-matrix-decode` — scramble-then-resolve per word. Distinct from the
  component `matrix-decode`; see §4.2.
- `caption-gradient-fill` — gradient clipped into the glyph with an elastic
  bounce entrance; the one that needs no background treatment to read.
- `caption-particle-burst` — particle explosion on keyword hits; the only caption
  that emits geometry outside the text box.
- `caption-emoji-pop` — stroked text with emoji inline and a horizontal squeeze
  entrance; take it when the emoji is content, not decoration.
- `caption-texture` — flowing texture mask (lava, marble, metal, wood, concrete,
  rock) over large uppercase; **the only caption in the group with a variables
  table**, and see §6 for what that table omits.
- `caption-parallax-layers` — 3D depth layering that places text *behind* the
  subject; reach for it when you have a cutout subject to sit in front of.
- `caption-camera-follow` — the outlier: **class A, mountable, 9s, no canvas, no
  locked timeline.** One sentence written across a world larger than the frame,
  the camera pulling back so each new word lands at the same size. Reach for it
  when the point is accumulation; it is the only caption you can mount and retime.
- `caption-blend-difference` — the other outlier: **class D, a paste snippet, no
  transcript, no GSAP.** A `mix-blend-mode: difference` text layer that
  auto-inverts per pixel against whatever is beneath. Reach for it when you need
  legibility over unpredictable footage and do not need karaoke timing at all.

### 3.2 TYPE — headline and word-block reveals (9)

Entrances for a line, a headline or a word list. Not caption timing.

- `headline-slam` (A) — the workhorse: a headline arrives hard and holds.
  Default choice for a title card.
- `char-slam-explode` (A) — per-character slam that scatters; use when the
  headline is short enough that per-glyph motion reads.
- `bottom-up-letters` (C) — letters rise into place from a masked baseline;
  cheapest of the per-character reveals, but you write the timeline.
- `line-by-line-slide` (C) — multi-line block, each line sliding in on a stagger;
  reach for it when the copy is a paragraph, not a headline.
- `line-swap` (A) — replaces one line with the next in place; the rotating-claim
  primitive. Use when the *change* is the point.
- `kinetic-type-swap` (A) — same job as `line-swap` with more aggressive motion
  between states; see §4.3.
- `morph-text` (B) — gooey SVG-threshold morph through a word list;
  `data-timeline-locked`, 1920×1080, 15s, Figtree from Google Fonts. Reach for
  it only when the liquid morph itself is the effect — it cannot be mounted or
  retimed.
- `matrix-decode` (C) — scramble-resolve cells. See §6: it ships the cells and
  the `data-final` attribute but **no decode animation.**
- `ascii-trail-reveal` (A) — content resolves out of a trailing ASCII wash; the
  one to use when you want a terminal register without an actual terminal.

### 3.3 EMPH — mark a word inside running text (3)

- `inline-highlight` (C) — CSS-scalar highlight behind a `<span>` in flowing
  copy; the lightest option and the only one that reflows with the text.
- `marker-highlight` (A) — four SVG marker styles (highlight, circle, underline,
  scribble) dash-drawn over a substring match. Reach for it when the mark should
  look drawn rather than printed. Overlaps `hw-underline`; see §4.4.
- `mk-emphasis-type` (B) — oversized low-contrast background word drifting behind
  the subject. Not emphasis of a word in a sentence — typography as texture.
  Exports `mkEmphasisIn` / `mkEmphasisOut`.

### 3.4 HAND — hand-drawn annotation (6)

The `hw-*` set is a **library, not five components.** All five class-B files
duplicate the same runtime — `window.hwOnUpdate`, `window.hwHash`,
`window.hwBoil` — so if you paste more than one into a host you have redefined
the shared functions. Copy the shared block once, then take only the
component-specific helpers.

- `hw-boil` — the base. `hwBoil` owns `x`/`y`/`rotation` on a target with a
  frame-drop cadence (3–4 classic, 1 frantic) plus `hwWobbleEllipse`. Take this
  when you want the boil on *your own* artwork.
- `hw-underline` — `hwMarkPath` draws underline/strike marks; the hand-drawn
  answer to `inline-highlight`.
- `hw-arrow` — `hwArrowPath(w, h, curve, seed)`; the only one that points at
  something off to the side.
- `hw-callout-circle` — circles a region; reach for it over `hw-box-label` when
  the target is round-ish or when you want no text attached.
- `hw-box-label` — `hwWobbleRect` plus an attached label; the one that names the
  thing it frames.
- `marker-checklist-card` (A) — a mountable checklist that ticks itself. The only
  member of this group that is a drop-in composition rather than a helper.

### 3.5 TRAN — shot-to-shot transitions (10)

- `fade-through` (C) — the neutral default; a through-black/through-colour
  crossfade.
- `directional-wipe` (C) — a hard edge on an axis; the cheapest non-fade.
- `iris-reveal` (A) — circular open/close with slot content; take it when you
  want the eye pushed to one point.
- `match-cut` (A) — a hard single-frame swap at `CUT_AT = 1.40s`, exactly frame
  42 at 30 fps. **No crossfade at all.** Reach for it when the whole idea is that
  two shots share a silhouette.
- `morph-swap` (A) — two slotted siblings on a shared 50%/50% origin;
  `condense` shrink-fades A as B scales up, `reshape` morphs the silhouette on
  `scaleX`/`scaleY`. Never tweens width/height. The general-purpose A→B for
  arbitrary caller content.
- `facet-morph` (A) — a faceted/shard break-up between states; use when
  `morph-swap` reads too smooth.
- `halftone-dissolve` (A, canvas) — dissolve through a halftone dot screen.
- `grid-pixelate-wipe` (D) — dissolve through growing pixel blocks; the
  no-variables, no-canvas alternative to `halftone-dissolve`.
- `ink-bleed-reveal` (A, canvas) — organic ink bloom; the wettest of the
  dissolves.
- `chromatic-aberration-wipe` (C) — RGB split during the wipe; the one that
  carries a "damaged signal" register.

### 3.6 CMP — hold two states against each other (3)

- `before-after-wipe` (A) — a travelling divider over two stacked slots; use when
  the comparison is *the same frame* changed.
- `comparison-split` (A) — a static split with both halves live; use when both
  states must be readable at once for a sustained beat.
- `grade-split-reveal` (A) — specifically a **colour-grade** split: same image,
  two grades. Reach for it over `comparison-split` when the difference is grade
  rather than content.

### 3.7 CAM — camera moves and focus (7)

- `drift-hold` (A) — a slow push/drift that holds; the ambient default under any
  static plate.
- `camera-scan-gate` (A) — a scanning gate pass across the frame.
- `camera-shake` (B) — `window.cameraShake(tl, target, opts)`; a helper you
  attach to your own element, not a scene. Its seek-safe driver is the reference
  implementation for the whole catalog (§7.1).
- `camera-rig-depth-stack` (D) — parallax layers on a virtual rig; paste-only, no
  variables, you write the timeline.
- `focus-rack` (A) — pulls focus between two named depths; the deliberate
  attention move.
- `focus-swap` (A) — swaps which of two subjects is sharp; reach for it over
  `focus-rack` when there are exactly two subjects and the swap is the beat.
- `focus-blur-resolve` (C) — resolves from blurred to sharp once; an *entrance*,
  not a rack. Use it when nothing needs to go out of focus afterwards.

### 3.8 PASS — full-frame passes, grounds and particles (9)

Things that sit over or under everything else.

- `grain-overlay` (D) — pure CSS film grain, no JS, no GSAP, no variables. The
  cheapest object in the entire slice.
- `grain-field` (A) — the mountable, themable, animated grain. Take this over
  `grain-overlay` whenever you can mount; see §4.5.
- `aurora-drift` (A) — slow coloured aurora ground; the calm background default.
- `mesh-gradient-bg` (D) — mesh-gradient ground as a paste snippet. See §4.6 —
  it and `confetti` share a body, and one of them ships dead code.
- `beat-pulse-background` (A) — a ground that pulses on a beat; the only
  background in the group that syncs.
- `light-sweep-pass` (A) — a specular sweep governed by **one property**:
  `--light-x`, a unitless scalar on `#root`. Band translate, per-element bloom,
  shadow offsets and ambient lift all read it through `calc()`/`clamp()`/`max()`
  in static CSS. Reach for it when many elements must catch the same light.
- `gloss-sweep` (A) — a single glossy highlight across one surface; use it when
  only one element needs the sheen and `light-sweep-pass` would be overkill.
- `ascii-render-pass` (A, canvas, slot) — re-renders slot content as ASCII;
  a whole-frame stylisation, not a reveal.
- `confetti` (D) — 22 `.particle` spans plus mesh/card/spot furniture; celebratory
  burst. Requires GSAP already on the page.

### 3.9 BEAT — music and rhythm sync (3)

- `beat-accent` (A, sfx) — a single accent hit on one beat; the smallest unit.
- `beat-timeline` (A, sfx) — a visible timeline/ruler advancing on beats; reach
  for it when the rhythm itself must be *seen*.
- `icon-morph-beat` (A) — an icon that morphs on each beat; the one that carries
  meaning rather than just pulse.

(`beat-pulse-background` lives in §3.8 because its job is the ground.)

### 3.10 DATA — numbers and charts (7)

- `count-up` (A) — a single number counting; take it when there is one figure.
- `conic-progress-ring` (A) — a percentage as a conic ring; the mountable,
  themable gauge.
- `mk-usage-arc` (B) — hairline arc gauge with a counting numeral, driven by one
  helper call (`mkArcIn(tl, target, at, value)`). Reads the circle's `r` so
  resizing the box works. Same job as `conic-progress-ring`; see §4.7.
- `animated-bar-chart` (D) — bars growing; no variables, no GSAP loaded, you
  write the timeline. The generic bar chart.
- `chart-story` (A) — a chart that narrates through several states; reach for it
  when the data needs more than one beat.
- `cut-the-curve` (A, sfx) — a curve being cut/clipped at a point; a rhetorical
  chart, not a neutral one.
- `decline-chart` (A) — specifically a downward trend. Reach for it over
  `chart-story` when "it went down" is the entire message.

### 3.11 DEV — device and browser mockups (3)

- `device-frame-stage` (A) — phone/tablet hardware frame with notch/island/body
  options. **Its variables channel is non-standard — see §6.1.**
- `browser-device-stage` (A, slot) — a browser chrome frame with a content slot;
  the one for web product shots.
- `multi-device-splay` (A) — phone + tablet + desktop fanning from a stack to
  −12° / 0° / +12° with an idle float. Reach for it when the point is "all
  platforms", not one screen.

### 3.12 UIM — product-UI micro-interactions (12)

Mostly transitions.dev ports (class C) that restyle cheaply and animate only when
you write the timeline.

- `micro-transitions` (C) — a *pack* of six UI micro-transitions driven by two
  CSS scalars, `--hf-micro-progress` and `--hf-micro-tab`. Take this first: if
  one of its six covers the job, you avoid installing several singles.
- `badge-pop` (C) — notification badge with elastic scale and count reveal.
- `blur-in` (C) / `blur-out-up` (C) — generic element entrance / exit. Pair them;
  neither is text-specific despite where they sort.
- `card-resize` (C) — a card changing size in place. Reach for `modal-morph`
  instead if children must re-flow rather than stretch.
- `modal-morph` (A, slot) — FLIP shared-element grow: both layouts measured once
  at mount, container morphed by transform only, keyed children counter-scaled
  onto their own measured rects. The only member that re-flows content correctly.
- `dynamic-grid` (C) — grid items reflowing between arrangements.
- `icon-swap` (C) — one icon replaced by another; see §4.8 against
  `icon-morph-beat`.
- `menu-morph` (C) — hamburger to X with fanning pills.
- `input-feedback` (C) — form-field validation states.
- `chat-message` (A) — a single message bubble arriving.
- `chat-thread` (A) — a full thread filling in. Take `chat-thread` when more than
  one message lands; `chat-message` when a single bubble is the beat. **Neither
  exposes bubble colour — §6.2.**

### 3.13 PTR — cursors, gestures, presence (3)

- `gesture-tap` (A) — a tap/press ripple at a point; the one for "the user did
  this".
- `cursor-glyph-trail` (A, slot) — a cursor dragging a glyph trail; decorative
  movement, single pointer.
- `multiplayer-cursors` (A) — 2–6 labelled collaborator cursors with
  token-derived colours converging on a centre zone. The only one that says
  *other people are here.* Labels are a comma-separated string variable; missing
  entries become deterministic `Guest N`.

### 3.14 PROOF — credibility lockups and brand closes (7)

- `avatar-group-hover` (C) — a small stacked avatar row; the "used by" strip.
- `avatar-cloud` (A, sfx) — many avatars arriving as a field; reach for it when
  the number is the point.
- `logo-wall` (A, sfx) — a grid of customer logos.
- `logo-sting` (A) — a short logo hit; the mid-roll bumper.
- `logo-brand-close` (A) — logo resolving into the brand lockup at the end.
- `cta-lockup` (A) — logo plus call-to-action held together.
- `cta-close` (A) — the closing CTA card. Order at the end of a film:
  `logo-brand-close` → `cta-lockup` → `cta-close`, from most brand to most ask.

### 3.15 STRUCT — structure, diagrams and assembly (5)

- `grid-card-assemble` (A, slot) — cards assembling into a grid; the layout
  build.
- `constellation-hub` (A) — nodes radiating from a hub; the "integrations"
  diagram.
- `locked-nucleus-orbit` (A) — a fixed nucleus with orbiting satellites. Reach
  for it over `constellation-hub` when the centre must dominate and the
  satellites are anonymous.
- `code-terminal-run` (A, slot) — a terminal typing and running a command; the
  developer-proof shot.
- `keyframe-scrub-stack` (D) — a stack of keyframes being scrubbed; the
  editor/tooling proof shot. Paste-only, no variables.

### 3.16 UTIL — motion helper libraries (3)

Not scenes. Each attaches behaviour to elements you already have.

- `arc-motion-path` (D) — moves an element along an arc instead of a straight
  line.
- `echo-trail` (A, slot) — leaves fading echoes behind a moving element.
- `motion-blur` (D) — `attachMotionBlur(selector, tl, opts)`; velocity-driven
  one-sided SVG ghost trail. Options: `blurScale` 0.008, `blurMax` 20,
  `stretchScale` 0.0002, `stretchMax` 0 (disabled), `axis` `"both"`. Must be
  called **after** all tweens and **before** `window.__timelines` registration,
  and targets must be animated via GSAP `x`/`y`, never `left`/`top`.

---

## 4. Near-duplicates — what actually differs

Fourteen pairs and clusters that look interchangeable in a name list and are not.

### 4.1 `caption-neon-glow` vs `caption-neon-accent`

Both are neon glows on class-B locked frames with no variables, so both are
edit-the-file. `caption-neon-glow` commits to a **fixed cyan-and-magenta
palette** with keyword accent colours. `caption-neon-accent` is **multi-colour**
and adds a **wiggle drift** — the glyphs move. Choose on whether you want motion
in the glow, not on colour: you are editing the hex either way.

### 4.2 `matrix-decode` vs `caption-matrix-decode`

Not variants of one thing.

- `caption-matrix-decode` (class B, locked, canvas, 8s) — a complete caption
  renderer that scrambles and resolves each word against a baked `WORDS` array.
- `matrix-decode` (class C, paste fragment) — renders one scrambling cell per
  character with variables `text`, `accent`, `size`, `glow`, writes the target to
  `data-final`, and **ships no decode animation at all.** Its entire shipped
  timeline recipe is a staggered fade-up:
  `tl.fromTo('.hf-catalog-matrix-decode span', {opacity:0,y:12}, {opacity:1,y:0,duration:0.18,stagger:0.035,ease:'power2.out'}, startTime)`.
  The header comment is explicit that `data-final` is there for "a decode routine
  [that] can read" it — the routine is yours to write.

If you want a scramble and are not doing captions, budget for writing the decode.

### 4.3 `line-swap` vs `kinetic-type-swap`

Opposite mechanics behind similar names.

- `line-swap` — replaces the **whole line**: A exits up through an
  `overflow:hidden` mask as B enters bottom-up on the same beat. Variables
  `line_a`, `line_b`, `swap_at`, `underline_word`.
- `kinetic-type-swap` — the sentence **stays fixed**; one masked slot sized to
  the widest word rolls through `options` and settles. Variables `prefix`,
  `suffix`, `options`, `cues`.

Two claims in sequence → `line-swap`. One claim with a rotating noun →
`kinetic-type-swap`.

### 4.4 `marker-highlight` vs `hw-underline` vs `inline-highlight`

All three mark a word; the difference is what you bring.

- `inline-highlight` (C) — CSS scalar on a `<span>` you already have. Reflows
  with the text. You write the timeline.
- `marker-highlight` (A) — a **complete text card**: owns `text`,
  `emphasis_word`, and a `style` enum of four marker treatments (highlight,
  circle, underline, scribble) dash-drawn over a substring match. Drop-in.
- `hw-underline` (B) — a **helper library** (`hwMarkPath`, `hwMarkOn`,
  `hwMarkOff`) that draws squiggle underline, double-pass strike and bracket
  marks onto *your* element. No variables, no card.

Note that `marker-highlight`'s `style: underline` and `hw-underline` produce the
same visual with entirely different install costs.

### 4.5 `grain-overlay` vs `grain-field`

- `grain-overlay` (D) — 95 lines, **zero `<script>` tags**, pure CSS, no
  variables. The cheapest object in the slice.
- `grain-field` (A) — 206 lines, two scripts, mountable, themable, variable-driven.

Take `grain-field` if you can mount. Take `grain-overlay` when you need grain
inside a document that must stay script-free.

### 4.6 `mesh-gradient-bg` vs `confetti` — shared body, dead code

These two share a body: the same `.mesh` / `.card` / `.spot` furniture and the
same GSAP integration recipe, differing by class prefix. Then:

- `confetti` has **22 `class="particle"` spans** in its markup and 46 `var(--…)`
  token references.
- `mesh-gradient-bg` has **zero particle spans** — but still ships the
  `.hf-catalog-mesh-gradient-bg .particle` CSS rule **and** the particle tween in
  its timeline recipe, guarded by `if (particles_mesh_gradient_bg.length)` so it
  silently no-ops. It also uses only 8 `var(--…)` references, none of them
  contract tokens.

So: `confetti` is the themed one and `mesh-gradient-bg` is a de-particled copy
carrying dead CSS and a dead tween. Route on intent — burst vs ground — and
delete the orphan particle rule when you paste `mesh-gradient-bg`.

### 4.7 `conic-progress-ring` vs `mk-usage-arc`

Same reading (a percentage plus a counting numeral), different technique and
different class.

- `conic-progress-ring` (A) — a **conic-gradient frontier with a radial mask**;
  a filled donut. Variables `progress`, `thickness`, `label`. Themable, mountable.
- `mk-usage-arc` (B) — an **SVG `stroke-dasharray` / `strokeDashoffset` circle**;
  a hairline arc. No variables; one helper call
  `mkArcIn(tl, target, at, value)` drives fill and count together. It reads the
  circle's own `r`, so resizing the 220px box and `r=92` together just works.

Thickness matters → `conic-progress-ring`. Hairline Apple-ish register, or you
are already pasting the `mk-*` set → `mk-usage-arc`.

### 4.8 `icon-swap` vs `icon-morph-beat`

- `icon-swap` (C) — scale-and-blur between shapes for toolbar/action state.
  Variables `shape`, `blur`, `size`, `tone`. No timeline; you write it.
- `icon-morph-beat` (A) — morphs between authored silhouettes, shifts to an
  accent colour and marks completion with **one restrained pulse**. Variables
  `pair`, `accent`.

State change in a UI → `icon-swap`. A completion moment on a beat →
`icon-morph-beat`.

### 4.9 `gloss-sweep` vs `light-sweep-pass`

- `gloss-sweep` (A) — **one card**: restrained slam, one diagonal specular gloss,
  then holds still. Variables `text`, `accent`, `sweep_angle`.
- `light-sweep-pass` (A, slot, sfx) — **a whole slotted scene** re-shaded. One
  property owns the pass: `--light-x`, a unitless scalar on `#root`. The band's
  translate, every element's highlight bloom, every shadow offset and the ambient
  lift all read it through `calc()`/`clamp()`/`max()` in static CSS. The scene
  itself never moves. Variables `sweep_at`, `angle`, `strength`, `accent`, `exit`.

One surface → `gloss-sweep`. Many elements that must catch the same light →
`light-sweep-pass`.

### 4.10 `chat-message` vs `chat-thread`

Same visual language (both hardcode the same iMessage hexes). `chat-message`
takes `type`, `text`, `cardTitle`, `cardDomain`, `tail`, `delivered` — one
bubble. `chat-thread` takes `contact`, `unread`, `messages`, `beat`, `dots`,
`receipt` — a filling conversation with typing dots and read receipts. Split on
message count, then accept the palette (§6.2).

### 4.11 `halftone-dissolve` vs `grid-pixelate-wipe` vs `ink-bleed-reveal`

Three dissolves, three costs. `halftone-dissolve` (A, canvas, slot) — dot screen,
mountable, needs the canvas pipeline. `grid-pixelate-wipe` (D) — growing pixel
blocks, no canvas, no variables, you write the timeline. `ink-bleed-reveal` (A,
canvas, slot) — organic bloom rather than a regular grid. Pick
`grid-pixelate-wipe` only when you must avoid canvas.

### 4.12 `focus-rack` vs `focus-swap` vs `focus-blur-resolve`

`focus-rack` (A) pulls between named depths — the deliberate move. `focus-swap`
(A) swaps which of exactly two subjects is sharp — the beat is the exchange.
`focus-blur-resolve` (C) only resolves blurred→sharp once and never goes back;
it is an entrance, and it has no timeline of its own.

### 4.13 `before-after-wipe` vs `comparison-split` vs `grade-split-reveal`

`before-after-wipe` (A, sfx, slot) — a travelling divider; the change is
revealed over time. `comparison-split` (A, sfx) — a static split held so both
sides read at once. `grade-split-reveal` (A) — specifically colour grade, and
notably **the only class-A member here without `container-type: size`** (§7.4).

### 4.14 The `hw-*` cluster (5 files, one library)

`hw-arrow`, `hw-boil`, `hw-box-label`, `hw-callout-circle`, `hw-underline` each
redefine the identical shared runtime: `window.hwOnUpdate`, `window.hwHash`,
`window.hwBoil` (and `hwWobbleEllipse` in two of them). Pasting two of these into
one host silently redefines those globals. Copy the shared block **once**, then
take only the file-specific helpers (`hwArrowPath`/`hwArrowOn`/`hwArrowOff`,
`hwBoxBuild`/`hwBoxOn`/`hwBoxOff`, `hwCalloutBuild`/`hwCalloutOn`/`hwCalloutOff`,
`hwMarkPath`/`hwMarkOn`/`hwMarkOff`).

---

## 5. Runtime requirements

Counted mechanically across all 107.

| Requirement                              | Count   | Who                                                                              |
| ---------------------------------------- | ------- | -------------------------------------------------------------------------------- |
| Ships its own GSAP 3.14.2 CDN `<script>` | **79**  | all 55 class A, all 24 class B                                                   |
| **Uses GSAP but does not load it**       | **4**   | `arc-motion-path`, `confetti`, `mesh-gradient-bg`, `motion-blur`                 |
| No GSAP anywhere in the file             | **24**  | all 18 class C, plus 6 class D                                                   |
| 2D canvas pipeline                       | **18**  | 15 `caption-*`, plus `ascii-render-pass`, `halftone-dissolve`, `ink-bleed-reveal` |
| External Google Fonts stylesheet         | **16**  | 15 `caption-*`, plus `morph-text`                                                |
| Dispatches `hf:sfx`                      | **14**  | see below                                                                         |
| Accepts caller content via a slot        | **13**  | see below                                                                         |

79 + 4 + 24 = 107. **The four that use GSAP without loading it are the trap**:
paste one of them into a document that has no GSAP and it fails silently at the
integration step, not at paste time.

**The single CDN URL, everywhere it appears:**
`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`. It is pinned to an
exact version in all 79 files; nothing in the slice loads a GSAP plugin.

**Canvas pipeline (18).** Every locked `caption-*` renders through a 2D canvas,
as do `ascii-render-pass`, `halftone-dissolve` and `ink-bleed-reveal`. If your
render path cannot give these a real canvas, none of the nineteen will produce a
frame — and the fifteen captions will fail as whole frames, not as a missing
layer.

**External fonts (16).** The fifteen locked captions and `morph-text` pull
`fonts.googleapis.com` / `fonts.gstatic.com` at render time. `morph-text` uses
`family=Figtree:wght@900&display=block` — `display=block` means the text is
**invisible** until the font arrives, so a network stall renders blank frames
rather than fallback-font frames. Everything else in the slice uses only
`var(--font-display / --font-body / --font-mono)` with a local fallback stack.

**`hf:sfx` dispatchers (14):** `avatar-cloud`, `beat-accent`, `beat-timeline`,
`before-after-wipe`, `camera-scan-gate`, `comparison-split`, `cut-the-curve`,
`device-frame-stage`, `facet-morph`, `iris-reveal`, `light-sweep-pass`,
`logo-wall`, `morph-swap`, `multiplayer-cursors`. These dispatch a bubbling
`CustomEvent("hf:sfx", { detail: { id, t }, bubbles: true })` and **never play
audio** — if nothing in the host listens, the event is inert.

**Slot-accepting (13):** `ascii-render-pass`, `before-after-wipe`,
`browser-device-stage`, `code-terminal-run`, `cursor-glyph-trail`, `echo-trail`,
`grid-card-assemble`, `halftone-dissolve`, `ink-bleed-reveal`, `iris-reveal`,
`light-sweep-pass`, `modal-morph`, `morph-swap`. Two slot conventions coexist and
are not interchangeable:

- **In-composition slots** — `<div class="…" data-slot="a">` inside the
  component. You replace the children of that element in your installed copy
  (`morph-swap`, `before-after-wipe`, most of the list).
- **Host-template slots** — the component queries the **host document** for
  `<template data-slot="modal-morph-card">` and clones it. `modal-morph` is the
  clear case; its slot content is cloned into *both* the card and the panel so
  the FLIP pairing has a counterpart for every `data-morph-key`.

**Theme-token conformance.** 40 of 107 use **no contract token at all** — no
`--bg`, `--fg`, `--muted`, `--surface`, `--border`, `--brand`, `--accent`,
`--accent-2`, `--font-*`, `--radius`, `--space-*`, `--dur-beat` or `--ease-*`.
Theme a frame and these forty will not follow. Most are class B or C where that
is expected, but **five are class A mountables, where it is not**:
`caption-camera-follow`, `chat-message`, `chat-thread`, `grade-split-reveal`,
`match-cut`. Of those, `chat-message` uses **no CSS custom property whatsoever**
— every colour is a literal hex.

---

## 6. Variables that lie — what you cannot change

Components whose variable set omits something a user would obviously reach for
first. Verified against the declared `data-composition-variables` and the
rendered Variables table, not against the prose.

### 6.1 `device-frame-stage` — a non-standard variables channel

Every other class-A component in the slice reads
`window.__hyperframes.getVariables()`. This one does not. Verbatim:

```js
var html = document.documentElement;
var declared = {};
try {
  JSON.parse(html.getAttribute("data-composition-variables") || "[]").forEach(
    function (variable) { declared[variable.id] = variable.default; },
  );
} catch (error) {}
var vars = Object.assign({}, declared, window.__hfVariables || {});
```

It reads declared defaults off `document.documentElement` and overrides off a
global `window.__hfVariables`. Two consequences follow, and I have read the
component but not the runtime that mounts it:

- After mount flattening, `document.documentElement` is the **host** document's
  `<html>`, which does not carry this primitive's
  `data-composition-variables` — so `declared` would come back empty and the
  fallbacks in the code (`vars.device === "tablet" ? … : "phone"`) become the
  real defaults. ⚑ [3/5]
- `data-variable-values` on the mount element is the documented override channel
  and feeds `getVariables()`, not `window.__hfVariables` — so setting
  `device`/`cutout`/`body` that way plausibly does nothing. ⚑ [3/5]

Either way the code path is unique in the slice. Test `device`, `cutout` and
`body` before relying on them.

Its three variables also have **empty "What it does" cells** in the rendered
table, so the docs give no guidance either.

Separately, its `!important` is load-bearing and must not be tidied away:

```css
#root { position:absolute; inset:0; width:100% !important; height:100% !important; container-type:size; }
```

The file's own comment explains why: the compiler's flatten step
(`prepareFlattenedInnerRoot`) reads this element's `data-width`/`data-height`
(required by the `root_missing_dimensions` lint rule) and force-writes them back
as inline `style="width:1920px;height:1080px"` — the 2×-oversized-and-bleeding
bug this primitive was fixed for.

### 6.2 Hardcoded values with no variable

| Component            | Not exposed                                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `match-cut`          | **`CUT_AT_BASE = 1.4`** — the cut time, which is the entire point. Variables are only `accent`, `label_a`, `label_b`. |
| `multi-device-splay` | The splay itself: x = −30 / −5 / +24 cqw, rotation = −12 / 0 / +12°, `CASCADE` 0.12s, `FAN_DURATION` 0.9s. Its **only** variable is `accent` — the sole single-variable class-A component in the slice. |
| `chat-message`, `chat-thread` | Every colour. Both hardcode the iMessage palette (`#0a80f8` blue, `#0a9c6b` / `#3ce6ac` green, `#8e8e93` grey) and `chat-message` uses **no CSS custom property at all**. Variables cover content and timing only. |
| all 15 locked `caption-*` | The transcript, `data-duration="8"`, `data-fps="30"`, and 1920×1080. Fourteen of the fifteen expose **no variables whatsoever**. |
| `matrix-decode`      | The decode animation. Cells and `data-final` ship; the scramble does not (§4.2). |
| `mesh-gradient-bg`   | Nothing themable — 8 `var(--…)` references, none of them contract tokens, plus an orphan `.particle` rule (§4.6). |
| `morph-text`         | Word list, `data-morph-speed` and `data-morph-pause` are **markup attributes**, not variables — editable, but not through `data-variable-values`. |
| `mk-emphasis-type`   | The word itself (markup) and `--mk-emph-color`, whose dark-scheme value is left as a CSS comment for you to swap by hand. |

### 6.3 Variables tables with missing descriptions

- **`camera-shake`** — all four (`shakeProfile`, `shakeIntensity`,
  `shakeFrequency`, `shakeRotation`) have an empty "What it does" cell. The nine
  `shakeProfile` values (`handheld-normal-mild`/`-strong`/`-extreme`,
  `handheld-wideangle-mild`/`-strong`, `handheld-tele-mild`/`-strong`,
  `rig-6d-shake`, `rig-6d-wobble`) are listed but never explained.
- **`caption-texture`** — its one variable is documented as accepting `string`
  with an empty description, even though the component ships exactly six
  textures (lava, marble, metal, wood, concrete, rock). The enum is named in the
  page description and nowhere in the schema.
- **`device-frame-stage`** — all three, as above.
- **`chat-thread`** — descriptions are present but the markdown table is ragged
  (rows carry more cells than the header), so it renders with spurious empty
  columns. A formatting defect, not a missing-content one.

---

## 7. Cross-cutting conventions

These are the laws the class-A files obey. Knowing them tells you what you may
safely change.

### 7.1 Seek determinism

Compositions are **seeked frame-by-frame, not played**. Every animated value must
be a pure function of `tl.time()`. The recurring rules, each observed in source:

- **No `Math.random`, no wall clock, no `requestAnimationFrame`.** Randomness is
  fixed-seed: `multiplayer-cursors` uses authored `WAYPOINTS` percentages;
  `hw-boil` uses `hwHash(n, seed) = fract(sin(n*127.1 + seed*311.7) * 43758.5453) * 2 - 1`.
- **`onUpdate` callbacks do not fire on `seek()`.** GSAP suppresses events on
  seek, so anything relying on `onUpdate` freezes on frame 0. Two sanctioned
  workarounds:
  - **Setter-driven** (`camera-shake`): tween a property whose setter does the
    work, because GSAP writes the property on every render including seeks.
    ```js
    var driver = {};
    Object.defineProperty(driver, "t", { get(){return value}, set(next){ value=next; apply(next); } });
    tl.to(driver, { t: dur, duration: dur, ease: "none" }, at);
    ```
  - **Tween-`onUpdate`** (`motion-blur`, `morph-text`): a *tween's* `onUpdate`
    does fire on seek, unlike `tl.eventCallback("onUpdate")`. `motion-blur` says
    so explicitly — "`tl.eventCallback("onUpdate")` is not available in the
    HyperFrames renderer; the runtime proxies the timeline object."
  - **Timeline-`onUpdate` plus an anchor tween** (`modal-morph`): an inert
    `tl.to({p:0},{p:1,duration:D,ease:"none"},0)` spanning `[0, D]` so the
    timeline's own `onUpdate` fires for every eventful seek and holds never clamp
    short.
- **One `onUpdate` per timeline.** `hw-boil` ships a dispatcher because a
  timeline has only one: `window.hwOnUpdate(tl, fn)` keeps a `tl.__hwRenders`
  array and installs a single `eventCallback`.
- **Measure once, then never again.** `modal-morph` takes both FLIP layouts
  synchronously at mount and every later frame is arithmetic on those rects.
- **No `will-change` on morphing layers.** `modal-morph` says why: "cached
  composited rasters from a scaled state leak pixel noise into out-of-order
  seeks."
- **`immediateRender: false`** on any `fromTo` that must not stamp its start
  values at build time (`morph-swap`, `multiplayer-cursors`).

### 7.2 The envelope model

Fixed `IN_BASE`, elastic `HOLD`, fixed `OUT_BASE`. When the clip is too short,
**both fixed phases scale by the same ratio** —
`envelopeScale = duration / (IN_BASE + OUT_BASE)` — and `HOLD` goes to zero.
**Never `gsap.timeScale()`.** Stated in nearly every class-A header comment.
`HOLD = max(0, D − (IN + OUT))`, `OUT_START = IN + HOLD`.

`multiplayer-cursors` shows the elaborated form: its drift legs are *floored*
into a finite count (`Math.floor(cursorWindow / DRIFT_LEG_BASE)`) and then
stretched evenly so a `yoyo`/`repeat` loop exactly fills the window without
overrunning `OUT`.

### 7.3 Tokens, accents and the shadowing bug

Contract tokens: `--bg --fg --muted --surface --border --brand --accent
--accent-2 --font-display --font-body --font-mono --radius --space-1..3
--dur-beat --ease-standard --ease-emphasis`.

The `accent` enum convention is fixed across the catalog: `green` → `--brand`,
`blue` → `--accent`, `violet` → `--accent-2`, each with a literal hex fallback.

**Five files carry a workaround for a real bundler bug** —
`ascii-render-pass`, `before-after-wipe`, `code-terminal-run`,
`halftone-dissolve`, `iris-reveal`:

```js
// The bundler mirrors composition variables as scoped CSS custom props, so this
// unit's own accent variable shadows the contract --accent token inside the
// subtree ("blue" is a valid CSS color and would render pure blue).
var computedAccent = getComputedStyle(root).getPropertyValue("--accent").trim();
if (computedAccent === "green" || computedAccent === "blue" || computedAccent === "violet") {
  accentColors.blue = "#61a8ff";
}
```

If you author a new component with an `accent` variable **and** read `--accent`
through `getComputedStyle`, you need this guard. The other class-A components
avoid it by only ever writing `--x-accent` and never reading `--accent` back.

### 7.4 Sizing

Class A: `#root { position:absolute; inset:0; container-type:size }`, all
measurements in `cqw`/`cqh`/`cqmin`, **no `data-width`/`data-height`**, styling
via `#root` (never a class, so scoping survives mounting).

Two class-A files break this: **`caption-camera-follow`** and
**`grade-split-reveal`** have no `container-type: size`. They will not scale with
the host box the way the other 53 do. [4/5]

### 7.5 Timeline keys

`window.__timelines["literal-slug"] = tl`. The key is always a **literal string**
because mount flattening strips `data-composition-id` off the inner root before
registration — several files say so in a comment. Do not compute the key from the
DOM.

### 7.6 Sound

Primitives dispatch `hf:sfx` and never play audio (§5). Fourteen do.

---

## 8. Gotchas and constraints

1. **Class C and D animate nothing.** 28 of 107 ship no timeline. The "Timeline
   integration" comment at the bottom of the file is the deliverable, not a
   footnote.
2. **Four files use GSAP without loading it** — `arc-motion-path`, `confetti`,
   `mesh-gradient-bg`, `motion-blur`. Silent failure at integration time.
3. **The `hw-*` set redefines shared globals.** Pasting two of the five into one
   host silently clobbers `hwOnUpdate` / `hwHash` / `hwBoil` (§4.14).
4. **`motion-blur` ordering is load-bearing.** Call `attachMotionBlur` after all
   tweens and before `window.__timelines` registration; it appends a tracking
   tween sized to `tl.duration()`, so a later `tl.set(document.body, {}, D)` must
   come *first* to establish the real duration. Targets must be animated on GSAP
   `x`/`y`, never `left`/`top`.
5. **`morph-text` renders blank on a slow font load** — Figtree is requested with
   `display=block`, which hides text until the font arrives.
6. **The 15 locked captions are whole frames.** `data-timeline-locked`, fixed
   1920×1080, 8s, 30fps, canvas, external fonts. They do not compose; they
   replace.
7. **`device-frame-stage`'s `!important` is required** (§6.1). Removing it
   reintroduces the 2×-oversize bleed.
8. **40 of 107 use no contract token**, five of them class A (§5). Theming a
   frame will not reach them.
9. **`mesh-gradient-bg` ships dead code** — a `.particle` CSS rule and a
   particle tween with no particles (§4.6).
10. **`matrix-decode` ships no decode** (§4.2).
11. **`match-cut`'s cut time is not a variable** (§6.2).
12. **Two class-A files lack container sizing** (§7.4).
13. **Doc-generation defect, catalog-wide:** newer pages emit their entire source
    **twice** — once inside `<VariablesExplorer>` and again in a `## Source`
    `<Accordion>` — roughly doubling page size. Affects the a–m slice broadly;
    it is a mirror/docs artefact, not a component defect.
14. **`caption-editorial-emphasis` and `caption-parallax-layers` need two edits.**
    Their text lives in a `W` array addressed by index from a separate `BLOCKS`
    array; changing the copy means changing both in step (§3.1).

---

## 9. Open questions

1. Does `data-variable-values` actually reach `device-frame-stage` through
   `window.__hfVariables`, or is that primitive's variable channel broken after
   mount? Requires the runtime source, which is outside this slice. (§6.1)
2. Is `window.__hfVariables` a documented global anywhere, or a legacy of an
   earlier variables contract? No other file in the a–m slice references it.
3. Are `caption-camera-follow` and `grade-split-reveal` deliberately exempt from
   `container-type: size`, or unconverted? (§7.4)
4. Is the accent-shadowing bundler bug (§7.3) fixed upstream? Five files carry
   the workaround; the other class-A files avoid the pattern rather than guard
   against it, so the two cannot be distinguished from source alone.
5. `mesh-gradient-bg`'s orphan particle code — was it forked from `confetti`, or
   both from a common ancestor? Either way, which is the maintained one?
6. `matrix-decode` promises a decode in its description and ships a stagger. Is
   there a canonical decode routine elsewhere in the catalog (the n–z half, or
   `pages/catalog/blocks/`) that it expects you to pair with?
7. The 15 locked captions are all exactly 8s/30fps. Is that a hard constraint of
   the caption render path or just the authored default?
8. Do the six `caption-texture` textures live in the component or as external
   assets? The schema says `string`, the description names six, and the source
   was read without resolving where the texture images come from. [2/5]
9. `micro-transitions` is a pack of six. Is there a documented list of which six,
   or is `--hf-micro-tab` the only index into them?
10. Does anything in the host runtime listen for `hf:sfx` by default, or is every
    one of the 14 dispatchers inert until an integrator wires it up?
