---
name: breakdown-reel
description: Reverse-engineer the editing style of a swiped social video — wordstamp transcript + 4fps low-tax frame render + contact-sheet montages → a running BREAKDOWN.md that decodes the motion-graphic patterns for replication with Outpost + Hyperframes.
argument-hint: "[path to a swiped video — WSL \\\\wsl$\\... or /home/... .mp4]"
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion]
---

<objective>
Tear down ONE swiped video to decode WHY its editing works, so Chris can replicate the style with Outpost (planning/structure) and Hyperframes (motion graphics). The output is a running markdown breakdown doc, built section by section, with the heaviest attention on MOTION — graphic movement, animation, transitions, pacing — not just the spoken content. The goal is to understand the *configs behind the visuals* well enough to rebuild them.

Target video: $ARGUMENTS
</objective>

<core_principles>
- **Style over content.** The transcript is context; the EDIT is the prize. Always ask "what is moving, when, and why."
- **Three motion clocks.** The signature of these videos is stacking independent motion layers (captions / cuts / Ken-Burns zoom) so something always moves even on a long shot. Hunt for this stack in every reel.
- **Token-efficient watching.** NEVER read 100s of individual frames. Read CONTACT-SHEET MONTAGES — one image per section. Individual frame reads only for a specific moment.
- **Low-tax frames.** 4fps, ~360px wide, q:v 6, timecodes burned in. Good enough to see what's happening, not high-res enough to eat context. (Chris's explicit rule.)
- **Honesty.** Mark each section ✅ (studied at 4fps) vs 🔍 (overview-level only). Never imply you studied a beat you only glanced at.
- **Real > fake.** These videos prove with real screenshots / real client clips / real analytics. Note it; never fabricate numbers or credibility when replicating (ties to the workspace NEVER-fabricate rule).
- **scope is for YouTube.** `outpost:scope` only ingests YouTube URLs. For a LOCAL swipe file, use ffmpeg directly (recipes below).
</core_principles>

<environment>
- **ffmpeg/ffprobe**: on PATH. Font for burned timecodes: `/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`.
- **Transcription (wordstamp = WhisperX word-level)** lives in video-use. `python` is NOT on PATH — call the venv python directly:
  - `VENV=/home/<you>/ops-sys/toolbox/skills/video-use/.venv/bin/python`
  - Run from `/home/<you>/ops-sys/toolbox/skills/video-use/`.
  - Do NOT wrap in `nohup` with bare `python` (it fails "permission denied"); call `$VENV` directly, background via the tool's run_in_background.
