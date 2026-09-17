#!/usr/bin/env python3
"""
fit-ease.py - fit an easing family, duration and start time to a motion.csv
window, by least squares, so G3/G5 of /pattern-extract stop guessing.

Why this exists. The PayCloud extraction (2026-08-27) read a triangular
frame-diff profile as "linear cross-fade", shipped it, and G5 killed it. The
correct answer (power1.inOut, 0.570 s) was then fitted BY HAND. Frame-diff is
the DERIVATIVE of opacity/position, so a triangle on diff is an S-curve on the
thing itself. This script fits every candidate family at once and prints the
ranking, so the first render is built from the fitted numbers.

Two kinds of window:

  --kind fade   the `diff` column is the derivative of a progress curve
                (cross-fade, dissolve, colour swap). Model:
                    diff(t) = b + A * E'((t - t0) / D)
  --kind move   a column (cx, cy, x0 ...) IS the progress curve
                (entrance, exit, slide). Model:
                    col(t) = p0 + travel * E((t - t0) / D)

E is one of the families below. All four/five parameters are free and
bounded to the window. Every family is fitted from several starting
durations so a local minimum does not pick the winner.

Usage:
  python fit-ease.py motion.csv --from 45.5 --to 46.9 --kind fade
  python fit-ease.py motion.csv --from 2.0 --to 3.4 --kind move --col cy
  add --json for a machine-readable block (provenance.json wants it)

Resolution: t0 and D are only known to +-1 frame (1/fps). Do not report
more digits than that. A window with fewer than 8 samples is refused.
"""

import argparse
import csv
import json
import math
import sys

import numpy as np
from scipy.optimize import least_squares

# ---------------------------------------------------------------------------
# Ease families: (E(p), E'(p)) on p in [0,1]. GSAP names where GSAP has one.
# expDecay is the library's own measured ease; k is fitted as an extra param.
# ---------------------------------------------------------------------------

def _io(pin_pow):
    # power{n}.inOut: E = 2^(n) p^(n+1) for p<.5, mirrored above.
    n = pin_pow + 1
    c = 2 ** pin_pow
    def E(p):
        return np.where(p < 0.5, c * p ** n, 1 - c * (1 - p) ** n)
    def dE(p):
        return np.where(p < 0.5, c * n * p ** (n - 1), c * n * (1 - p) ** (n - 1))
    return E, dE

def _out(pin_pow):
    n = pin_pow + 1
    def E(p):
        return 1 - (1 - p) ** n
    def dE(p):
        return n * (1 - p) ** (n - 1)
    return E, dE

def _in(pin_pow):
    n = pin_pow + 1
    def E(p):
        return p ** n
    def dE(p):
        return n * p ** (n - 1)
    return E, dE

def _sine_io():
    def E(p):
        return -(np.cos(np.pi * p) - 1) / 2
    def dE(p):
        return (np.pi / 2) * np.sin(np.pi * p)
    return E, dE

def _expo_io():
    ln2 = math.log(2)
    def E(p):
        return np.where(p < 0.5, 0.5 * 2 ** (20 * p - 10), 1 - 0.5 * 2 ** (-20 * p + 10))
    def dE(p):
        return np.where(p < 0.5, 10 * ln2 * 2 ** (20 * p - 10), 10 * ln2 * 2 ** (-20 * p + 10))
    return E, dE

def _linear():
    return (lambda p: p), (lambda p: np.ones_like(p))

def _expdecay(k):
    den = 1 - math.exp(-k)
    def E(p):
        return (1 - np.exp(-k * p)) / den
    def dE(p):
        return k * np.exp(-k * p) / den
    return E, dE

FAMILIES = {
    "linear":        lambda k: _linear(),
    "power1.inOut":  lambda k: _io(1),
    "power2.inOut":  lambda k: _io(2),
    "power3.inOut":  lambda k: _io(3),
    "sine.inOut":    lambda k: _sine_io(),
    "expo.inOut":    lambda k: _expo_io(),
    "power1.out":    lambda k: _out(1),
    "power2.out":    lambda k: _out(2),
    "power3.out":    lambda k: _out(3),
    "power1.in":     lambda k: _in(1),
    "power2.in":     lambda k: _in(2),
    "expDecay(k)":   lambda k: _expdecay(k),
}
HAS_K = {"expDecay(k)"}


