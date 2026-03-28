---
description: Scaffold a new podcast project directory for catshand
---

Initialize a new podcast project in the current directory using `catshand_dev prjinit`.

Steps:
1. Ask the user for the project name and list of host names.
2. Run `catshand_dev prjinit --name "$PROJECT_NAME"` (or guide them through the interactive prompts).
3. Verify the created folder structure matches the expected layout:
   - `raw/` — source audio files
   - `wav/` — converted WAV files
   - `edit/` — editing workspace
   - `output/` — final exports
   - `config.json` — project configuration (validated by `ProjectConfig` Pydantic model)
4. Confirm `config.json` is populated with the correct host names and sample rate.

If the command fails, check that `pixi install` has been run and the `catshand` package is installed in the active environment.
