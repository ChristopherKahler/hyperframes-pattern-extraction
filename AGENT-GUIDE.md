# AGENT GUIDE — read this before touching anything

You are an AI agent working with a video pattern-extraction kit. This file is
every tool in it, what each one is for, and which to reach for when. Read it
cold; it assumes nothing.

**If you read only one thing:** the two failure modes this kit exists to prevent
are (1) judging a video from thumbnails instead of looking at it, and (2)
hand-building something the catalog already ships. Both feel like efficiency.
Both cost more than they save.

---

## The mental model

Three layers, and they do not overlap:

| Layer | Owns | Never does |
|---|---|---|
| `watch.py` (`/watch-video`) | **seeing** — frames, cuts, motion numbers, 1:1 defect crops | decide what a pattern is |
| `/pattern-extract` | **turning what was seen into approved, codified patterns** | reimplement seeing |
| `pattern-library/` | **the templates** every admitted pattern must fit | hold anything unapproved |

When extracting, you *call* the watching tool. You never write your own frame
extraction. That rule exists because a reimplementation quietly drops the
native-resolution defect pass, which is the step that catches real bugs.

---

## Every tool, and when to reach for it

### `tools/watch-video/watch.py` — see a video properly

The entry point for looking at anything. Takes a rendered MP4, a URL, or a
HyperFrames project directory (which it renders first, into a version dir).

```bash
python tools/watch-video/watch.py "<target>" --note "what changed this pass"
```

It extracts frames, measures them, writes `motion.csv`, builds contact sheets
and **native-resolution defect crops**, then deletes the raw frames. Output lands
in `<source>.watch/vNNN/`, keeping a ring of the last 3 versions.

| Flag | Default | What it does |
|---|---|---|
| `--cell-width` | 960 | px per contact-sheet cell (50% of 1080p) |
| `--grid` | 3x2 | sheet layout — keep the cells big |
| `--sheet-fps` | 2 | sheet cells per second of video |
| `--defect-at` | 80% through | timestamp for the 1:1 crops |
| `--no-defect` | off | **do not use this** — see below |
| `--roi` | whole frame | `X0,Y0,X1,Y1` to restrict analysis |
| `--stride` | 1 | compare frame N to N-stride |
| `--workers` | — | render workers; 1 keeps Chrome windows down |
| `--from` / `--to` | — | a time window — **requires `--partial`** |
| `--partial` | — | the user's own words asking for a range |
| `--sheets-to` | — | keep sheets somewhere permanent |

Timestamps take `83`, `1:23`, or `1:02:03`.

**A range is a hard error unless the user asked for one.** `watch.py` refuses
`--from/--to` without `--partial "<their words>"`. This is enforced in code, not
advice. Narrowing a request to save bandwidth or context produces an inaccurate
read, and correcting it costs more than the full pass.

**Open every `defect_*.jpg` before any sheet.** A 470px contact-sheet cell is a
24% thumbnail of a 1920px frame. On 2026-08-27 a caption overlapped its subline
by 29px and a divider ran through the artwork; both were glaring at 1:1 and
invisible on the sheet. Typography bugs, hairline overruns, clipped glyphs and
collisions live only in the native crops.

**Verify the unique-frame count.** 1-2 unique frames means the source is static
or truncated. Stop and say so rather than describing a still as a video.

### `tools/watch-video/motion.py` — numbers, not impressions

Measures a directory of frames into a CSV: per-frame diff, centroid, bounding
box. This is where every timing claim comes from.

```bash
python tools/watch-video/motion.py <frames_dir> --fps <F> --roi X0,Y0,X1,Y1 --stride N
```

| Flag | Default | Note |
|---|---|---|
| `--thresh` | 12 | luma delta that counts as "this pixel moved" |
| `--work-width` | 320 | downscale for the math; `0` = native |
| `--stride` | 1 | raise to 8-15 to see slow drift that compression erases between adjacent frames |
| `--roi` | whole frame | in **source** pixel coords |

