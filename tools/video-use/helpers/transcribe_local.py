#!/usr/bin/env python3
"""Transcribe a video locally with WhisperX + pyannote.

Drop-in replacement for `transcribe.py` that avoids the ElevenLabs Scribe API.
Writes the same JSON shape to <edit_dir>/transcripts/<video_stem>.json so the
downstream packer and renderer keep working unchanged.

Pipeline:
    1. ffmpeg extract mono 16kHz wav (identical to transcribe.py)
    2. faster-whisper ASR via WhisperX (word_timestamps=True, initial_prompt
       biased toward disfluencies so "um"/"uh"/false starts are transcribed)
    3. wav2vec2 forced alignment for precise word boundaries (±20-40ms typical,
       tighter than Scribe's ±50-100ms drift)
    4. pyannote 3.x diarization (optional — skipped when --no-diarize)
    5. Merge: walk word_segments, emit type="word" entries, synthesize
       type="spacing" entries between consecutive words whose gap > 0.

Runs on CPU by default (int8 quantization). large-v3 on a modern desktop CPU
transcribes at roughly 0.3-0.7x realtime — a 30 min source takes 40-90 min.
Pass --device cuda --compute-type float16 if you want to use a GPU instead.

Output JSON shape (matches Scribe contract consumed by pack_transcripts.py
and render.py):

    {
      "language_code": "en",
      "words": [
        {"type": "word",    "text": "Hello",  "start": 0.12, "end": 0.48,
         "speaker_id": "speaker_0"},
        {"type": "spacing", "text": " ",      "start": 0.48, "end": 0.61},
        {"type": "word",    "text": "world.", "start": 0.61, "end": 1.05,
         "speaker_id": "speaker_0"},
        ...
      ]
    }

Audio events (laughter/applause/sighs) are NOT emitted — Whisper has no
native event detection. If you need them, pass --audio-events to enable a
separate YAMNet pass (not yet implemented; see FORK-NOTES.md).

Caching: if <edit_dir>/transcripts/<stem>.json exists, the transcription
is skipped. Identical contract to transcribe.py (Hard Rule 9).

Usage:
    python helpers/transcribe_local.py <video_path>
    python helpers/transcribe_local.py <video_path> --model large-v3
    python helpers/transcribe_local.py <video_path> --num-speakers 2
    python helpers/transcribe_local.py <video_path> --no-diarize
    python helpers/transcribe_local.py <video_path> --language en
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Auto-reexec into the project venv if present and we're not already in it.
# Keeps `python helpers/transcribe_local.py ...` working without needing the
# user to activate the venv first.
_VENV_PY = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
if _VENV_PY.exists() and sys.executable != str(_VENV_PY):
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

import argparse
import gc
import json
import subprocess
import tempfile
import time


# ---------------------------------------------------------------------------
# Env / config
# ---------------------------------------------------------------------------

# Biases Whisper's decoder toward transcribing disfluencies verbatim instead
# of cleaning them up. Combined with condition_on_previous_text=False
# (WhisperX default), this preserves ~85% of fillers vs Scribe's ~98%.
DEFAULT_FILLER_PROMPT = (
    "Umm, uh, ah, so, like, you know, I mean, well, right, okay, "
    "uhh, hmm, uhh... false start, let me try again."
)

# pyannote HF model IDs — both require accepting terms of use on HF once
# per account, then an HF_TOKEN in env or .env.
DIARIZE_MODEL = "pyannote/speaker-diarization-3.1"


def load_env_vars() -> dict[str, str]:
    env: dict[str, str] = {}
    for candidate in [Path(__file__).resolve().parent.parent / ".env", Path(".env")]:
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("HF_TOKEN", "HUGGINGFACE_TOKEN"):
        if k in os.environ:
            env.setdefault(k, os.environ[k])
    return env


# ---------------------------------------------------------------------------
# Model cache — load once per process, not per file
# ---------------------------------------------------------------------------

_MODEL_CACHE: dict = {}


def _get_asr_model(model_name: str, device: str, compute_type: str, language: str | None):
    key = ("asr", model_name, device, compute_type, language or "auto")
    if key not in _MODEL_CACHE:
        import whisperx  # imported lazily so scribe path doesn't need torch

        asr_options = {
            "initial_prompt": DEFAULT_FILLER_PROMPT,
            # WhisperX defaults condition_on_previous_text to False already,
            # but pin it explicitly to prevent decoder from retroactively
            # cleaning up filler sequences across windows.
            "condition_on_previous_text": False,
        }
        _MODEL_CACHE[key] = whisperx.load_model(
            model_name,
            device=device,
            compute_type=compute_type,
            language=language,
            asr_options=asr_options,
        )
    return _MODEL_CACHE[key]


def _get_align_model(language: str, device: str):
    key = ("align", language, device)
    if key not in _MODEL_CACHE:
        import whisperx
        _MODEL_CACHE[key] = whisperx.load_align_model(language_code=language, device=device)
    return _MODEL_CACHE[key]


def _get_diarize_pipeline(hf_token: str, device: str):
    key = ("diarize", device)
    if key not in _MODEL_CACHE:
        import whisperx
        _MODEL_CACHE[key] = whisperx.DiarizationPipeline(
            model_name=DIARIZE_MODEL,
            use_auth_token=hf_token,
            device=device,
        )
    return _MODEL_CACHE[key]


def clear_model_cache() -> None:
    """Release VRAM. Call between large batches if memory gets tight."""
    _MODEL_CACHE.clear()
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Audio extraction (identical to transcribe.py — keeps one canonical wav spec)
# ---------------------------------------------------------------------------


def extract_audio(video_path: Path, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Core transcription
# ---------------------------------------------------------------------------


def _normalize_speaker_id(raw: str | None) -> str | None:
    """pyannote returns 'SPEAKER_00', Scribe returns 'speaker_0'. Normalize
    to Scribe's shape so pack_transcripts.py's speaker_X stripping works
    unchanged."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s.upper().startswith("SPEAKER_"):
        try:
            return f"speaker_{int(s.split('_', 1)[1])}"
        except (ValueError, IndexError):
            return s.lower()
    return s


