"""Unit test for converter."""

from pathlib import Path
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import converter
from zampy.datasets.catalog import EthCanopyHeight
from zampy.datasets.eth_canopy_height import parse_tiff_file
from . import data_folder


path_dummy_data = data_folder / "eth-canopy-height"

# ruff: noqa: B018


def test_check_convention_not_support():
    convention = "fake_convention"
    with pytest.raises(ValueError, match="not supported"):
        converter.check_convention(convention)


def test_check_convention_not_exist():
    convention = Path("fake_path")
    with pytest.raises(FileNotFoundError, match="could not be found"):
        converter.check_convention(convention)


def test_convert_var():
    """Test _convert_var function."""
    ds = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    ds_convert = converter._convert_var(ds, "height_of_vegetation", "decimeter")

    assert np.allclose(
        ds_convert["height_of_vegetation"].values,
        ds["height_of_vegetation"].values * 10.0,
        equal_nan=True,
    )


def test_convert_var_name():
    """Test convert function.

    In this test, no unit-conversion is performed. Only the variable name is updated.
    """
    ds = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    ds_convert = converter.convert(
        data=ds, dataset=EthCanopyHeight(), convention="ALMA"
    )

    assert list(ds_convert.data_vars)[0] == "Hveg"


def test_convert_unit():
    """Test convert function.

    In this test, unit conversion is performed.
    """
    ds = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    ds["height_of_vegetation"].attrs["units"] = "decimeter"
    ds_convert = converter.convert(
        data=ds, dataset=EthCanopyHeight(), convention="ALMA"
    )

    assert np.allclose(
        ds_convert["Hveg"].values,
        ds["height_of_vegetation"].values / 10.0,
        equal_nan=True,
    )


def test_convert_no_conversion():
    """Test convert function.

    In this test, no conversion is performed. The input will be returned without change.
    """
    dummy_ds = xr.Dataset(
        data_vars=dict(
            temperature=(
                ["latitude", "longitude"],
                np.random.randn(1, 2),
                {"units": "Celsius"},
            ),
        ),
        coords=dict(
            lon=(["longitude"], [110, 111]),
            lat=(["latitude"], [20]),
        ),
        attrs=dict(units="Weather dataset."),
    )

    ds_convert = converter.convert(
        data=dummy_ds, dataset=EthCanopyHeight(), convention="ALMA"
    )

    assert list(ds_convert.data_vars)[0] == "temperature"
