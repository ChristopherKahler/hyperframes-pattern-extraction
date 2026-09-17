#!/usr/bin/env python3
"""Batch-transcribe every video in a directory.

Walks <videos_dir> for common video extensions, writes transcripts to
<videos_dir>/edit/transcripts/<name>.json. Cached per-file.

Two engines:
  - local  (default): WhisperX + pyannote on CPU. No API, no cost.
  - scribe: ElevenLabs Scribe. Requires ELEVENLABS_API_KEY.

Local engine runs serially with a shared model to avoid reloading between
files. Scribe engine uses parallel workers (the API fans out better).

Usage:
    python helpers/transcribe_batch.py <videos_dir>
    python helpers/transcribe_batch.py <videos_dir> --engine scribe --workers 4
    python helpers/transcribe_batch.py <videos_dir> --model large-v3 --threads 8
    python helpers/transcribe_batch.py <videos_dir> --num-speakers 2
    python helpers/transcribe_batch.py <videos_dir> --edit-dir /custom/edit
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_VENV_PY = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
if _VENV_PY.exists() and sys.executable != str(_VENV_PY):
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


VIDEO_EXTS = {".mp4", ".MP4", ".mov", ".MOV", ".mkv", ".MKV", ".avi", ".AVI", ".m4v"}


def find_videos(videos_dir: Path) -> list[Path]:
    return sorted(
        p for p in videos_dir.iterdir()
        if p.is_file() and p.suffix in VIDEO_EXTS
    )


def _run_scribe(pending: list[Path], edit_dir: Path, args) -> list[tuple[Path, str]]:
    from transcribe import load_api_key, transcribe_one
    api_key = load_api_key()

    errors: list[tuple[Path, str]] = []
    print(f"transcribing {len(pending)} files via Scribe with {args.workers} parallel workers")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                transcribe_one,
                video=v,
                edit_dir=edit_dir,
                api_key=api_key,
                language=args.language,
                num_speakers=args.num_speakers,
                verbose=False,
            ): v
            for v in pending
        }
        for fut in as_completed(futures):
            v = futures[fut]
            try:
                out = fut.result()
                print(f"  + {v.stem}  →  {out.name}")
            except Exception as e:
                errors.append((v, str(e)))
                print(f"  x {v.stem}  FAILED: {e}")
    return errors


def _run_local(pending: list[Path], edit_dir: Path, args) -> list[tuple[Path, str]]:
    from transcribe_local import load_env_vars, transcribe_one

    env = load_env_vars()
    hf_token = env.get("HF_TOKEN") or env.get("HUGGINGFACE_TOKEN")
    diarize = not args.no_diarize
    if diarize and not hf_token:
        print("note: HF_TOKEN not set — continuing without speaker labels", file=sys.stderr)

    print(f"transcribing {len(pending)} files via local WhisperX "
          f"({args.model} on {args.device}) — serial")

    errors: list[tuple[Path, str]] = []
    for v in pending:
        try:
            out = transcribe_one(
                video=v,
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
                verbose=True,
            )
            print(f"  + {v.stem}  →  {out.name}")
        except Exception as e:
            errors.append((v, str(e)))
            print(f"  x {v.stem}  FAILED: {e}")
    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch transcribe a directory of videos")
    ap.add_argument("videos_dir", type=Path, help="Directory containing source videos")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <videos_dir>/edit)")
    ap.add_argument("--engine", choices=["local", "scribe"], default="local",
                    help="Transcription engine (default: local)")
    ap.add_argument("--workers", type=int, default=4,
                    help="Parallel workers for Scribe engine only (default: 4)")
    ap.add_argument("--language", type=str, default=None,
                    help="ISO language code (e.g. 'en'). Omit to auto-detect.")
    ap.add_argument("--num-speakers", type=int, default=None,
                    help="Number of speakers when known. Improves diarization.")
    # Local-engine only
    ap.add_argument("--model", default="large-v3",
                    help="[local] faster-whisper model. Default large-v3.")
    ap.add_argument("--device", default="cpu",
                    help="[local] cpu | cuda (default: cpu)")
    ap.add_argument("--compute-type", default=None,
                    help="[local] int8 | float16 | int8_float16")
    ap.add_argument("--batch-size", type=int, default=4,
                    help="[local] WhisperX batch size (default: 4)")
    ap.add_argument("--threads", type=int, default=None,
                    help="[local] CPU threads (default: all available)")
    ap.add_argument("--min-speakers", type=int, default=None,
                    help="[local] Lower bound for diarization")
    ap.add_argument("--max-speakers", type=int, default=None,
                    help="[local] Upper bound for diarization")
    ap.add_argument("--no-diarize", action="store_true",
                    help="[local] Skip speaker diarization")
    args = ap.parse_args()

    videos_dir = args.videos_dir.resolve()
    if not videos_dir.is_dir():
        sys.exit(f"not a directory: {videos_dir}")

    edit_dir = (args.edit_dir or (videos_dir / "edit")).resolve()
    (edit_dir / "transcripts").mkdir(parents=True, exist_ok=True)

    videos = find_videos(videos_dir)
    if not videos:
        sys.exit(f"no videos found in {videos_dir}")

    already_cached = [v for v in videos if (edit_dir / "transcripts" / f"{v.stem}.json").exists()]
    pending = [v for v in videos if v not in already_cached]

    print(f"found {len(videos)} videos ({len(already_cached)} cached, {len(pending)} to transcribe)")
    if not pending:
        print("nothing to do")
        return

    t0 = time.time()
    if args.engine == "scribe":
        errors = _run_scribe(pending, edit_dir, args)
    else:
        errors = _run_local(pending, edit_dir, args)

    dt = time.time() - t0
    print(f"\ndone in {dt:.1f}s")
    if errors:
        print(f"{len(errors)} failures:")
        for v, msg in errors:
            print(f"  {v.name}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
