# Extraction child — the contract

You are one extraction child of `/pattern-extract`, spawned by the orchestrator
`cougar` (project `video-gen`). You own the candidates named in your prompt and
nothing else. Read this whole file before your first tool call after boot duties.

The goal of the whole programme: a library of motion patterns good enough that a
session can build a video at the PayCloud bar from the library alone. Your two
patterns are two bricks of that. Token spend, runtime and context are NOT
constraints. Chris said so, repeatedly. Do the full pass every time; double-verify;
when in doubt do more, not less.

## Files you must read first, in this order

1. `$REPO/commands/pattern-extract.md` — the gates G0–G6 you run
2. `$REPO/pattern-library/LIBRARY.md` — the library shape
3. `$REPO/pattern-library/hfpat.js` — the builders, `eases()`, `layout()`
4. `$REPO/pattern-library/example/index.html` — a complete composition
5. `<run>/build/orbit-draft.js` — a finished DRAFT
   builder from this same reference: measured constants with provenance comments, mirror
   handled in code (`HFPat.activeLayout()`), a `guard*` that throws before render. Copy its shape.
6. `<run>/G1-G2-candidates.md` — your candidates'
   rows, and the G2 measurements already made on this reference
7. `<run>/teardown/paycloud-teardown.md` — the whole film, measured
8. Your workspace `CLAUDE.md` (HyperFrames scaffold contract: `class="clip"`, `data-start`,
   `window.__timelines["main"]`, determinism)

## Your workspace

`<run>/children/<your-title>/` — a scaffolded
HyperFrames project (`hyperframes.json`, `package.json`, `CLAUDE.md`, `pattern-library/`
junction). The reference mp4 is already at `scratch/dl/_38ybzeZ9i8.mp4` so `watch.py`
runs offline. Everything you produce stays inside this directory. **Never edit
`pattern-library/hfpat.js`, `tokens.css`, `LIBRARY.md`, `hfpat-index.json` or anything
under `pattern-library/` — that junction points at the live library.** Drafts go in
`drafts/`.

## Gates — run every one, in order, for EACH of your patterns

**G0 — see it. WATCH ALL OF IT.** Run the full watch on the reference yourself:

```
python $REPO/tools/watch-video/watch.py "https://www.youtube.com/watch?v=_38ybzeZ9i8" --note "G0 <your-title>" --keep --scratch scratch
```

Open every `defect_*.jpg`, then every `sheet_*.jpg` (all ~29). Not a sample. Never pass
`--from/--to`. The frames stay on disk because of `--keep`; note the frames dir it
prints, you need it for G2. Then re-read your candidates' rows in `G1-G2-candidates.md`
and confirm the frame ranges against what you saw. If you disagree with the row, say so
in your report with frame numbers.

**G2 — measure.** Numbers, not impressions, every timing cites a frame or CSV row.

- `python $REPO/tools/watch-video/motion.py <frames_dir> --fps 30 --roi X0,Y0,X1,Y1 --out g2/<slug>.csv`
  with an ROI tight on the moving element. Full-frame diff on a small element sits at
  the noise floor and flattens the curve — that is exactly how the first orbit rebuild
  mis-read its cross-fade.
- **Every entrance, exit or transition gets fitted, not eyeballed:**
  `python $REPO/tools/watch-video/fit-ease.py g2/<slug>.csv --from A --to B --kind fade|move [--col cy] --json`
  Frame-diff is the DERIVATIVE of opacity/position: a triangle on `diff` is an S-curve
  on the thing itself. fit-ease ranks every family and says whether the winner is
  decisive. Record the whole JSON block in provenance.
- Continuous motion: speed px/frame, direction, path class, from centroid traces.
- Repeats: compare diff profiles frame by frame. Near-identical tails = one asset reused.
- Below ~0.3 px/frame the classification is noise. Say so.

**G2b — check the catalog before building.** Run `hfcat <mechanism words>` (and
`hfcat --show <slug>` on anything close). Our patterns are builders on `hfpat.js`, so a
catalog hit is (a) a possible implementation to adapt and (b) a fact for provenance.
Record the query, the top matches, and your decision (`hand-build: <why>` or
`adapted <slug>: <what>`). A `no catalog match` line is a legitimate answer.

**G3 — fit to the template shape.** `HFPat.<name>(tl, selectorOrElement, opts)`, chainable.
Measurements become `opts` defaults with the fitted numbers. Decide what a caller controls
(duration, travel, count, stagger, `at`) and what is internal. Name the closest GSAP ease
and the fitted residual.

**G4 — rebuild.** `drafts/<slug>.js`, loaded after `pattern-library/hfpat.js`, attaching
`HFPat.<slug>` and a `HFPat.guard<Slug>` that throws before render on the failure
classes `check` cannot see. **Generic content only — never the reference's palette, copy,
icons or subject.** Both layouts from ONE file with ONE differing line
(`HFPat.layout(window.__LAYOUT__ || "standard")`); mirror by swapping positions, never by
flipping pixels. Use `tokens.css` variables. No borders, rules, underlines, hairlines.
Nothing static beyond ~2 s (use `driftField` if needed). `npm run check` must pass 0/0 —
suppress only per LIBRARY.md's method (measure before you silence).

