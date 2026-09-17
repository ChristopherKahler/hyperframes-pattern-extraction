---
description: Word-level timestamp transcript (+ true word-level SRT) for any audio/video — the anchoring artifact for HyperFrames, Filmora keyframes, and caption pop-ins. Runs the video-use local WhisperX engine in WSL and auto-stages Windows-sourced media into WSL-native fs first.
argument-hint: "[path to audio/video] [--diarize N] [--scribe]"
allowed-tools: [Bash, PowerShell, Read, Write, Edit, AskUserQuestion]
type: command
status: active
tags: [transcription, wordstamps, srt, video-use, hyperframes, sermon, wsl, anchoring]
relatedTo: [clone-short, breakdown-reel, sermon-assistant, video-use]
---

<objective>
Produce a **word-level timestamp transcript** of an audio/video file so every spoken word maps to an exact start/end timecode — the substrate for frame-accurate editing: HyperFrames overlays, Filmora keyframes, caption pop-ins, sermon-clip anchoring.

Two artifacts, both delivered:
1. `<name>.json` — Scribe-shaped `words[]` (type=word|spacing, start, end, text). The machine-readable anchor source (what HyperFrames / caption engines read).
2. `<name>.words.srt` — **one SRT cue per word**. The portable anchor (Filmora/Premiere/Resolve import, manual scrubbing).

Input: $ARGUMENTS  (a media path; optionally `--diarize N` for N speakers, or `--scribe` to use ElevenLabs instead of local)
</objective>

<environment_model>
- **The transcription engine lives in WSL.** `~/ops-sys/toolbox/skills/video-use/.venv` (WhisperX large-v3 + wav2vec2 forced alignment, CPU/int8). Windows has no equivalent env — every transcription runs through `wsl.exe -d Ubuntu bash -lc '...'`.
- **The Bash tool here is Git Bash (MINGW64), not WSL.** It reaches Windows paths as `/c/...`. It does NOT share the WSL filesystem and it **mangles `//wsl.localhost` UNC paths** ("Read-only file system") — never use Git Bash to copy into WSL.
- **PowerShell is the Windows↔WSL bridge.** It reads `C:\...` and writes `\\wsl.localhost/Ubuntu\...` natively. Use it for all staging copies.
</environment_model>

<hard_rules>
- **WSL cannot read `/mnt/c` on this machine — the entire Windows mount is permission-denied to WSL binaries.** (Windows Explorer/Filmora read the file fine; `ffmpeg`/`ffprobe` inside WSL get `Permission denied` / ffmpeg exit 243.) Therefore: **any Windows-sourced media MUST be staged into WSL-native fs before transcribing.** Never point `transcribe_local.py` at a `/mnt/c/...` path on this box.
  - Stage with PowerShell → `\\wsl.localhost/Ubuntu\home/<you>\wordsrt-src\<name>`, then transcribe the native path `~/wordsrt-src/<name>`.
- **Word-level verbatim ASR only.** `transcribe_local.py` (or `--scribe`). Never phrase/SRT mode out of the ASR — the word-level SRT is *derived* by `word_srt.py`, never asked of the model. (video-use Hard Rule 8.)
- **Cache per source — never re-transcribe.** If `edit/transcripts/<name>.json` already exists, skip ASR and go straight to the SRT step. (video-use Hard Rule 9.)
- **Long job → background + monitor.** Local CPU runs ~0.3–0.7× realtime (a 19-min file ≈ 30–60 min). Launch with `nohup ... &`, log to `~/wordsrt-<stem>.log`, poll — do not block.
- **`--no-diarize` is the default.** No `HF_TOKEN` is configured, and sermons/talking-heads are single-speaker. Only drop it (and pass `--num-speakers N`) when the user passes `--diarize N` AND `HF_TOKEN` exists in the skill `.env`.
- **Never write inside the skill dir.** Outputs land in `edit/` beside the (staged) source. (video-use Hard Rule 12.)
</hard_rules>

<pipeline>

