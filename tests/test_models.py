import pytest
from pydantic import ValidationError

from catshand.models import (
    AudacityConfig,
    AudtMaterial,
    Audio2WavOptions,
    ProjectConfig,
)


class TestProjectConfig:
    def test_valid(self):
        cfg = ProjectConfig(
            project_name="EP028",
            hosts=["Mike", "Robin"],
            guests=["Alice"],
        )
        assert cfg.project_name == "EP028"
        assert len(cfg.hosts) == 2

    def test_default_guests_empty(self):
        cfg = ProjectConfig(project_name="EP028", hosts=["Mike"])
        assert cfg.guests == []

    def test_empty_hosts_raises(self):
        with pytest.raises(ValidationError, match="at least one host"):
            ProjectConfig(project_name="EP028", hosts=[])

    def test_empty_project_name_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            ProjectConfig(project_name="   ", hosts=["Mike"])

    def test_roundtrip_json(self):
        cfg = ProjectConfig(project_name="EP001", hosts=["HWC"], guests=["Guest1"])
        restored = ProjectConfig.model_validate_json(cfg.model_dump_json())
        assert restored == cfg


class TestAudacityConfig:
    def _valid_material(self, **kwargs):
        defaults = dict(
            opmusic_path="op.wav",
            endmusic_path="end.wav",
            endcredit_path="endcredit.wav",
            transition_path="transition/",
            root="/data/materials",
        )
        defaults.update(kwargs)
        return AudtMaterial(**defaults)

    def test_valid(self):
        cfg = AudacityConfig(material=self._valid_material())
        assert cfg.track_height == 80

    def test_missing_root_raises(self):
        with pytest.raises(ValidationError, match="material.root"):
            AudacityConfig(material=self._valid_material(root=""))

    def test_defaults(self):
        cfg = AudacityConfig(material=self._valid_material())
        assert cfg.track_offset == 29.6
        assert cfg.endmusic_offset == -4.0


class TestAudio2WavOptions:
    def test_valid(self, tmp_path):
        opts = Audio2WavOptions(prj_dir=tmp_path)
        assert opts.bitrate == 32000
        assert opts.threads == 1

    def test_bitrate_zero_raises(self, tmp_path):
        with pytest.raises(ValidationError, match="bitrate must be positive"):
            Audio2WavOptions(prj_dir=tmp_path, bitrate=0)

    def test_threads_zero_raises(self, tmp_path):
        with pytest.raises(ValidationError, match="threads must be"):
            Audio2WavOptions(prj_dir=tmp_path, threads=0)