def read_window(path, t_from, t_to, col):
    t, y = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                tt = float(row["t"])
            except (KeyError, ValueError):
                continue
            if tt < t_from or tt > t_to:
                continue
            v = row.get(col, "")
            if v == "" or v is None:
                continue
            t.append(tt)
            y.append(float(v))
    return np.array(t), np.array(y)


def clamp01(p):
    return np.clip(p, 0.0, 1.0)


def fit_family(name, t, y, kind, fps):
    """Least-squares fit of one family. Returns dict or None."""
    span = t[-1] - t[0]
    ymin, ymax = float(y.min()), float(y.max())
    amp0 = ymax - ymin if ymax > ymin else 1.0
    best = None
    # starting durations: a spread across the window, so the optimiser is
    # not trapped by a peak-width guess that happens to be wrong
    for D0 in (span * f for f in (0.15, 0.3, 0.5, 0.7, 0.9)):
        if D0 < 2.0 / fps:
            continue
        if kind == "fade":
            i_pk = int(np.argmax(y))
            t00 = t[i_pk] - D0 / 2
        else:
            t00 = t[0] + (span - D0) / 2
        k0 = 3.0
        if kind == "fade":
            x0 = [t00, D0, amp0, ymin]
            lo = [t[0] - span, 2.0 / fps, 0.0, -abs(ymin) - amp0]
            hi = [t[-1], span * 2, amp0 * 20, ymax]
        else:
            x0 = [t00, D0, float(y[-1] - y[0]) or amp0, float(y[0])]
            lo = [t[0] - span, 2.0 / fps, -abs(amp0) * 20 - 1e-6, ymin - amp0 * 5]
            hi = [t[-1], span * 2, abs(amp0) * 20 + 1e-6, ymax + amp0 * 5]
        if name in HAS_K:
            x0.append(k0); lo.append(0.05); hi.append(30.0)

        def resid(x):
            t0, D, A, b = x[:4]
            k = x[4] if name in HAS_K else None
            E, dE = FAMILIES[name](k)
            p = (t - t0) / D
            if kind == "fade":
                g = np.where((p >= 0) & (p <= 1), dE(clamp01(p)), 0.0)
                # E' is a density on p; per-second density scales by 1/D.
                # A absorbs the scale so units stay in diff units.
                model = b + A * g / max(np.max(g) if np.max(g) > 0 else 1.0, 1e-9)
            else:
                model = b + A * E(clamp01(p))
            return model - y

        try:
            r = least_squares(resid, x0, bounds=(lo, hi), max_nfev=4000)
        except ValueError:
            continue
        rms = float(np.sqrt(np.mean(r.fun ** 2)))
        if best is None or rms < best["rms"]:
            best = {"family": name, "t0": float(r.x[0]), "D": float(r.x[1]),
                    "A": float(r.x[2]), "b": float(r.x[3]),
                    "k": float(r.x[4]) if name in HAS_K else None,
                    "rms": rms}
    if best is None:
        return None
    rng = float(y.max() - y.min()) or 1.0
    best["rms_pct_of_amp"] = 100.0 * best["rms"] / rng   # % of the DATA range, one denominator for every family
    return best


