---
type: reference
status: active
tags: [ffmpeg, frame-extraction, mpdecimate, scdet, drawtext, video-analysis, motion-graphics, dedupe]
relatedTo: [video-gen]
---

# FFmpeg Levers - Watching a Video Frame-Accurately

Verified against **ffmpeg 8.0-essentials** at `C:\ProgramData\chocolatey\bin\ffmpeg.exe` on 2026-08-27.
All defaults below were dumped from that binary, not recalled.

Goal: extract exactly the frames that carry information, at a granularity where nothing is lost, without drowning in redundant stills.

---

## The mental model

Four independent axes. Tune them separately or you will chase your tail.

| Axis | Question it answers | Filters |
|---|---|---|
| **Sampling** | How often do I look? | `fps`, `select`, `thumbnail` |
| **Reduction** | Which of those are worth keeping? | `mpdecimate`, `decimate` |
| **Detection** | Where does something actually happen? | `scdet`, `select='gt(scene,X)'`, `freezedetect`, `blackdetect` |
| **Presentation** | How legible is what I get? | `scale`, `crop`, `drawtext`, `tile`, `-q:v` |

Sampling sets the ceiling on what is *knowable*. Reduction sets the cost. Detection tells you where to spend. Presentation decides whether the answer is readable once you have it.

---

## Windows escaping (read this first or nothing will run)

Inside a filtergraph, a colon separates options, so any colon in a *value* must be backslash-escaped:

```bash
# WRONG - the C: breaks the filtergraph
drawtext=fontfile=C:/Windows/Fonts/consolab.ttf:text='hi'

# RIGHT - escape the drive colon AND the colon inside pts:hms
drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':text='%{pts\:hms}'
```

Fonts confirmed present on this machine: `consolab.ttf` (bold mono, best for burn-in), `consola.ttf`, `arialbd.ttf`, `arial.ttf`.

Wrap the whole `-vf` argument in single quotes in Git Bash. In PowerShell, prefer single quotes too and avoid `%` at the start of a token.

---

## 0. Recon - never guess the source

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration,pix_fmt \
  -of default=noprint_wrappers=1 IN.mp4
```

`r_frame_rate` is the container's nominal rate; `avg_frame_rate` is what actually landed. If they disagree, the file is variable-frame-rate and every `fps=` filter is a resample. Know this before you reason about frame numbers.

Exact frame count when `nb_frames` is missing:

```bash
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames -of csv=p=0 IN.mp4
```

---

## 1. Sampling - how often you look

### `fps=N`
Resamples to a constant rate. Duplicates frames when N exceeds source rate, drops when below. Simple, predictable, and what you want 90% of the time.

```bash
-vf "fps=10"     # 100ms grid
-vf "fps=30"     # 33ms grid - native for most social video
-vf "fps=1/2"    # one frame every 2 seconds
```

### Native rate - no resampling at all
Omit any fps filter. You get every coded frame, and `%{n}` then equals the true frame index. **Use this whenever frame numbers must be citable.**

### `select` expressions - surgical
```bash
# Frames 400 through 460 inclusive, nothing else
-vf "select='between(n,400,460)'" -vsync vfr

# A 2-second window by time
-vf "select='between(t,12.5,14.5)'" -vsync vfr

# Every 3rd frame
-vf "select='not(mod(n,3))'" -vsync vfr

# Only keyframes - fast structural skim
-vf "select='eq(pict_type,I)'" -vsync vfr
```

Any `select` needs `-vsync vfr` or ffmpeg pads the output back to constant rate and you get duplicates.

### `thumbnail=N`
Picks the single most representative frame from each batch of N. Good for a coarse arc, useless for motion analysis - it deliberately discards the transition frames you care about.

---

## 2. Reduction - `mpdecimate`, the lever that makes high fps affordable

This is the one that matters. It drops frames that are near-duplicates of the previous kept frame, so a 30fps capture of a mostly-static talking head collapses to the handful of frames where something changed.

**Real defaults from your binary:**

| Option | Default | Meaning |
|---|---|---|
| `hi` | **768** | If any single 8x8 block differs by more than this, the frame is kept |
| `lo` | **320** | Blocks differing by more than this count toward `frac` |
| `frac` | **0.33** | If more than this fraction of blocks exceed `lo`, the frame is kept |
| `max` | **0** | Max consecutive drops (positive) or min interval between drops (negative). 0 = unlimited |
| `keep` | **0** | Similar consecutive frames to keep before dropping starts |

**Direction of tuning, which is counter-intuitive:**

- **Lower** `hi`/`lo`/`frac` → stricter about what counts as a duplicate → **keeps more frames** → more sensitive to small changes.
- **Higher** → drops aggressively → fewer frames.

For motion graphics, where a caption pop may change 2% of the frame, defaults are far too coarse. Start here:

```bash
mpdecimate=hi=200:lo=100:frac=0.02
```

That says: keep the frame if any block moves meaningfully, or if even 2% of blocks shift a little. A single word appearing will survive that filter; it will not survive the defaults.

**Tuning loop - count before you write files:**

```bash
# Dry run. Writes nothing. Reports how many frames survive.
ffmpeg -hide_banner -i IN.mp4 \
  -vf "fps=30,mpdecimate=hi=200:lo=100:frac=0.02" \
  -vsync vfr -f null - 2>&1 | tail -3
