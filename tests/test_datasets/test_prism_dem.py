"""Unit test for ETH canopy height dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import prism_dem
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from . import data_folder


@pytest.fixture(scope="function")
def dummy_dir(tmp_path_factory):
    """Create a dummpy directory for testing."""
    return tmp_path_factory.mktemp("data")


class TestPrismDEM:
    """Test the PrismDEM class."""

    @patch("urllib.request.urlretrieve")
    def test_download(self, mock_urlretrieve, dummy_dir):
        """Test download functionality.

        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
        bbox = SpatialBounds(54, 5, 53, 4)
        variable = ["elevation"]
        download_dir = Path(dummy_dir, "download")

        prism_dem_dataset = prism_dem.PrismDEM90()
        prism_dem_dataset.download(
            download_dir=download_dir,
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
        )

        # make sure that the download is called
        assert mock_urlretrieve.called

        # check property file
        with (download_dir / "prism-dem-90" / "properties.json").open(
            mode="r", encoding="utf-8"
        ) as file:
            json_dict = json.load(file)
            # check property
            assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        prism_dem_dataset = prism_dem.PrismDEM90()
        prism_dem_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "prism-dem-90",
                "Copernicus_DSM_30_N53_00_E004_00.nc",
            )
        )

        return ds, prism_dem_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)

        assert type(ds) == xr.Dataset

    def test_load(self, dummy_dir):
        """Test load function."""
        _, prism_dem_dataset = self.ingest_dummy_data(dummy_dir)

        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
        bbox = SpatialBounds(54, 5, 53, 4)
        variable = ["elevation"]

        ds = prism_dem_dataset.load(
            ingest_dir=Path(dummy_dir),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=0.25,
        )

        # we assert the regridded coordinates
        expected_lat = [53.00, 53.25, 53.50, 53.75, 54.0]
        expected_lon = [4.00, 4.25, 4.50, 4.75, 5.0]

        np.testing.assert_allclose(ds["latitude"].values, expected_lat)
        np.testing.assert_allclose(ds["longitude"].values, expected_lon)

    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, prism_dem_dataset = self.ingest_dummy_data(dummy_dir)
        prism_dem_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.
