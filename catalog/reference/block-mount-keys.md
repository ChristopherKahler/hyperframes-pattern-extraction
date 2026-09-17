---
type: reference
status: active
tags: [hyperframes, catalog, blocks, mount-key, composition-id, troubleshooting, canonical-reference, video-gen]
relatedTo: [video-gen, hyperframes, catalog-blocks-guide, catalog-index]
---

# Block mount keys — the 44 mismatches

**Open this when an installed block does nothing.**

The docs' usage snippet for every block tells you to mount it as
`data-composition-id="<slug>"`. **44 of 154 blocks declare something else internally** and register
their GSAP timeline under that other key. Mount them with the slug and nothing runs.

Machine-readable form for all 154: [block-mount-keys.json](block-mount-keys.json).
Routing and what each block is for: [catalog-blocks-guide.md](catalog-blocks-guide.md).

## The fix

```html
<!-- WRONG - what the block's own docs page tells you to paste -->
<div data-composition-id="code-snippet-dark-plus"
     data-composition-src="compositions/code-snippet-dark-plus.html" ...></div>

<!-- RIGHT - the key the installed file actually declares and registers -->
<div data-composition-id="vscode-dark-plus"
     data-composition-src="compositions/code-snippet-dark-plus.html" ...></div>
```

The slug still names the **install command** and the **file path**. Only the mount key differs.

## Three rules cover all 44

There are no stragglers: 27 + 12 + 5 = 44.

| Rule | n | Mount key is |
|---|---|---|
| **1. Generic `main`** | 27 | literally `main` for every one |
| **2. `vscode-` rename** | 12 | `code-snippet-<theme>` → `vscode-<theme>` |
| **3. `vfx-` internal name** | 5 | the project's own name, listed below |

> **Rule 1 also means those 27 blocks cannot coexist.** They collide with each other on both
> `data-composition-id="main"` and `window.__timelines["main"]`. Install a second one and rename it
> first. This is every shader transition and every transition pack — exactly the blocks someone is
> most likely to want two of.

---

## Rule 1 — generic `main` (27)

Every B1 shader transition and every B2 transition pack. All mount as `main`.

**The 14 shader transitions**

| Slug | Mount key |
|---|---|
| `chromatic-radial-split` | `main` |
| `cinematic-zoom` | `main` |
| `cross-warp-morph` | `main` |
| `domain-warp-dissolve` | `main` |
| `flash-through-white` | `main` |
| `glitch` | `main` |
| `gravitational-lens` | `main` |
| `light-leak` | `main` |
| `ridged-burn` | `main` |
| `ripple-waves` | `main` |
| `sdf-iris` | `main` |
| `swirl-vortex` | `main` |
| `thermal-distortion` | `main` |
| `whip-pan` | `main` |

**The 13 transition packs**

| Slug | Mount key |
|---|---|
| `transitions-3d` | `main` |
| `transitions-blur` | `main` |
| `transitions-cover` | `main` |
| `transitions-destruction` | `main` |
| `transitions-dissolve` | `main` |
| `transitions-distortion` | `main` |
| `transitions-grid` | `main` |
| `transitions-light` | `main` |
| `transitions-mechanical` | `main` |
| `transitions-other` | `main` |
| `transitions-push` | `main` |
| `transitions-radial` | `main` |
| `transitions-scale` | `main` |

---

## Rule 2 — `code-snippet-*` → `vscode-*` (12)

A systematic rename, not a per-file bug: strip `code-snippet-`, prefix `vscode-`.

| Slug | Mount key |
|---|---|
| `code-snippet-dark-2026` | `vscode-dark-2026` |
| `code-snippet-dark-modern` | `vscode-dark-modern` |
| `code-snippet-dark-plus` | `vscode-dark-plus` |
| `code-snippet-high-contrast` | `vscode-high-contrast` |
| `code-snippet-high-contrast-light` | `vscode-high-contrast-light` |
| `code-snippet-light-2026` | `vscode-light-2026` |
| `code-snippet-light-modern` | `vscode-light-modern` |
| `code-snippet-light-plus` | `vscode-light-plus` |
| `code-snippet-monokai` | `vscode-monokai` |
| `code-snippet-solarized-light` | `vscode-solarized-light` |
| `code-snippet-visual-studio-dark` | `vscode-visual-studio-dark` |
| `code-snippet-visual-studio-light` | `vscode-visual-studio-light` |

> **The rule covers only these 12 VS Code theme blocks.** The other `code-snippet-*` blocks are
> correctly keyed: all 12 `code-snippet-apple-terminal-*` and `code-snippet-flight` mount as their
> own slug.

### Second trap on these same 12 pages