```

Read `frame=` in the output. Target 150-400 unique frames for a 60-second reel. Too many, raise `frac` toward 0.05. Too few, lower `hi` toward 120.

**On `-vsync vfr` - measured 2026-08-27, not assumed.**

Tested against a fixture whose true unique-frame count was known (61 of 90):

| Output | With `-fps_mode vfr` | Without |
|---|---|---|
| JPEG sequence (`image2`) | 61/90 ✅ | 61/90 ✅ |

For **image-sequence output the flag changed nothing** - image2 does not pad back to CFR. The widely repeated "vfr is mandatory" line applies to **video-file output**, where the muxer re-duplicates dropped frames. Keep `-fps_mode vfr` (the ffmpeg 8.0 name; `-vsync vfr` is the deprecated alias) as a harmless default, but do not blame it when counts look wrong.

**Threshold behaviour, measured on subtle motion** (fixture truth: 13 unique of 90):

| Setting | Kept |
|---|---|
| defaults `hi=768 lo=320 frac=0.33` | **7/13** - silently loses content |
| `hi=200:lo=100:frac=0.02` | **13/13** - exact |

**When a count looks impossible, suspect the fixture before the flags.** A test clip built with `drawbox=x='...t...'` produced 90 frames of which only **2 were unique** - drawbox did not animate the box. Every dedupe setting correctly returned 2, which read as a filter bug and was not one. `overlay=x='...t...'` animates correctly. Always verify:

```bash
md5sum frames/f_*.jpg | awk '{print $1}' | sort -u | wc -l
```

### `decimate` vs `mpdecimate`
`decimate` drops one frame in every N on a fixed cadence (it exists for inverse telecine). It is not content-aware. For this work you always want `mpdecimate`.

---

## 3. Detection - let the machine find the events

### `scdet` - purpose-built scene detection (preferred, ffmpeg 8.0)

```bash
ffmpeg -hide_banner -i IN.mp4 -vf "scdet=threshold=10" -f null - 2>&1 \
  | grep lavfi.scd
```

| Option | Default | Range |
|---|---|---|
| `threshold` / `t` | **10** | 0-100. Lower = more sensitive, more cuts reported |
| `sc_pass` / `s` | false | Pass only scene-change frames downstream |

Threshold 10 catches hard cuts. Drop to 4-6 to catch soft dissolves and whip transitions. Below 3 you start reporting camera motion as cuts.

**Export only the cut frames, numbered:**

```bash
ffmpeg -hide_banner -i IN.mp4 \
  -vf "scdet=threshold=6:sc_pass=1,drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':\
text='%{n} | %{pts\:hms}':x=8:y=8:fontsize=30:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=6" \
  -vsync vfr -q:v 3 cuts/%04d.jpg
```

### `select='gt(scene,X)'` - the older path
```bash
ffmpeg -i IN.mp4 -filter:v "select='gt(scene,0.25)',showinfo" -f null - 2>&1 \
  | sed -n 's/.*pts_time:\([0-9.]*\).*/\1/p' > cuts.txt
