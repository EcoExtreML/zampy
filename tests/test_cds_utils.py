"""Unit test for cds utils functions."""

from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import cds_utils
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from . import ALL_DAYS
from . import ALL_HOURS
from . import data_folder


@pytest.fixture(scope="function")
def valid_path_config(tmp_path_factory):
    """Create a dummy .zampy_config file."""
    fn = tmp_path_factory.mktemp("usrhome") / "zampy_config.yml"
    with open(fn, mode="w", encoding="utf-8") as f:
        f.write("cdsapi:\n  url: a\n  key: 123:abc-def\n")
        f.write("adsapi:\n  url: a\n  key: 123:abc-def")
    return fn


@patch("cdsapi.Client.retrieve")
def test_cds_request_era5(mock_retrieve, valid_path_config):
    """ "Test cds request for downloading data from CDS server."""
    product = "reanalysis-era5-single-levels"
    variables = ["eastward_component_of_wind"]
    cds_var_names = {"eastward_component_of_wind": "10m_u_component_of_wind"}
    time_bounds = TimeBounds(
        np.datetime64("2010-01-01T00:00:00"), np.datetime64("2010-01-31T23:00:00")
    )
    spatial_bounds = SpatialBounds(54, 56, 1, 3)
    path = Path(__file__).resolve().parent
    overwrite = True

    # create a dummy .cdsapirc
    patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
    with patching:
        cds_utils.cds_request(
            product,
            variables,
            time_bounds,
            spatial_bounds,
            path,
            cds_var_names,
            overwrite,
        )

        mock_retrieve.assert_called_with(
            product,
            {
                "product_type": "reanalysis",
                "variable": ["10m_u_component_of_wind"],
                "year": "2010",
                "month": "1",
                "day": ALL_DAYS,
                "time": ALL_HOURS,
                "area": [
                    spatial_bounds.north,
                    spatial_bounds.west,
                    spatial_bounds.south,
                    spatial_bounds.east,
                ],
                "format": "netcdf",
            },
        )


@patch("cdsapi.Client.retrieve")
def test_cds_request_cams_co2(mock_retrieve, valid_path_config):
    """ "Test cds request for downloading data from CDS server."""
    product = "cams-global-ghg-reanalysis-egg4"
    variables = ["co2_concentration"]
    cds_var_names = {"co2_concentration": "carbon_dioxide"}
    time_bounds = TimeBounds(
        np.datetime64("2003-01-02T00:00:00"), np.datetime64("2003-01-04T00:00:00")
    )
    spatial_bounds = SpatialBounds(54, 56, 1, 3)
    path = Path(__file__).resolve().parent
    overwrite = True

    # create a dummy .cdsapirc
    patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
    with patching:
        cds_utils.cds_request(
            product,
            variables,
            time_bounds,
            spatial_bounds,
            path,
            cds_var_names,
            overwrite,
        )

        mock_retrieve.assert_called_with(
            product,
            {
                "model_level": "60",
                "variable": [cds_var_names["co2_concentration"]],
                "date": "2003-01-02/2003-01-04",
                "step": ["0", "3", "6", "9", "12", "15", "18", "21"],
                "area": [
                    spatial_bounds.north,
                    spatial_bounds.west,
                    spatial_bounds.south,
                    spatial_bounds.east,
                ],
                "format": "netcdf",
            },
        )


@patch("cdsapi.Client.retrieve")
def test_cds_request_land_cover(mock_retrieve, valid_path_config):
    """ "Test cds request for downloading data from CDS server."""
    dataset = "satellite-land-cover"
    time_bounds = TimeBounds(
        np.datetime64("2020-01-01T00:00:00"), np.datetime64("2020-12-31T00:00:00")
    )
    path = Path(__file__).resolve().parent
    overwrite = True

    # create a dummy .cdsapirc
    patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
    with patching:
        cds_utils.cds_request_land_cover(
            dataset,
            time_bounds,
            path,
            SpatialBounds(54, 56, 1, 3),
            overwrite,
        )

    mock_retrieve.assert_called_with(
        dataset,
        {
            "variable": "all",
            "format": "zip",
            "year": "2020",
            "version": "v2_1_1",
            "area": [54, 3, 1, 56],
        },
    )


def test_cds_api_key_config_exist(valid_path_config):
    """Test zampy config exists."""
    patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
    with patching:
        url, api_key = cds_utils.cds_api_key("era5")
        assert url == "a"
        assert api_key == "123:abc-def"


def test_cds_api_key_config_apikey_not_exist(tmp_path_factory):
    """Test zampy config exists but the required api key is missing."""
    fn = tmp_path_factory.mktemp("usrhome") / "zampy_config.yml"
    with open(fn, mode="w", encoding="utf-8") as f:
        f.write("wrong_key:\n")
    patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", fn)
    with patching:
        with pytest.raises(KeyError, match="No cdsapi key was found at"):
            cds_utils.cds_api_key("era5")