**1 · Resolve the source.** Take the path from `$ARGUMENTS` (or the file the user just referenced). Note its `stem` (basename without extension) — used for the staging name, the log name, and the output names.

**2 · Stage into WSL-native fs (PowerShell).** Because of the `/mnt/c` block, always stage a Windows-sourced file:
```powershell
$dest = '\\wsl.localhost/Ubuntu\home/<you>\wordsrt-src'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item '<C:\full\path\to\file.ext>' (Join-Path $dest '<file.ext>') -Force
```
The WSL-native input is now `~/wordsrt-src/<file.ext>`. (If the source is already inside WSL-native fs, skip staging and use it directly.)

**3 · Duration + estimate (WSL ffprobe).**
```bash
wsl.exe -d Ubuntu bash -lc 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ~/wordsrt-src/<file.ext>'
```
Report duration and the ~0.3–0.7× realtime estimate so the user knows the wait.

**4 · Transcribe word-level, in the background.** (Default local engine. `--scribe` routes to ElevenLabs via `transcribe.py`, needs `ELEVENLABS_API_KEY`.)
```bash
wsl.exe -d Ubuntu bash -lc '
cd ~/ops-sys/toolbox/skills/video-use
nohup .venv/bin/python helpers/transcribe_local.py ~/wordsrt-src/<file.ext> --no-diarize \
  > ~/wordsrt-<stem>.log 2>&1 &
echo "PID=$!"; sleep 6; cat ~/wordsrt-<stem>.log'
```
Confirm the log advances past `extracting audio` into `asr (large-v3 ...)`. Output JSON will be written to `~/wordsrt-src/edit/transcripts/<stem>.json`.

**5 · Monitor to completion.** Poll the log / check for the JSON. Completion = the JSON file exists and the log shows the align+write finished. Do not re-run while it's working.
```bash
wsl.exe -d Ubuntu bash -lc 'ls -la ~/wordsrt-src/edit/transcripts/<stem>.json 2>/dev/null && tail -3 ~/wordsrt-<stem>.log'
```

**6 · Derive the word-level SRT.**
```bash
wsl.exe -d Ubuntu bash -lc 'cd ~/ops-sys/toolbox/skills/video-use && \
  .venv/bin/python helpers/word_srt.py ~/wordsrt-src/edit/transcripts/<stem>.json'
```
Writes `~/wordsrt-src/edit/transcripts/<stem>.words.srt` (one cue per word). Optional flags: `--pad 0.04` to nudge cue ends, `--min-dur` for floor.

**7 · Deliver back to Windows (PowerShell).** WSL can't write to `/mnt/c` either — copy the artifacts to the Windows side beside the source so they're in the editor's reach:
```powershell
$srcdir = '\\wsl.localhost/Ubuntu\home/<you>\wordsrt-src\edit\transcripts'
$out    = 'C:\full\path\to\source_folder'   # where the original video lives
Copy-Item "$srcdir\<stem>.json"       $out -Force
Copy-Item "$srcdir\<stem>.words.srt"  $out -Force
```

**8 · Report.** Give the user: JSON path, word-SRT path, word count, audio duration, and a one-line anchoring note (e.g. "every word now has start/end ms — anchor HyperFrames or Filmora keyframes against these"). Optionally offer the packed phrase-level view (`pack_transcripts.py --edit-dir ~/wordsrt-src/edit`) for fast human reading.

</pipeline>

<optional_followups>
- **Sermon content package** → feed the transcript to `/sermon-assistant` for summary, description, titles, hooks.
- **Edit the video** → the full video-use loop (cut from word boundaries, grade, overlays, burn captions).
- **Short-form clone** → `/clone-short` consumes the same wordstamp step for HyperFrames comps.
</optional_followups>

<companions>
- video-use skill: `~/ops-sys/toolbox/skills/video-use/` (engine, `transcribe_local.py`, `word_srt.py`, `pack_transcripts.py`, `render.py`).
- `/clone-short` — uses the identical wordstamp step (its step 4) for avatar reels.
- `/sermon-assistant` — turns the resulting transcript into a YouTube content package.
</companions>
