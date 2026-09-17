---
type: reference
status: active
tags: [hyperframes, catalog, blocks, routing-taxonomy, gsap, webgl, html-in-canvas, canonical-reference, video-gen]
relatedTo: [video-gen, hyperframes, hyperframes-docs-mirror, catalog-index]
---

# HyperFrames catalog blocks — routing guide

**All 154 read from source.** This is the map the mechanical index cannot be: blocks grouped by
the *job* they do, with the near-duplicates named and their actual differences proven by diffing
the source rather than the blurbs. Use [catalog-index.md](catalog-index.md) for slug → install
command → variable schema; use this file to decide **which** block, and to find out what will bite
you after you install it.

---

## 1. Read this first — the six facts that change how you pick

**1. 132 of 154 blocks have no variables at all.** Only 22 declare any. For the other 132, "changing
the text" means editing the installed HTML. That is the single biggest determinant of whether a
block is reusable or is a one-off you will fork.

**2. 44 blocks register their timeline under a key that is not their slug — and 27 of those use the
generic `main`.** The docs' own usage snippet tells you to mount `data-composition-id="<slug>"`
while the file declares something else. See §3; it is the most likely reason an installed block
does nothing.

**3. Every block loads GSAP 3.14.2 from `cdn.jsdelivr.net`.** All 154, no exceptions. Twelve also
load `three@0.147.0`; five load `d3@7` + `topojson-client@3.1.0`.

**4. Five blocks fetch map geography over the network at render time.** That contradicts the
framework's own rule ("Never rely on a … render-time network request", `pages/help.md`). They will
fail on an offline render host. See §9.

**5. Eight blocks require the experimental HTML-in-Canvas API** (`layoutSubtree` /
`drawElementImage`). No polyfill exists — one of them says so in its own fallback copy. See §12.

**6. 43 blocks install supporting files; 111 are a single self-contained HTML file.**
`ios26-liquid-glass` pulls 28 files including GLTF models. Cheap to try ≠ cheap to install.

### Shape of the set

| Split | Count |
|---|---|
| Landscape 1920×1080 | 141 |
| Portrait 1080×1920 | 12 |
| Portrait 1440×2560 | 1 (`flowchart-vertical`) |
| Ship a paste-in usage snippet | 45 |
| Source-only (no snippet section) | 109 |
| Single file | 111 |
| Install supporting files | 43 |
| Declare variables | 22 |
| Shortest / longest | `hw-scribble-transition` 2.2 s / `message-thread-reveal` 25.77 s |

---

## 2. The routing taxonomy

Seventeen groups, a strict partition — every block appears exactly once.

| Group | n | Reach for it when |
|---|---|---|
| **A1** Terminal windows | 12 | You want a macOS Terminal running a command |
| **A2** Editor windows | 12 | You want a full VS Code workbench typing code |
| **A3** Code motion | 9 | You have code and want *one* thing to happen to it |
| **B1** Shader transitions | 14 | You want a GPU scene-to-scene effect — but read §7 first |
| **B2** DOM transition packs | 13 | Same, CSS/DOM-based, several variants per pack |
| **B3** Overlay transitions | 3 | You want to cut *underneath* a covering overlay |
| **C** Lower thirds | 14 | A name and role on screen over footage |
| **D** Vertical ad templates | 10 | A portrait story that plays out over 7–26 s |
| **E** Social platform cards | 7 | One recognisable platform card as an overlay |
| **F** Maps | 8 | Geography, choropleth, or a route |
| **G** Charts & diagrams | 7 | Numbers or a decision tree |
| **H** Generative / parametric | 11 | A background or camera move you tune by number |
| **I** HTML-in-Canvas 3D | 13 | Live DOM as a WebGL texture — heaviest tier |
| **J** Media-treatment overlays | 6 | Dress footage the host owns |
| **K** Hand-drawn | 5 | Marker/sketch register |
| **L** Minimal presentation | 2 | Restrained corporate emphasis |
| **M** Finished spots | 8 | A whole piece to study or strip for parts |

---

## 3. The id trap — read before you install anything

The pattern: the docs' **Usage** snippet says mount `data-composition-id="<slug>"`. The installed
file declares a different id internally and registers its timeline under **that** key.

```html
<!-- what the docs tell you to paste for code-snippet-dark-plus -->
<div data-composition-id="code-snippet-dark-plus"
     data-composition-src="compositions/code-snippet-dark-plus.html" ...></div>
```

```js
// what the installed file actually does
window.__timelines["vscode-dark-plus"] = ...
window.createVSCodeThemeComposition("vscode-dark-plus", { id: "dark-plus", ... });
```

**44 of 154 blocks have this mismatch.** Three sub-cases:

| Sub-case | Blocks | Registers as |
|---|---|---|
| The generic `main` | all 14 B1 shader transitions + all 13 B2 transition packs | `main` |
| `vscode-` prefix | all 12 A2 editor themes | `vscode-<theme>` |
| Internal project name | `vfx-iphone-device`, `vfx-liquid-glass`, `vfx-magnetic`, `vfx-portal`, `vfx-shatter` | `devices-canvas`, `liquid-glass`, `magnetic-cursor`, `portal-transition`, `glass-shatter` |

> **The 27 `main` blocks cannot coexist.** Install two shader transitions or two transition packs
> into one project and they collide on both `data-composition-id="main"` and
> `window.__timelines["main"]`. Rename one before adding the second. ⚑ [4/5] — read directly from
> source; I could not execute a render to observe the failure, but both the DOM selector and the
> timeline registry key are literal duplicates.