**Below ~0.3 px/frame, classification is noise.** Say so instead of guessing.

**Near-identical diff tails between two effects mean one asset reused**, not two
similar effects. Check before admitting both.

### `tools/watch-video/fit-ease.py` — fit the curve, don't guess it

Least-squares fits an easing family, duration and start time to a window of
`motion.csv`. Use it at G3 (fit) and G5 (converge).

```bash
python tools/watch-video/fit-ease.py motion.csv --from 45.5 --to 46.9 --kind fade
python tools/watch-video/fit-ease.py motion.csv --from 2.0 --to 3.4 --kind move --col cy
python tools/watch-video/fit-ease.py motion.csv --from 2.0 --to 3.4 --kind move --col cy --json
```

**`--kind` is the thing to get right.** Frame-diff is the *derivative* of
opacity or position, so a triangle on `diff` is an S-curve on the thing itself.

- `--kind fade` — the `diff` column is the derivative of a progress curve
  (cross-fade, dissolve, colour swap)
- `--kind move` — a named column (`cx`, `cy`, `x0`...) **is** the progress curve
  (entrance, exit, slide); pass it with `--col`

This script exists because a real extraction read a triangular diff profile as
"linear cross-fade", shipped it, and the convergence gate killed it. The correct
answer (`power1.inOut`, 0.570s) then had to be fitted by hand. Fit first.

`--compare REBUILD_CSV` diffs a rebuild against the reference — that is the G5
convergence number.

**Resolution limit:** `t0` and duration are known only to ±1 frame (1/fps).
Never report more precision than that.

### `tools/watch-video/reel.py` — one labelled reel for human approval

Stills cannot show motion, and eight separate files is eight things to open on a
phone. This concatenates renders into **one** reel with each clip labelled on
screen, so a human watches once and replies with names.

```bash
python tools/watch-video/reel.py OUT.mp4 --dir renders/
python tools/watch-video/reel.py OUT.mp4 --clip orbitStage/standard a.mp4 --clip orbitStage/mirror b.mp4
python tools/watch-video/reel.py OUT.mp4 --manifest clips.json
```

Each clip gets a 0.6s title slate plus its label burned bottom-left for the whole
duration, normalised to 1920x1080 @30fps yuv420p with no audio so concat is
byte-safe. It writes `<out>.manifest.json` mapping index, label, file and reel
timestamps — so "clip 3 is wrong" resolves to a filename without guessing.

`--font` defaults to a Windows path (`C:/Windows/Fonts/consola.ttf`). On
macOS/Linux pass your own monospace TTF.

### `bin/hfcat` — search the catalog BEFORE building

379 finished, parameterised items: 154 blocks, 218 components, 7 patterns from
this library. **Query this before hand-building any visual element.** Hand-
building a duplicate is the most common waste in this workflow.

```bash
hfcat "stat counter"          # search everything
hfcat --type block "reveal"   # block | component | hfpat
hfcat --show count-up         # variable schema + the CORRECT mount key
hfcat --vars -n 20 "chart"
hfcat --json "logo"           # for scripting
```

Then `hyperframes add <slug>` to install. On `no catalog match`, hand-build with
the miss on record.

**`--show` is not optional.** 44 of the 154 blocks mount under a key that is not
their slug. Mounting one under its slug silently renders nothing.

### `hyperframes` — the rendering framework

The CLI that turns a composition into video. Node >=22, renders through
puppeteer-core against a real Chrome.

```bash
hyperframes init <dir>        # scaffold a project
hyperframes add <slug>        # install a catalog block/component
hyperframes check             # validate before rendering
hyperframes render            # produce the MP4
hyperframes doctor            # what's installed, what's missing
```

`check` gates the render. Read `pattern-library/LIBRARY.md` for the two library
patterns that fail `check` out of the box and why, and for the list of what
`check` cannot see at all — that list is the reason the 1:1 defect pass exists.

### `ffmpeg` / `ffprobe` — everything underneath

