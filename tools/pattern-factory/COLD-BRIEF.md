# Cold-test child — the contract (G8, batched)

You are a cold-test child. You have never seen the reference video and you must not
look for it. Your job is to build a short motion graphic on a subject named in your
prompt, using ONLY the pattern library plus the draft builders listed in your prompt,
and to report every place the templates left you guessing.

You are a gap finder, not a scoreboard. Every question you would have asked is a hole
in the templates; write it down instead of working around it silently.

## What you get

- `$REPO/pattern-library/` (junctioned as `pattern-library/`
  in your workspace): `LIBRARY.md`, `hfpat.js`, `tokens.css`, `example/index.html`
- `drafts/*.js` in your workspace: the candidate builders, each with a header comment
  naming its `HFPat.<name>(tl, el, opts)` signature, its `opts`, and its guard
- your workspace `CLAUDE.md` (HyperFrames scaffold contract)

Read `LIBRARY.md` first and follow it. Read each draft's header. Nothing else.

## What you build

One composition, 8–15 s, 1920x1080, generic content on the subject given, that uses
EVERY draft builder listed at least once, in both layouts (`standard` and `mirror`, one
file, one differing line). Run `HFPat.guard()` and every `guard*` the drafts expose
before rendering. `npm run check` 0/0. Render with `--workers 2`.

Then watch your own render (`python $REPO/tools/watch-video/watch.py
renders/cold-standard.mp4 --keep --scratch scratch`), open every `defect_*.jpg` and every
sheet, and fix what you find. Deliver only when you would put your name on it.

## Deliverables

```
index.html
renders/cold-standard.mp4
renders/cold-mirror.mp4
GAPS.md      one row per gap: what you needed | where you looked | what you found | what you decided | line of LIBRARY.md or draft you acted on
REPORT.md    what you built, which builder did what, anything a draft could not do
```

## Rules

- No coaching: do not ping the orchestrator with questions mid-run. Log them in GAPS.md.
- Do not open `pattern-library/baselines/` (regression references, not creative reference).
- Do not read anything under `extract-*/` other than your own workspace.
- Report to `cougar` only: `booted`, `DELIVERED <paths>`. Never ping chris.
- Stay alive after delivery for the G8b interview.
