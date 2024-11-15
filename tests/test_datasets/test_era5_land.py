"""Unit test for ERA5-land dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from tests import ALL_DAYS
from tests import ALL_HOURS
from tests import data_folder
from zampy.datasets.catalog import ERA5Land
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


@pytest.fixture(scope="function")
def valid_path_config(tmp_path_factory):
    """Create a dummy .zampy_config file."""
    fn = tmp_path_factory.mktemp("usrhome") / "zampy_config.yml"
    with open(fn, mode="w", encoding="utf-8") as f:
        f.write("cdsapi:\n  url: a\n  key: 123:abc-def\n")
        f.write("adsapi:\n  url: a\n  key: 123:abc-def")
    return fn


@pytest.fixture(scope="function")
def dummy_dir(tmp_path_factory):
    """Create a dummpy directory for testing."""
    return tmp_path_factory.mktemp("data")


class TestERA5Land:
    """Test the ERA5Land class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_config, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-02-15"))
        bbox = SpatialBounds(60, 10, 50, 0)
        variable = ["dewpoint_temperature"]
        cds_var_names = ["2m_dewpoint_temperature"]
        download_dir = Path(dummy_dir, "download")

        era5_land_dataset = ERA5Land()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
        with patching:
            era5_land_dataset.download(
                download_dir=download_dir,
                time_bounds=times,
                spatial_bounds=bbox,
                variable_names=variable,
                overwrite=True,
            )

            # make sure that the download is called
            mock_retrieve.assert_called_once_with(
                "reanalysis-era5-land",
                {
                    "product_type": "reanalysis",
                    "variable": cds_var_names,
                    "year": "2020",
                    "month": "1",
                    "day": ALL_DAYS,
                    "time": ALL_HOURS,
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
            with (download_dir / "era5-land" / "properties.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                json_dict = json.load(file)
                # check property
                assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        era5_land_dataset = ERA5Land()
        era5_land_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "era5-land",
                "era5-land_dewpoint_temperature_2020-1.nc",
            )
        )

        return ds, era5_land_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert isinstance(ds, xr.Dataset)

    def test_load(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(60.0, 0.3, 59.7, 0.0)
        variable = ["dewpoint_temperature"]

        era5_land_dataset = ERA5Land()
        era5_land_dataset.ingest(download_dir=data_folder, ingest_dir=Path(dummy_dir))

        ds = era5_land_dataset.load(
            ingest_dir=Path(dummy_dir),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=0.1,
        )

        # we assert the regridded coordinates
        expected_lat = [59.7, 59.8, 59.9]
        expected_lon = [0.0, 0.1, 0.2]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

        # check if valid_time not in the dataset
        assert "valid_time" not in ds.dims

    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, era5_land_dataset = self.ingest_dummy_data(dummy_dir)
        era5_land_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.
