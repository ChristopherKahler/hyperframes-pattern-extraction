# Working in this repo

**Read [AGENT-GUIDE.md](AGENT-GUIDE.md) before doing anything.** It is every tool
in this kit, what each is for, and the rules that make the pipeline work.

Fast orientation:

- Installing on a fresh machine → [SETUP.md](SETUP.md)
- Building with the pattern library → `pattern-library/LIBRARY.md`
- **Before hand-building any visual element** → `hfcat "<what you need>"`
  (379 ready-made blocks, components and patterns; `--show <slug>` for the
  correct mount key, which for 44 of 154 blocks is not the slug)
- Before judging a video → `python tools/watch-video/watch.py <target>`, then
  open every native-resolution `defect_*.jpg` before any contact sheet

Two rules that are enforced in code, not prose:

- `watch.py` refuses `--from/--to` without `--partial "<the user's words>"`.
  Never narrow a watch request yourself.
- Nothing enters `hfpat.js` or `hfpat-index.json` without an explicit human
  approval, via `codify.py fold`. `codify.py register` parks it in `PENDING.md`
  until then.
