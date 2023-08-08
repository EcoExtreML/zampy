from pathlib import Path
import pytest
from zampy.recipe import config_loader


def test_valid_config(tmp_path: Path, mocker):
    mocker.patch(
        "pathlib.Path.home",
        return_value=tmp_path,
    )
    config_dir = tmp_path / ".config" / "zampy"
    config_dir.mkdir(parents=True)
    valid_config = f"working_directory: {tmp_path}\n"
    with (config_dir / "zampy_config.yml").open("w") as f:
        f.write(valid_config)

    config = config_loader()
    assert config == {"working_directory": str(tmp_path)}


def test_missing_config(tmp_path: Path, mocker):
    mocker.patch(
        "pathlib.Path.home",
        return_value=tmp_path,
    )
    with pytest.raises(FileNotFoundError):
        config_loader()


def test_missing_key(tmp_path: Path, mocker):
    mocker.patch(
        "pathlib.Path.home",
        return_value=tmp_path,
    )
    config_dir = tmp_path / ".config" / "zampy"
    config_dir.mkdir(parents=True)
    with (config_dir / "zampy_config.yml").open("w") as f:
        f.write("nonsense")

    with pytest.raises(ValueError, match="No `working_directory` key"):
        config_loader()
