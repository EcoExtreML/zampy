"""Unit tests for the FAPAR-LAI dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import dask.distributed
import numpy as np
import pytest
import xarray as xr
from zampy.datasets.catalog import FaparLAI
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from . import data_folder


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
        times = TimeBounds(np.datetime64("2019-01-01"), np.datetime64("2019-01-31"))
        bbox = SpatialBounds(54, 56, 1, 3)
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
                    "year": "2019",
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

    @pytest.mark.slow
    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        dask.distributed.Client()

        ingest_dir = Path(dummy_dir) / "ingest"
        ingest_dir.mkdir()

        lai_dataset = FaparLAI()
        lai_dataset.ingest(
            download_dir=data_folder / "fapar-lai" / "download", ingest_dir=ingest_dir
        )

        with xr.open_mfdataset((ingest_dir / "fapar-lai").glob("*.nc")) as ds:
            assert isinstance(ds, xr.Dataset)

    @pytest.mark.slow  # depends on ingested data being available
    def test_load(self):
        """Test load function."""
        times = TimeBounds(np.datetime64("2019-01-01"), np.datetime64("2019-01-31"))
        bbox = SpatialBounds(39, -107, 37, -109)
        variable = ["leaf_area_index"]

        lai_dataset = FaparLAI()

        ds = lai_dataset.load(
            ingest_dir=data_folder / "fapar-lai" / "ingest",
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=1.0,
        )

        # we assert the regridded coordinates
        expected_lat = [37.0, 38.0, 39.0]
        expected_lon = [-109.0, -108.0, -107.0]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    @pytest.mark.slow  # depends on ingested data being available
    def test_convert(self):
        """Test convert function."""
        lai_dataset = FaparLAI()
        lai_dataset.convert(
            ingest_dir=data_folder / "fapar-lai" / "ingest", convention="ALMA"
        )
