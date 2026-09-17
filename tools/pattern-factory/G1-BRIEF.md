# G0 + G1 child — the contract (one per reference)

You own the first two gates of `/pattern-extract` for ONE reference video, and you
produce the machine-readable candidate list the factory fans out from. You do not
build anything.

## Read first

1. `$REPO/commands/pattern-extract.md` — G0 and G1 exactly
2. `$REPO/pattern-library/LIBRARY.md` — what the library
   already holds, so nothing shipped is re-admitted under a new name
3. `$REPO/pattern-library/PENDING.md` — what is in flight
4. `<run>/G1-G2-candidates.md` — the shape
   of a good candidate list (reusable across subjects; mechanisms, not appearances)
5. `<run>/G1.json` — the exact JSON shape
   you must emit
6. `<run>/teardown/QUEUE.md` — the screening rule
   (count shots ≥ 2.5 s; under ~25 % usable it is a montage and you say so)
7. Any teardown for this reference under `references/` if one exists

## G0 — WATCH ALL OF IT

```
python $REPO/tools/watch-video/watch.py "<url>" --note "G0 <reference>" --keep --scratch scratch
```

Open every `defect_*.jpg`, then every `sheet_*.jpg`. All of them. Never `--from/--to`.
Verify the unique-frame count. Note the kept frames dir. If the video is a montage by
the screening rule, say so in your report and stop after G1 with the count.

## G1 — candidates

Name every distinct, reusable-across-subjects motion mechanism with its time range(s),
the mechanism in one sentence (what moves, how, on what ease family if visible), and the
library gap it fills (or the library pattern it duplicates, in which case it is NOT a
candidate). Expect 5–15 on a real reference. Also list what you detected and did not
admit, with the reason. Every time cites a frame or a sheet.

Then group candidates into child assignments of 1–2 patterns each (same scene, or same
mechanism family), with a one-line `why`.

## Deliverables

```
G1-candidates.md          human-readable, same shape as the PayCloud one
G1.json                   EXACT shape of extract-paycloud/G1.json: reference{id,url,name,duration_s,fps,frames,cached_mp4,teardown?}, g0{by,date,artifacts_opened}, candidates[], assignments[], detected_not_admitted[]
```

`cached_mp4` is the path watch.py printed (`scratch/dl/<id>.mp4`), absolute.

## Reporting

`base relay ping --to cougar` on: booted · G0 done (N artifacts opened, unique frames) ·
DELIVERED with both paths. Never ping chris. Stay alive afterwards.