def _whisperx_to_scribe_words(word_segments: list[dict]) -> list[dict]:
    """Transform WhisperX word_segments into Scribe-shaped word list with
    synthesized spacing entries between consecutive words that have a gap.

    Missing timestamps: WhisperX may fail to align some words (rare, happens
    with heavy noise). Drop those — emitting words without timestamps breaks
    the packer's gap detection."""
    out: list[dict] = []
    prev_end: float | None = None

    for w in word_segments:
        text = (w.get("word") or "").strip()
        if not text:
            continue
        start = w.get("start")
        end = w.get("end")
        if start is None or end is None:
            # Unaligned word — skip rather than emit with guessed timestamps.
            continue
        start = float(start)
        end = float(end)

        if prev_end is not None and start > prev_end:
            # Insert a spacing entry covering the silence gap. The packer
            # uses (end - start) on spacing entries to decide phrase
            # boundaries — this is the load-bearing bit.
            out.append({
                "type": "spacing",
                "text": " ",
                "start": prev_end,
                "end": start,
            })

        entry = {
            "type": "word",
            "text": text,
            "start": start,
            "end": end,
        }
        speaker = _normalize_speaker_id(w.get("speaker"))
        if speaker is not None:
            entry["speaker_id"] = speaker
        out.append(entry)
        prev_end = end

    return out


