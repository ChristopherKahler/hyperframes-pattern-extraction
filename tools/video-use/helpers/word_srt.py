#!/usr/bin/env python3
"""Convert a Scribe/WhisperX-shaped transcript JSON into a WORD-LEVEL SRT.

The transcript JSON is the shape emitted by ``transcribe_local.py`` /
``transcribe.py`` — a top-level ``words[]`` array whose entries are either
``{"type":"word", "text", "start", "end", ...}`` or ``{"type":"spacing", ...}``.

This emits one SRT cue PER WORD (not per phrase), so every spoken word maps to
an exact start/end timecode. That is the artifact you anchor against for
frame-accurate work: HyperFrames overlays, Filmora keyframes, caption pop-ins.

Usage:
  word_srt.py <transcript.json> [-o out.srt] [--min-dur 0.06] [--pad 0.0]

If -o is omitted, writes ``<json_dir>/<json_stem>.words.srt``.
"""
import argparse
import json
import sys
from pathlib import Path


def ts(seconds: float) -> str:
    """seconds -> SRT timecode HH:MM:SS,mmm"""
    if seconds < 0:
        seconds = 0.0
    ms_total = int(round(seconds * 1000))
    h, ms_total = divmod(ms_total, 3_600_000)
    m, ms_total = divmod(ms_total, 60_000)
    s, ms = divmod(ms_total, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser(description="word-level transcript JSON -> word-level SRT")
    ap.add_argument("transcript", help="path to the transcript .json")
    ap.add_argument("-o", "--out", help="output .srt path (default: <stem>.words.srt beside the json)")
    ap.add_argument("--min-dur", type=float, default=0.06,
                    help="minimum cue duration in seconds (default 0.06)")
    ap.add_argument("--pad", type=float, default=0.0,
                    help="seconds to extend each word's end timecode (default 0)")
    args = ap.parse_args()

    src = Path(args.transcript)
    data = json.loads(src.read_text(encoding="utf-8"))
    words = [w for w in data.get("words", [])
             if w.get("type") == "word" and str(w.get("text", "")).strip()]
    if not words:
        sys.exit(f"no word entries found in {src}")

    out = Path(args.out) if args.out else src.parent / (src.stem + ".words.srt")

    blocks = []
    for i, w in enumerate(words, 1):
        start = float(w["start"])
        end = float(w.get("end", start)) + args.pad
        if end - start < args.min_dur:
            end = start + args.min_dur
        blocks.append(f"{i}\n{ts(start)} --> {ts(end)}\n{str(w['text']).strip()}\n")

    out.write_text("\n".join(blocks), encoding="utf-8")
    print(f"wrote {len(words)} word cues -> {out}")


if __name__ == "__main__":
    main()
