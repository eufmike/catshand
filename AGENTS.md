# Catshand — Agent Guide

Catshand (Cat's Hand, 猫の手も借りたい) is a CLI toolbox for podcast audio editing and production. It automates pre-editing and post-editing workflows, integrates with Audacity via named pipes, and uses OpenAI's Whisper API for transcription.

## Project Layout

```
catshand/
├── src/catshand/          # Main package
│   ├── main.py            # CLI entry (argparse, legacy)
│   ├── main_dev.py        # CLI entry (typer, active)
│   ├── tools/             # Subcommand implementations
│   ├── config/            # JSON config templates
│   └── CLI/               # Shell script helpers
├── agents/
│   └── commands/          # Reusable slash-command definitions
├── .claude/
│   └── commands/          # Symlinks → agents/commands/
├── references/
│   ├── plans/             # Implementation plans
│   ├── decisions/         # Architecture decision records
│   └── progress/          # Historical progress reports
├── tests/                 # Pytest test suite
├── spec.md                # Tech stack specification
└── pyproject.toml         # Project metadata + tool config
```

## Tech Stack (v0.4.0+)

| Concern | Tool |
|---|---|
| CLI | [Typer](https://typer.tiangolo.com/) |
| Data models / validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Parallel processing | [Dask](https://www.dask.org/) |
| Environment management | [Pixi](https://prefix.dev/) |
| Linting | Ruff |
| Type checking | MyPy |
| Testing | Pytest |

See [spec.md](spec.md) for design rationale and usage patterns.

## CLI Entry Points

```bash
# Run the development CLI (typer-based, v0.4.0 target)
catshand_dev --help

# Run the legacy CLI (argparse-based)
catshand --help
```

### Available Subcommands

| Command | Module | Description |
|---|---|---|
| `prjinit` | `tools/prjinit.py` | Initialize a new podcast project |
| `audio2wav` | `tools/audio2wav.py` | Convert audio files to WAV + normalize |
| `silrm` | `tools/silrm.py` | Remove silence from audio tracks |
| `audiosplit` | `tools/audiosplit.py` | Split audio at timestamp markers |
| `trackmerger` | `tools/trackmerger.py` | Merge multi-track audio |
| `audmerger` | `tools/audmerger.py` | Merge with spatial audio metadata |
| `audacitypipe` | `tools/audacitypipe.py` | Automate Audacity via named pipe |
| `prjsummary` | `tools/prjsummary.py` | Transcribe and summarize project |
| `linkparser` | `tools/linkparser.py` | Parse links from episode notes |
| `cleanvoice` | `tools/cleanvoice.py` | Clean voice tracks |

## Development Workflow

```bash
# Install environment (pixi)
pixi install

# Run tests
pixi run pytest
# or directly:
pytest tests/

# Lint
pixi run ruff check src/
pixi run mypy src/

# Format
pixi run ruff format src/
```

## Audacity Integration

Catshand communicates with Audacity through a named pipe (`pipefunc.py`). Audacity must be running with scripting enabled.

- Mac pipe path: `/tmp/audacity_script_pipe.to.{pid}`
- Config: `src/catshand/config/audt_config.json`
- Known issue: Audacity 3.6.4 broke the pipe protocol — use 3.6.1.

## OpenAI Integration

Set `OPENAI_API_KEY` in your environment. The `prjsummary` command uses Whisper for transcription and GPT for summarization.

## Agent Commands

Custom slash commands live in `agents/commands/` and are symlinked into `.claude/commands/` for Claude Code access.

| Command | File | Description |
|---|---|---|
| `/project-init` | [agents/commands/project-init.md](agents/commands/project-init.md) | Scaffold a new podcast project |
| `/transcribe` | [agents/commands/transcribe.md](agents/commands/transcribe.md) | Transcribe audio files |
| `/postedit` | [agents/commands/postedit.md](agents/commands/postedit.md) | Run post-editing pipeline |

## Key Configuration Files

- `src/catshand/config/audt_config.json` — Audacity automation parameters
- `src/catshand/config/hosts_dict.json` — Speaker/host name mappings
- `pyproject.toml` — All tool configuration (ruff, mypy, pytest, bumpver)
- `pixi.toml` — Environment definition (replaces conda YML)
