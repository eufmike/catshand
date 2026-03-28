---
description: Run the full post-editing pipeline for a catshand podcast project
---

Execute the post-editing workflow: silence removal → track merging → Audacity automation.

Prerequisites:
- Project initialized (`/project-init`)
- WAV files present in `wav/` (`audio2wav` completed)
- Audacity 3.6.1 running with scripting enabled (not 3.6.4 — known pipe bug)

Pipeline steps:

1. **Silence removal**
   ```bash
   catshand_dev silrm --project-dir <project_dir>
   ```

2. **Track merging**
   ```bash
   catshand_dev trackmerger --project-dir <project_dir>
   ```

3. **Audacity post-processing** (requires Audacity open)
   ```bash
   catshand_dev audacitypipe --project-dir <project_dir>
   ```

4. Verify output in `edit/` directory — each host should have a processed stereo track.

Troubleshooting:
- If `audacitypipe` hangs: confirm Audacity is open and `Preferences > Modules > mod-script-pipe` is enabled.
- On macOS, the pipe file appears at `/tmp/audacity_script_pipe.to.<pid>`.
- If tracks are out of sync, check the split timestamps in the project's `config.json`.