def transcribe_one(
    video: Path,
    edit_dir: Path,
    model_name: str = "large-v3",
    device: str | None = None,
    compute_type: str | None = None,
    batch_size: int = 4,
    threads: int | None = None,
    language: str | None = None,
    num_speakers: int | None = None,
    min_speakers: int | None = None,
    max_speakers: int | None = None,
    diarize: bool = True,
    hf_token: str | None = None,
    initial_prompt: str | None = None,
    verbose: bool = True,
) -> Path:
    """Transcribe a single video locally. Returns path to transcript JSON.

    Cached: returns existing path immediately if the transcript already exists.
    Matches transcribe.py:transcribe_one() return shape so transcribe_batch.py
    can swap engines without further changes."""
    import whisperx  # lazy

    # Device/precision defaults — CPU-first. Explicit opt-in for GPU via
    # --device cuda so background tasks don't surprise-grab VRAM.
    if device is None:
        device = "cpu"
    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "int8"

    # CTranslate2 CPU threading. Defaults to os.cpu_count() which in WSL2
    # may undercount — pass threads explicitly if you've tuned .wslconfig.
    if device == "cpu" and threads is not None and threads > 0:
        os.environ.setdefault("OMP_NUM_THREADS", str(threads))

    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"

    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path

    if verbose:
        print(f"  extracting audio from {video.name}", flush=True)

    t0 = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, audio_path)

        audio = whisperx.load_audio(str(audio_path))

        # --- Step 1: ASR -----------------------------------------------------
        if verbose:
            print(f"  asr ({model_name} on {device}/{compute_type})", flush=True)

        # Override the module-level prompt if caller supplied their own.
        if initial_prompt is not None:
            asr_key = ("asr", model_name, device, compute_type, language or "auto")
            # Rebuild model with custom prompt (rare path).
            _MODEL_CACHE.pop(asr_key, None)
            import whisperx as _wx
            model = _wx.load_model(
                model_name, device=device, compute_type=compute_type,
                language=language,
                asr_options={
                    "initial_prompt": initial_prompt,
                    "condition_on_previous_text": False,
                },
            )
            _MODEL_CACHE[asr_key] = model
        else:
            model = _get_asr_model(model_name, device, compute_type, language)

        result = model.transcribe(audio, batch_size=batch_size)
        detected_language = result.get("language", language or "en")

        # --- Step 2: Align ---------------------------------------------------
        if verbose:
            print(f"  aligning ({detected_language})", flush=True)
        align_model, align_meta = _get_align_model(detected_language, device)
        result = whisperx.align(
            result["segments"],
            align_model,
            align_meta,
            audio,
            device,
            return_char_alignments=False,
        )

        # --- Step 3: Diarize (optional) --------------------------------------
        if diarize:
            if not hf_token:
                if verbose:
                    print("  no HF_TOKEN — skipping diarization", flush=True)
            else:
                if verbose:
                    print("  diarizing", flush=True)
                diarize_pipeline = _get_diarize_pipeline(hf_token, device)
                diarize_kwargs: dict = {}
                if num_speakers is not None:
                    diarize_kwargs["num_speakers"] = num_speakers
                if min_speakers is not None:
                    diarize_kwargs["min_speakers"] = min_speakers
                if max_speakers is not None:
                    diarize_kwargs["max_speakers"] = max_speakers
                diarize_segments = diarize_pipeline(audio, **diarize_kwargs)
                result = whisperx.assign_word_speakers(diarize_segments, result)

    # --- Step 4: Transform into Scribe-shaped JSON ---------------------------
    word_segments = result.get("word_segments", [])
    if not word_segments:
        # Some whisperx versions return words only inside segments; flatten.
        word_segments = [
            w for seg in result.get("segments", []) for w in seg.get("words", [])
        ]

    scribe_words = _whisperx_to_scribe_words(word_segments)

    payload = {
        "language_code": detected_language,
        "words": scribe_words,
        # Mark the source engine so FORK-NOTES consumers can distinguish.
        "_engine": "whisperx-local",
        "_model": model_name,
    }

    out_path.write_text(json.dumps(payload, indent=2))
    dt = time.time() - t0

    if verbose:
        kb = out_path.stat().st_size / 1024
        word_count = sum(1 for w in scribe_words if w["type"] == "word")
        print(f"  saved: {out_path.name} ({kb:.1f} KB) in {dt:.1f}s")
        print(f"    words: {word_count}  lang: {detected_language}")

    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video locally with WhisperX + pyannote")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--model", default="large-v3",
                    help="faster-whisper model name (large-v3, large-v2, medium, small, base, tiny)")
    ap.add_argument("--device", default="cpu", help="cpu | cuda (default: cpu)")
    ap.add_argument("--compute-type", default=None,
                    help="int8 | float16 | int8_float16 (default: int8 on cpu, float16 on cuda)")
    ap.add_argument("--batch-size", type=int, default=4,
                    help="whisperx batch size. Lower = less RAM. Default 4 (CPU-friendly).")
    ap.add_argument("--threads", type=int, default=None,
                    help="OMP/CPU threads (default: all available). Useful on WSL2.")
    ap.add_argument("--language", default=None,
                    help="ISO language code (e.g. 'en'). Omit to auto-detect.")
    ap.add_argument("--num-speakers", type=int, default=None)
    ap.add_argument("--min-speakers", type=int, default=None)
    ap.add_argument("--max-speakers", type=int, default=None)
    ap.add_argument("--no-diarize", action="store_true",
                    help="Skip speaker diarization (no HF_TOKEN required)")
    ap.add_argument("--initial-prompt", default=None,
                    help="Override the default filler-preserving initial prompt")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    env = load_env_vars()
    hf_token = env.get("HF_TOKEN") or env.get("HUGGINGFACE_TOKEN")

    diarize = not args.no_diarize
    if diarize and not hf_token:
        print("note: diarize requested but HF_TOKEN not set — continuing without speaker labels",
              file=sys.stderr)

    transcribe_one(
        video=video,
        edit_dir=edit_dir,
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
        batch_size=args.batch_size,
        threads=args.threads,
        language=args.language,
        num_speakers=args.num_speakers,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        diarize=diarize,
        hf_token=hf_token,
        initial_prompt=args.initial_prompt,
    )


if __name__ == "__main__":
    main()