```
`scene` here is 0-1, not 0-100. Roughly, `gt(scene,0.25)` ≈ `scdet=threshold=25`. Use this when you want the timestamps as plain text.

### `freezedetect` - find held frames and dead air
```bash
ffmpeg -i IN.mp4 -vf "freezedetect=n=0.003:d=0.5" -f null - 2>&1 | grep freezedetect
```
`n` = noise tolerance, `d` = minimum duration in seconds. Tells you where nothing moves, which is where you can safely skip.

### `blackdetect` - transitions through black
```bash
ffmpeg -i IN.mp4 -vf "blackdetect=d=0.05:pix_th=0.10" -f null - 2>&1 | grep black_start
```

---

## 4. Presentation - making frames readable

### `drawtext` burn-in - the accountability lever

Burn identity into the pixels so any claim about timing can be checked against the image.

| Token | Gives |
|---|---|
| `%{n}` | Frame number **as seen by the filter** (post-`fps`, post-`mpdecimate`) |
| `%{pts\:hms}` | Timestamp as `HH:MM:SS.mmm` |
| `%{pts}` | Raw presentation timestamp |
| `%{pict_type}` | I / P / B frame type |

```bash
drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':text='%{n} | %{pts\:hms}':\
x=8:y=8:fontsize=28:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=6
```

**Trap:** `%{n}` counts frames *entering drawtext*. Put `drawtext` **after** `mpdecimate` and the numbers are sequential survivors (1,2,3...). Put it **before** and they are source frame numbers with gaps. Both are useful; know which you built.

To keep true source numbers through a dedupe, burn first:

```bash
-vf "drawtext=...text='src %{n}'...,mpdecimate=hi=200:lo=100:frac=0.02"
```

### `scale` - the legibility floor

| Width | Readable? |
|---|---|
| 360px | Layout and motion only. On-screen text is mush |
| 640px | Large caption text legible |
| 960px | Small UI text and numbers legible |
| Native | Everything, at full token cost |

`scale=640:-2` preserves aspect and forces even height (required by most encoders).

Verdict: **360px is where the information you want gets destroyed.** For motion-graphic teardown use 640 minimum, 960 when reading on-screen numbers.

### `crop` - isolate one animating element
```bash
crop=W:H:X:Y      # crop=400:200:340:1200
```
Crop to just the caption zone and you can afford native resolution and native frame rate on that region. This is the cheapest way to read an easing curve exactly.

### `tile` - contact sheets
```bash
tile=6x8:margin=4:padding=3:color=white
```
6 columns at 30fps = 200ms per row. At 10fps = 600ms per row. Pick columns so one row equals a meaningful time unit, then motion reads left-to-right.

Add `-frames:v 1` to emit a single sheet; omit it to emit a sheet per N frames.

### Output quality
```bash
-q:v 2    # near-lossless JPEG, large
-q:v 3-4  # good for reading text
-q:v 6    # layout only
```
Use `.png` instead when you need pixel-exact color sampling. It is 3-5x larger.

---

## 5. Seek precision

```bash
ffmpeg -ss 12.5 -i IN.mp4 ...     # BEFORE -i: fast, seeks to nearest keyframe, INEXACT
ffmpeg -i IN.mp4 -ss 12.5 ...     # AFTER -i: decodes from 0, frame-EXACT, slower
```

For frame-accurate work always put `-ss` after `-i`. For a rough skim of a long file, before is fine.

Hybrid for long sources: coarse-seek before, fine-seek after.
```bash
ffmpeg -ss 600 -i IN.mp4 -ss 12.5 -to 14.5 ...
```

---

## 6. Composed recipes

### A. Full-coverage deduped extract - "no lost frames"
```bash
ffmpeg -hide_banner -i IN.mp4 \
  -vf "fps=30,mpdecimate=hi=200:lo=100:frac=0.02,scale=640:-2,\
drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':text='%{n} | %{pts\:hms}':\
x=8:y=8:fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=5" \
  -vsync vfr -q:v 4 frames/%05d.jpg
```
Run the `-f null -` dry run first to check the count.

### B. Easing curve on one element - native rate, cropped
```bash
ffmpeg -hide_banner -i IN.mp4 -ss 8.20 -to 9.20 \
  -vf "crop=500:220:290:1180,scale=500:-2,\
drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':text='%{pts\:hms}':\
x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.8,tile=6x5:margin=3:padding=3" \
  -frames:v 1 -q:v 2 ease.jpg
```
Native rate inside a 1-second window on a cropped region = every frame of that animation, one image.

### C. Cut table as text
```bash
ffmpeg -hide_banner -i IN.mp4 -vf "scdet=threshold=6" -f null - 2>&1 \
  | grep -oE "lavfi\.scd\.time: [0-9.]+" | awk '{print $2}' > cuts.txt
wc -l cuts.txt
```

### D. Frame-exact window, every frame, nothing dropped
```bash
ffmpeg -hide_banner -i IN.mp4 \
  -vf "select='between(n,412,478)',scale=960:-2,\
drawtext=fontfile='C\:/Windows/Fonts/consolab.ttf':text='%{n}':x=8:y=8:\
fontsize=30:fontcolor=yellow:box=1:boxcolor=black@0.8" \
  -vsync vfr -q:v 3 win/%04d.jpg
```

---

## 7. The rule that makes it trustworthy

Detection is ffmpeg's job. Interpretation is the model's job.

If a timing claim cannot be traced to a burned-in frame number sitting in an image, it was invented. Generate the cut table and the numbered frames first, then reason only over those artifacts.

---

## Quick reference

| Want | Lever |
|---|---|
| Every frame that changed | `fps=30,mpdecimate=hi=200:lo=100:frac=0.02` + `-vsync vfr` |
| Fewer frames out | Raise `frac` toward 0.1, raise `hi` |
| More frames out | Lower `frac` toward 0.01, lower `hi` toward 120 |
| Exact cut list | `scdet=threshold=6` |
| More cuts detected | Lower `scdet` threshold toward 4 |
| Read on-screen text | `scale=960:-2` and `-q:v 3` |
| Read an easing curve | `crop` the element, native fps, 1s window, `tile=6x5` |
| Count before writing | `-f null -` and read `frame=` |
| Citable frame numbers | `drawtext` with `%{n}`, placed deliberately before or after dedupe |
| Frame-exact seek | `-ss` **after** `-i` |
