#!/usr/bin/env python3
"""
reel.py - concatenate pattern renders into ONE labelled approval reel (G7).

Chris, 2026-08-27: stills cannot show motion, and eight separate files is
eight things to open on a phone. One reel, every clip labelled on screen, he
watches once and replies with names.

Each clip gets:
  - a 0.6 s slate before it: big label, centred, so he knows what is coming
  - the label burned bottom-left for the clip's whole duration
  - normalised to 1920x1080 @ 30 fps yuv420p, no audio, so concat is byte-safe

A manifest (<out>.manifest.json) records index, label, file and the reel
timestamps of every clip, so a reply like "3 is wrong" or "packetRide mirror
is wrong" maps back to a file without guessing.

Usage:
  python reel.py OUT.mp4 --dir renders/                 # every *.mp4, sorted, label = stem
  python reel.py OUT.mp4 --clip orbitStage/standard a.mp4 --clip orbitStage/mirror b.mp4
  python reel.py OUT.mp4 --manifest clips.json          # [{"label":..., "file":...}, ...]
  --font /path/to/monospace.ttf   --slate 0.6   --crf 18
  (--font is auto-detected per platform; override with it or $PEK_FONT)
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

W, H, FPS = 1920, 1080, 30


def die(msg):
    print("reel: " + msg, file=sys.stderr)
    sys.exit(1)


def ff_escape_text(s):
    # drawtext text escaping: backslash, quote, colon, percent, semicolon
    out = []
    for ch in s:
        if ch in "\\':%;,[]":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def ff_escape_path(p):
    # inside a filter option: forward slashes, escape the drive colon
    return p.replace("\\", "/").replace(":", "\\:")


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        die(f"ffprobe could not read {path}: {r.stderr.strip()[-300:]}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffmpeg failed:\n  " + " ".join(cmd) + "\n" + r.stderr[-1500:])


def default_font():
    """First monospace TTF that exists on this machine.

    The label burn-in needs a real font file for ffmpeg drawtext. Returns None
    when nothing is found, so main() can ask for --font rather than dying on a
    path that only ever existed on one machine.
    """
    env = os.environ.get("PEK_FONT")
    if env:
        return env
    candidates = [
        # Windows
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        # macOS
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/Library/Fonts/Courier New.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--dir", default=None, help="take every *.mp4 in this dir, sorted")
    ap.add_argument("--clip", nargs=2, action="append", metavar=("LABEL", "FILE"), default=[])
    ap.add_argument("--manifest", default=None, help='json list of {"label","file"}')
    ap.add_argument("--font", default=None,
                    help="monospace TTF for the burned-in labels; "
                         "auto-detected per platform, or set PEK_FONT")
    ap.add_argument("--slate", type=float, default=0.6, help="seconds of title slate before each clip; 0 disables")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--title", default=None, help="optional opening slate text (e.g. the reference name)")
    a = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        die("ffmpeg/ffprobe not on PATH")
    if not a.font:
        a.font = default_font()
    if not a.font:
        die("no monospace font found on this machine.\n"
            "  Pass --font /path/to/a/monospace.ttf, or set PEK_FONT.")
    if not os.path.exists(a.font):
        die(f"font not found: {a.font}")

    clips = []
    out_abs = os.path.abspath(a.out)
    if a.manifest:
        for row in json.load(open(a.manifest, encoding="utf-8")):
            clips.append((row["label"], row["file"]))
    for label, f in a.clip:
        clips.append((label, f))
    if a.dir:
        for f in sorted(glob.glob(os.path.join(a.dir, "*.mp4"))):
            if os.path.abspath(f) == out_abs:
                continue
            clips.append((os.path.splitext(os.path.basename(f))[0], f))
    if not clips:
        die("no clips. Use --dir, --clip or --manifest.")
    for _, f in clips:
        if not os.path.exists(f):
            die(f"missing clip: {f}")

    font = ff_escape_path(os.path.abspath(a.font))
    tmp = tempfile.mkdtemp(prefix="reel-")
    parts = []
    manifest = []
    cursor = 0.0

    def slate(text, seconds, path):
        txt = ff_escape_text(text)
        vf = (f"drawtext=fontfile='{font}':text='{txt}':fontcolor=white:fontsize=64:"
              f"x=(w-text_w)/2:y=(h-text_h)/2")
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
             f"color=c=#101010:s={W}x{H}:r={FPS}:d={seconds}",
             "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf),
             "-pix_fmt", "yuv420p", "-an", path])

    if a.title and a.slate > 0:
        p = os.path.join(tmp, "000_title.mp4")
        slate(a.title, max(a.slate, 1.2), p)
        parts.append(p)
        cursor += max(a.slate, 1.2)

    for i, (label, f) in enumerate(clips, 1):
        if a.slate > 0:
            p = os.path.join(tmp, f"{i:03d}_slate.mp4")
            slate(f"{i}  {label}", a.slate, p)
            parts.append(p)
            cursor += a.slate
        dur = probe_duration(f)
        txt = ff_escape_text(f"{i}  {label}")
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},"
              f"drawtext=fontfile='{font}':text='{txt}':fontcolor=white:fontsize=36:"
              f"box=1:boxcolor=black@0.55:boxborderw=14:x=48:y=h-th-48")
        p = os.path.join(tmp, f"{i:03d}_clip.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-i", f, "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf),
             "-pix_fmt", "yuv420p", "-an", p])
        parts.append(p)
        manifest.append({"index": i, "label": label, "file": os.path.abspath(f),
                         "start_s": round(cursor, 3), "end_s": round(cursor + dur, 3),
                         "duration_s": round(dur, 3)})
        cursor += dur

    lst = os.path.join(tmp, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for p in parts:
            fh.write("file '" + p.replace("\\", "/").replace("'", "'\\''") + "'\n")
    os.makedirs(os.path.dirname(out_abs) or ".", exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", out_abs])
    shutil.rmtree(tmp, ignore_errors=True)

    mpath = out_abs[:-4] + ".manifest.json" if out_abs.lower().endswith(".mp4") else out_abs + ".manifest.json"
    json.dump({"reel": out_abs, "total_s": round(cursor, 3), "clips": manifest},
              open(mpath, "w", encoding="utf-8"), indent=2)

    print(f"reel: {out_abs}  ({cursor:.1f}s, {len(clips)} clips)")
    print(f"      manifest {mpath}")
    for m in manifest:
        print(f"  {m['index']:>2}  {m['start_s']:>6.1f}s - {m['end_s']:>6.1f}s  {m['label']}")


if __name__ == "__main__":
    main()