Render: `npx hyperframes render -o renders/<slug>-standard.mp4 --workers 2` and again with
`window.__LAYOUT__="mirror"` → `renders/<slug>-mirror.mp4`. Two workers, not auto: four
children share this machine.

**G5 — converge, mechanically.** Watch your render (`watch.py renders/<slug>-standard.mp4
--keep --scratch scratch`), run `motion.py` over its frames with the matching ROI, then:

```
python $REPO/tools/watch-video/fit-ease.py g2/<slug>.csv --from A --to B --kind ... --compare g5/<slug>-rebuild.csv --compare-from a --compare-to b --json
```

`mean_abs_error_pct` ≤ 5 → G6. 5–15 → adjust parameters, re-render, re-run. > 15 → the
classification is wrong, back to G2. Record every round's number. The reference and the
rebuild must be measured with the SAME instrument settings (ROI proportional, same fps).

**G6 — defect pass at 1:1.** `watch.py` on both renders; open EVERY `defect_*.jpg` and
every sheet. Checklist from pattern-extract G6, all items, per layout. Any failure: fix,
re-render, re-check. Never deliver a render with a known defect. Also measure ink over
the FULL glyph height when spacing type (LIBRARY.md, gap 7).

## Deliverables — exact paths, all inside your workspace

```
drafts/<slug>.js                      the draft builder (+ guard), provenance comments inline
index.html                            the composition demonstrating BOTH patterns (or one file per slug)
renders/<slug>-standard.mp4           1920x1080 @30, ~4-9 s, generic content
renders/<slug>-mirror.mp4             same file, one line differs
g2/, g5/                              CSVs and fit-ease JSON for every measurement
provenance/<slug>.json                schema below
REPORT.md                             G10 table for your patterns + everything detected but not admitted + open issues
pending/<slug>.md                     the PENDING block: proposed hfpat-index.json row + LIBRARY.md row (schema below)
```

`provenance/<slug>.json`:

```json
{
  "slug": "", "title": "", "kind": "hfpat",
  "reference": {"id": "_38ybzeZ9i8", "url": "", "times_s": [[a, b]], "frames": [[f0, f1]]},
  "mechanism": "", "library_gap": "",
  "hfcat": {"query": "", "matches": ["slug: why it is / is not this"], "decision": ""},
  "measurements": [{"what": "", "window_s": [a, b], "roi": [x0, y0, x1, y1], "tool": "fit-ease|motion.py|centroid", "result": {}}],
  "fit": {"family": "", "duration_s": 0, "t0_s": 0, "rms_pct": 0, "decisive": true, "runner_up": ""},
  "opts": {"defaults the builder ships": "with the fitted values"},
  "g5": {"rounds": [{"n": 1, "mean_abs_error_pct": 0, "change": ""}], "final_pct": 0},
  "g6": {"check": "0 errors 0 warnings", "defect_crops_opened": 8, "sheets_opened": 0, "suppressions": [], "items": {"guard_clean": true, "no_borders": true, "alpha_masks": true, "no_clipping": true, "nothing_static_2s": true, "contrast": "N/N"}},
  "layouts": {"standard": "renders/<slug>-standard.mp4", "mirror": "renders/<slug>-mirror.mp4"},
  "enforced": "what the guard/builder asserts or derives instead of documenting",
  "known_open": [], "convergence_rounds": 0
}
```

`pending/<slug>.md`:

````
## <slug> — PENDING  (child: <title>, <date>)
mechanism: ...
reference: _38ybzeZ9i8 @ a–b s (frames f0–f1)
renders: renders/<slug>-standard.mp4 · renders/<slug>-mirror.mp4
G5 final: N% (rounds: k) · G6: clean · hfcat: <decision>
```json
{ "slug": "...", "kind": "hfpat", "title": "...", "description": "...", "install": "HFPat.<slug>(tl, el, opts)", "writes": "", "source": "$REPO/pattern-library\\hfpat.js", "enforced": "...", "layouts": ["standard", "mirror"], "provenance": "PayCloud _38ybzeZ9i8 a–b s; <fit family> <D> s, rms N%", "convergence": "<final G5 %> after <k> rounds", "approved": null }
```
LIBRARY row: | `<slug>` | <what it is> | <provenance incl. convergence> |
````

## Reporting — to cougar, never to chris

- After boot: `base relay ping --to cougar --msg "<title>: booted, G0 starting"`
- Stage changes only: `G0 done (N artifacts opened)`, `G2 done <slug>`, `G5 <slug> N%`,
  `DELIVERED <slug>` with the render paths. Not findings — those go in REPORT.md.
- Blocked: say what, and what you tried. Do not idle silently.
- Done: one final ping listing every deliverable path, then write your `.status` as
  `idle: delivered` and stay alive for the G8b interview.

## Standing rules

- `/watch-video` is a called tool. Never reimplement seeing.
- Every timing claim cites a frame number or CSV row.
- The reference's subject never enters the library. Only parameters transfer.
- Measure before you silence a `check` finding; record the number.
- Do not ask Chris anything. Ask cougar, once, with what you tried.
- Determinism: no `Date.now`, no `Math.random`, no fetch, pure `fromTo`.
- A pattern is portable or it is not; your builder must not depend on your composition.