All twelve published pages render a literal **`' + compositionId + '`** as a composition id — string
interpolation from the page template leaking into the output. A reader copying the id from that
spot gets a broken string rather than either the slug or the real key. Use `vscode-<theme>` from the
table above.

---

## Rule 3 — `vfx-*` internal project name (5)

No pattern to derive; read the key.

| Slug | Mount key |
|---|---|
| `vfx-iphone-device` | `devices-canvas` |
| `vfx-liquid-glass` | `liquid-glass` |
| `vfx-magnetic` | `magnetic-cursor` |
| `vfx-portal` | `portal-transition` |
| `vfx-shatter` | `glass-shatter` |

`vfx-anamorphic-flare`, `vfx-liquid-background` and `vfx-text-cursor` are **not** in this group —
they mount as their own slug.

---

## Not a mismatch: the 9 dynamic registrations

These have **no literal `__timelines["..."]`** anywhere in the file. They register through a variable
that holds their own declared `data-composition-id` — which equals the slug. **Mount them with the
slug; they are correct.** Listed here only so a keyword search for a missing timeline key finds them
and stops.

| Slug | Registers via | Mount key |
|---|---|---|
| `camcorder-hud` | `compositionId` | `camcorder-hud` |
| `code-3d-extrude` | `id` / `spec.id` | `code-3d-extrude` |
| `code-particle-assemble` | `id` / `spec.id` | `code-particle-assemble` |
| `code-shader-dissolve` | `id` / `spec.id` | `code-shader-dissolve` |
| `editorial-flash-overlay` | `compositionId` | `editorial-flash-overlay` |
| `freeze-frame-dressing` | `compositionId` | `freeze-frame-dressing` |
| `organic-light-leak-overlay` | `compositionId` | `organic-light-leak-overlay` |
| `oscilloscope-trace` | `COMP_ID` | `oscilloscope-trace` |
| `spiral-galaxy` | `COMP_ID` | `spiral-galaxy` |

In the JSON these carry `mount_key_dynamic: true` and a `mount_key_reason`. They are **not** null:
the key is known.

Four of them (`camcorder-hud`, `editorial-flash-overlay`, `freeze-frame-dressing`,
`organic-light-leak-overlay`) are host-attached overlays that print their own diagnostic when
unhosted — e.g. *"Camcorder HUD could not find its composition host"*. If you see that message the
problem is the missing host, not the mount key.

---

## Other reasons an installed block does nothing

Checked from source across all 154; each is a field in the JSON.

| Symptom | Cause | Affected |
|---|---|---|
| Two transitions, one runs | Both mounted `main` | any 2 of the 27 |
| Blank frame on an offline render host | Block fetches geography at render time | `us-map`, `us-map-bubble`, `us-map-flow`, `world-map`, `spain-map` — use `us-map-hex` instead |
| Blank frame in a browser without the experimental API | Needs `layoutSubtree` / `drawElementImage`, no polyfill | `ios26-liquid-glass`, `macos-tahoe-liquid-glass`, `vfx-iphone-device`, `vfx-liquid-background`, `vfx-liquid-glass`, `vfx-magnetic`, `vfx-portal`, `vfx-shatter` |
| Glass panels render as flat boxes | Local `lib/liquid-glass.iife.js` missing after install | `liquid-glass-context-menu`, `liquid-glass-media-controls`, `liquid-glass-notification`, `liquid-glass-widgets` |
| Nothing loads at all | GSAP 3.14.2 unreachable — **all 154 require it** from `cdn.jsdelivr.net` | all 154 |
| Setting a variable has no effect | The block declares none — 132 of 154 | see `var_count` |

---

## Reading the JSON

```json
"code-snippet-dark-plus": {
  "mount_key": "vscode-dark-plus",
  "matches_slug": false,
  "mismatch_family": "vscode-rename",
  "install_files": 2,
  "needs": ["gsap"],
  "render_time_network": false,
  "var_count": 0,
  "mount_key_source": "literal-timeline-key",
  "mount_key_dynamic": false,
  "var_source": "none",
  "doc_shows_interpolation_artifact": true
}
```

Totals in the file: 154 blocks · 44 mismatches (27 + 12 + 5) · 9 dynamic-but-resolvable ·
0 null mount keys · 5 render-time-network · 8 html-in-canvas · 16 three.js (4 of them from the local
lib, not a CDN) · 5 d3 + 5 topojson · 154 gsap · 22 with variables · max install footprint 29 files
(`ios26-liquid-glass`).

**Derivation:** literal `__timelines["..."]` wins; otherwise the declared `data-composition-id`
with interpolation artifacts filtered out. The 44/27 split was reproduced independently by the
orchestrator using different regexes and matched exactly.
