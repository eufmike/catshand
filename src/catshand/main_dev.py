"""Catshand CLI (v0.4.0+) — Typer-based entry point.

All subcommands are registered here. Business logic lives in the
individual tools/ modules, each of which exposes a main(**kwargs) function.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer

app = typer.Typer(
    name="catshand",
    help=(
        "Cat's Hand (猫の手も借りたい) — podcast audio editing toolbox. "
        "Automates pre- and post-editing workflows for Tripod Cat's Podcast."
    ),
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# prjinit — project initialization
# ---------------------------------------------------------------------------
@app.command()
def prjinit(
    root_dir: Annotated[
        Path,
        typer.Option("--root-dir", "-d", help="Parent directory for the project folder"),
    ],
    project_name: Annotated[
        str,
        typer.Option("--project-name", "-n", help="Project name, e.g. EP028"),
    ],
    material_dir: Annotated[
        Optional[Path],
        typer.Option("--material-dir", "-m", help="Material folder (default: <project>/material)"),
    ] = None,
) -> None:
    """Initialize a new podcast project folder."""
    from catshand.tools import prjinit as _prjinit

    _prjinit.main(rootdir=root_dir, prj_n=project_name, mat_dir=material_dir)


# ---------------------------------------------------------------------------
# audio2wav — audio format conversion + normalization
# ---------------------------------------------------------------------------
@app.command()
def audio2wav(
    prj_dir: Annotated[
        Path,
        typer.Option("--prj-dir", "-p", help="Project directory"),
    ],
    input_dir: Annotated[
        Optional[Path],
        typer.Option("--input-dir", "-i", help="Source audio folder (default: <prj>/00_Raw)"),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output-dir", "-o", help="Output folder (default: <prj>/<input>_wav)"),
    ] = None,
    bitrate: Annotated[int, typer.Option(help="WAV bitrate")] = 32000,
    match_name: Annotated[
        bool, typer.Option("--match-name", "-m", help="Fuzzy-match filenames to host/guest names")
    ] = False,
    compressor: Annotated[bool, typer.Option("-c", help="Apply dynamic range compressor")] = False,
    loudness: Annotated[bool, typer.Option("-l", help="Apply loudness normalization")] = False,
    noisereduce: Annotated[bool, typer.Option("-r", help="Apply noise reduction")] = False,
    finetune: Annotated[bool, typer.Option(help="Export pre-effect WAV for comparison")] = False,
    threads: Annotated[int, typer.Option("-t", help="Parallel worker count")] = 1,
) -> None:
    """Convert audio files to WAV with optional DSP effects."""
    from catshand.tools import audio2wav as _audio2wav

    _audio2wav.main(
        prj_dir=prj_dir,
        input_dir=input_dir,
        output_dir=output_dir,
        bitrate=bitrate,
        match_name=match_name,
        compressor=compressor,
        loudness=loudness,
        noisereduce=noisereduce,
        finetune=finetune,
        threads=threads,
    )


# ---------------------------------------------------------------------------
# silrm — silence removal
# ---------------------------------------------------------------------------
@app.command()
def silrm(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p", help="Project directory")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("-o")] = None,
    threads: Annotated[int, typer.Option("-t")] = 1,
) -> None:
    """Remove silence from audio tracks."""
    from catshand.tools import silrm as _silrm

    _silrm.main(
        prj_dir=prj_dir,
        input_dir=input_dir,
        output_dir=output_dir,
        threads=threads,
    )


# ---------------------------------------------------------------------------
# audiosplit — split audio at timestamps
# ---------------------------------------------------------------------------
@app.command()
def audiosplit(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("-o")] = None,
) -> None:
    """Split audio files at specified timestamp markers."""
    from catshand.tools import audiosplit as _audiosplit

    _audiosplit.main(prj_dir=prj_dir, input_dir=input_dir, output_dir=output_dir)


# ---------------------------------------------------------------------------
# trackmerger — merge multi-track audio
# ---------------------------------------------------------------------------
@app.command()
def trackmerger(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("-o")] = None,
    stereo: Annotated[bool, typer.Option(help="Convert to stereo")] = True,
    volume_adj: Annotated[Optional[str], typer.Option("-v", help="Volume adjustments (comma-separated dB)")] = None,
) -> None:
    """Merge multiple host audio tracks into one."""
    from catshand.tools import trackmerger as _trackmerger

    volume_list = [x.strip() for x in volume_adj.split(",")] if volume_adj else None
    _trackmerger.main(
        prj_dir=prj_dir,
        input_dir=input_dir,
        output_dir=output_dir,
        stereo=stereo,
        volume_adj=volume_list,
    )


# ---------------------------------------------------------------------------
# audmerger — audio merge with spatial metadata
# ---------------------------------------------------------------------------
@app.command()
def audmerger(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("-o")] = None,
) -> None:
    """Merge tracks with spatial audio metadata."""
    from catshand.tools import audmerger as _audmerger

    _audmerger.main(prj_dir=prj_dir, input_dir=input_dir, output_dir=output_dir)


# ---------------------------------------------------------------------------
# audacitypipe — Audacity automation
# ---------------------------------------------------------------------------
@app.command()
def audacitypipe(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
) -> None:
    """Automate Audacity post-processing via named pipe (requires Audacity 3.6.1)."""
    from catshand.tools import audacitypipe as _audacitypipe

    _audacitypipe.main(prj_dir=prj_dir)


# ---------------------------------------------------------------------------
# prjsummary — transcription + summarization
# ---------------------------------------------------------------------------
@app.command()
def prjsummary(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    language: Annotated[str, typer.Option("--language", help="Whisper language code (e.g. zh, en)")] = "auto",
    threads: Annotated[int, typer.Option("-t")] = 1,
) -> None:
    """Transcribe and summarize a podcast project using OpenAI Whisper."""
    from catshand.tools import prjsummary as _prjsummary

    _prjsummary.main(
        prj_dir=prj_dir,
        input_dir=input_dir,
        language=language,
        threads=threads,
    )


# ---------------------------------------------------------------------------
# linkparser — parse links from episode notes
# ---------------------------------------------------------------------------
@app.command()
def linkparser(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
) -> None:
    """Parse and validate links from episode show notes."""
    from catshand.tools import linkparser as _linkparser

    _linkparser.main(prj_dir=prj_dir)


# ---------------------------------------------------------------------------
# cleanvoice — voice cleaning
# ---------------------------------------------------------------------------
@app.command()
def cleanvoice(
    prj_dir: Annotated[Path, typer.Option("--prj-dir", "-p")],
    input_dir: Annotated[Optional[Path], typer.Option("-i")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("-o")] = None,
) -> None:
    """Apply voice cleaning to audio tracks."""
    from catshand.tools import cleanvoice as _cleanvoice

    _cleanvoice.main(prj_dir=prj_dir, input_dir=input_dir, output_dir=output_dir)


if __name__ == "__main__":
    app()