def _normalise_direct(t, y, kind, fps):
    """Family-free normalisation. fade: pulse from baseline to peak; move: step
    from start plateau to end plateau. Returns (t50, n(t), rise_10_90_s).

    Plateaus are estimated ITERATIVELY: a first pass uses the window tails,
    then the baseline is re-taken from every sample before t10 and the end
    plateau from every sample after t90, twice. Fixed 10% tails made the gate
    swing 2.9% -> 5.1% on the same curves when the rebuild window grew by six
    frames (px-connect packetRide, 2026-08-29)."""
    t = np.asarray(t, dtype=float); y = np.asarray(y, dtype=float)
    def crossings(n_rising, level):
        idx = np.where(n_rising >= level)[0]
        if len(idx) == 0:
            return None
        i = int(idx[0])
        if i == 0:
            return float(t[0])
        y0, y1 = n_rising[i - 1], n_rising[i]
        f = (level - y0) / (y1 - y0) if y1 != y0 else 0.0
        return float(t[i - 1] + f * (t[i] - t[i - 1]))
    if kind == "fade":
        k = max(3, len(y) // 5)
        b = float(np.median(np.sort(y)[:k]))
        pk = float(np.max(y))
        i_pk = int(np.argmax(y))
        for _ in range(2):
            n = (y - b) / max(pk - b, 1e-9)
            t10 = crossings(n[:i_pk + 1], 0.1)
            if t10 is None:
                break
            pre = y[t < t10 - 1.0 / fps]
            if len(pre) >= 3:
                b = float(np.median(pre))
        n = (y - b) / max(pk - b, 1e-9)
        rising = n[:i_pk + 1]
    else:
        k = max(3, len(y) // 10)
        b0 = float(np.median(y[:k])); b1 = float(np.median(y[-k:]))
        for _ in range(2):
            n = (y - b0) / (b1 - b0 if abs(b1 - b0) > 1e-9 else 1e-9)
            t10 = crossings(n, 0.1); t90 = crossings(n, 0.9)
            if t10 is None or t90 is None:
                break
            pre = y[t < t10 - 1.0 / fps]; post = y[t > t90 + 1.0 / fps]
            if len(pre) >= 3:
                b0 = float(np.median(pre))
            if len(post) >= 3:
                b1 = float(np.median(post))
        n = (y - b0) / (b1 - b0 if abs(b1 - b0) > 1e-9 else 1e-9)
        rising = n
    t50 = crossings(rising, 0.5); t10 = crossings(rising, 0.1); t90 = crossings(rising, 0.9)
    rise = (t90 - t10) if (t10 is not None and t90 is not None) else None
    return t50, n, rise


def g5_direct(a, col, fps, t_ref, y_ref):
    """G5 without any family: both curves normalised on their OBSERVED baseline
    and peak/plateau, aligned at their OWN half-progress time (t50), compared on
    one elapsed grid. px-ink (2026-08-29) showed the fitted --compare can pick a
    different near-degenerate family per side and penalise a faithful rebuild;
    this number cannot, so it is the gate number. The fitted compare stays as a
    diagnostic."""
    cf = a.compare_from if a.compare_from is not None else a.t_from
    ct = a.compare_to if a.compare_to is not None else a.t_to
    t2, y2 = read_window(a.compare, cf, ct, col)
    if len(t2) < 8:
        return {"error": f"only {len(t2)} samples in rebuild window {cf}-{ct}"}
    def score(tr, yr, tb, yb):
        t50a, n1, r1 = _normalise_direct(tr, yr, a.kind, fps)
        t50b, n2, r2 = _normalise_direct(tb, yb, a.kind, fps)
        if t50a is None or t50b is None:
            return None
        span = max([x for x in (r1, r2) if x] or [0.5]) * 1.5
        grid = np.arange(-span, span, 1.0 / fps)
        v1 = np.interp(grid + t50a, tr, n1)
        v2 = np.interp(grid + t50b, tb, n2)
        return (float(np.mean(np.abs(v1 - v2))) * 100.0,
                float(np.max(np.abs(v1 - v2))) * 100.0, t50a, t50b, r1, r2, span)
    base = score(np.asarray(t_ref), np.asarray(y_ref), t2, y2)
    if base is None:
        return {"error": "could not find a half-progress crossing on one side"}
    err, mx, t50a, t50b, r1, r2, span = base
    # window sensitivity: trim/extend each side by up to 2 frames
    spread = []
    tr_all, yr_all = read_window(a.csv, a.t_from - 3.0 / fps, a.t_to + 3.0 / fps, col)
    tb_all, yb_all = read_window(a.compare, cf - 3.0 / fps, ct + 3.0 / fps, col)
    for d1 in (-2, 0, 2):
        for d2 in (-2, 0, 2):
            m1 = (tr_all >= a.t_from + d1 / fps) & (tr_all <= a.t_to - d1 / fps)
            m2 = (tb_all >= cf + d2 / fps) & (tb_all <= ct - d2 / fps)
            if m1.sum() < 8 or m2.sum() < 8:
                continue
            r = score(tr_all[m1], yr_all[m1], tb_all[m2], yb_all[m2])
            if r:
                spread.append(r[0])
    lo, hi = (min(spread), max(spread)) if spread else (err, err)
    verdict = ("proceed to G6" if err <= 5 else
               "adjust parameters, re-run" if err <= 15 else
               "classification is wrong, not the parameters: back to G2")
    return {"method": "direct (family-free): observed baseline/peak, t50-aligned",
            "ref_t50": round(t50a, 3), "rebuild_t50": round(t50b, 3),
            "ref_rise_10_90_s": None if r1 is None else round(r1, 3),
            "rebuild_rise_10_90_s": None if r2 is None else round(r2, 3),
            "grid_span_s": round(span, 3), "mean_abs_error_pct": round(err, 2),
            "max_abs_error_pct": round(mx, 2),
            "window_sensitivity_pct": [round(lo, 2), round(hi, 2)],
            "window_sensitive": bool(hi - lo > 3.0),
            "verdict": verdict, "gate": {"proceed": 5, "adjust": 15}}


def g5_compare(a, col, fps, t_ref, y_ref, best_ref):
    """The G5 gate, mechanical. Both curves are normalised by their OWN fitted
    baseline and amplitude, aligned at their OWN fitted t0, then compared at
    the same elapsed seconds on the reference's frame grid. Percentiles of
    detected frames are never used: different absolute times, meaningless."""
    cf = a.compare_from if a.compare_from is not None else a.t_from
    ct = a.compare_to if a.compare_to is not None else a.t_to
    t2, y2 = read_window(a.compare, cf, ct, col)
    if len(t2) < 8:
        return {"error": f"only {len(t2)} samples in rebuild window {cf}-{ct}"}
    res2 = [r for r in (fit_family(n, t2, y2, a.kind, fps) for n in FAMILIES) if r]
    res2.sort(key=lambda r: r["rms"])
    b2 = res2[0]
    span = max(best_ref["D"], b2["D"]) * 1.25          # cover both tails
    grid = np.arange(-0.15 * span, span, 1.0 / fps)     # elapsed seconds from t0
    n1 = np.interp(grid + best_ref["t0"], t_ref, (y_ref - best_ref["b"]) / best_ref["A"])
    n2 = np.interp(grid + b2["t0"], t2, (y2 - b2["b"]) / b2["A"])
    err = float(np.mean(np.abs(n1 - n2))) * 100.0
    verdict = ("proceed to G6" if err <= 5 else
               "adjust parameters, re-run" if err <= 15 else
               "classification is wrong, not the parameters: back to G2")
    return {"rebuild_csv": a.compare, "ref_window": [a.t_from, a.t_to],
            "rebuild_window": [cf, ct],
            "rebuild_best": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in b2.items()},
            "mean_abs_error_pct": round(err, 2), "verdict": verdict,
            "gate": {"proceed": 5, "adjust": 15}}


def _slope(t, y):
    A = np.vstack([t, np.ones_like(t)]).T
    (m, c), res, _, _ = np.linalg.lstsq(A, y, rcond=None)
    pred = m * t + c
    travel = abs(float(y[-1] - y[0])) or 1.0
    rms_pct = 100.0 * float(np.sqrt(np.mean((pred - y) ** 2))) / travel
    return float(m), rms_pct, travel


def linear_mode(a, col, t, y):
    """Constant-velocity travel (packetRide 2026-08-29): no plateau exists on
    either side by construction, so the plateau-to-plateau gate cannot converge.
    The physical comparison is the slope: speed ratio between reference and
    rebuild, each with its own linearity residual."""
    if len(t) < 8:
        print(f"fit-ease: only {len(t)} samples in window", file=sys.stderr); sys.exit(1)
    m1, r1, tr1 = _slope(np.asarray(t), np.asarray(y))
    out = {"csv": a.csv, "column": col, "kind": "linear", "window": [a.t_from, a.t_to],
           "samples": int(len(t)), "speed_units_per_s": round(m1, 3),
           "linearity_rms_pct_of_travel": round(r1, 3), "travel": round(tr1, 2)}
    if a.compare:
        cf = a.compare_from if a.compare_from is not None else a.t_from
        ct = a.compare_to if a.compare_to is not None else a.t_to
        t2, y2 = read_window(a.compare, cf, ct, col)
        if len(t2) < 8:
            print(f"fit-ease: only {len(t2)} samples in rebuild window", file=sys.stderr); sys.exit(1)
        m2, r2, tr2 = _slope(t2, y2)
        ratio = abs(m2 / m1) if m1 else float("inf")
        err = abs(ratio - 1.0) * 100.0
        verdict = ("proceed to G6" if err <= 5 else "adjust parameters, re-run" if err <= 15
                   else "classification is wrong, not the parameters: back to G2")
        if max(r1, r2) > 5.0:
            verdict += "  (WARNING: a side is not linear, rms>5% of travel; use --kind move)"
        out["g5"] = {"method": "physical: speed ratio (no plateau)", "rebuild_window": [cf, ct],
                     "ref_speed": round(m1, 3), "rebuild_speed": round(m2, 3),
                     "speed_ratio": round(ratio, 4), "mean_abs_error_pct": round(err, 2),
                     "ref_linearity_rms_pct": round(r1, 3), "rebuild_linearity_rms_pct": round(r2, 3),
                     "verdict": verdict, "gate": {"proceed": 5, "adjust": 15}}
    if a.json:
        print(json.dumps(out, indent=2)); return
    print(f"fit-ease  linear  column={col}  window {a.t_from}-{a.t_to}s  {len(t)} samples")
    print(f"  speed {m1:.3f} units/s   linearity rms {r1:.2f}% of travel ({tr1:.1f} units)")
    if "g5" in out:
        g = out["g5"]
        print(f"  G5 (GATE, physical)  rebuild speed {g['rebuild_speed']:.3f}  ratio {g['speed_ratio']:.4f}  "
              f"-> |error| {g['mean_abs_error_pct']:.2f}%  rebuild linearity rms {g['rebuild_linearity_rms_pct']:.2f}%")
        print(f"      {g['verdict']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--from", dest="t_from", type=float, required=True)
    ap.add_argument("--to", dest="t_to", type=float, required=True)
    ap.add_argument("--kind", choices=["fade", "move", "linear"], default="fade",
                    help="fade: diff pulse; move: plateau-to-plateau step; linear: constant-velocity "
                         "travel (no plateaus), compared by SLOPE ratio + linearity residual")
    ap.add_argument("--col", default=None,
                    help="column to fit (default: diff for fade, cy for move)")
    ap.add_argument("--fps", type=float, default=None,
                    help="frames per second; inferred from t spacing if omitted")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--compare", default=None, metavar="REBUILD_CSV",
                    help="G5: fit a second csv (the rebuild) and score it against this one at matched elapsed time")
    ap.add_argument("--compare-from", type=float, default=None)
    ap.add_argument("--compare-to", type=float, default=None)
    a = ap.parse_args()

    col = a.col or ("diff" if a.kind == "fade" else "cy")
    t, y = read_window(a.csv, a.t_from, a.t_to, col)
    if a.kind == "linear":
        return linear_mode(a, col, t, y)
    if len(t) < 8:
        print(f"fit-ease: only {len(t)} samples of '{col}' in {a.t_from}-{a.t_to}s; "
              f"need >= 8. Widen the window or pick a column that is populated.",
              file=sys.stderr)
        sys.exit(1)
    fps = a.fps or (1.0 / float(np.median(np.diff(t))))
    frame = 1.0 / fps

    results = []
    for name in FAMILIES:
        r = fit_family(name, t, y, a.kind, fps)
        if r:
            results.append(r)
    results.sort(key=lambda r: r["rms"])
    lin = next((r for r in results if r["family"] == "linear"), None)
    for r in results:
        r["vs_linear"] = (lin["rms"] / r["rms"]) if lin and r["rms"] > 0 else None
    best = results[0]
    runner = results[1] if len(results) > 1 else None
    # "no ambiguity" needs the winner to beat the runner-up by a margin the
    # instrument can resolve. Under 10% apart, say so instead of picking.
    margin = (runner["rms"] / best["rms"] - 1.0) * 100 if runner and best["rms"] > 0 else None
    decisive = margin is not None and margin >= 10.0

    out = {
        "csv": a.csv, "column": col, "kind": a.kind,
        "window": [a.t_from, a.t_to], "samples": int(len(t)), "fps": round(fps, 3),
        "resolution_s": round(frame, 4),
        "best": {k: (round(v, 4) if isinstance(v, float) else v)
                 for k, v in best.items()},
        "decisive": decisive, "margin_pct_over_runner_up": None if margin is None else round(margin, 1),
        "ranking": [{"family": r["family"], "D": round(r["D"], 3),
                     "t0": round(r["t0"], 3), "rms_pct_of_amp": round(r["rms_pct_of_amp"], 2),
                     "vs_linear": None if r["vs_linear"] is None else round(r["vs_linear"], 2),
                     "k": None if r["k"] is None else round(r["k"], 3)}
                    for r in results[:a.top]],
    }
    if a.compare:
        out["g5"] = g5_direct(a, col, fps, t, y)             # THE gate number
        out["g5_fitted"] = g5_compare(a, col, fps, t, y, best)  # diagnostic only

    if a.json:
        print(json.dumps(out, indent=2))
        return

    print(f"fit-ease  {a.kind}  column={col}  window {a.t_from}-{a.t_to}s  "
          f"{len(t)} samples @ {fps:.2f} fps  (resolution +-{frame*1000:.0f} ms)")
    print()
    print(f"  {'family':<14} {'duration':>9} {'start':>9} {'end':>9} {'rms % amp':>10} {'x linear':>9}")
    for r in results[:a.top]:
        vl = "-" if r["vs_linear"] is None else f"{r['vs_linear']:.2f}"
        kk = f"  k={r['k']:.2f}" if r["k"] is not None else ""
        print(f"  {r['family']:<14} {r['D']:>8.3f}s {r['t0']:>8.3f}s {r['t0']+r['D']:>8.3f}s "
              f"{r['rms_pct_of_amp']:>9.2f}% {vl:>9}{kk}")
    print()
    b = best
    tag = "DECISIVE" if decisive else "NOT decisive"
    print(f"  best: {b['family']}  D={b['D']:.3f}s  t0={b['t0']:.3f}s  "
          f"({tag}: {margin:.1f}% better than runner-up {runner['family'] if runner else '-'})"
          if margin is not None else f"  best: {b['family']}  D={b['D']:.3f}s")
    if not decisive:
        print("  -> two families fit within 10% of each other. The instrument cannot"
              " separate them; pick the simpler one and record both in provenance.")
    if b["rms_pct_of_amp"] > 15:
        print("  -> best fit is worse than 15% of range: this window is NOT one ease."
              " Flat top = linear over a longer span, or two overlapping events. Re-cut the window.")
    if "g5" in out:
        g = out["g5"]
        print()
        if "error" in g:
            print(f"  G5 direct: {g['error']}")
        else:
            print(f"  G5 (GATE, family-free)  ref rise10-90 {g['ref_rise_10_90_s']}s  "
                  f"rebuild rise10-90 {g['rebuild_rise_10_90_s']}s  t50-aligned")
            print(f"      mean |error| {g['mean_abs_error_pct']:.2f}%  max {g['max_abs_error_pct']:.2f}%  "
                  f"-> {g['verdict']}")
            lo, hi = g["window_sensitivity_pct"]
            print(f"      window sensitivity (+-2 frames each side): {lo:.2f}% .. {hi:.2f}%"
                  + ("  <- WINDOW-SENSITIVE: widen both windows to include flat plateaus" if g["window_sensitive"] else ""))
        gf = out.get("g5_fitted") or {}
        if "error" not in gf:
            print(f"  G5 fitted (diagnostic only): rebuild best {gf['rebuild_best']['family']} "
                  f"D={gf['rebuild_best']['D']:.3f}s vs reference {b['family']} D={b['D']:.3f}s; "
                  f"mean |error| {gf['mean_abs_error_pct']:.1f}%")


if __name__ == "__main__":
    main()
