---
description: Transcribe podcast audio files using OpenAI Whisper via catshand
---

Transcribe audio files in a catshand project using the `prjsummary` command.

Requirements:
- `OPENAI_API_KEY` must be set in the environment.
- Audio files must already be converted to WAV (run `audio2wav` first if needed).

Steps:
1. Confirm `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY` (should not be empty).
2. Run transcription:
   ```bash
   catshand_dev prjsummary --project-dir <project_dir>
   ```
3. Output is written to `<project_dir>/transcript/` as JSON and text files.
4. Review the transcript files and report any segments with low confidence scores.

Notes:
- Large files are automatically segmented before submission to the Whisper API.
- Token usage is logged; check `output/token_usage.json` for cost tracking.
- Language defaults to auto-detect; pass `--language zh` for Mandarin Chinese episodes.
