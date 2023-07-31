"""Unit test for ERA5 dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import era5
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from . import data_folder


@pytest.fixture(scope="function")
def valid_path_cds(tmp_path_factory):
    """Create a dummy .cdsapirc file."""
    fn = tmp_path_factory.mktemp("usrhome") / ".cdsapirc"
    with open(fn, mode="w", encoding="utf-8") as f:
        f.write("url: a\nkey: 123:abc-def")
    return fn


@pytest.fixture(scope="function")
def dummy_dir(tmp_path_factory):
    """Create a dummpy directory for testing."""
    return tmp_path_factory.mktemp("data")


class TestERA5:
    """Test the ERA5 class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_cds, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2010-01-01"), np.datetime64("2010-01-31"))
        bbox = SpatialBounds(54, 56, 1, 3)
        variable = ["10m_v_component_of_wind"]
        download_dir = Path(dummy_dir, "download")

        era5_dataset = era5.ERA5()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.utils.CDSAPI_CONFIG_PATH", valid_path_cds)
        with patching:
            era5_dataset.download(
                download_dir=download_dir,
                time_bounds=times,
                spatial_bounds=bbox,
                variable_names=variable,
                overwrite=True,
            )

            # make sure that the download is called
            mock_retrieve.assert_called_once_with(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "variable": variable,
                    "year": "2010",
                    "month": "1",
                    # fmt: off
                "day": [
                    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                    "31",
                ],
                "time": [
                    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00",
                    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
                    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                    "21:00", "22:00", "23:00",
                ],
                    # fmt: on
                    "area": [
                        bbox.north,
                        bbox.west,
                        bbox.south,
                        bbox.east,
                    ],
                    "format": "netcdf",
                },
            )

            # check property file
            with (download_dir / "era5" / "properties.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                json_dict = json.load(file)
                # check property
                assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        era5_dataset = era5.ERA5()
        era5_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "era5",
                "era5_10m_v_component_of_wind_1996-1.nc",
            )
        )

        return ds, era5_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert type(ds) == xr.Dataset

    def test_load(self):
        """Test load function."""
        times = TimeBounds(np.datetime64("1996-01-01"), np.datetime64("1996-01-02"))
        bbox = SpatialBounds(39, -107, 37, -109)
        variable = ["10m_v_component_of_wind"]

        era5_dataset = era5.ERA5()

        ds = era5_dataset.load(
            ingest_dir=Path(data_folder),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=1.0,
            regrid_method="flox",
        )

        # we assert the regridded coordinates
        expected_lat = [37.0, 38.0, 39.0]
        expected_lon = [-109.0, -108.0, -107.0]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, era5_dataset = self.ingest_dummy_data(dummy_dir)
        era5_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.


def test_convert_to_zampy(dummy_dir):
    """Test function for converting file to zampy format."""
    ingest_folder = Path(data_folder, "era5")
    era5.convert_to_zampy(
        ingest_folder=Path(dummy_dir),
        file=Path(ingest_folder, "era5_10m_v_component_of_wind_1996-1.nc"),
        overwrite=True,
    )

    ds = xr.load_dataset(Path(dummy_dir, "era5_10m_v_component_of_wind_1996-1.nc"))

    assert list(ds.data_vars)[0] == "northward_component_of_wind"


def test_parse_nc_file_10m_wind():
    """Test parsing netcdf file function with 10 meter velocity u/v component."""
    variables = {
        "10m_v_component_of_wind": "northward_component_of_wind",
        "10m_u_component_of_wind": "eastward_component_of_wind",
    }
    for variable in variables:
        ds = era5.parse_nc_file(data_folder / "era5" / f"era5_{variable}_1996-1.nc")
        expected_var_name = variables[variable]
        assert list(ds.data_vars)[0] == expected_var_name
        assert ds[expected_var_name].attrs["units"] == "meter_per_second"


def test_parse_nc_file_radiation():
    """Test parsing netcdf file function with surface radiation."""
    variables = {
        "surface_thermal_radiation_downwards": "strd",
        "surface_solar_radiation_downwards": "ssrd",
    }
    for variable in variables:
        ds_original = xr.load_dataset(
            data_folder / "era5" / f"era5_{variable}_1996-1.nc"
        )
        ds = era5.parse_nc_file(data_folder / "era5" / f"era5_{variable}_1996-1.nc")

        assert list(ds.data_vars)[0] == variable
        assert ds[variable].attrs["units"] == "watt_per_square_meter"
        assert np.allclose(
            ds_original[variables[variable]].values,
            ds[variable].values * 3600,
            equal_nan=True,
        )


def test_parse_nc_file_precipitation():
    """Test parsing netcdf file function with precipitation."""
    ds_original = xr.load_dataset(
        data_folder / "era5" / "era5_mean_total_precipitation_rate_1996-1.nc"
    )
    ds = era5.parse_nc_file(
        data_folder / "era5" / "era5_mean_total_precipitation_rate_1996-1.nc"
    )
    expected_var_name = "total_precipitation"

    assert list(ds.data_vars)[0] == expected_var_name
    assert ds["total_precipitation"].attrs["units"] == "millimeter_per_second"
    assert np.allclose(
        ds_original["mtpr"].values,
        ds["total_precipitation"].values * era5.WATER_DENSITY / 1000,
        equal_nan=True,
    )


def test_parse_nc_file_pressure():
    """Test parsing netcdf file function with surface pressure."""
    ds = era5.parse_nc_file(data_folder / "era5" / "era5_surface_pressure_1996-1.nc")
    expected_var_name = "surface_pressure"

    assert list(ds.data_vars)[0] == expected_var_name
    assert ds["surface_pressure"].attrs["units"] == "pascal"
