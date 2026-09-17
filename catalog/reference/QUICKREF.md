---
type: reference
status: active
tags: [hyperframes, quickref, operator-card, prompting, cheatsheet, video-gen]
relatedTo: [hyperframes, video-gen, hyperframes-docs-mirror]
---

# HyperFrames operator card

Keep this open while authoring. Full detail: [prompting.md](prompting.md) · [catalog-index.md](catalog-index.md)

## 1 · The prompt skeleton

```text
[route]      /motion-graphics          slash command loads workflow + framework rules
[spec]       8-second 1920x1080        defaults: 1920x1080 @ 30fps
[beats]      Beat 1 (0-4s): ...        timestamps + pacing ("then hold on the cursor")
[copy]       "SHIP FASTER."            quote it or it gets paraphrased; / = line break
[technique]  Adapt `code-typing`       exact block slug; blocks are starting points
[negatives]  No narration, no audio    "no narration" != silent; say "no audio"
```

Per element inside a beat: **element · motion · layout · style · timing**, one sentence, any order.

## 2 · Route

| Input | Route |
|---|---|
| URL / brief / script → promo, launch, or site tour | `/product-launch-video` |
| Text only, every visual invented | `/faceless-explainer` |
| GitHub PR | `/pr-to-video` |
| Existing talking head → captions | `/embedded-captions` |
| Existing talking head → graphic overlays | `/talking-head-recut` |
| Logo / stat / tweet, <10s, no narration | `/motion-graphics` |
| Music track drives the cuts | `/music-to-video` |
| Click-through deck (never render it) | `/slideshow` |
| Multi-scene, narrated, or nothing else fits | `/general-video` |

Unsure → `/hyperframes`. Skip the interview with **"Just build it — don't ask me anything."** Answers land in `BRIEF.md`; edit that file to change one.

## 3 · Loop

```bash
npx hyperframes init my-video
npx hyperframes preview                    # keep running; judging blind wastes renders
npx hyperframes lint && npx hyperframes check   # both must pass
npx hyperframes render --output final.mp4
```

`check` = headless browser: overflow, collisions, mid-timeline runtime errors, WCAG AA contrast.

## 4 · Find a block

```bash
npx hyperframes catalog                      # table of everything
npx hyperframes catalog --type block --tag social
npx hyperframes catalog --json
npx hyperframes catalog --human-friendly     # picker; installs on select
npx hyperframes add <slug>
```

372 items: 154 blocks, 218 components. **Never invent a slug** — a made-up name sends the agent guessing at raw GLSL.

## 5 · Ease words

| Say | Get | Say | Get |
|---|---|---|---|
| smooth | `power2.out` | dramatic | `expo.out` |
| snappy | `power4.out` | dreamy | `sine.inOut` |
| bouncy | `back.out` | springy | `elastic.out` |

fast 0.2s = energy · medium 0.4s = professional · slow 0.6s = luxury · 1–2s = cinematic

## 6 · Camera words

slow push-in → 4–8% scale · pull back → scale down · pan across → horizontal translate · **drone orbit / crane → Three.js only** · whip to → fast blurred slide · parallax → layers at different rates

## 7 · Pacing words

punchy cuts → 1.5–4s per idea · cinematic holds → long beats + ambient idle · beat-synced → on the analyzed grid · breathing room → a held moment · ambient idle → 1–2% breathing scale + drift

## 8 · Motion rules (imperatives)

1. **Never write "holds motionless."** Write "settles into a gentle ambient idle."
2. **Give every scene one continuous camera move.** Compute the ease over a window longer than the render so it never dies.
3. **No two elements share a start or end time.** Each offset must be shorter than the animation it offsets.
4. **Combine properties only when they say the same thing.** Entrances ease out, exits ease in, moves ease in-out, impacts ease in.
5. **Overshoot transforms only.** Never overshoot a number — it renders a value that was never true.
6. **Move each plane at its distance.** Occlusion sells depth, not blur. One foreground element, not two.
7. **Pick the tempo before the ease.** Showreel = 1.5–4s per idea.
8. **Seed every random.** mulberry32, and quantize holds on the integer frame index, never on seconds.

## 9 · Kill the slideshow

A slideshow = scenes independent + energy uniform. Fix needs **both**: something crosses the boundary (shared element, space, or motion vector) **and** the energy varies (a dwell — a genuine 1.5–2.5s full stop while the point lands, camera resting, world still resolving). Ask for the two properties, and name the tell you are forbidding.

## 10 · Transitions