- **WSL path input**: if the arg is `\\wsl$\Ubuntu\home\...`, convert to `/home/...` (strip `\\wsl$\Ubuntu`, swap `\`→`/`).
</environment>

<process>

**0 · Resolve + inventory.** Normalize the path. `ffprobe` for width/height/fps/duration/audio. Note aspect (9:16 / 4:5 / 1:1 / 16:9) and genre guess. Create the workspace: `<video_dir>/<name>-analysis/{frames,sheets}`.

**1 · Transcribe (wordstamp) — kick off in background first** (it's the slow step, CPU ~realtime):
```bash
cd /home/<you>/ops-sys/toolbox/skills/video-use
VENV=.venv/bin/python
$VENV helpers/transcribe_local.py <VIDEO> --no-diarize --language en
# output → <video_dir>/edit/transcripts/<name>.json
# then pack: $VENV helpers/pack_transcripts.py --edit-dir <video_dir>/edit  → edit/takes_packed.md
```

**2 · Render 4fps low-tax timecoded frames** (the "render 4 fps" deliverable):
```bash
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf
ffmpeg -hide_banner -loglevel error -i <VIDEO> \
  -vf "fps=4,scale=360:-2,drawtext=fontfile=$FONT:text='%{pts\:hms}':x=5:y=5:fontsize=15:fontcolor=yellow:box=1:boxcolor=black@0.65:boxborderw=3" \
  -q:v 6 <ANALYSIS>/frames/f_%04d.jpg
# Frame N → time = (N-1)/4 seconds.
```

**3 · Overview montage (1fps tiled)** — see the whole visual arc at a glance:
```bash
ffmpeg -hide_banner -loglevel error -i <VIDEO> \
  -vf "fps=1,drawtext=fontfile=$FONT:text='%{pts\:hms}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=4,scale=240:-2,tile=6x8:margin=4:padding=3:color=white" \
  -an <ANALYSIS>/sheets/overview_%02d.jpg
```
Read the overview sheets + the packed transcript. From them, **define the structural sections** (hook / reframe / problem / proof / mechanism / authority / offer / CTA / proof-stack — adapt to the reel).

**4 · Section montages (4fps, 4 cols = 1 second per row)** — for each MOTION-RICH section, so animation reads left-to-right within a row:
```bash
# mk <start_s> <end_s> <rows = end-start> <name>
ffmpeg -hide_banner -loglevel error -ss <START> -to <END> -i <VIDEO> \
  -vf "fps=4,drawtext=fontfile=$FONT:text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=4,scale=280:-2,tile=4x<ROWS>:margin=4:padding=4:color=white" \
  -frames:v 1 <ANALYSIS>/sheets/<name>.jpg
```
Read each. Prioritize sections with graphics (list reveals, name-drops, cards, charts, CTA arrows, transitions). Skip dense 4fps on sections that are pure talking-head-with-captions once that pattern is established — mark them 🔍.

**5 · Easing pass (the "config behind the visual") — 12–24fps micro-crops.** 4fps cannot resolve sub-250ms animation curves. For ~4 key animation moments (a caption pop, a graphic slide-in, an arrow bounce, a transition), pull a tight high-fps strip to read the easing:
```bash
# 1-second window at 24fps, 6 cols → ~0.04s steps. Optional crop=W:H:X:Y to isolate the animating element.
ffmpeg -hide_banner -loglevel error -ss <T> -to <T+1> -i <VIDEO> \
  -vf "fps=24,scale=240:-2,tile=6x4:margin=2:padding=2:color=white" -frames:v 1 <ANALYSIS>/sheets/ease_<label>.jpg
```
Only go this deep where it changes how you'd rebuild it. Note: pop vs scale-spring vs slide, in/out duration, hold length, zoom rate.

**6 · Maintain the running BREAKDOWN.md** (skeleton below). Update it live as each section is studied — log, note, decode. This doc is the deliverable.

**7 · Close the loop.** End with: the one most-replicable insight, what's confidently spec'd vs still guessed, and offer the next fork (finish remaining sections / prototype in Hyperframes / extract a reusable template / deeper easing).
</process>

<breakdown_doc_skeleton>
Write to `<ANALYSIS>/BREAKDOWN.md`:

1. **Source facts** — file, dims, fps, duration, audio, aspect, genre, talent, asset index.
2. **Style in one paragraph** — the whole edit philosophy compressed.
3. **Structural section map** — table: # · section · ~time · job · dominant visual.
4. **Editing-pattern catalog (P1…Pn)** — each pattern: what it is + **Rebuild:** note (Outpost step or Hyperframes component). Cover at minimum: captions (style + animation), B-roll sync logic, proof-via-real-screenshots, graphic reveals, authority/name-drop technique, result/CTA cards, CTA motion, Ken-Burns/anti-static, transitions, pace law.
5. **⚡ Movement summary table** — layer · cadence · motion · why. End with the single biggest replicable lesson.
6. **Section-by-section deep dive** — per section: transcript quote, B-roll list, graphic/motion technique, timing. ✅/🔍 tag.
7. **Replication targets** — checkbox list mapping patterns → concrete Outpost script steps + Hyperframes components to build.
8. **Running log / open questions** — resolved vs open; next build step.
9. **Asset index** — every frame/sheet/transcript path.
</breakdown_doc_skeleton>

<constraints>
- One image per section when reading (montages), not frame dumps.
- 4 columns on section sheets so each row = 1.0s (motion reads horizontally).
- Burn timecodes into every frame/cell (yellow on dark box).
- Keep frames ~360w / q:v 6 — low tax.
- Lead with MOTION analysis; content is supporting context.
- Be honest about studied (✅) vs glanced (🔍).
- Don't fabricate; flag the real-asset aesthetic for honest replication.
- If transcription is slow, keep working (frames, overview, doc skeleton) while it runs.
</constraints>
