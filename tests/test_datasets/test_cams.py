"""Unit test for CAMS dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from tests import data_folder
from zampy.datasets.catalog import CAMS
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


class TestCAMS:
    """Test the CAMS class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_config, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2003-01-02"), np.datetime64("2003-01-04"))
        bbox = SpatialBounds(60, 10, 50, 0)
        variable = ["co2_concentration"]
        cds_var_names = ["carbon_dioxide"]
        download_dir = Path(dummy_dir, "download")

        cams_dataset = CAMS()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
        with patching:
            cams_dataset.download(
                download_dir=download_dir,
                time_bounds=times,
                spatial_bounds=bbox,
                variable_names=variable,
                overwrite=True,
            )

            # make sure that the download is called
            mock_retrieve.assert_called_once_with(
                "cams-global-ghg-reanalysis-egg4",
                {
                    "model_level": "60",
                    "variable": cds_var_names,
                    "date": f"{str(times.start)}/{str(times.end)}",
                    "step": ["0", "3", "6", "9", "12", "15", "18", "21"],
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
            with (download_dir / "cams" / "properties.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                json_dict = json.load(file)
                # check property
                assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        cams_dataset = CAMS()
        cams_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "cams",
                "cams_co2_concentration_2020_01_01-2020_02_15.nc",
            )
        )

        return ds, cams_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert isinstance(ds, xr.Dataset)

    def test_load(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(59.75, 2.25, 57.5, 0)
        variable = ["co2_concentration"]

        cams_dataset = CAMS()
        cams_dataset.ingest(download_dir=data_folder, ingest_dir=Path(dummy_dir))

        ds = cams_dataset.load(
            ingest_dir=Path(dummy_dir),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=1.0,
        )

        # we assert the regridded coordinates
        expected_lat = [57.5, 58.5, 59.5]
        expected_lon = [0.0, 1.0, 2.0]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, cams_dataset = self.ingest_dummy_data(dummy_dir)
        cams_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.