def test_time_bounds_to_year_month():
    """Test year and month pair converter function."""
    times = TimeBounds(np.datetime64("2010-01-01"), np.datetime64("2010-01-31"))
    expected = [("2010", "1")]
    year_month_pairs = cds_utils.time_bounds_to_year_month(times)
    assert expected == year_month_pairs


@pytest.fixture(scope="function")
def dummy_dir(tmp_path_factory):
    """Create a dummpy directory for testing."""
    return tmp_path_factory.mktemp("data")


def test_convert_to_zampy(dummy_dir):
    """Test function for converting file to zampy format."""
    ingest_folder = Path(data_folder, "era5")
    cds_utils.convert_to_zampy(
        ingest_folder=Path(dummy_dir),
        file=Path(ingest_folder, "era5_northward_component_of_wind_2020-1.nc"),
        overwrite=True,
    )

    ds = xr.open_dataset(Path(dummy_dir, "era5_northward_component_of_wind_2020-1.nc"))

    assert list(ds.data_vars)[0] == "northward_component_of_wind"


class TestParser:
    """Test parsing netcdf files for all relevant variables."""

    def test_parse_nc_file_10m_wind(self):
        """Test parsing netcdf file function with 10 meter velocity u/v component."""
        variables = ["northward_component_of_wind", "eastward_component_of_wind"]
        for variable in variables:
            ds = cds_utils.parse_nc_file(
                data_folder / "era5" / f"era5_{variable}_2020-1.nc"
            )
            expected_var_name = variable
            assert list(ds.data_vars)[0] == expected_var_name
            assert ds[expected_var_name].attrs["units"] == "meter_per_second"

    def test_parse_nc_file_radiation(self):
        """Test parsing netcdf file function with surface radiation."""
        variables = {
            "surface_thermal_radiation_downwards": "strd",
            "surface_solar_radiation_downwards": "ssrd",
        }
        for variable in variables:
            ds_original = xr.open_dataset(
                data_folder / "era5" / f"era5_{variable}_2020-1.nc"
            )
            ds = cds_utils.parse_nc_file(
                data_folder / "era5" / f"era5_{variable}_2020-1.nc"
            )

            assert list(ds.data_vars)[0] == variable
            assert ds[variable].attrs["units"] == "watt_per_square_meter"
            assert np.allclose(
                ds_original[variables[variable]].values,
                ds[variable].values * 3600,
                equal_nan=True,
            )

    def test_parse_nc_file_precipitation(self):
        """Test parsing netcdf file function with precipitation."""
        ds_original = xr.open_dataset(
            data_folder / "era5" / "era5_total_precipitation_2020-1.nc"
        )
        ds = cds_utils.parse_nc_file(
            data_folder / "era5" / "era5_total_precipitation_2020-1.nc"
        )
        expected_var_name = "total_precipitation"

        assert list(ds.data_vars)[0] == expected_var_name
        assert ds["total_precipitation"].attrs["units"] == "millimeter_per_second"
        assert np.allclose(
            ds_original["mtpr"].values,
            ds["total_precipitation"].values * cds_utils.WATER_DENSITY / 1000,
            equal_nan=True,
        )

    def test_parse_nc_file_pressure(self):
        """Test parsing netcdf file function with surface pressure."""
        ds = cds_utils.parse_nc_file(
            data_folder / "era5" / "era5_surface_pressure_2020-1.nc"
        )
        expected_var_name = "surface_pressure"

        assert list(ds.data_vars)[0] == expected_var_name
        assert ds["surface_pressure"].attrs["units"] == "pascal"

    def test_parse_nc_file_air_temperature(self):
        """Test parsing netcdf file function with 2 meter temperature."""
        ds = cds_utils.parse_nc_file(
            data_folder / "era5-land" / "era5-land_air_temperature_2020-1.nc"
        )
        expected_var_name = "air_temperature"

        assert list(ds.data_vars)[0] == expected_var_name
        assert ds["air_temperature"].attrs["units"] == "kelvin"

    def test_parse_nc_file_dew_temperature(self):
        """Test parsing netcdf file function with 2 meter dewpoint temperature."""
        ds = cds_utils.parse_nc_file(
            data_folder / "era5-land" / "era5-land_dewpoint_temperature_2020-1.nc"
        )
        expected_var_name = "dewpoint_temperature"

        assert list(ds.data_vars)[0] == expected_var_name
        assert ds["dewpoint_temperature"].attrs["units"] == "kelvin"

    def test_parse_nc_file_co2_concentration(self):
        """Test parsing netcdf file function with co2 concentration."""
        ds = cds_utils.parse_nc_file(
            data_folder / "cams" / "cams_co2_concentration_2020_01_01-2020_02_15.nc"
        )
        expected_var_name = "co2_concentration"

        assert list(ds.data_vars)[0] == expected_var_name
        assert ds["co2_concentration"].attrs["units"] == "fraction"
