#!/usr/bin/env python3
"""
motion.py - turn a frame sequence into a numeric motion time series.

Answers the questions a contact sheet cannot:
  - how fast is this transition, and what is its easing shape
  - which direction is a thing moving
  - is that card actually drifting, or is it static

Usage:
  python motion.py FRAMES_DIR [--fps 30] [--out motion.csv] [--roi X0,Y0,X1,Y1]
                              [--work-width 320] [--quiet]

Frames must be named so that lexical sort equals temporal order
(f_00001.jpg, f_00002.jpg, ...).

CSV columns
  i            index in the sequence (0-based)
  t            seconds, = i / fps
  file         source filename
  diff         mean absolute luma difference vs previous frame, 0-255
  changed_pct  percent of pixels that moved more than --thresh
  cx, cy       centroid of changed pixels, in SOURCE pixel coords
  x0,y0,x1,y1  bounding box of change, SOURCE pixel coords
  dx, dy       centroid movement since previous changed frame, source px
  speed        magnitude of (dx,dy), source px per frame
  angle        direction of motion, degrees; 0=right, 90=down, 180=left, 270=up
"""

import argparse
import csv
import math
import os
import sys

import numpy as np
from PIL import Image


def load_gray(path, work_width):
    im = Image.open(path).convert("L")
    src_w, src_h = im.size
    if work_width and src_w > work_width:
        scale = work_width / src_w
        im = im.resize((work_width, max(1, int(round(src_h * scale)))), Image.BILINEAR)
    else:
        scale = 1.0
    return np.asarray(im, dtype=np.int16), scale, src_w, src_h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--thresh", type=int, default=12,
                    help="luma delta that counts as 'this pixel moved' (default 12)")
    ap.add_argument("--work-width", type=int, default=320,
                    help="downscale width for the math; 0 = native (default 320)")
    ap.add_argument("--roi", default=None,
                    help="restrict analysis to X0,Y0,X1,Y1 in SOURCE pixel coords")
    ap.add_argument("--stride", type=int, default=1,
                    help="compare frame N against N-STRIDE instead of N-1. "
                         "Raise to 8-15 to see slow drift that compression "
                         "erases between adjacent frames (default 1)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    files = sorted(
        f for f in os.listdir(args.frames_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    if len(files) < 2:
        sys.exit(f"need at least 2 frames in {args.frames_dir}, found {len(files)}")

    out_path = args.out or os.path.join(args.frames_dir, "motion.csv")

    scale = 1.0
    roi = None
    last_centroid = None
    rows = []
    history = []          # keeps the last `stride` frames for strided comparison
    stride = max(1, args.stride)

    for i, fn in enumerate(files):
        cur, scale, src_w, src_h = load_gray(os.path.join(args.frames_dir, fn), args.work_width)

        if args.roi and roi is None:
            x0, y0, x1, y1 = (int(v) for v in args.roi.split(","))
            roi = (max(0, int(x0 * scale)), max(0, int(y0 * scale)),
                   min(cur.shape[1], int(x1 * scale)), min(cur.shape[0], int(y1 * scale)))
        if roi:
            cur = cur[roi[1]:roi[3], roi[0]:roi[2]]

        history.append(cur)
        if len(history) > stride + 1:
            history.pop(0)

        if len(history) <= stride:
            rows.append(dict(i=i, t=round(i / args.fps, 4), file=fn,
                             diff=0.0, changed_pct=0.0,
                             cx="", cy="", x0="", y0="", x1="", y1="",
                             dx="", dy="", speed="", angle=""))
            continue

        prev = history[0]
        if cur.shape != prev.shape:
            continue

        d = np.abs(cur - prev)
        diff_mean = float(d.mean())
        mask = d > args.thresh
        n = int(mask.sum())
        changed_pct = 100.0 * n / mask.size

        cx = cy = bx0 = by0 = bx1 = by1 = ""
        dx = dy = speed = angle = ""

        if n > 0:
            ys, xs = np.nonzero(mask)
            # centroid weighted by how much each pixel changed
            w = d[mask].astype(np.float64)
            cxw = float((xs * w).sum() / w.sum())
            cyw = float((ys * w).sum() / w.sum())
            ox = roi[0] if roi else 0
            oy = roi[1] if roi else 0
            cx = round((cxw + ox) / scale, 1)
            cy = round((cyw + oy) / scale, 1)
            bx0 = int((xs.min() + ox) / scale)
            by0 = int((ys.min() + oy) / scale)
            bx1 = int((xs.max() + ox) / scale)
            by1 = int((ys.max() + oy) / scale)

            if last_centroid is not None:
                dx = round(cx - last_centroid[0], 1)
                dy = round(cy - last_centroid[1], 1)
                speed = round(math.hypot(dx, dy), 2)
                angle = round(math.degrees(math.atan2(dy, dx)) % 360, 1)
            last_centroid = (cx, cy)

        rows.append(dict(i=i, t=round(i / args.fps, 4), file=fn,
                         diff=round(diff_mean, 3), changed_pct=round(changed_pct, 3),
                         cx=cx, cy=cy, x0=bx0, y0=by0, x1=bx1, y1=by1,
                         dx=dx, dy=dy, speed=speed, angle=angle))

    cols = ["i", "t", "file", "diff", "changed_pct", "cx", "cy",
            "x0", "y0", "x1", "y1", "dx", "dy", "speed", "angle"]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    if args.quiet:
        print(out_path)
        return

    diffs = np.array([r["diff"] for r in rows], dtype=float)
    pcts = np.array([r["changed_pct"] for r in rows], dtype=float)
    active = diffs > 0.05

    print(f"frames        : {len(rows)}  @ {args.fps} fps  ({len(rows)/args.fps:.2f}s)")
    print(f"csv           : {out_path}")
    print(f"diff  mean/max: {diffs.mean():.3f} / {diffs.max():.3f}")
    print(f"moving frames : {int(active.sum())} / {len(rows)}  "
          f"({100.0*active.sum()/len(rows):.1f}%)")

    # events: frames whose change is far above the local norm = cuts / hard hits
    if diffs.max() > 0:
        med = float(np.median(diffs[diffs > 0])) if (diffs > 0).any() else 0.0
        spike_cut = max(med * 6.0, diffs.max() * 0.5)
        spikes = [r for r in rows if r["diff"] >= spike_cut and r["diff"] > 0]
        print(f"\nhard events (diff >= {spike_cut:.2f}):")
        for r in spikes[:20]:
            print(f"  t={r['t']:<7} frame {r['i']:<5} diff={r['diff']:<8} "
                  f"changed={r['changed_pct']}%")
        if not spikes:
            print("  none")

    # sustained low-level motion = drift, float, slow pan
    drift = [r for r in rows
             if isinstance(r["speed"], float) and 0 < r["changed_pct"] < 8.0]
    if drift:
        sp = np.array([r["speed"] for r in drift], dtype=float)
        an = np.array([r["angle"] for r in drift], dtype=float)
        print(f"\nsubtle motion : {len(drift)} frames, "
              f"speed mean {sp.mean():.2f} px/f, max {sp.max():.2f}")
        # circular motion shows a steadily rotating angle
        da = np.diff(an)
        da = (da + 180) % 360 - 180
        if len(da) > 4:
            turn = float(np.mean(da))
            consistency = float(np.mean(np.sign(da) == np.sign(turn)))
            shape = "circular/orbital" if consistency > 0.7 and abs(turn) > 2 else \
                    "linear" if abs(turn) < 2 else "irregular"
            print(f"path shape    : {shape}  "
                  f"(mean turn {turn:+.1f}deg/frame, consistency {consistency:.0%})")


if __name__ == "__main__":
    main()
