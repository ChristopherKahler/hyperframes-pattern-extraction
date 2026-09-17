# SETUP — get this machine to what the source machine does

Written to be executed top to bottom by an AI agent on a fresh machine, or by a
human reading along. **Verify each step's check line before moving on.** A tool
that is "probably installed" is the most common cause of a failure three steps
later that looks like something else entirely.

Target platform is **Windows**, because that is what the pipeline was built and
measured on. macOS/Linux notes are inline where they differ; nothing here is
Windows-only in principle, but the ffmpeg quoting rules in
[docs/FFMPEG-LEVERS.md](docs/FFMPEG-LEVERS.md) and the console-window fix in
`tools/hyperframes-fix/` are Windows-specific.

Versions in the **Verified** column are what the source machine actually runs, as
of 2026-09-17. Newer is normally fine; where it is not, it says so.

| Tool | Verified | Needed for | Hard requirement |
|---|---|---|---|
| Python | 3.12.6 | every script in `tools/` | 3.10+ |
| numpy | 2.3.4 | frame differencing, motion measurement | yes |
| Pillow | 12.0.0 | contact sheets, defect crops | yes |
| scipy | 1.16.3 | ease curve fitting (`fit-ease.py`) | yes |
| ffmpeg + ffprobe | 8.0 | frame extraction, all encoding | yes |
| yt-dlp | 2026.08.19 | watching a reference off a URL | only for URLs |
| Node.js | 22.11.0 | HyperFrames CLI | **>=22**, enforced |
| npm | 11.2.0 | installing HyperFrames | yes |
| hyperframes | 0.8.16 | rendering compositions | yes |
| Chrome / Chromium | any recent | HyperFrames renders through puppeteer-core | yes |
| WhisperX | large-v3 | word-level transcripts (`/wordsrt`) | only for captions |
| git | any | cloning this repo | yes |

---

## 1 · Python 3.12 and the three libraries

The measurement scripts are the heart of this kit and they are pure Python.

```powershell
# Windows — https://www.python.org/downloads/  (tick "Add python.exe to PATH")
python -V                      # check: Python 3.10 or newer
python -m pip install --upgrade pip
python -m pip install numpy pillow scipy
```

```bash
# macOS / Linux
python3 -V
python3 -m pip install numpy pillow scipy
```

**Check:**

```bash
python -c "import numpy, PIL, scipy; print(numpy.__version__, PIL.__version__, scipy.__version__)"
```

If `python` resolves to something unexpected on Windows (the Microsoft Store
stub is a common trap), find the real one and set `PEK_PYTHON` — every launcher
in `bin/` honours it:

```powershell
(Get-Command python).Source        # e.g. C:\Python312\python.exe
$env:PEK_PYTHON = "C:\Python312\python.exe"
```

## 2 · ffmpeg and ffprobe

Both, on PATH. `watch.py` extracts frames with ffmpeg and reads duration and
frame rate with ffprobe; without ffprobe you get a confusing failure inside the
frame-count step rather than a clean "not found".

```powershell
# Windows, via Chocolatey (what the source machine uses)
choco install ffmpeg
# or via winget
winget install Gyan.FFmpeg
```

```bash
# macOS
brew install ffmpeg
# Debian/Ubuntu
sudo apt install ffmpeg
```

**Check:** `ffmpeg -version` and `ffprobe -version` both print a version line.

Read [docs/FFMPEG-LEVERS.md](docs/FFMPEG-LEVERS.md) before writing any filter
chain by hand. It covers the quoting rules that differ between Git Bash and
PowerShell, which is where most one-off ffmpeg commands die on Windows.

## 3 · yt-dlp — only if you watch references off the web

```bash
python -m pip install --upgrade yt-dlp
```

**Check:** `yt-dlp --version`

**This one goes stale fast.** YouTube breaks it every few weeks. If a URL fails
with missing formats or a 403 partway through a download, that is the symptom:

```bash
python -m pip install -U yt-dlp
```

`watch.py` finds it via `shutil.which("yt-dlp")`, so it must be a real executable
on PATH, not only importable as a module.