Every frame extraction, crop, concat and encode. You rarely call it directly —
`watch.py` and `reel.py` wrap it — but when you do, read
[docs/FFMPEG-LEVERS.md](docs/FFMPEG-LEVERS.md) first. It covers the filter
chains this workflow actually uses and, critically, the quoting rules that differ
between Git Bash and PowerShell. Most one-off ffmpeg commands on Windows die on
quoting, not on the filter.

### `yt-dlp` — reading a reference off the web

Invoked by `watch.py` when the target is a URL; you do not normally call it
yourself. Clips are cached per range, so re-watching the same window costs no
network.

**The fetched clip is re-encoded.** `t=0` is exact and motion is faithful, but
**encode quality is not** — never measure PSNR or banding off a fetched
reference.

If a URL fails with missing formats or a 403 partway through, yt-dlp is stale:
`python -m pip install -U yt-dlp`.

### WhisperX — word-level timestamps

Not part of pattern extraction. Needed by `/wordsrt` and `/breakdown-reel`, where
every spoken word must map to an exact start/end timecode for caption pop-ins and
frame-accurate overlays.

Two artifacts: a `words[]` JSON (what caption engines read) and a `.words.srt`
with **one cue per word** (importable into Filmora/Premiere/Resolve).

Rules that matter:

- **Word-level verbatim ASR only.** Never ask the model for phrase or SRT mode.
  Derive the word-level SRT from the word JSON afterwards.
- **Cache per source.** If the JSON exists, skip ASR entirely.
- **~0.3-0.7x realtime on CPU.** A 19-minute file is 30-60 minutes. Background
  it and poll; never block a session on it.
- Diarisation is off by default and needs an `HF_TOKEN`.

See [commands/wordsrt.md](commands/wordsrt.md) for the full pipeline.

### `tools/pattern-factory/` — parallelising the gates

`factory.py` fans extraction gates across parallel agent sessions via a local
spawn hub; `codify.py` is the only thing that writes into the library.

**`codify.py` is the gate on the library.** Two verbs:

- `codify.py register` — writes a pattern into `PENDING.md` with its exact index
  row. This is where an extracted pattern waits.
- `codify.py fold` — moves it from `PENDING.md` into `hfpat-index.json` and
  `hfpat.js`. **Only after an explicit human approval.**

Never hand-edit `hfpat-index.json`. Never fold without a recorded yes.

#### Running the gates without a spawn hub

`factory.py` expects a hub at `PEK_HUB` (default `http://127.0.0.1:7799/api/spawn`).
**You do not need one.** The hub only automates spawning child sessions; the
briefs it would hand them are plain markdown you can run yourself:

| Brief | Use it for |
|---|---|
| `tools/pattern-factory/G1-BRIEF.md` | the candidate-listing pass over a reference |
| `tools/pattern-factory/CHILD-BRIEF.md` | a full per-pattern extraction lane |
| `tools/pattern-factory/COLD-BRIEF.md` | the G8 cold test — a session that has never seen the reference |

Open a fresh session, paste the brief, point it at this repo. The G8 cold test
**must** be a session with no context from the extraction — that is the entire
point of the gate.

---

## The pipeline

Full detail in [commands/pattern-extract.md](commands/pattern-extract.md). The
shape:

| Gate | What | Automated? |
|---|---|---|
| G0 | See it — full watch, every defect crop opened | tool |
| G1 | Candidate list — 5-10 distinct patterns with frame ranges | you |
| G2 | Measure — travel, duration, easing family, decay constant | tool |
| G3 | Fit to the builder template shape | tool + you |
| G4 | Rebuild in HyperFrames from the **numbers**, generic content | you |
| G5 | Converge — ≤5% mean error at matched elapsed time | **automated gate** |
| G6 | Defect pass at 1:1 | **automated gate** |
| G7 | **Human approves a rendered replication** | **HARD STOP** |
| G7b | Layout variations — `standard` and `mirror` | you |
| G8 | Cold-session reproduction from templates alone | **gate** |
| G9 | Codify into the templates | `codify.py fold` |
| G10 | Report | you |
| G11 | Log the run in `LEDGER.md` | you |

