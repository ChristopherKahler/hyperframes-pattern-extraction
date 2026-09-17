# video-use — Usage

How to boot a fresh Claude Code session and use this. Works two ways: through Claude (the intended UX) or by calling the helpers directly from your shell.

## Setup state (already done on this machine)

- Cloned to `apps/video-use/`, symlinked to `~/.claude/skills/video-use`
- `.venv/` created with torch, whisperx, pyannote, faster-whisper, ctranslate2
- `ffmpeg` + `ffprobe` symlinked from Windows chocolatey
- Helpers auto-reexec into `.venv/bin/python` — no manual activation needed

## One-time setup remaining

Only needed if you want speaker diarization (who said what):

1. Create HF token (Read scope): https://huggingface.co/settings/tokens
2. Accept terms while logged in:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. `cp apps/video-use/.env.example apps/video-use/.env` then paste `HF_TOKEN=hf_xxxxx`

Skip this and pass `--no-diarize` if you don't need speaker labels.

---

## Path A — Through Claude Code (normal workflow)

The skill is designed to be driven by conversation. Claude reads `SKILL.md`, inventories your footage, proposes a strategy, waits for your OK, then edits.

```bash
cd /path/to/folder/with/videos
claude
```

Then in the session:

> edit these into a launch video

Claude will:
1. Inventory the files, transcribe via local WhisperX (default, no API call), pack into `edit/takes_packed.md`
2. Ask you questions shaped by what it sees
3. Propose a strategy in plain English
4. Wait for your OK
5. Build the EDL, render, self-eval, show preview
6. Iterate on feedback, then final render → `edit/final.mp4`

First run transcribes — slow because it downloads ~5GB of models. Subsequent runs are fast.

## Path B — Run helpers directly (testing/debugging)

Useful for sanity-checking the transcriber without firing up the whole skill loop.

### Test with a short clip

```bash
cd /path/to/video-use

# Transcribe (no diarize = skips speaker labels, no HF_TOKEN needed)
python helpers/transcribe_local.py /path/to/clip.mp4 --no-diarize

# With diarization (needs HF_TOKEN in .env)
python helpers/transcribe_local.py /path/to/clip.mp4 --num-speakers 2

# Batch a folder
python helpers/transcribe_batch.py /path/to/videos/ --no-diarize
```

Output lands at `/path/to/clip_parent/edit/transcripts/clip.json`.

### Verify it worked

```bash
# See the raw transcript
cat /path/to/clip_parent/edit/transcripts/clip.json | head -50

# Pack into the phrase-level markdown (what the LLM would read)
python helpers/pack_transcripts.py --edit-dir /path/to/clip_parent/edit
cat /path/to/clip_parent/edit/takes_packed.md
```

If the packed markdown shows phrase-level lines with timestamps and (optionally) speaker tags, the pipeline works end-to-end.

## Engine switching

Both entry points default to `--engine local`. To use Scribe explicitly (requires `ELEVENLABS_API_KEY` in `.env`):

```bash
python helpers/transcribe_batch.py /path/to/videos/ --engine scribe --workers 4
```

## Common flags

| Flag | Meaning |
|---|---|
| `--model large-v3` | Whisper model size. Default is accurate + slowest. Options: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3` |
| `--device cuda` | Use GPU instead of CPU. Defaults to CPU. |
| `--compute-type int8` | Quantization. `int8` (CPU default, fastest), `float16` (GPU default), `int8_float16` (GPU, lower VRAM) |
| `--batch-size 4` | Lower = less RAM. Default 4 on CPU. |
| `--threads 8` | CPU thread count. Default uses all available. WSL2 may undercount. |
| `--language en` | Skip auto-detect. |
| `--num-speakers 2` | When known — improves diarization. |
| `--no-diarize` | Skip speaker labels, no HF_TOKEN needed. |

## Expected throughput (this machine)

- CPU (i7-10700KF @ 4 WSL threads, int8, large-v3): roughly **0.3–0.7x realtime**
  - 5 min clip ≈ 7–15 min wall time
  - 30 min clip ≈ 40–90 min
  - 60 min clip ≈ 1.5–3 hrs
- GPU (GTX 1070, float16): roughly **3–5x realtime** — same hardware, much faster, but grabs VRAM from other work

Bump WSL threads by editing `C:\Users\<you>\.wslconfig`:
```
[wsl2]
processors=12
memory=24GB
```
Then `wsl --shutdown` from Windows PowerShell to apply.

## First-run model downloads (automatic, one-time)

On first transcription the stack downloads to `~/.cache/huggingface/`:
- Whisper `large-v3` weights — ~3 GB
- wav2vec2 alignment model — ~1.2 GB (per language)
- pyannote diarization — ~500 MB

After that: instant model load from cache.

## Troubleshooting

**"HF_TOKEN not set" warning** — either add it to `.env` or pass `--no-diarize`.

**Transcript empty or short** — run without `--language` to let Whisper auto-detect. Or check the source audio is actually speech (not music only).

**OOM on CPU** — lower `--batch-size 1` and drop to `--model medium`.

**Transcript cached when you don't want it to be** — delete `edit/transcripts/<name>.json` and re-run.

**Skill feels slow to respond** — first-run model downloads are happening. Watch bandwidth. After that, load is fast.

## What not to touch

- `SKILL.md` — the skill's operational brain (merge-sensitive to upstream). Small fork edits only, documented in `FORK-NOTES.md`.
- `helpers/transcribe.py` — untouched upstream Scribe reference.
- `helpers/pack_transcripts.py`, `helpers/render.py` — untouched upstream consumers.

All fork-specific changes live in `helpers/transcribe_local.py`, `helpers/transcribe_batch.py`, `pyproject.toml`, `.env.example`, and `FORK-NOTES.md`.