---

## 4. A1 — Terminal windows (12)

Full slugs: `code-snippet-apple-terminal-basic` · `code-snippet-apple-terminal-clear-dark` ·
`code-snippet-apple-terminal-clear-light` · `code-snippet-apple-terminal-grass` ·
`code-snippet-apple-terminal-homebrew` · `code-snippet-apple-terminal-man-page` ·
`code-snippet-apple-terminal-novel` · `code-snippet-apple-terminal-ocean` ·
`code-snippet-apple-terminal-pro` · `code-snippet-apple-terminal-red-sands` ·
`code-snippet-apple-terminal-silver-aerogel` · `code-snippet-apple-terminal-solid-colors`

**All twelve are the same composition**: a 1400×700 window on a 1920×1080 stage, traffic lights,
type-a-command → reveal output line by line → blinking cursor. All 12 s. All ~8 KB. All correctly
keyed to their own slug.

They are the **macOS Terminal.app built-in profiles**. What actually differs, proven by diffing all
11 against `basic`:

1. **The palette** — window background, titlebar, text colour, shadow tint.
2. **The demo command and its fake output** — not just a skin.
3. **Minor timing offsets** (line stagger 0.08 s vs 0.1 s, blink schedule).

| Block | Command it runs | Prompt / window |
|---|---|---|
| `basic` | `ls -la` | `user@Mac ~ %` · light grey, the only one with a `Last login:` line |
| `clear-dark` | `npm audit` | translucent dark over gradient |
| `clear-light` | `git log --oneline -8` | translucent light, `backdrop-filter: blur` |
| `grass` | `npm test` | black + `#00c100` green |
| `homebrew` | `brew outdated` | black + `#00cf00`, brighter than grass |
| `man-page` | `man curl` | **window retitled `man — 80×24`**, adds `.indent`/`.section` classes |
| `novel` | `python3` | sepia `#c9a86c` paper |
| `ocean` | `docker ps` | blue `#224fbe` |
| `pro` | `npm run build` | black + grey `#bbbbbb`, prompt `user@Mac myapp %` |
| `red-sands` | `curl -s api.example.com/status \| jq` | oxblood `#7b140e` |
| `silver-aerogel` | `df -h && vm_stat` | neutral graphite |
| `solid-colors` | `npx hyperframes init my-video` | purple `#4c0099` — the on-brand one |

**Routing:** pick by *palette against your scene*, then rewrite the command. Because the command is
hardcoded (`const command = "ls -la"`) and the output is static `<span class="output-line">`
markup, the demo content is a starting point in every case. If your video is about HyperFrames
itself, `solid-colors` already runs the right command.

**Limit:** zero variables. Command, output lines, prompt string, window title all live in source.

---

## 5. A2 — Editor windows (12)

Full slugs: `code-snippet-dark-2026` · `code-snippet-dark-modern` · `code-snippet-dark-plus` ·
`code-snippet-high-contrast` · `code-snippet-high-contrast-light` · `code-snippet-light-2026` ·
`code-snippet-light-modern` · `code-snippet-light-plus` · `code-snippet-monokai` ·
`code-snippet-solarized-light` · `code-snippet-visual-studio-dark` ·
`code-snippet-visual-studio-light`

A **full VS Code workbench**: activity bar with SVG icons, explorer tree, editor tabs, breadcrumbs,
per-character typing with a caret that tracks the frontier, active-line highlight, integrated
terminal panel with mock test output, status bar, and a 3D perspective tilt at the end. 11 s,
~40 KB each, plus 1 supporting file under `assets/`.

**These twelve are one engine, twelve pre-bound calls.** The whole workbench plus a
`applyTheme(root, theme)` / `setVar` system ships inside *every* file; each one ends with a single
call passing its own theme object:

```js
window.createVSCodeThemeComposition("vscode-monokai", {
  id: "monokai", label: "Monokai", sourceFile: "monokai-color-theme.json",
  ui: {...}, tokens: { comment:…, keyword:…, function:…, string:…, … }
});
```

Colours are transcribed from the real `microsoft/vscode` built-in theme JSON, named per block in
`sourceFile` (`dark_plus.json`, `hc_black.json`, `monokai-color-theme.json`, …).

**Consequence worth knowing:** install **one**, then change the theme object in that one call to get
any of the other eleven. Installing all twelve gets you twelve copies of the same engine. The
function also accepts a **string** id and looks it up in `window.VSCODE_THEME_REGISTRY` — but no
block defines that registry, so pass the object. ⚑ [3/5] the registry may live in the unshown
supporting `assets/` file; the docs never display it.

**Routing between them is purely light/dark/contrast:**

| Need | Use |
|---|---|
| The default dark everyone recognises | `dark-plus` |
| Newest dark / light | `dark-2026`, `light-2026` |
| Current VS Code default pairing | `dark-modern`, `light-modern` |
| Legacy VS Code look | `visual-studio-dark`, `visual-studio-light` |
| Accessibility / projector | `high-contrast`, `high-contrast-light` |
| Warm, distinctive | `monokai` (dark), `solarized-light` (light) |
| Plain light | `light-plus` |

**Two real limits:**

- **The demo code is identical in all twelve** — a Python "functional toolkit" (`pluck_deep`, a `reduce` lambda). Verified by md5 of the `codeLines` array across the family: same hash.
- **The code is hand-tokenised.** There is no syntax highlighter at runtime; `codeLines` is an array of `{ text, token }` pairs. To show *your* code you must re-author that token array by hand, token by token. This is the least obvious and most expensive limit in the entire catalog.

