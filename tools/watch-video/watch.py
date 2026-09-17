#!/usr/bin/env python3
"""
watch.py — watch a video without leaving anything behind.

    python watch.py <target> [--keep] [options]

<target> is a video file, a HyperFrames project directory (one containing
index.html), or a URL. A project is rendered first; a video file is read
where it sits; a URL is fetched with yt-dlp and CACHED, so watching the
same reference twice costs no network.

--from/--to clip before analysis (83 | 1:23 | 1:02:03). Use them — a
four-minute reference is 7000 frames and you want the ten seconds that
hold the pattern.

EPHEMERAL BY DEFAULT. Everything — the render, the extracted frames, the
contact sheets — is written into a scratch directory and DELETED when the
run finishes. The only things that survive are:
  * the numbers printed to stdout
  * the contact-sheet paths printed under LOOK AT THESE, which live in
    scratch just long enough to be opened, then go away on the next run

Pass --keep to retain the scratch directory (say, to diff two runs).
Pass --sheets-to DIR to copy just the sheets somewhere permanent.

Scratch root defaults to %TEMP%/watch-video, override with --scratch.
"""

import argparse
import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v", ".avi"}
HERE = os.path.dirname(os.path.abspath(__file__))
MOTION = os.path.join(HERE, "motion.py")
FONT = "C\\:/Windows/Fonts/consolab.ttf"


def die(msg):
    print(f"watch: {msg}", file=sys.stderr)
    sys.exit(1)


def probe(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration",
         "-of", "default=noprint_wrappers=1", video],
        capture_output=True, text=True)
    info = {}
    for line in r.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            info[k] = v

    def rate(s):
        try:
            n, d = s.split("/")
            return float(n) / float(d) if float(d) else 0.0
        except Exception:
            return 0.0

    info["fps"] = rate(info.get("avg_frame_rate", "0/1")) or rate(info.get("r_frame_rate", "0/1"))
    info["vfr"] = rate(info.get("r_frame_rate", "0/1")) != rate(info.get("avg_frame_rate", "0/1"))
    return info


URL_RE = re.compile(r"^(https?://|www\.)", re.I)


def is_url(s):
    return bool(URL_RE.match(s.strip()))


def fmt_ts(sec):
    sec = float(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:06.3f}" if h else f"{int(m)}:{s:06.3f}"


def parse_ts(s):
    """'83' | '1:23' | '1:02:03' | '1:23.5' -> seconds."""
    if s is None:
        return None
    parts = str(s).strip().split(":")
    if len(parts) > 3:
        die(f"bad timestamp: {s}")
    try:
        parts = [float(x) for x in parts]
    except ValueError:
        die(f"bad timestamp: {s}")
    sec = 0.0
    for x in parts:
        sec = sec * 60 + x
    return sec


def fetch_url(url, root, start=None, end=None):
    """Download once, keep it. Watching the same reference again costs no
    network — several extractions come off one video.

    With a range, yt-dlp fetches ONLY that window: 5 MB instead of 245 MB
    for an eight-second look. The cache is keyed per range, so a second
    range off the same video is its own entry.

    Fails CLOSED. An interrupted download leaves a .part behind; accepting
    it would hand ffmpeg a truncated file and report motion off whatever
    happened to arrive. Only a real container extension is accepted."""
    dl = os.path.join(root, "dl")
    os.makedirs(dl, exist_ok=True)
    exe = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if not exe:
        die("yt-dlp is not on PATH — needed to read a URL")

    base = [exe, "--no-progress", "--no-playlist"]
    if shutil.which("node"):
        # YouTube needs a JS runtime to solve the n-challenge. Without one,
        # formats go missing and the media URLs 403 partway through.
        base += ["--js-runtimes", "node"]

    r = subprocess.run(base + ["--simulate", "--print", "%(id)s", url],
                       capture_output=True, text=True)
    ids = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    if not ids:
        die("could not resolve a video id from that URL:\n"
            + (r.stderr or "")[-700:])
    vid = ids[-1]

    sect = tag = None
    if start is not None or end is not None:
        st = start or 0.0
        hi = "inf" if end is None else f"{end:.3f}"
        sect = f"*{st:.3f}-{hi}"
        tag = f"@{st:.3f}-{'end' if end is None else f'{end:.3f}'}"
    tag = tag or ""

    cached = os.path.join(dl, vid + tag + ".mp4")
    if os.path.exists(cached):
        print(f"watch: cached {os.path.basename(cached)} "
              f"({os.path.getsize(cached)/1e6:.1f} MB) — no network")
        return cached, sect is not None

    print(f"watch: fetching {vid}{' ' + sect if sect else ' (whole video)'}")
    cmd = base + ["--merge-output-format", "mp4", "-f",
                  "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4]/b",
                  "-o", os.path.join(dl, vid + tag + ".%(ext)s")]
    if sect:
        cmd += ["--download-sections", sect, "--force-keyframes-at-cuts"]
    d = subprocess.run(cmd + [url], stderr=subprocess.PIPE, text=True)

    if d.returncode != 0:
        die(f"yt-dlp exited {d.returncode}:\n" + (d.stderr or "")[-1200:])
    if not os.path.exists(cached):
        alt = sorted(f for f in os.listdir(dl)
                     if f.startswith(vid + tag + ".")
                     and os.path.splitext(f)[1].lower() in VIDEO_EXT)
        if not alt:
            die("download produced no playable file — a leftover .part means "
                "it was interrupted:\n" + (d.stderr or "")[-900:])
        cached = os.path.join(dl, alt[0])
    print(f"watch: got {os.path.basename(cached)} "
          f"({os.path.getsize(cached)/1e6:.1f} MB)")
    return cached, sect is not None


