# HF Token Setup — For Later

Speaker diarization in `transcribe_local.py` uses pyannote models, which require a free HuggingFace account + model-access approval. Takes ~2 minutes. Until you do this, pass `--no-diarize` or accept that transcripts won't have `speaker_id` labels.

## Steps

1. **Create account** (skip if you have one): https://huggingface.co/join

2. **Create a token** — https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: `video-use` (or anything)
   - Type: **Read** (that's all that's needed — don't use Write/Fine-grained)
   - Copy the token — it starts with `hf_`

3. **Accept model terms** — while logged in, visit each page and click "Agree and access repository":
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

   Both are required. Forgetting one causes a cryptic 401 on first run.

4. **Save the token locally:**
   ```bash
   cd /path/to/video-use
   cp .env.example .env
   # Edit .env and paste the token after HF_TOKEN=
   ```

   `.env` is gitignored — safe to store the token there.

## Verify it works

```bash
cd /path/to/video-use
python helpers/transcribe_local.py /path/to/any/short/clip.mp4
```

Should see `diarizing` in the log output and the resulting JSON should include `"speaker_id": "speaker_0"` fields on word entries. If you see `no HF_TOKEN — skipping diarization`, the env file didn't load — check the variable name is exactly `HF_TOKEN=` with no quotes.

## If it fails

- **401 Unauthorized on first run** → you missed accepting terms on one of the two model pages in step 3. Go back and accept both.
- **`HF_TOKEN` not picked up** → check `.env` is in `apps/video-use/` (not parent dir) and the line reads exactly `HF_TOKEN=hf_...`.
- **Still not working** → `export HF_TOKEN=hf_...` in your shell and re-run; if that works, the `.env` parser is the issue.