---

## 6. A3 — Code motion (9)

One code panel, one thing happening to it. All correctly slug-keyed except the three WebGL ones,
which register dynamically. All share a chrome (`bg-glow`, traffic `dot r/y/g`, JetBrains Mono, a
filename tab) and use **Shiki-generated token spans**, so — like A2 — the displayed code is
pre-tokenised output, not live highlighting.

| Block | Technique | Reach for it instead of its neighbours when |
|---|---|---|
| `code-typing` | DOM, 5 s | The point is *writing* — token-streamed reveal with a tracking caret |
| `code-highlight` | DOM, 5 s | The point is **one line** — a sweep band lights it while the rest dims |
| `code-scroll` | DOM, 6 s, 56 KB | The file is **long** — camera scrolls to bring a target line to centre |
| `code-diff` | DOM, 6 s | The point is a **change** — red lines collapse, green lines expand |
| `code-morph` | DOM, 7 s | The point is a **refactor** — tokens glide between positions (Shiki Magic Move re-driven as a paused GSAP timeline) |
| `code-snippet-flight` | DOM, 6 s | Several snippets **assemble** into one program (block-level FLIP) |
| `code-3d-extrude` | three.js, 8 s | You want real depth — lit, bevelled 3D slab rotating in space |
| `code-particle-assemble` | three.js, 8 s | Spectacle — GPU points fly to the exact glyph pixels |
| `code-shader-dissolve` | three.js, 7 s | Code "compiles into existence" from seeded noise |

**Near-duplicate warning:** `code-highlight` and `code-scroll` both spotlight a line. Use
`code-highlight` when the line is already on screen; `code-scroll` when it is not. `code-morph` and
`code-diff` both show an edit — `code-diff` shows it as a *reviewable diff*, `code-morph` shows it
as a *continuous transformation*.

**Limit:** all nine have zero variables; the code, filename and theme are in source.

---

## 7. B1 — Shader transitions (14) — not what the name suggests

`domain-warp-dissolve` (01) · `ridged-burn` (02) · `whip-pan` (03) · `sdf-iris` (04) ·
`ripple-waves` (05) · `gravitational-lens` (06) · `cinematic-zoom` (07) ·
`chromatic-radial-split` (08) · `glitch` (09) · `swirl-vortex` (10) · `thermal-distortion` (11) ·
`flash-through-white` (12) · `cross-warp-morph` (13) · `light-leak` (14)

A complete numbered set (the files literally render "09 / 14"). 4 s, 1920×1080, ~13–14 KB each.

> **These are demo cards, not drop-in transitions.** Each file is a two-panel layout: the effect
> runs in a **1200 px** left panel; the right **720 px** panel is a spec card showing the effect
> name, a suggested prompt, and a prose description. It ships with its own dummy "SCENE A" /
> "SCENE B" pair. It does not transition *your* content.

**How it works, and why that matters.** The two dummy scenes are rasterised to a texture by a
hand-rolled DOM-to-canvas painter inside the file. That painter walks `querySelectorAll("*")`,
fills each element's background colour, and draws direct text nodes **centred** in their box. It
handles no images, no gradients, no borders, no real text layout. Then the two textures feed the
fragment shader.

So repurposing one against real content means replacing that capture path, not just swapping the
scene divs. Treat these as **a shader library to lift from**, plus a preview of what each looks
like. There is a graceful fallback: no WebGL → `console.warn` and an empty paused timeline.

| Effect | What the shader actually does |
|---|---|
| `domain-warp-dissolve` | Cascaded `fbm(p + fbm(p))` displaces both scenes; iridescent cosine-palette edge glow |
| `ridged-burn` | `abs(noise)` sharp lightning-crack edges; blackbody gradient, ember sparks |
| `whip-pan` | Horizontal slide with **10-sample directional motion blur** |
| `sdf-iris` | Aspect-corrected circle SDF from centre; triple onion-ring glow |
| `ripple-waves` | Exponential sine waves, sharp crests; scenes ripple in opposite phases |
| `gravitational-lens` | Warp toward a gravity well, chromatic aberration, event-horizon darkening |
| `cinematic-zoom` | Zoom-blur with per-channel radial offset; from zooms out, to zooms in |
| `chromatic-radial-split` | RGB channels separate and converge radially |
| `glitch` | Scan lines, block scramble, chromatic aberration, flicker, posterisation |
| `swirl-vortex` | Opposing swirls on an FBM-warped spiral path |
| `thermal-distortion` | FBM heat shimmer rising from the bottom, warm haze |
| `flash-through-white` | Both scenes brighten to a white midpoint — **for dark backgrounds where a dip-to-black is invisible** |
| `cross-warp-morph` | Shared FBM field displaces both scenes in opposite directions |
| `light-leak` | Beer-Lambert falloff, ACES tone mapping, directional flare streak |

**Picking between the close ones:** `flash-through-white` vs `light-leak` — flash is a hard
white-out cut, light-leak is a warm organic bleed. `swirl-vortex` vs `domain-warp-dissolve` — swirl
is rotational, domain-warp is turbulent. `cinematic-zoom` vs `chromatic-radial-split` — both radial,
but zoom moves scale and split moves colour channels.

---

## 8. B2 / B3 — Transition packs and overlay transitions (13 + 3)