| Energy | Shader | CSS |
|---|---|---|
| Calm | `cross-warp-morph`, `thermal-distortion` | `transitions-blur`, `transitions-dissolve` |
| Medium | `whip-pan`, `cinematic-zoom` | `transitions-push`, `transitions-cover` |
| High | `ridged-burn`, `glitch`, `chromatic-radial-split` | `transitions-scale`, `transitions-destruction` |

Duration: calm 0.5–0.8s · medium 0.3–0.5s · high 0.15–0.3s. **One primary + one accent.** Never fade out then fade in — the transition *is* the exit.

## 11 · Workhorse slugs

**Code** `code-typing` `code-diff` `code-highlight` `code-scroll` `code-morph` · themes `code-snippet-apple-terminal-<profile>`, `code-snippet-monokai`
**Data** `data-chart` `apple-money-count` `bar-chart-race`
**Maps** `us-map` (choropleth) `us-map-bubble` `us-map-flow` `us-map-hex` `world-map` `spain-map` `nyc-paris-flight`
**Lower thirds** `lt-clean-bar` `lt-bold-block` · cardless over footage: `lt-accent-underline` `lt-side-rule` · bright scenes: `lt-dark-card`
**Social** `x-post` `reddit-post` `spotify-card` `macos-notification` `yt-lower-third`
**Captions** `caption-kinetic-slam` (one word full-frame) `caption-highlight` (TikTok line) `caption-neon-glow` `caption-clip-wipe`
**VFX** `vfx-shatter` `vfx-portal` `vfx-liquid-background` `vfx-iphone-device`
**Polish** `grain-overlay` `vignette` `shimmer-sweep` `parallax-zoom`

## 12 · Pin the runtime

Real depth, lighting, or a camera → **"Three.js via the adapter."** CSS perspective reads flat. Existing `.lottie` / `.json` → **Lottie**, by path. Everything else → say nothing, GSAP is the default.

## 13 · Determinism

`t = frame / fps`. No wall clock, no network at render time, no unseeded randomness, no `async`/`await` in timeline setup. Bake live values in or pass them as variables. Say **"seeded."**

## 14 · Audio

"No narration" ≠ silent. BGM needs a mood **and** a level ("under −18 dB"). Describe symptoms, not filters. Music fighting the VO → ask for a **carve**, not a duck. TTS: HeyGen Starfish → ElevenLabs → local Kokoro (`af_heart` demo, `am_adam` tutorial, `af_sky` marketing).

## 15 · Pace to the voice

**VO-paced reveals: elements land on their spoken cues; the narration never waits for the visuals.** Word timings come free from transcription.

## 16 · Brand

Never say "on-brand." Point at **`frame.md`** (frontmatter = normative hexes and fonts; prose = intent), a site, or a Figma file. Brand is truth for **color and type, not layout** — a 1px border at 0.06 opacity is invisible after H.264. Assets by path; prefer SVG logos. Import Figma tokens *before* components.

## 17 · Density contract

**One focal element at display scale + at least two supporting elements on their own cues + persistent chrome.** Asymmetric 60/40. Display type ≈ 1/10 frame width. Three depth layers. A frame that fills all three roles at t=0 is a poster, not a scene. Name **one spectacle beat** or it gets dropped.

## 18 · Iterate

One variable per render. **Absolute targets** ("dot radius = 25% of row spacing"), never relative nudges. **Freeze what works**: "framing and motion are right — don't touch them." Edit verbs map to attributes: move → `data-start` · trim → `data-duration` · restack → `data-track-index` · front-trim (media only) → `data-media-start` · level → `data-volume`.

## 19 · Output

Default MP4 / 1920×1080 / 30fps / `standard` (visually lossless at 1080p). `draft` while iterating, `high` for the master only. 4K = 4× slower, 3–5× larger, and does nothing for a 1080p `<video>`. Transparency: **MOV = ProRes 4444 for editors · WebM = VP9, browsers only · PNG sequence for compositing.** A full-frame design has nothing to be transparent.

## 20 · Five that bite

1. Compositions **hold their final state** — a literal "hold" is a frozen frame; an explicit fade-out before a cut is a jump cut with a dip.
2. **Never animate a clip's own `opacity`/`display`.** The framework owns clip visibility. Two clips on one `data-track-index` must not overlap.
3. **Render duration comes from `data-duration`, not GSAP timeline length.** Never pad with an empty `tl.set()`.
4. **Never `render` a `/slideshow` deck** — it truncates silently to the first scene. Use `hyperframes present`.
5. **An authored CSS custom property beats a same-named variable.** Override per render with `--variables`, and prove it re-skinned by rendering twice and diffing — a template that never re-skins passes every gate.
