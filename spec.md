# Catshand v0.4.0 — Technical Specification

## Overview

This document describes the modernized technology choices for catshand v0.4.0+. The goal is to replace ad-hoc patterns from earlier versions with consistent, well-typed, testable code.

---

## CLI — Typer

**Replace:** `argparse` (legacy `main.py`) and mixed `click`/`argparse` usage.

**Use:** [Typer](https://typer.tiangolo.com/) for all CLI commands.

### Rationale
- Derives argument parsers from Python type annotations — no boilerplate.
- Automatic `--help` generation with rich formatting.
- Native support for subcommand groups, which maps cleanly to the `tools/` module structure.
- Already partially adopted in `main_dev.py`.

### Pattern

```python
import typer
from typing import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def audio2wav(
    input_dir: Annotated[Path, typer.Argument(help="Source audio directory")],
    output_dir: Annotated[Path, typer.Option("--out", help="Output directory")] = Path("wav"),
    normalize: Annotated[bool, typer.Option(help="Apply loudness normalization")] = True,
) -> None:
    """Convert audio files to WAV format."""
    ...
```

### Subcommand Registration

Each tool in `tools/` exposes a `typer.Typer()` instance. The root `app` in `main_dev.py` adds them:

```python
from catshand.tools import audio2wav, silrm, trackmerger

app = typer.Typer()
app.add_typer(audio2wav.app, name="audio2wav")
app.add_typer(silrm.app, name="silrm")
```

---

## Data Models — Pydantic v2

**Replace:** Plain dicts, JSON loaded into `dict`, untyped config objects.

**Use:** [Pydantic v2](https://docs.pydantic.dev/) for all configuration, project metadata, and inter-module data structures.

### Rationale
- Schema validation at the boundary (config files, API responses, user input).
- Auto-generates JSON schema — useful for config documentation.
- `model_validator` and `field_validator` replace scattered validation logic.
- Works well with Typer (shared type annotations).

### Pattern

```python
from pydantic import BaseModel, field_validator
from pathlib import Path

class ProjectConfig(BaseModel):
    project_name: str
    hosts: list[str]
    input_dir: Path
    output_dir: Path
    sample_rate: int = 44100

    @field_validator("hosts")
    @classmethod
    def at_least_one_host(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Project must have at least one host")
        return v

class AudacityConfig(BaseModel):
    pipe_path: Path
    timeout_seconds: float = 10.0
    tracks: list[str] = []
```

Config files (`audt_config.json`, `hosts_dict.json`) are loaded and validated with Pydantic:

```python
config = ProjectConfig.model_validate_json(Path("config.json").read_text())
```

---

## Parallel Processing — Dask

**Replace:** `multiprocessing` with `fork` start method (breaks on macOS/Windows for some libraries).

**Use:** [Dask](https://www.dask.org/) bag and delayed APIs for batch audio processing.

### Rationale
- Dask delayed works as a drop-in replacement for function-level parallelism.
- Dask bag is natural for processing collections of audio files.
- Works correctly across platforms without spawn/fork ambiguity.
- Progress bars via `tqdm` or Dask's own dashboard.
- Scales from laptop to cluster without code changes.

### Pattern — Dask Delayed

```python
import dask
from dask import delayed

@delayed
def process_file(path: Path, output_dir: Path) -> Path:
    # CPU-bound audio processing
    ...
    return result_path

tasks = [process_file(p, output_dir) for p in input_files]
results = dask.compute(*tasks, scheduler="processes")
```

### Pattern — Dask Bag (batch operations)

```python
import dask.bag as db

bag = db.from_sequence(input_files, npartitions=4)
results = bag.map(lambda p: process_file(p, output_dir)).compute()
```

### Scheduler Selection

| Scenario | Scheduler |
|---|---|
| CPU-bound (audio DSP) | `"processes"` |
| I/O-bound (API calls) | `"threads"` |
| Single-threaded debug | `"synchronous"` |

---

## Environment Management — Pixi

**Replace:** conda `environment.yml` files and pip `requirements.txt`.

**Use:** [Pixi](https://prefix.dev/) with `pixi.toml` for hermetic, reproducible environments.

### Rationale
- Single lock file (`pixi.lock`) captures exact versions for all platforms.
- Supports conda and PyPI packages in the same manifest.
- Defines named tasks (`pixi run test`, `pixi run lint`) — replaces Makefile.
- Faster than conda; compatible with existing conda-forge packages (librosa, etc.).

### pixi.toml Structure

```toml
[project]
name = "catshand"
version = "0.4.0"
channels = ["conda-forge", "defaults"]
platforms = ["osx-arm64", "osx-64", "linux-64", "win-64"]

[dependencies]
python = ">=3.11"
numpy = ">=1.26"
pandas = ">=2.2"
librosa = ">=0.10"
pydub = ">=0.25"
dask = ">=2024.1"

[pypi-dependencies]
catshand = { path = ".", editable = true }
typer = ">=0.12"
pydantic = ">=2.0"
openai = ">=1.13"
tiktoken = ">=0.6"

[feature.dev.dependencies]
pytest = "*"
ruff = "*"
mypy = "*"

[environments]
default = { features = [] }
dev = { features = ["dev"] }

[tasks]
test = "pytest tests/"
lint = "ruff check src/"
fmt = "ruff format src/"
typecheck = "mypy src/"
```

### Common Commands

```bash
pixi install          # create/sync the environment
pixi run test         # run pytest
pixi run lint         # run ruff
pixi run fmt          # format code
pixi run typecheck    # run mypy
pixi shell            # activate shell in environment
```

---

## Summary of Changes from v0.3

| Aspect | v0.3 | v0.4+ |
|---|---|---|
| CLI framework | argparse + click (mixed) | Typer (unified) |
| Config/data models | plain dicts | Pydantic v2 models |
| Parallelism | `multiprocessing` (fork) | Dask delayed/bag |
| Env management | conda YML + requirements.txt | pixi + pixi.toml |
| Python version target | 3.9–3.12 | 3.11+ |