**B2 packs** are the DOM/CSS counterpart to B1, and share the same demo-card framing and the same
`main` id. Each pack holds several named variants shown in sequence, which is why durations run
11–24 s: they are **showcases**, not a single usable transition.

| Pack | Variants it contains |
|---|---|
| `transitions-dissolve` (24 s) | Crossfade · Blur Crossfade · Focus Pull · Color Dip (to black) |
| `transitions-push` (24 s) | Push Slide · Vertical Push · Elastic Push (overshoot) · Squeeze |
| `transitions-blur` (20 s) | Blur Through · Directional Blur (motion skew) · Calm Blur Through |
| `transitions-other` (20 s) | Flash Cut · Gravity Drop · Morph Circle |
| `transitions-cover` (21 s) | Horizontal Blinds · Vertical Blinds · Staggered Blocks |
| `transitions-light` (21 s) | Light Leak · Film Burn · Overexposure Burn |
| `transitions-radial` (20 s) | Circle Iris · Diamond Iris · Diagonal Split |
| `transitions-scale` (15 s) | Zoom Through · Zoom Out |
| `transitions-mechanical` (15 s) | Shutter (close/open) · Clock Wipe |
| `transitions-distortion` (21 s) | Glitch · Chromatic Aberration · Ripple |
| `transitions-destruction` (14 s) | Page Burn |
| `transitions-grid` (11 s) | Grid Dissolve |
| `transitions-3d` (11 s) | one 3D perspective flip/rotate |

**Overlaps to know:** `transitions-light` duplicates B1's `light-leak`; `transitions-distortion`
duplicates B1's `glitch`; `transitions-radial` overlaps B1's `sdf-iris`. Choose the **B2** version
when you want CSS/DOM and no WebGL dependency; choose **B1** when you want the GPU look.

**B3 — overlay transitions** are the genuinely reusable ones, because they are designed for the host
to cut underneath while covered:

| Block | Duration | Mechanism |
|---|---|---|
| `hw-scribble-transition` | 2.2 s | Scribble bands accumulate to a solid backstop, host cuts beneath, scribble clears |
| `mk-clone-wall-transition` | 2.4 s | Tiled word wall covers the frame, inverts via difference blending, clears |
| `beat-freeze-cut` | 6 s | Beat-driven speed ramp → freeze-frame hit → hard cut, for music-led promos |

> **If you want an actual transition to use, start in B3, not B1 or B2.**

---

## 9. F — Maps (8)

| Block | Projection / data | Deps | Offline-safe |
|---|---|---|---|
| `us-map` | Choropleth, staggered state reveals, gradient legend | d3 + topojson | **No** |
| `us-map-bubble` | Proportional city markers + connection lines | d3 + topojson | **No** |
| `us-map-flow` | Origin-destination arcs over a base map | d3 + topojson | **No** |
| `world-map` | Natural Earth, country-by-country, rotating globe inset | d3 + topojson | **No** |
| `spain-map` | Conic conformal, by autonomous community | d3 + topojson | **No** |
| `us-map-hex` | Equal-weight hex tile per state | **none** | **Yes** |
| `north-korea-locked-down` | Bitmap map + red scribble + editorial wash | none (`assets/korea-map.png`) | Yes |
| `nyc-paris-flight` | Bitmap map + SVG great-circle path + SFX | none (`assets/map-nyc-paris.png`) | Yes |

> **The five d3 maps fetch their geography at render time:**
> `https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json`,
> `world-atlas@2/countries-110m.json`, `es-atlas@0.6.0/es/autonomous_regions.json`.
> These are the **only 5 blocks in the catalog that make a runtime network request**, and
> `pages/help.md` explicitly says never to depend on one during rendering. On a sealed render host
> they fail. Vendor the topojson locally, or use `us-map-hex`.

**Routing:** value per state → `us-map` (geographic truth) or `us-map-hex` (equal visual weight for
small states, and no network). Cities → `us-map-bubble`. Movement between cities → `us-map-flow`
(many) or `nyc-paris-flight` (one hero route, with sound). Countries → `world-map`. One country
called out editorially → `north-korea-locked-down` is the template even though it is named for its
demo subject.

---

## 10. C — Lower thirds (14)

Eleven `lt-*` blocks are one family: **4.8 s, 1920×1080, ~4 KB, zero variables**, and all carrying
the same placeholder — `Dr. Maya Chen` / `Host — Neuroscientist`. They differ in card treatment,
font, and entrance. Tagged `podcast` `interview`.

| Block | Card | Font | Entrance | Pick it when |
|---|---|---|---|---|
| `lt-clean-bar` | White card + accent tab | Montserrat | clip-wipe | Default safe choice |
| `lt-dark-card` | Charcoal card | Montserrat | slide-up + drawn underline | Footage is **bright** |
| `lt-soft-pill` | Rounded white pill + status dot | Montserrat | `back.out(1.7)` scale-pop | Friendly, informal |
| `lt-bold-block` | Solid dark block | Archivo Black | wipe + slam, `back.out(2)` | High-energy |
| `lt-color-block` | Accent-colour block | League Gothic | slide with overshoot | High-energy, colour-led |
| `lt-stack-bars` | Two bars, opposing wipes | Archivo Black | `power4.out` | Name and role as separate hits |
| `lt-accent-underline` | **Cardless** | Oswald | rise + rule draws L→R | Over footage, minimal |
| `lt-side-rule` | **Cardless**, vertical bar | League Gothic | rise | Over footage, minimal |
| `lt-kicker-name` | **Cardless** + eyebrow tag | Archivo Black | `back.out(2)` | You need an episode/segment label |
| `lt-mask-reveal` | **Cardless** | Montserrat | accent sweep clip-reveals the name | You want the reveal itself to be the motion |
| `lt-neon-border` | Rounded panel, travelling light arcs | Inter | arcs snap corner to corner | **The only parametric one — 9 variables** |

