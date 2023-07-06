"""Unit test for regridding."""

from pathlib import Path
import numpy as np
import pytest
from zampy.datasets import EthCanopyHeight
from zampy.datasets import converter
from zampy.datasets.eth_canopy_height import parse_tiff_file


path_dummy_data = Path(__file__).resolve().parent / "test_data" / "eth-canopy-height"

# ruff: noqa: B018 (protected-access)


def test_check_convention_not_support():
    convention = "fake_convention"
    with pytest.raises(ValueError, match="not supported"):
        converter.check_convention(convention)


def test_check_convention_not_exist():
    convention = Path("fake_path")
    with pytest.raises(FileNotFoundError, match="could not be found"):
        converter.check_convention(convention)


def test_convert():
    ds = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    ds_convert = converter.convert(
        data=ds, dataset=EthCanopyHeight(), convention="ALMA"
    )

    assert list(ds_convert.data_vars)[0] == "Hveg"


def test_convert_var():
    ds = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    ds_convert = converter._convert_var(ds, "height_of_vegetation", "decimeter")

    assert np.allclose(
        ds_convert["height_of_vegetation"].values,
        ds["height_of_vegetation"].values * 10.0,
        equal_nan=True,
    )