## 4 · Node 22+ and the HyperFrames CLI

HyperFrames declares `engines: {node: ">=22"}` and it is enforced, not advisory.

```bash
node -v                        # must be v22.x or newer
npm i -g hyperframes
hyperframes --version
```

HyperFrames renders through **puppeteer-core**, which does not bundle a browser.
You need a real Chrome or Chromium installed. On a machine with Chrome already
present this is normally automatic; if rendering fails complaining about a
browser, install one and re-run.

**Check:** `hyperframes doctor` — it reports what it can and cannot find.

**Windows console-window fix.** On Windows, renders can spawn visible console
windows that steal focus for the whole run. The source machine patches this:

```powershell
pwsh tools/hyperframes-fix/fix-windows-console.ps1
```

Read the script before running it — it edits the installed `hyperframes`
package's `launch.js`, and an upgrade will overwrite the patch.

## 5 · hfcat — search the catalog before building anything

This is the piece an AI most needs and is least likely to discover on its own.
The catalog holds **379 finished, parameterised items**: 154 blocks, 218
components, and the 7 patterns in this repo's own library. Hand-building
something the catalog already has is the single most common waste in this
workflow.

The indexes ship in this repo, so `hfcat` works straight from a clone. Put
`bin/` on PATH:

```powershell
# Windows, current session
$env:PATH = "$PWD\bin;$env:PATH"
# Windows, permanent
[Environment]::SetEnvironmentVariable(
  "PATH", "$PWD\bin;" + [Environment]::GetEnvironmentVariable("PATH", "User"), "User")
```

```bash
# macOS / Linux
export PATH="$PWD/bin:$PATH"       # add to ~/.zshrc or ~/.bashrc to persist
chmod +x bin/hfcat
```

**Check:**

```bash
hfcat counter
# -> "N of 379 catalog items match 'counter'"
```

If it says `index not found`, `PEK_ROOT` is not resolving. Set it explicitly to
the repo root:

```bash
export PEK_ROOT=/path/to/hyperframes-pattern-extraction     # or $env:PEK_ROOT on Windows
```

### Usage

```bash
hfcat "stat counter"              # search everything
hfcat --type block "reveal"       # blocks only  (also: component, hfpat)
hfcat --show count-up             # variable schema + the CORRECT mount key
hfcat --vars -n 20 "chart"        # show variable counts, 20 results
hfcat --json "logo"               # machine-readable, for scripting
```

**`--show` matters more than it looks.** 44 of the 154 blocks mount under a key
that is **not** their slug. Installing a block and mounting it under its slug
silently renders nothing. Always `--show` before wiring one in.

### Optional: the full docs mirror

Each catalog row cites an upstream documentation page. Those pages are
HyperFrames' own content and are **not** redistributed in this repo, so
`hfcat --show` prints the page path plus a note rather than opening it. To get
the real pages:

```powershell
pwsh tools/hyperframes-fix/mirror-docs.ps1          # writes ./hyperframes-docs/
$env:HF_DOCS = "$PWD\hyperframes-docs"
python tools/hyperframes-fix/build-catalog-index.py # rebuild the index from it
```

`hyperframes-docs/` is gitignored — it is generated, never committed.

### Optional: the hfcat nudge hook

`hooks/hfcat-nudge.py` reminds an AI session that the catalog exists every time
it touches a HyperFrames command or edits a composition file, and records
whether it has actually queried yet this session. It always exits 0 and never
blocks a tool call.

Wire it into Claude Code's `settings.json` under `PreToolUse`:

```json
{"matcher": "Bash|PowerShell|Write|Edit|MultiEdit",
 "hooks": [{"type": "command",
            "command": "python /abs/path/to/hooks/hfcat-nudge.py"}]}
```

Use an absolute path and your real interpreter. Without this, a session started
outside the project directory has never heard of `hfcat` and will hand-build
things the catalog already ships.

## 6 · WhisperX — only if you need word-level transcripts

Needed by `/wordsrt` and `/breakdown-reel`, not by `/pattern-extract`. **Skip
this section if you are only extracting motion patterns.**

