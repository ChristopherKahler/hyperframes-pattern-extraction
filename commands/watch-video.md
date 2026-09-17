---
description: Watch a video — a rendered MP4, a YouTube URL, or an in-progress HyperFrames project — at a resolution where defects are actually visible. Machine-measured cuts and motion, large contact sheets, and a mandatory native-resolution defect pass.
---

# /watch-video

`$ARGUMENTS` = a video file, a **URL**, or a HyperFrames project directory, plus any focus note.

One command does everything:

```bash
python $REPO/tools/watch-video/watch.py <target> --note "what changed this pass"
```

A project is rendered first (into a version dir, never into `renders/`); a video file is read where it sits. Frames are extracted, measured, and **deleted**. A ring of the last 3 versions stays beside the source in `<source>.watch/` — one ring per source, so a new reference never evicts an old one's sheets.

## Watching a reference off the web

```bash
python .../watch.py "https://www.youtube.com/watch?v=XXXX" --from 1:23 --to 1:38 --note "the counter hit"
```

- Timestamps take `83`, `1:23`, or `1:02:03`.
- **A range is a HARD ERROR unless Chris named it.** `watch.py` refuses `--from/--to` without `--partial "<his words>"`. This is enforced in code, not advice: narrowing his ask to save bandwidth or context produces an inaccurate read and costs him more of both to correct.
- The clip is **cached per range**, so re-watching the same window costs no network. A different range off the same video is its own entry.
- Downloads and their rings live under `%TEMP%/watch-video/dl/`. Pass `--sheets-to DIR` for anything worth keeping.
- The fetched clip is re-encoded, so `t=0` is exact. **Motion is faithful; encode quality is not** — never measure PSNR or banding off a fetched reference.

If a URL fails with missing formats or a 403 partway through, yt-dlp is stale: `python -m pip install -U yt-dlp`. YouTube breaks it every few weeks.

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

## The rule that matters most

**A contact sheet is not looking at the video.**

On 2026-08-27 a caption overlapped its own subline by 29px and a divider rule ran straight through the artwork. Both were glaring at 1:1. Both were invisible on a 4x4 sheet, because a 470px cell is a **24% thumbnail of a 1920px frame** — the collision was smaller than one pixel there. Chris spotted both instantly from a native crop.

Therefore, every run:

1. **Open every `defect_*.jpg`.** They are native-resolution horizontal bands, no downscaling. This is where typography bugs, hairline overruns, clipped glyphs, and collisions live. Not optional.
2. **Then** open the `sheet_*.jpg` for pacing and content.
3. Numbers from `motion.csv` for timing. Never describe motion from a sheet.

Cells default to **960px** (50% of 1080p) on a **3x2** grid. Do not shrink them to save context. Chris's standing instruction: *"I would rather you absorb half a million tokens before you even render than iterate constantly over small nagging details."*

---

## Defect checklist — run against the 1:1 crops, every pass

Arithmetic beats eyeballing for the first four. Compute them from the CSS before rendering.

- [ ] **Text block collisions.** For each absolutely-positioned text element: `top + (font-size x line-height x lines)` must be less than the next element's `top`. This is the bug that shipped.
- [ ] **Underline / highlight bars** sit behind their own text only, and do not reach into the element below.
- [ ] **Full-width rules** (`left:X; right:Y`) — confirm they are meant to cross the whole frame. If they cross artwork, constrain to a `width`.
- [ ] **Bottom-edge flush.** An element ending at exactly the canvas height reads as unfinished. Leave margin.
- [ ] Glyph clipping at container edges, especially descenders and any masked/overflow-hidden reel.
- [ ] Rotated elements: check corners have not left the canvas.
- [ ] Contrast of small text against its actual backdrop, not the page background.
- [ ] Anything static for more than ~2s in a short piece — dead air reads as broken.

`npm run check` catches contrast, overflow, occlusion, and tween overwrites. Run it before rendering. It does **not** catch the collisions above, because they are within-tolerance geometry.

---

## Flags

| Flag | Default | Use |
|---|---|---|
| `--note "..."` | — | label stored with the version; always pass it |
| `--ring N` | 3 | versions kept beside the project |
| `--cell-width N` | 960 | contact-sheet cell width |
| `--grid CxR` | 3x2 | sheet layout |
| `--sheet-fps N` | 2 | cells per second of video |
| `--defect-at T` | 80% through | timestamp for the 1:1 crops |
| `--no-defect` | off | never pass this |
| `--stride N` | 1 | raise to 8-15 for slow drift compression erases |
| `--roi X0,Y0,X1,Y1` | — | isolate one element |
| `--workers N` | 1 | HyperFrames render workers; 1 minimises Chrome windows |
| `--keep` | off | retain the frame scratch dir |

## Storage contract

| Artifact | Fate |
|---|---|
| Extracted frames | deleted every run — this is the 200 MB part |
| Render, sheets, defect crops, motion.csv | kept in `.watch/vNNN/`, ring of 3 |
| Older versions | dropped automatically |

## Reading the numbers

- `changed_pct` is the honest activity signal. The summary's "moving frames" uses a 0.05 threshold and reports ~99% on near-static content.
- Transition duration = count of elevated-`diff` frames / fps. Report in **ms**.
- `speed` down the CSV is the easing curve: flat = linear, slow-fast-slow = ease-in-out, decaying = ease-out, overshoot-and-settle = spring.
- Below ~0.3 px/frame the path classification is noise. Say so rather than guessing.

## Converge loop

To match a reference: classify the pattern, guess its parameters, rebuild, render, run the same `motion.py` over both, and compare `speed mean` / `mean turn` / `path shape`. Error cancels because it is the same measurement on both sides. Perfect perception is not required; correct classification is.
