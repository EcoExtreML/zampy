"""Unit tests for the FAPAR-LAI dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from tests import data_folder
from zampy.datasets.catalog import FaparLAI
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


class TestFaparLAI:
    """Test the FaparLAI class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_config, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-31"))
        bbox = SpatialBounds(60, 10, 50, 0)
        variable = ["leaf_area_index"]
        download_dir = Path(dummy_dir, "download")

        lai_dataset = FaparLAI()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
        with patching:
            lai_dataset.download(
                download_dir=download_dir,
                time_bounds=times,
                spatial_bounds=bbox,
                variable_names=variable,
                overwrite=True,
            )

            # make sure that the download is called
            mock_retrieve.assert_called_once_with(
                "satellite-lai-fapar",
                {
                    "format": "zip",
                    "variable": "lai",
                    "horizontal_resolution": "1km",
                    "product_version": "v3",
                    "satellite": "proba",
                    "sensor": "vgt",
                    "month": "01",
                    "nominal_day": ["10", "20", "31"],
                    "year": "2020",
                    "area": [
                        bbox.north,
                        bbox.west,
                        bbox.south,
                        bbox.east,
                    ],
                },
            )

            # check property file
            with (download_dir / "fapar-lai" / "properties.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                json_dict = json.load(file)
                # check property
                assert json_dict["variable_names"] == variable

    def test_ingest(self, dummy_dir):
        """Test ingest function."""

        lai_dataset = FaparLAI()
        lai_dataset.ingest(
            download_dir=data_folder, ingest_dir=dummy_dir
        )

        ds = xr.open_mfdataset((dummy_dir / "fapar-lai").glob("*.nc"))
        assert isinstance(ds, xr.Dataset)

    def test_load(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(60.0, 0.3, 59.7, 0.0)
        variable = ["leaf_area_index"]

        lai_dataset = FaparLAI()
        lai_dataset.ingest(
            download_dir=data_folder, ingest_dir=dummy_dir
        )

        ds = lai_dataset.load(
            ingest_dir=dummy_dir,
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=0.1,
        )

        # we assert the regridded coordinates
        expected_lat = [59.7, 59.8, 59.9]
        expected_lon = [0.0 , 0.1, 0.2]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    @pytest.mark.slow  # depends on ingested data being available
    def test_convert(self):
        """Test convert function."""
        lai_dataset = FaparLAI()
        lai_dataset.convert(
            ingest_dir=data_folder / "fapar-lai" / "ingest", convention="ALMA"
        )
