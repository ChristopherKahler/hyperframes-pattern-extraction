# Fork notes

This fork adds a CPU-first local transcription engine so the skill works without an ElevenLabs API key.

## What changed from upstream

| File | Change |
|---|---|
| `helpers/transcribe_local.py` | **New.** WhisperX + pyannote replacement that emits Scribe-shaped JSON. Drop-in for `transcribe.py`. |
| `helpers/transcribe_batch.py` | Rewritten to route via `--engine local\|scribe`. Local engine runs serially with a shared model. |
| `pyproject.toml` | Added `[project.optional-dependencies].local` with whisperx, torch, pyannote. |
| `.env.example` | Added `HF_TOKEN` (required for diarization). |
| `helpers/transcribe.py` | **Unchanged.** Upstream Scribe reference. |
| `helpers/pack_transcripts.py`, `helpers/render.py` | **Unchanged.** Consumers of the JSON contract. |
| `SKILL.md` | **Unchanged.** Preserves the skill's canonical brain. |

## JSON contract

Both engines emit the same shape so everything downstream (packer, renderer, EDL generator) stays identical:

```json
{
  "language_code": "en",
  "words": [
    {"type": "word",    "text": "Hello",  "start": 0.12, "end": 0.48, "speaker_id": "speaker_0"},
    {"type": "spacing", "text": " ",      "start": 0.48, "end": 0.61},
    {"type": "word",    "text": "world.", "start": 0.61, "end": 1.05, "speaker_id": "speaker_0"}
  ]
}
```

The `spacing` entries are load-bearing: `pack_transcripts.py` uses `spacing.end - spacing.start` to detect silence gaps ≥ 0.5s and break phrases on them. The local transcriber synthesizes these from inter-word gaps in WhisperX's forced-aligned output.

## Local vs Scribe — honest tradeoffs

| Aspect | Scribe | Local (WhisperX large-v3) |
|---|---|---|
| Word timestamp precision | ±50-100ms drift | ±20-40ms (wav2vec2 forced alignment, often tighter) |
| Filler preservation | ~98% verbatim | ~85% — Whisper trained to drop disfluencies. Mitigated by `initial_prompt` + `condition_on_previous_text=False` |
| Audio events `(laughs)` `(applause)` | Native inline tags | Not emitted. Add a YAMNet pass if needed. |
| Speaker diarization | Native | pyannote 3.1 (requires HF_TOKEN) |
| Cost | ~$0.40/hr of audio | $0 after one-time model downloads (~5GB) |
| Throughput (CPU, 4 threads, large-v3 int8) | N/A — API | ~0.3-0.7x realtime. 30 min video = 40-90 min to transcribe. |
| Throughput (GPU, float16) | N/A | ~3-5x realtime typical |
| First-run cost | None | ~5GB model download (Whisper + wav2vec2 + pyannote) |

## Hard-rule compliance

Hard Rule 8 says "word-level verbatim ASR only, never normalized fillers." The local engine only *mostly* complies — Whisper will still drop some fillers. The `initial_prompt` + `condition_on_previous_text=False` combo gets close but is not perfect. If editorial precision matters (keeping false-start detection sharp), use `--engine scribe` for that specific project.

Hard Rule 9 (cache per source) is preserved — same output path, same skip-if-exists behavior.

All other hard rules (applied during render, not transcribe) are untouched.

## Usage

```bash
# One-time install
pip install -e ".[local]"

# Transcribe a single video (defaults: cpu, large-v3, int8, diarize on)
python helpers/transcribe_local.py /path/to/video.mp4

# Batch a folder
python helpers/transcribe_batch.py /path/to/videos/

# Skip diarization if you don't have HF_TOKEN set up yet
python helpers/transcribe_local.py /path/to/video.mp4 --no-diarize

# Force GPU
python helpers/transcribe_local.py /path/to/video.mp4 --device cuda --compute-type float16

# Fallback to Scribe for one project
python helpers/transcribe_batch.py /path/to/videos/ --engine scribe
```

## Upstream sync

When upstream changes, pull into this fork and pay attention to:
- `transcribe.py` — if upstream modifies it, merge cleanly (we didn't touch it)
- `pack_transcripts.py` — if the JSON contract changes, update `_whisperx_to_scribe_words()` in `transcribe_local.py`
- `render.py` — if it starts consuming new word fields, mirror them in the local transcriber

The `_engine` and `_model` fields in local output are private metadata — upstream's consumers ignore unknown keys.