**`lt-neon-border` is the exception worth knowing:** `name`, `role`, `accent`, `movement`
(enum: step/glide), `speed`, `cornerRadius`, `thickness`, `arcLength`, `glow`. If you need a lower
third you can drive from data or reuse across episodes without editing HTML, this is the only one in
the family that qualifies.

**The other three in the group:**

| Block | Why not an `lt-*` |
|---|---|
| `lower-third-bild` | News/tabloid style, tight-fit text boxes, white bar with red drop-shadow. **2 variables** (`TXT_MAIN_1_Line`, `TXT_SUB`) and bundled Barlow Condensed woff2. German-press register |
| `yt-lower-third` | Subscribe CTA with avatar + follower count + subscribe/subscribed toggle — a **conversion** element, not an identification one |
| `news-ticker` | Broadcast ribbon with LIVE label and a scrolling crawl — for headlines, not people |

---

## 11. D / E — Vertical ad templates (10) and social cards (7)

### D — the portrait story blocks

These are the **most variable-rich blocks in the catalog** and the ones actually built for reuse.
All 1080×1920 except `thread-message-stack`.

| Block | Length | Vars | The story it tells |
|---|---|---|---|
| `message-thread-reveal` | 25.8 s | **21** | A full SMS conversation — bubbles, typing indicators, a link card, emoji reactions, delivered receipts, thread scrolling beat by beat, closing card |
| `notes-reveal` | 24.9 s | 9 | A note typed character by character in a notes app, then a hand-lettered paper card with a ticked checklist |
| `claude-exchange` | 21.4 s | **14 ⚠ undocumented** | Claude-style: prompt → search step → reasoning → streamed answer with citations |
| `ai-chat-reveal` | 19.3 s | 13 | Generic AI chat: keyboard rises, question sent, reply streams on a token rhythm, branded closing card |
| `chatgpt-exchange` | 14.9 s | **22 ⚠ undocumented** | ChatGPT-style: prompt → streamed answer → a comparison **table** assembles → scroll back |
| `notification-cascade` | 14 s | 10 | Phone notifications stack up, each pushing the pile down, then lift away into a closing card |
| `slack-notification-ad` | 12 s | **25 ⚠ undocumented** | Lock screen filling with escalating Slack video requests, then the payoff |
| `heygen-avatar-promo-card` | 10 s | **17 ⚠ undocumented** | Offer card: avatar mosaic + promo typography + code callout. Installs 15 files |
| `share-sheet-carousel` | 7.2 s | 11 | Share sheet springs up, cycles previews on a fast cut rhythm, ends on an accept tap |
| `thread-message-stack` | 8 s | 0 | Landscape conversation stack, "source-owned editable" — the one you edit rather than parameterise |

> **⚠ The four marked blocks declare variables in `<html data-composition-variables>` but their
> published page renders no Variables table.** `chatgpt-exchange` (22), `claude-exchange` (14),
> `heygen-avatar-promo-card` (17), `slack-notification-ad` (25) — 78 tunable inputs invisible to
> anyone reading the docs page. Read the attribute in the installed file to see them. (Confirmed by
> the orchestrator against all 372 catalog pages; the index now records a `var_source` field.)

**Routing:** an SMS story → `message-thread-reveal`. An AI product story → `chatgpt-exchange` if the
payoff is a **table/comparison**, `claude-exchange` if it is **research and citations**,
`ai-chat-reveal` if you want it unbranded. Notification pressure → `slack-notification-ad` (work
pressure) or `notification-cascade` (accumulating good news). A personal/handwritten register →
`notes-reveal`.

### E — social platform cards

One recognisable card, 5 s unless noted, all zero variables — placeholder copy is in source.

| Block | Dims | Ships with |
|---|---|---|
| `x-post` | 1920×1080 | `@Hyperframes`, engagement counts 2.3K/10.9K/150K |
| `reddit-post` | 1920×1080 | `r/hyperframes`, 4.2k upvotes, "Prompt to change this title…" |
| `spotify-card` | **1080×1920** | Now-playing card, album art, progress bar |
| `macos-notification` | 1920×1080 | Banner + app icon, "Prompt to replace this title" |
| `yt-comment-card` | 1920×1080 | Comment typing on with avatar pop + likes row |
| `instagram-follow` | **1080×1920** | Profile card, 47.5K followers, follow→following toggle |
| `tiktok-follow` | **1080×1920** | Same pattern, 1,999 followers |

**Near-duplicates:** `instagram-follow`, `tiktok-follow` and `yt-lower-third` are the same
composition — DM Sans, shared `assets/avatar.jpg`, `elastic.out(1, 0.4)` on the button, a
follow/subscribe toggle. They differ **only** in platform chrome and orientation: the first two are
portrait 4.5 s, `yt-lower-third` is landscape 4.5 s. Pick by platform and aspect, nothing else.

---

## 12. I — HTML-in-Canvas and 3D (13) — the heaviest tier

Two distinct dependency stories that the index does not separate.