**G5 thresholds:** ≤5% proceed · 5-15% adjust parameters and re-run · >15% the
*classification* is wrong, not the parameters — go back to G2.

---

## Hard rules

Each of these is on the record because skipping it produced a measured failure.

1. **A contact sheet is not looking at the video.** Open every `defect_*.jpg` at
   native resolution, first, every pass.
2. **Watch all of what was named.** Never invent a `--from/--to` range. Never
   open sheet 4 of 15 and reason about the rest. Never summarise a video from its
   cuts table instead of looking at it. Token cost and context budget are **not**
   constraints on video digestion.
3. **Every timing claim cites a frame number or a CSV row.** No prose timings.
4. **The reference's subject never enters the library.** Not the palette, not the
   copy, not the concept. Only measured parameters transfer. Copying any of the
   rest is how a library becomes a clone.
5. **A candidate is only a pattern if it is reusable across subjects.** "Blue
   gradient with a phone" is not a pattern. "Element rises and settles on an
   exponential ease" is.
6. **G7 cannot be inferred.** Silence, a topic change, or a general compliment
   about the session is not approval. Only an explicit yes. If several patterns
   came from one reference, get a verdict on each — approval of one is not
   approval of the batch.
7. **A pattern is portable or it is not.** This session succeeding proves
   nothing. The cold test is the proof.
8. **When a session misreads a rule, make the rule impossible to get wrong.**
   Rewording is the same failure with better prose. Convert it to a derived
   parameter, a value measured at runtime, an order the builder derives itself,
   or a `guard*` that throws before rendering. If it genuinely cannot be
   enforced, say why in one line beside the prose.
9. **Interview before editing a template.** When a cold session's render has
   defects, do not diagnose the template yourself — you would be inferring which
   instruction was ambiguous. The child read it and produced the defect; it is
   the only thing in the loop with the causal answer. Ask it, then quote its
   wording in the fix.
10. **One cold run, not rounds.** The cold session is a gap finder, not a
    scoreboard. Five rounds on the first library produced five distinct failure
    classes and never a pass, because each fresh session probes somewhere new.
    Harvest every gap from one run and iterate on the template.
11. **Mirror by swapping positions, never by flipping pixels.**
    `transform: scaleX(-1)` mirrors the type and every word reads backwards. The
    rail moves to the opposite edge, the field moves across, the tilt inverts its
    sign, and type is never transformed. The mask must follow the layout — a
    one-sided scrim left in place puts mirrored cards under the dark half.
12. **Admitted or not.** No provisional entries. A library nobody trusts is worse
    than a small one.

---

## Determinism

Renders must be reproducible frame for frame. In any builder you write:

- No `Date.now()`, no `Math.random()`, no `fetch`
- Pure `fromTo` — a single paused timeline, seek-safe
- Derive timing from `opts.budget` rather than hardcoding it
- Run `HFPat.guard()` before rendering and `hyperframes check` after

---

## Where to look next

| Question | File |
|---|---|
| How do I use the library? | `pattern-library/LIBRARY.md` |
| What patterns exist? | `hfcat --type hfpat`, or `pattern-library/hfpat-index.json` |
| What's waiting for approval? | `pattern-library/PENDING.md` |
| What did past runs cost, and why? | `pattern-library/LEDGER.md` |
| How do I write an ffmpeg filter here? | `docs/FFMPEG-LEVERS.md` |
| How do I plan a video? | `docs/PLAYBOOK.md` |
| Why are there two index files? | `docs/hfcat-hfpat-index-spec.md` |
| How do I install all this? | `SETUP.md` |

**Read `LEDGER.md` before a run, not after.** It records the root causes from
every previous cold-session interview. The same root cause appearing twice means
a template edit did not take — rewrite it differently rather than adding a second
sentence beside the first.
