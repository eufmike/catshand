"""Pydantic v2 models for catshand configuration and data structures."""

from pathlib import Path

from pydantic import BaseModel, field_validator, model_validator


class ProjectConfig(BaseModel):
    """Schema for <project>/config/config.json."""

    project_name: str
    hosts: list[str]
    guests: list[str] = []

    @field_validator("hosts")
    @classmethod
    def at_least_one_host(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Project must have at least one host")
        return v

    @field_validator("project_name")
    @classmethod
    def project_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("project_name must not be empty")
        return v


class AudtMaterial(BaseModel):
    """Material paths within audt_config.json."""

    opmusic_path: str
    endmusic_path: str
    endcredit_path: str
    transition_path: str
    root: str = ""


class AudacityConfig(BaseModel):
    """Schema for <project>/config/audt_config.json."""

    track_height: int = 80
    track_offset: float = 29.6
    highlight_offset: float = 10.0
    endcredt_offset: float = 9.2
    endmusic_offset: float = -4.0
    material: AudtMaterial

    @model_validator(mode="after")
    def material_root_set(self) -> "AudacityConfig":
        if not self.material.root:
            raise ValueError(
                "audt_config.json must have material.root set to the materials directory"
            )
        return self


class Audio2WavOptions(BaseModel):
    """Runtime options for the audio2wav tool."""

    prj_dir: Path
    input_dir: Path | None = None
    output_dir: Path | None = None
    bitrate: int = 32000
    match_name: bool = False
    compressor: bool = False
    loudness: bool = False
    noisereduce: bool = False
    finetune: bool = False
    threads: int = 1

    @field_validator("bitrate")
    @classmethod
    def bitrate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"bitrate must be positive, got {v}")
        return v

    @field_validator("threads")
    @classmethod
    def threads_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"threads must be >= 1, got {v}")
        return v


class SilenceRemovalOptions(BaseModel):
    """Runtime options for the silrm tool."""

    prj_dir: Path
    input_dir: Path | None = None
    output_dir: Path | None = None
    min_silence_len: int = 500
    silence_thresh: int = -50
    threads: int = 1


class TrackMergerOptions(BaseModel):
    """Runtime options for the trackmerger tool."""

    prj_dir: Path
    input_dir: Path | None = None
    output_dir: Path | None = None
    stereo: bool = True