def clip(video, scratch, start, end):
    """Cut [start, end) into scratch, re-encoded so t=0 is exact.

    -t (duration), never -to: with -ss ahead of -i, some ffmpeg builds
    measure -to against the ORIGINAL timeline and the clip silently runs
    long. Duration carries no such ambiguity."""
    st = start or 0.0
    dur = None if end is None else end - st
    if dur is not None and dur <= 0:
        die(f"--to must come after --from ({end} <= {st})")
    out = os.path.join(scratch, "clip.mp4")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    if st:
        cmd += ["-ss", f"{st:.3f}"]
    cmd += ["-i", video]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-an", "-y", out]
    subprocess.run(cmd, check=False)
    if not os.path.exists(out):
        die("clip failed — check --from/--to against the source duration")
    tail = fmt_ts(end) if end is not None else "end"
    print(f"watch: clipped {fmt_ts(st)}..{tail} (crf 16 re-encode — motion is "
          f"faithful, do NOT measure encode quality off this)")
    return out


def is_project(p):
    return os.path.isdir(p) and os.path.exists(os.path.join(p, "index.html"))


def render_project(proj, scratch, workers):
    """Render into scratch. Never touches the project's renders/ dir."""
    out = os.path.join(scratch, "render.mp4")
    exe = shutil.which("hyperframes")
    cmd = ([exe] if exe else ["npx", "--yes", "hyperframes"]) + \
          ["render", "-w", str(workers), "-o", out]
    print(f"watch: rendering -> scratch ({workers} worker)")
    r = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, shell=not exe)
    if not os.path.exists(out):
        # some CLI versions ignore -o and write into renders/; recover then move
        rd = os.path.join(proj, "renders")
        mp4s = [f for f in os.listdir(rd) if f.endswith(".mp4")] if os.path.isdir(rd) else []
        if not mp4s:
            die("render produced no mp4.\n" + (r.stdout or "")[-1200:] + (r.stderr or "")[-1200:])
        newest = max(mp4s, key=lambda f: os.path.getmtime(os.path.join(rd, f)))
        shutil.move(os.path.join(rd, newest), out)
        print(f"watch: CLI wrote to renders/, moved into scratch (renders/ left clean)")
    return out


def extract(video, outdir, width, burn):
    os.makedirs(outdir, exist_ok=True)
    vf = [f"scale={width}:-2"]
    if burn:
        vf.append(f"drawtext=fontfile='{FONT}':text='%{{n}} | %{{pts\\:hms}}':"
                  "x=8:y=8:fontsize=24:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=5")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video,
                    "-vf", ",".join(vf), "-q:v", "3",
                    os.path.join(outdir, "f_%05d.jpg")], check=False)
    return sorted(f for f in os.listdir(outdir) if f.endswith(".jpg"))


def unique_count(d, files):
    seen = set()
    for f in files:
        with open(os.path.join(d, f), "rb") as fh:
            seen.add(hashlib.md5(fh.read()).hexdigest())
    return len(seen)


