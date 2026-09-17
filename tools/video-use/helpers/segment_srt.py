#!/usr/bin/env python3
"""Segment-level SRT from a video-use transcript .json.

word_srt.py emits one cue per word (karaoke). This emits readable subtitle cues
by grouping words: break on silence, sentence end, line budget, or max duration
-- whichever comes first. Use this for normal captions (YouTube, Filmora).

The local whisperx engine emits {"words": [...]} with no "segments" key, so cues
are rebuilt from word timings here.
"""

import argparse
import json
from pathlib import Path


def ts(seconds: float) -> str:
    """Seconds -> SRT timestamp (HH:MM:SS,mmm)."""
    h, rem = divmod(max(seconds, 0.0), 3600)
    m, s = divmod(rem, 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"


def wrap(text: str, width: int) -> str:
    """Break a cue into two balanced lines at the space nearest the midpoint."""
    if len(text) <= width:
        return text
    mid = len(text) // 2
    left = text.rfind(" ", 0, mid)
    right = text.find(" ", mid)
    if left == -1 and right == -1:
        return text
    if left == -1:
        cut = right
    elif right == -1:
        cut = left
    else:
        cut = left if (mid - left) <= (right - mid) else right
    return text[:cut] + "\n" + text[cut + 1:]


def build_cues(words, gap, max_chars, max_dur, min_sent_chars):
    cues, cur = [], []
    for w in words:
        if cur:
            text = " ".join(x["text"] for x in cur)
            silence = w["start"] - cur[-1]["end"]
            duration = cur[-1]["end"] - cur[0]["start"]
            sentence_end = cur[-1]["text"].endswith((".", "?", "!"))
            if (silence >= gap
                    or len(text) + 1 + len(w["text"]) > max_chars
                    or duration >= max_dur
                    or (sentence_end and len(text) >= min_sent_chars)):
                cues.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    return cues


def main() -> None:
    ap = argparse.ArgumentParser(description="Segment-level SRT from a transcript .json")
    ap.add_argument("transcript", type=Path, help="path to the transcript .json")
    ap.add_argument("-o", "--out", type=Path, default=None,
                    help="output .srt path (default: <stem>.srt beside the json)")
    ap.add_argument("--gap", type=float, default=0.6,
                    help="silence in seconds that forces a cue break (default: 0.6)")
    ap.add_argument("--max-chars", type=int, default=84,
                    help="max characters per cue, two lines (default: 84)")
    ap.add_argument("--max-dur", type=float, default=6.0,
                    help="max cue duration in seconds (default: 6.0)")
    ap.add_argument("--min-sent-chars", type=int, default=25,
                    help="don't break on a sentence end shorter than this (default: 25)")
    ap.add_argument("--line-width", type=int, default=42,
                    help="wrap to two lines past this width (default: 42)")
    args = ap.parse_args()

    data = json.loads(args.transcript.read_text(encoding="utf-8"))
    words = [w for w in data.get("words", []) if w.get("type") == "word"]
    if not words:
        raise SystemExit(f"no word-level entries in {args.transcript}")

    cues = build_cues(words, args.gap, args.max_chars, args.max_dur, args.min_sent_chars)

    out = args.out or args.transcript.with_suffix(".srt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, cue in enumerate(cues, 1):
            body = wrap(" ".join(x["text"] for x in cue), args.line_width)
            f.write(f"{i}\n{ts(cue[0]['start'])} --> {ts(cue[-1]['end'])}\n{body}\n\n")

    print(f"  saved: {out.name}  cues: {len(cues)}  words: {len(words)}")


if __name__ == "__main__":
    main()