**(a) Eight blocks call `layoutSubtree` / `drawElementImage` — the experimental HTML-in-Canvas API.**
`ios26-liquid-glass` · `macos-tahoe-liquid-glass` · `vfx-iphone-device` · `vfx-liquid-background` ·
`vfx-liquid-glass` · `vfx-magnetic` · `vfx-portal` · `vfx-shatter`

`vfx-magnetic` states the constraint in its own on-screen copy: *"Impossible without native
drawElementImage — no polyfill exists."* `vfx-portal` and `vfx-shatter` ship a visible
**"HTML-in-Canvas Required"** fallback panel. Confirm your render browser supports it before
building on these.

**(b) Four blocks need a locally-installed runtime**, `lib/liquid-glass.iife.js` — not a CDN, so it
must survive the install: `liquid-glass-context-menu` · `liquid-glass-media-controls` ·
`liquid-glass-notification` · `liquid-glass-widgets`. These four are one family (frosted glass
panels over an aurora shader background) differing only in the UI they show: a context menu, media
controls, notification cards, stat widgets/pill chips.

| Block | Duration | Install weight | What it is |
|---|---|---|---|
| `ios26-liquid-glass` | 15 s | **28 files** (GLTF `models/`, `lib/`, `assets/icons/`) | 3D iPhone, full iOS 26 home screen, shader wallpaper, dock, glass notifications |
| `macos-tahoe-liquid-glass` | 15 s | **18 files** (models, wallpapers, icons) | 3D MacBook, glass menu bar, Finder window, dock, cinematic camera move |
| `vfx-iphone-device` | 15 s | 4 GLTF files | iPhone 15 Pro Max **and** MacBook with live HTML screens, morphing glass lens, 360° turntable |
| `vfx-liquid-background` | 12 s | 1 | Vertex displacement on a subdivided plane; HTML floats above a rippling fluid |
| `vfx-shatter` | 12 s | 1 | A live page shatters into glass shards |
| `vfx-portal` | 10 s | 1 | One page opens as a portal into another |
| `vfx-liquid-glass` | 20 s | 1 | Liquid-glass parallax over marketing panels |
| `vfx-magnetic` | 15 s | 1 | WebGL2 gaussian warp + chromatic aberration pulling pixels toward a cursor |
| `vfx-text-cursor` | 8 s | 1 | Text reveal with cursor glow and chromatic shadow rays (canvas post-processing, **no** layoutSubtree) |

**Routing:** need a phone in frame → `vfx-iphone-device` (4 files, also does the MacBook) before
`ios26-liquid-glass` (28 files). Need the OS itself to be the subject → `ios26-liquid-glass` or
`macos-tahoe-liquid-glass`. Need glass UI **without** 3D or GLTF → the four `liquid-glass-*` panels.

---

## 13. H — Generative / parametric (11) — the genuinely reusable tier

If §1's headline is "132 blocks have no variables", this group is the counterweight: these are
parameterised by physically meaningful numbers, and several state their maths in the description.
**This is where to look first when you want something you can drive rather than fork.**

| Block | Vars | Parameters that matter |
|---|---|---|
| `rack-focus` | 11 | `nearfocus`, `farfocus`, `focallength`, `aperture` (f-number), `blades` (bokeh shape), `catseye`, `pullstart`, `pullduration`, `pullease` — a real focus pull; carries its own two-depth content |
| `halftone-field` | 11 | `frequency`, `speed`, `cellSize`, `gamma`, 4 palette stops, `quantize` — LED-wall plasma **built to run under type** |
| `gallery-tunnel` | 10 | `images` (comma-separated paths), `imageMix`, `speed`, `palette`, `grid`, `fill`, `fog` — infinite corridor of panels; **accepts your images** |
| `weight-wave` | 9 | `text`, `weightFrom`/`weightTo`, `crestWidth`, `sweepSpeed`, `slant`, `direction` — a crest of thickness travelling a headline via the `wght`/`slnt` **variable-font axes**, not transforms |
| `cosmic-orb` | 9 | `hue`, `accent`, `spin`, `stars`, `glow`, `size`, `pulse`, `pulseEnvelope` — **beat-pulse envelope takes comma-separated samples**, so it can be driven from audio |
| `vfx-anamorphic-flare` | 8 | `intensity`, `threshold`, `streakLength`, `tint`, `bloomRadius`, `emitters` — measured constants: 0.3 high-pass, 80 horizontal taps at quarter res, `0x7a8aff` tint |
| `oscilloscope-trace` | 7 | `waveform` (enum), `frequency`, `amplitude`, `persistenceMs` (phosphor tau), `sweepRate`, `dataSeries` — **`dataSeries` plots your own numbers** |
| `spiral-galaxy` | 7 | `stars`, `arms`, `rate`, `glow`, `size`, `core`/`rim` colour — 20,000 additive sprites, seeded once and **solved directly from time so any frame renders standalone** |
| `camera-dolly-zoom` | 4 | `direction` (enum), `strength`, `subjectDistance`, `easing` — focal length solved from `d · tan(fov/2) = const` every frame |
| `mk-background` | 0 | Two drifting radial blobs, rounded-card bar mask, optional frosted mode |
| `yt-lcd-background` | 0 | Scanlines with drift, pixel grid, static grain, chromatic-fringe title |

**`spiral-galaxy`'s note is the one to generalise:** solving from time rather than accumulating means
every frame is independently renderable — exactly what the framework's seek-safe contract requires.
Blocks that integrate state frame-over-frame are the ones that break under scrubbing.

