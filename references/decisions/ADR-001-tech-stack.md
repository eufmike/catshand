# ADR-001: Modernized Tech Stack for v0.4.0

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** Mike Chien-Cheng Shih

---

## Context

Catshand v0.3.6 reached a functional plateau with four technical debts blocking further development:

1. **Two CLI frameworks coexisting** — `main.py` uses `argparse`; `main_dev.py` uses `typer`. Users face inconsistent interfaces and devs must maintain two registration paths per command.
2. **Config as raw dicts** — JSON configs are loaded with `json.load()` into plain dicts. No validation at load time means errors surface as `KeyError` deep in processing code, not at startup.
3. **`multiprocessing` fork hangs** — `mp.set_start_method("fork", force=True)` in `audio2wav.py` causes silent hangs on macOS when librosa/numpy native extensions are active. Several user-reported hangs traced here.
4. **Conda environment fragmentation** — Three divergent `environment.yml` variants in `archive/`; `requirements.txt` is a compiled dump not suitable for direct dev use. Lock files are missing.

---

## Decision

Adopt four targeted replacements:

### 1. CLI: Typer (replaces argparse + click mix)

**Chosen over:** `click` directly, `argparse`.

**Rationale:**
- Derives CLI arguments from Python type annotations — zero boilerplate argument registration.
- `typer.Typer()` instances compose cleanly (each tool registers its own sub-app).
- `main_dev.py` already uses Typer; completing the migration unifies the entry point.
- Click is kept as a transitive dependency (Typer builds on it) but not used directly.

**Trade-off:** Typer < 1.0 has had occasional breaking changes between minor versions. Pin `typer>=0.12`.

### 2. Data Models: Pydantic v2 (replaces plain dicts)

**Chosen over:** `dataclasses`, `attrs`, `TypedDict`.

**Rationale:**
- JSON config files (`config.json`, `audt_config.json`) map directly to Pydantic models with `model_validate_json()`.
- Field validators catch bad values at load time with clear error messages.
- `model_json_schema()` auto-generates config documentation.
- Pydantic v2 is significantly faster than v1 (Rust core).

**Trade-off:** Pydantic v2 API differs from v1 (`validator` → `field_validator`, `__root__` → custom root model). Not an issue since there are no existing Pydantic models in the codebase.

### 3. Parallelism: Dask (replaces multiprocessing fork)

**Chosen over:** `concurrent.futures`, `joblib`, `ray`.

**Rationale:**
- `dask.delayed` is a minimal-invasive decorator that replaces `mp.Pool.apply_async` call sites.
- `scheduler="processes"` uses spawn, not fork — eliminates the macOS hang.
- `scheduler="synchronous"` makes tests deterministic without code changes.
- Dask bag is idiomatic for the "list of audio files → list of results" pattern that appears in every tool.
- Lighter than Ray for single-machine use; more capable than `joblib` (distributed path open).

**Trade-off:** Dask adds ~50 MB to the environment. Acceptable given librosa/numpy are already large.

### 4. Environment: Pixi (replaces conda YML + requirements.txt)

**Chosen over:** conda + pip, poetry, uv.

**Rationale:**
- Single `pixi.toml` replaces three divergent `environment.yml` files.
- `pixi.lock` captures exact versions for all platforms in one file — reproducible across Mac/Linux.
- Supports both conda-forge packages (librosa, numpy) and PyPI packages in one manifest.
- Named tasks (`pixi run test`, `pixi run lint`) replace ad-hoc shell commands.
- Faster than conda for solves; `pixi install` works offline from the lock file.

**Trade-off:** Pixi is newer than conda (~2023); tooling integrations (IDEs, CI) are maturing. The lock file format is not conda-lock compatible.

---

## Consequences

- `main.py` (argparse) is kept as a legacy entry point (`catshand` CLI) but receives no new commands. All new development targets `main_dev.py` (Typer, `catshand_dev` CLI).
- Each tool in `tools/` will expose a `typer.Typer()` app and a standalone `main(**kwargs)` function (callable from tests without CLI parsing).
- A new `src/catshand/models.py` holds all Pydantic models shared across tools.
- `multiprocessing` import in `audio2wav.py` will be removed; replaced with `dask.delayed`.
- `archive/environment*.yml` files are retained for historical reference but deprecated.
- CI/CD should use `pixi install --frozen` to reproduce the locked environment.
