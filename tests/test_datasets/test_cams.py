"""Unit test for CAMS dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from zampy.datasets.catalog import CAMS
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


class TestCAMS:
    """Test the CAMS class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_cds, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2003-01-02"), np.datetime64("2020-12-31"))
        bbox = SpatialBounds(54, 56, 1, 3)
        variable = ["co2_concentration"]
        cds_var_names = ["carbon_dioxide"]
        download_dir = Path(dummy_dir, "download")

        cams_dataset = CAMS()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.cds_utils.CDSAPI_CONFIG_PATH", valid_path_cds)
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
                "cams_co2_concentration_2003_01-2020_12.nc",
            )
        )

        return ds, cams_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert isinstance(ds, xr.Dataset)

    def test_load(self):
        """Test load function."""
        times = TimeBounds(np.datetime64("1996-01-01"), np.datetime64("1996-01-02"))
        bbox = SpatialBounds(39, -107, 37, -109)
        variable = ["co2_concentration"]

        cams_dataset = CAMS()

        ds = cams_dataset.load(
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
        _, cams_dataset = self.ingest_dummy_data(dummy_dir)
        cams_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.