**Routing:** background under text → `halftone-field` (says so explicitly) or `mk-background`
(quieter). Hero space visual → `spiral-galaxy` (structured) or `cosmic-orb` (bubble/orb, beat-
reactive). Your images in motion → `gallery-tunnel`. A camera move as the effect → `rack-focus`
(focus) or `camera-dolly-zoom` (vertigo). Instrument/retro data → `oscilloscope-trace`. Lens
character over anything → `vfx-anamorphic-flare`.

---

## 14. G, J, K, L, M — the remainder

### G — Charts and diagrams (7)

| Block | Vars | Use it for |
|---|---|---|
| `bar-chart-race` | 10 | Ranked bars overtaking over time. `series` takes `Name: v1, v2, …` **one per line**; `periods` comma-separated. The most data-drivable block in the catalog |
| `data-chart` | 0 | Static-series bar **+** line combo, NYT-style typography, value labels, source line |
| `mk-line-graph` | 0 | One or two series drawing on, dots popping, labels riding the draw front |
| `mk-progress-stat` | 0 | A single big numeral counting up with a progress track |
| `split-flap-board` | 5 | Solari departure board — `boardText`, `flapAlphabet`, `flipDuration`, `cellStagger`, `cellCount`. A **mechanical** text reveal, not a fade |
| `flowchart` | 0 | Decision tree, sticky-note nodes, cursor interaction, **deliberate typing correction** ("Pythom" → "Python") |
| `flowchart-vertical` | 0 | Same, portrait **1440×2560** — the only block at that size |

**Choosing:** ranking over time → `bar-chart-race` (the only one you can feed real data without
editing HTML). Trend → `mk-line-graph` (minimal) or `data-chart` (editorial, with a second axis).
One number → `mk-progress-stat`.

### J — Media-treatment overlays (6)

These **attach to a host composition** rather than standing alone. Four of them register their
timeline dynamically and print a diagnostic if unhosted — e.g. *"Camcorder HUD could not find its
composition host"*. That message is the fastest way to recognise the class.

| Block | Dresses footage with |
|---|---|
| `camcorder-hud` | REC dot, battery, editable date, timeline-driven counter |
| `editorial-flash-overlay` | Finite neutral-warm light layers for a seek-safe camera-flash cut |
| `organic-light-leak-overlay` | Amber/red/gold leak layers for memory beats |
| `freeze-frame-dressing` | Paper, tape and flash dressing for a freeze-frame or cutout subject |
| `yt-vertical-fill` | Fills a widescreen frame from portrait media via blurred-scale, mirror, or copy side fills |
| `mk-placeholder-grid` | N-up rounded media grid (2-up, 3-up, 4-up, 3×2, hero+two) with per-cell inside-scale framing |

> `hw-frame` and `yt-vertical-fill` both note in their own descriptions: *images live inside the
> block; keep live footage in the host.*

### K — Hand-drawn (5)

One marker/sketch register, all bundling a handwriting font under `assets/fonts/`, all with correct
slug ids, several "boiling" (frame-to-frame line jitter).

`hw-title` (display text, word-by-word highlight sweep, seeded squiggle underline) ·
`hw-text-cloud` (speech bubble with positionable tail, per-character typing) ·
`hw-path-text` (handwriting flowing along any SVG path — **the path is the only geometry input**) ·
`hw-pipeline` (wobbled boxes + curved connectors drawn from a node list) ·
`hw-frame` (media in a hand-drawn border with corner doodles and a caption).

`hw-pipeline` vs `flowchart`: same job, opposite register — sketch vs sticky-note UI.

### L — Minimal presentation (2)

`mk-callout-highlight` — a sentence whose **word-by-word emphasis is driven by a single scalar**, so
you tween one value to sync highlighting to a voiceover. The karaoke/caption primitive.
`mk-specs-list` — staggered spec rows with an accent underline sweep, light and dark schemes.

### M — Finished spots (8)

Complete pieces. Study them or strip them for parts; none is a component.

| Block | What it is |
|---|---|
| `ui-3d-reveal` | 13 s, **100 KB — the largest block**. Perspective 3D reveal of a full design-tool UI |
| `blue-sweater-intro-video` | 12 s creator intro resolving into an X follow card. Bundles SFX |
| `vpn-youtube-spot` | 7 s app-store-find-and-install insert with SFX |
| `app-showcase` | 5.5 s fitness app, three floating phone screens |
| `apple-money-count` | 5 s counter $0→$10,000, green flash, money burst, `assets/sfx-production.wav` |
| `logo-outro` | 6 s piece-by-piece logo assembly, glow bloom, tagline, URL pill |
| `yt-logo-intro` | 6 s logo stamp on a lined board with an accent arrow chip |
| `yt-prism-title` | 6 s display title on a **transparent root** — usable as an overlay |

**Four blocks ship sound**: `apple-money-count`, `blue-sweater-intro-video`, `nyc-paris-flight`,
`vpn-youtube-spot` (tagged `sfx`). They are the only blocks in the catalog that bring their own
audio.

---

## 15. Gotchas and constraints

