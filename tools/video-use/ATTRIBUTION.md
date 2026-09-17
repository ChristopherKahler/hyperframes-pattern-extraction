# Attribution — this directory is a fork

Everything in `tools/video-use/` originates from **[browser-use/video-use](https://github.com/browser-use/video-use)**, MIT licensed. The upstream
licence is carried verbatim in [LICENSE](LICENSE) and applies to this whole
directory.

It is vendored here rather than linked because `/wordsrt` and `/breakdown-reel`
call these helpers by filename. Without them those commands do not run.

## Upstream, unmodified

Authored by Gregor Žunič and the browser-use contributors:

| File | Role |
|---|---|
| `helpers/transcribe.py` | ElevenLabs Scribe transcription (the hosted path) |
| `helpers/pack_transcripts.py` | packs word JSON into phrase-broken takes |
| `helpers/render.py` | EDL / render generation |
| `helpers/grade.py` | colour grading |
| `helpers/timeline_view.py` | timeline visualisation |
| `SKILL.md` | the skill's canonical brain |
| `README.md`, `poster.html`, `static/`, `skills/manim-video/` | upstream docs and assets |

## Fork additions

Authored by Christopher Kahler, same MIT terms:

| File | Why it exists |
|---|---|
| `helpers/transcribe_local.py` | **The reason for the fork.** WhisperX + pyannote replacement for Scribe, emitting Scribe-shaped JSON so nothing downstream changes. Runs with no API key. |
| `helpers/word_srt.py` | derives a **one-cue-per-word** SRT from the word JSON |
| `helpers/segment_srt.py` | phrase-level SRT, derived the same way |
| `helpers/bg_fetch.py` | background asset fetch |
| `helpers/transcribe_batch.py` | rewritten to route `--engine local\|scribe` |
| `pyproject.toml` | adds the `[local]` extra: whisperx, torch, pyannote |
| `.env.example` | adds `HF_TOKEN` for diarisation |
| `USAGE.md`, `FORK-NOTES.md`, `HF-TOKEN-SETUP.md` | fork docs |

## The contract that holds it together

Both engines emit the same JSON, so the packer, renderer and EDL generator are
identical either way:

```json
{"language_code": "en",
 "words": [
   {"type": "word",    "text": "Hello",  "start": 0.12, "end": 0.48, "speaker_id": "speaker_0"},
   {"type": "spacing", "text": " ",      "start": 0.48, "end": 0.61},
   {"type": "word",    "text": "world.", "start": 0.61, "end": 1.05, "speaker_id": "speaker_0"}
 ]}
```

**The `spacing` entries are load-bearing.** `pack_transcripts.py` uses
`spacing.end - spacing.start` to find silence gaps ≥0.5s and break phrases on
them. `transcribe_local.py` synthesises them from inter-word gaps in WhisperX's
forced-aligned output. Strip them and phrase breaking silently stops working.

## Local vs Scribe, honestly

| | Scribe (hosted) | Local (WhisperX large-v3) |
|---|---|---|
| Word timestamp precision | ±50-100ms drift | ±20-40ms (wav2vec2 forced alignment) |
| Filler preservation | ~98% verbatim | ~85% — Whisper is trained to drop disfluencies |
| Audio events `(laughs)` | native inline tags | not emitted |
| Diarisation | native | pyannote 3.1, needs `HF_TOKEN` |
| Cost | ~$0.40/hr audio | $0 after a ~5GB one-time model download |
| Throughput | API | CPU ~0.3-0.7x realtime · GPU float16 ~3-5x |

A 30-minute video is 40-90 minutes to transcribe on CPU. Background it.

See [FORK-NOTES.md](FORK-NOTES.md) for the full upstream diff rationale.