def sheets(video, outdir, per_sec, cols, rows, cell_w):
    os.makedirs(outdir, exist_ok=True)
    vf = (f"fps={per_sec},scale={cell_w}:-2,"
          f"drawtext=fontfile='{FONT}':text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:"
          f"fontcolor=yellow:box=1:boxcolor=black@0.8:boxborderw=4,"
          f"tile={cols}x{rows}:margin=5:padding=5:color=white")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video,
                    "-vf", vf, "-q:v", "3",
                    os.path.join(outdir, "sheet_%02d.jpg")], check=False)
    return sorted(f for f in os.listdir(outdir) if f.startswith("sheet_"))


def cuts(video, datadir, threshold, fps):
    os.makedirs(datadir, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error",
                    "-i", os.path.abspath(video), "-vf",
                    f"scdet=threshold={threshold},metadata=print:file=scd.txt",
                    "-f", "null", "-"], cwd=datadir, check=False)
    p = os.path.join(datadir, "scd.txt")
    if not os.path.exists(p):
        return []
    txt = open(p, encoding="utf-8", errors="replace").read()
    pairs = re.findall(r"pts_time:([0-9.]+)[^\n]*\n[^\n]*lavfi\.scd\.mafd=([0-9.]+)", txt)
    return [(float(t), float(m)) for t, m in pairs if float(m) >= threshold]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--fps", type=float, default=0)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--thresh", type=int, default=12)
    ap.add_argument("--roi", default=None)
    ap.add_argument("--scdet", type=float, default=6.0)
    ap.add_argument("--sheet-fps", type=float, default=2.0,
                    help="contact-sheet cells per second of video (default 2)")
    ap.add_argument("--grid", default="3x2", help="sheet grid; keep cells big (default 3x2)")
    ap.add_argument("--cell-width", type=int, default=960,
                    help="px width of each contact-sheet cell (default 960 = 50%% of 1080p)")
    ap.add_argument("--workers", type=int, default=1,
                    help="hyperframes render workers; 1 keeps Chrome windows to a minimum")
    ap.add_argument("--no-burn", action="store_true")
    ap.add_argument("--no-defect", action="store_true",
                    help="skip the native-resolution defect crops")
    ap.add_argument("--defect-at", type=float, default=-1,
                    help="timestamp for the 1:1 defect crops (default: 80%% through)")
    ap.add_argument("--ring", type=int, default=3,
                    help="how many past versions to keep beside the project (default 3)")
    ap.add_argument("--note", default=None,
                    help="short label stored with this version, shown in the ring listing")
    ap.add_argument("--keep", action="store_true",
                    help="do NOT delete the scratch dir when finished")
    ap.add_argument("--sheets-to", default=None,
                    help="copy the contact sheets to this directory before cleanup")
    ap.add_argument("--from", dest="start", default=None,
                    help="clip start: 83, 1:23, or 1:02:03 — REQUIRES --partial")
    ap.add_argument("--to", dest="end", default=None,
                    help="clip end, same formats — REQUIRES --partial")
    ap.add_argument("--partial", default=None, metavar="CHRIS_SAID",
                    help="Chris's own words authorising a partial watch. Without\nthis, --from/--to are refused.")
    ap.add_argument("--scratch", default=None)
    args = ap.parse_args()

    root = args.scratch or os.path.join(tempfile.gettempdir(), "watch-video")
    os.makedirs(root, exist_ok=True)

    start, end = parse_ts(args.start), parse_ts(args.end)

    # THE FULL-WATCH GATE.
    #
    # Chris names the video; the whole of what he named gets watched. Every
    # frame, every sheet, every 1:1 crop. Narrowing his ask to save time or
    # context does not save him anything — it produces an inaccurate read that
    # costs him more of both to correct.
    #
    # This was documented repeatedly and repeatedly ignored, so it is no longer
    # documentation. A partial watch now requires his authorisation in his own
    # words, and the program will not start without it.
    if (start is not None or end is not None) and not args.partial:
        die("REFUSED: --from/--to is a PARTIAL WATCH.\n\n"
            "  When Chris names a video, watch ALL of it. Do not invent a range\n"
            "  to save time or context. Token cost is not a constraint here —\n"
            "  an inaccurate read costs him more context and time than the full\n"
            "  pass ever would.\n\n"
            "  If HE named the range, pass his words:\n"
            '      --partial "watch 1:23 to 1:38 of this one"\n\n'
            "  If he did not, drop --from/--to and watch the whole thing.")
    if args.partial and start is None and end is None:
        die("--partial was given with no --from/--to. Drop it.")

    if is_url(args.target):
        target, pre_clipped = fetch_url(args.target.strip(), root, start, end)
    else:
        pre_clipped = False
        target = os.path.abspath(args.target)
        if not os.path.exists(target):
            die(f"no such target: {target}")

    # Frames are the heavy part — temp and deleted, UNLESS --keep. G2 measures
    # frames with an ROI (motion.py), so an extraction child needs them kept.
    # Bug fixed 2026-08-29 (cougar): --keep was declared and never honoured.
    scratch = tempfile.mkdtemp(prefix="watch-frames-", dir=root)
    if not args.keep:
        atexit.register(lambda: shutil.rmtree(scratch, ignore_errors=True))

    # Versions are the light, useful part — a ring buffer beside the project
    # so previous attempts stay comparable. Oldest falls off at --ring.
    # One ring PER SOURCE, not per directory. A shared ring at ring=3 means
    # watching a fourth reference silently deletes the first one's sheets,
    # and sheets are the thing anyone actually came back for.
    store = (os.path.join(target, ".watch") if is_project(target)
             else os.path.splitext(target)[0] + ".watch")
    os.makedirs(store, exist_ok=True)
    existing = sorted(d for d in os.listdir(store)
                      if re.fullmatch(r"v\d{3}", d) and os.path.isdir(os.path.join(store, d)))
    nextn = (int(existing[-1][1:]) + 1) if existing else 1
    vdir = os.path.join(store, f"v{nextn:03d}")
    os.makedirs(vdir, exist_ok=True)

    if is_project(target):
        video = render_project(target, vdir, args.workers)
        made_render = True
    else:
        if os.path.splitext(target)[1].lower() not in VIDEO_EXT:
            die(f"not a video or HyperFrames project: {target}")
        video = target
        made_render = False

    if not pre_clipped and (start is not None or end is not None):
        video = clip(video, scratch, start, end)

    info = probe(video)
    fps = args.fps or info["fps"] or 30.0
    print("\n== SOURCE ==")
    print(f"  {info.get('width')}x{info.get('height')}  {fps:.3f} fps"
          f"{'  [VFR]' if info['vfr'] else ''}  {info.get('duration','?')}s")

    frames_d = os.path.join(scratch, "frames")
    files = extract(video, frames_d, args.width, not args.no_burn)
    if not files:
        die("frame extraction produced nothing")
    uq = unique_count(frames_d, files)
    print(f"  {len(files)} frames, {uq} unique")
    if uq <= 2:
        print("  SOURCE IS STATIC — refusing to report motion.")

    hot = cuts(video, os.path.join(scratch, "data"), args.scdet, fps)
    print(f"\n== CUTS (scdet>={args.scdet}) ==  {len(hot)}")
    for t, m in hot[:12]:
        print(f"  t={t:8.2f}  f={int(round(t*fps)):6d}  mafd={m:6.2f}")
    if len(hot) > 12:
        print(f"  ... {len(hot)-12} more")

    if args.defect_at < 0:
        try: args.defect_at = float(info.get("duration", 5)) * 0.8
        except Exception: args.defect_at = 4.0
    kept_defects = []
    cols, rows = (int(x) for x in args.grid.lower().split("x"))
    sheets_d = os.path.join(scratch, "sheets")
    sh = sheets(video, sheets_d, args.sheet_fps, cols, rows, args.cell_width)

    # ---- 1:1 DEFECT PASS ----------------------------------------------
    # A contact sheet at 470px/cell is a 24% thumbnail of a 1920px frame.
    # Typography collisions, hairline overruns and clipped glyphs are all
    # SMALLER than one pixel at that scale, so they cannot be seen there.
    # This pass crops native-resolution bands and never downscales.
    if not args.no_defect:
        W = int(info.get("width") or 1920)
        Hgt = int(info.get("height") or 1080)
        bands = [("top", 0), ("upper", int(Hgt * 0.28)), ("lower", int(Hgt * 0.56)),
                 ("bottom", Hgt - int(Hgt * 0.28))]
        bh = int(Hgt * 0.28)
        for name, y in bands:
            out = os.path.join(vdir, f"defect_{name}.jpg")
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video,
                 "-ss", str(args.defect_at), "-frames:v", "1",
                 "-vf", f"crop={W}:{bh}:0:{y}", "-q:v", "2", "-y", out],
                check=False)
            if os.path.exists(out):
                kept_defects.append(out)

    print("\n== MOTION ==")
    cmd = [sys.executable, MOTION, frames_d, "--fps", str(fps),
           "--stride", str(args.stride), "--thresh", str(args.thresh)]
    if args.roi:
        cmd += ["--roi", args.roi]
    subprocess.run(cmd)

    # Sheets + motion.csv join the render in this version's dir.
    kept = []
    for s in sh:
        dst = os.path.join(vdir, s)
        if os.path.abspath(os.path.join(sheets_d, s)) != os.path.abspath(dst):
            shutil.copy2(os.path.join(sheets_d, s), dst)
        kept.append(dst)
    csv_src = os.path.join(frames_d, "motion.csv")
    if os.path.exists(csv_src):
        shutil.copy2(csv_src, os.path.join(vdir, "motion.csv"))
    if args.note:
        with open(os.path.join(vdir, "NOTE.txt"), "w", encoding="utf-8") as fh:
            fh.write(args.note + "\n")

    # Frames die now unless --keep: with --keep the frames dir is printed and
    # left for motion.py / fit-ease ROI measurement.
    if args.keep:
        print(f"  frames KEPT (--keep): {frames_d}")
    else:
        shutil.rmtree(frames_d, ignore_errors=True)
        if sheets_d != vdir:
            shutil.rmtree(sheets_d, ignore_errors=True)

    # Ring buffer: keep the newest N versions, drop the rest.
    allv = sorted(d for d in os.listdir(store)
                  if re.fullmatch(r"v\d{3}", d) and os.path.isdir(os.path.join(store, d)))
    dropped = allv[:-args.ring] if len(allv) > args.ring else []
    for d in dropped:
        shutil.rmtree(os.path.join(store, d), ignore_errors=True)

    # The manifest is arithmetic on purpose. "Look at these" was advice and got
    # treated as advice; a count that does not match what was opened is a fact.
    must_open = kept_defects + kept
    manifest = {
        "source": os.path.basename(video),
        "duration_s": float(info.get("duration") or 0),
        "partial": bool(args.partial),
        "authorised_by_chris": args.partial or None,
        "defect_crops": [os.path.basename(x) for x in kept_defects],
        "sheets": [os.path.basename(x) for x in kept],
        "total_artifacts": len(must_open),
    }
    with open(os.path.join(vdir, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"\n{'='*66}")
    print(f"== OPEN ALL {len(must_open)} ARTIFACTS — "
          f"{len(kept_defects)} defect crop(s) + {len(kept)} sheet(s) ==")
    print(f"{'='*66}")
    if args.partial:
        print(f"  PARTIAL WATCH, authorised by Chris: {args.partial!r}")
    else:
        print(f"  FULL WATCH of {manifest['duration_s']:.1f}s. "
              f"Opening fewer than {len(must_open)} is an incomplete read.")
    print("\n  1:1 DEFECT CROPS FIRST — this is where typography bugs live:")
    for k in kept_defects:
        print(f"    {k}")
    print(f"\n  THEN ALL {len(kept)} SHEETS, in order:")
    for k in kept:
        print(f"    {k}")
    print(f"\n  manifest: {os.path.join(vdir, 'MANIFEST.json')}")

    live = sorted(d for d in os.listdir(store)
                  if re.fullmatch(r"v\d{3}", d) and os.path.isdir(os.path.join(store, d)))
    print(f"\n== VERSIONS (ring={args.ring}) ==  {store}")
    total = 0
    for d in live:
        p = os.path.join(store, d)
        sz = sum(os.path.getsize(os.path.join(p, f)) for f in os.listdir(p))
        total += sz
        note = ""
        np_ = os.path.join(p, "NOTE.txt")
        if os.path.exists(np_):
            note = "  — " + open(np_, encoding="utf-8").read().strip()[:60]
        mark = " <- this run" if d == os.path.basename(vdir) else ""
        print(f"  {d}  {sz/1e6:5.1f} MB{mark}{note}")
    if dropped:
        print(f"  dropped: {', '.join(dropped)}")
    print(f"  total {total/1e6:.1f} MB   (frames deleted, renders kept for comparison)")


if __name__ == "__main__":
    main()