Word-level timestamps are the anchoring substrate for caption pop-ins and
frame-accurate overlays: every spoken word maps to an exact start/end timecode.

The source machine runs it in a **WSL Ubuntu virtualenv** (~2.1 GB with the
large-v3 model and wav2vec2 forced alignment, CPU/int8). Nothing about WhisperX
requires WSL — it is simply where that machine keeps it. A native install works:

```bash
python -m pip install whisperx
# first run downloads the model (several GB)
whisperx <audio> --model large-v3 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H \
         --language en --no_align False --output_format json
```

Notes carried over from the source setup, worth knowing:

- **Runtime is ~0.3-0.7x realtime on CPU.** A 19-minute file takes 30-60 minutes.
  Launch it in the background and poll; do not block a session on it.
- **Cache per source. Never re-transcribe.** If the JSON already exists, skip
  straight to deriving the SRT.
- **Word-level verbatim ASR only.** Never ask the model for phrase or SRT mode —
  derive the word-level SRT from the word JSON afterwards.
- **Diarisation is off by default.** It needs a HuggingFace token
  (`HF_TOKEN`) and single-speaker sources do not benefit.
- If you run it under WSL as the source machine does, read the environment notes
  at the top of [commands/wordsrt.md](commands/wordsrt.md) first — that file
  documents a real trap where WSL cannot read `/mnt/c` on that box, so Windows
  media must be staged into the WSL filesystem before transcribing.

## 7 · Install the pipeline commands into your AI

The files in `commands/` are the pipeline. They are written as Claude Code slash
commands; any agent that can read a markdown playbook can follow them.

**Claude Code:**

```powershell
# Windows
copy commands\*.md "$env:USERPROFILE\.claude\commands\"
```

```bash
# macOS / Linux
cp commands/*.md ~/.claude/commands/
```

Then `/pattern-extract`, `/watch-video`, `/breakdown-reel` and `/wordsrt` are
available in any session.

**Any other agent:** point it at [AGENT-GUIDE.md](AGENT-GUIDE.md), which is
written to be read cold.

## 8 · Full verification

Run all of these. Every line should succeed.

```bash
python -c "import numpy, PIL, scipy; print('py deps ok')"
ffmpeg  -version | head -1
ffprobe -version | head -1
node -v
hyperframes --version
hfcat counter | head -2
python tools/watch-video/watch.py --help | head -3
python tools/hyperframes-fix/hfcat.py --help | head -3
```

Then prove the whole chain end to end on a real file — a short MP4 you already
have:

```bash
python tools/watch-video/watch.py "<some.mp4>" --note "setup verification"
```

It should extract frames, write `motion.csv`, emit `sheet_*.jpg` contact sheets
and native-resolution `defect_*.jpg` bands into a `.watch/vNNN/` directory beside
the source, then delete the raw frames. **Open a `defect_*.jpg` and confirm it is
full resolution, not a thumbnail.** If it is a thumbnail, something downscaled it
and the whole defect pass is worthless — fix that before doing real work.

## Environment variables this kit honours

All optional. Every one defaults to something sensible derived from the repo's
own location, so a plain clone works with none of them set.

| Variable | Default | Use |
|---|---|---|
| `PEK_ROOT` | derived from script location | repo root, if auto-detection fails |
| `PEK_LIB` | `$PEK_ROOT/pattern-library` | point at a different library |
| `PEK_PYTHON` | `python` | the interpreter `bin/hfcat` should use |
| `HF_DOCS` | `$PEK_ROOT/catalog` | a full HyperFrames docs mirror |
| `PEK_REEL` | `$PEK_ROOT/tools/watch-video/reel.py` | — |
| `PEK_HUB` | `http://127.0.0.1:7799/api/spawn` | an agent-spawn hub, if you run one |
| `PEK_RELAY_INBOX` | `~/.pattern-extract/relay-inbox` | where child sessions write status |

The last two only matter for `tools/pattern-factory/factory.py`, which automates
fanning gates out across parallel agent sessions. **You do not need a spawn hub
to use this kit** — see "Running the gates without a spawn hub" in
[AGENT-GUIDE.md](AGENT-GUIDE.md).