1. **All 154 require `cdn.jsdelivr.net`** for GSAP 3.14.2. No block is dependency-free.
2. **27 blocks share `data-composition-id="main"`** and cannot coexist without renaming (§3).
3. **44 blocks register a timeline key ≠ slug** while their docs snippet uses the slug (§3).
4. **5 blocks fetch geography at render time** — breaks the framework's own offline-render rule (§9).
5. **8 blocks need the experimental HTML-in-Canvas API**; no polyfill exists (§12).
6. **4 blocks need a local `lib/liquid-glass.iife.js`** that must survive install (§12).
7. **132 of 154 have no variables.** Reuse means editing source.
8. **4 blocks have variables the published page never shows** — 78 hidden inputs (§11).
9. **A2's displayed code is hand-tokenised.** No highlighter runs; changing the code means rewriting a `{text, token}` array by hand (§5).
10. **A1's command and output are hardcoded strings** in the timeline script and the markup (§4).
11. **B1's 14 "transitions" do not transition your content** — they carry dummy scenes and a toy DOM-to-canvas rasteriser that handles only background colours and centred text (§7).
12. **B2's packs are multi-variant showcases**, which is why they run 11–24 s. They are not one transition each (§8).
13. **`ios26-liquid-glass` installs 28 files**; `macos-tahoe-liquid-glass` 18; `heygen-avatar-promo-card` 15.
14. **All 11 `lt-*` blocks ship the same placeholder name** (`Dr. Maya Chen` / `Host — Neuroscientist`) — an unedited install is visibly a template.
15. **J-group overlays fail visibly when unhosted**, printing "could not find its composition host".
16. **109 of 154 pages have no usage-snippet section** — you get the full source file and must write the mount yourself.
17. **`flowchart-vertical` is 1440×2560**, the only block not at 1920×1080 or 1080×1920.
18. **`flowchart`'s "Pythom" is deliberate** — the block animates a typing correction. Not a typo to fix.
19. **`vfx-liquid-glass`, `vfx-magnetic`, `vfx-portal`, `vfx-shatter`, `vfx-iphone-device` carry two composition ids each** — the internal one wins.
20. **Blocks whose description names a demo subject are still templates** — `north-korea-locked-down`, `nyc-paris-flight`, `blue-sweater-intro-video` are patterns, not fixed content.

### Variable-coverage gaps — where the declared variables miss the obvious

Blocks that *do* have variables but leave something a user would plainly want to change locked in source:

- **`ai-chat-reveal`** (13 vars) — every string is exposed, but not the **accent/brand colour**, the chat bubble styling, or the 19.33 s pacing. You can rewrite the words, not re-brand it.
- **`message-thread-reveal`** (21 vars) — exposes every message and the closing card, but **not the emoji reaction set styling, bubble colours, or the phone chrome**.
- **`notification-cascade`** (10 vars) — four messages exposed; the **number** of notifications is not, so a five-notification version means editing source.
- **`split-flap-board`** (5 vars) — `cellCount` and `flapAlphabet` are exposed but **colour is not**; the board's palette is CSS-only.
- **`bar-chart-race`** (10 vars) — takes real data and an `accent`, but **not the bar colour ramp per series**, so multi-series colour coding needs source edits.
- **`camera-dolly-zoom`** (4 vars) — the move is fully parametric, but the **subject and background content are hardcoded**, so applying it to your own scene is a source job.
- **`lt-neon-border`** (9 vars) — the best-parameterised lower third, yet **font family is not a variable** while `accent`, `glow` and `thickness` are.
- **`gallery-tunnel`** (10 vars) — accepts your images, but **not per-image timing**; contribution is by fill rate only.
- **`heygen-avatar-promo-card`** (17 vars) — exposes 5 colour tokens and all copy, but **not the avatar mosaic images**, which are among its 15 installed assets.

---

## 16. Open questions

1. **Does the composition-id mismatch actually break at runtime, or does the host resolve by `data-composition-src`?** The mismatch is certain from source; the failure mode is not. This is the single highest-value thing to test — it affects 44 blocks.
2. **What is in the `assets/` supporting file the 12 A2 editor blocks install?** Never shown in the docs. It may hold `VSCODE_THEME_REGISTRY`, which would make the string-id path work.
3. **Is `window.VSCODE_THEME_REGISTRY` defined anywhere shipped?** Referenced in every A2 block, defined in none of them.
4. **Do the 5 d3 maps cache their topojson on install?** The install text lists no supporting files for them, which implies not.
5. **Is `lib/liquid-glass.iife.js` the same file for all four `liquid-glass-*` blocks?** Installing several may duplicate or conflict.
6. **What is the supported way to change a block's composition id after install?** Every collision fix depends on this, and no block page documents it.
7. **Which blocks are seek-safe?** Only `spiral-galaxy` explicitly claims frame-independent solving. The framework requires determinism; blocks that animate via accumulated state would violate it, and nothing labels them.
8. **Do the 4 SFX blocks' audio files participate in the mixer** (tracks, carve, groups) or play as raw media? Relevant to `pages/studio/audio-*`.
9. **How does the `mk-callout-highlight` scalar bind to a voiceover** in practice — a tween, a variable, or an automation lane?
10. **B1's numbering runs "01/14"–"14/14" but the set has no index page.** Whether a combined "all 14 shaders" block exists is unstated. ⚑

---

## Related topics

- [Mechanical index: slug, install, variable schema for all 372 items](catalog-index.md) · [JSON form](catalog-index.json)
- [Studio and onboarding — the GUI that installs and edits these](studio-and-onboarding.md)
- Source mirror: `pages/catalog/blocks/` (154 files, 5.3 MB raw / 3.0 MB of source)

**Blocks read: 154 / 154 assigned.** Every file in `pages/catalog/blocks/`, JSX preamble and preview
iframe skipped, HTML/CSS/JS source read. Near-duplicate families were additionally verified by
diffing full source between members rather than by comparing descriptions.
