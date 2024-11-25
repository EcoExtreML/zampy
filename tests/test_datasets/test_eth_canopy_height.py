"""Unit test for ETH canopy height dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from tests import data_folder
from zampy.datasets import eth_canopy_height
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


@pytest.fixture(scope="function")
def dummy_dir(tmp_path_factory):
    """Create a dummpy directory for testing."""
    return tmp_path_factory.mktemp("data")


class TestEthCanopyHeight:
    """Test the EthCanopyHeight class."""

    @patch("urllib.request.urlretrieve")
    def test_download(self, mock_urlretrieve, dummy_dir):
        """Test download functionality.

        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-02-15"))
        bbox = SpatialBounds(60, 10, 50, 0)
        variable = ["height_of_vegetation"]
        download_dir = Path(dummy_dir, "download")

        canopy_height_dataset = eth_canopy_height.EthCanopyHeight()
        canopy_height_dataset.download(
            download_dir=download_dir,
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
        )

        # make sure that the download is called
        assert mock_urlretrieve.called

        # check property file
        with (download_dir / "eth-canopy-height" / "properties.json").open(
            mode="r", encoding="utf-8"
        ) as file:
            json_dict = json.load(file)
            # check property
            assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        canopy_height_dataset = eth_canopy_height.EthCanopyHeight()
        canopy_height_dataset.ingest(
            download_dir=data_folder, ingest_dir=Path(temp_dir)
        )

        return canopy_height_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        _ = self.ingest_dummy_data(dummy_dir)
        ds = xr.open_dataset(
            Path(
                dummy_dir,
                "eth-canopy-height",
                "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.nc",
            )
        )

        assert isinstance(ds, xr.Dataset)

    def test_load(self, dummy_dir):
        """Test load function."""
        canopy_height_dataset = self.ingest_dummy_data(dummy_dir)

        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(60.0, 0.3, 59.7, 0.0)
        variable = ["height_of_vegetation"]

        ds = canopy_height_dataset.load(
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

    def test_convert(self, dummy_dir):
        """Test convert function."""
        canopy_height_dataset = self.ingest_dummy_data(dummy_dir)
        canopy_height_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.


def test_get_filenames():
    """Test file names generator."""
    bbox = SpatialBounds(54, 8, 51, 3)
    expected = [
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        "ETH_GlobalCanopyHeight_10m_2020_N51E006_Map.tif",
    ]

    file_names = eth_canopy_height.get_filenames(bbox)
    assert file_names == expected


def test_get_filenames_sd():
    """Test file names of standard deviation."""
    bbox = SpatialBounds(54, 8, 51, 3)
    expected = [
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map_SD.tif",
        "ETH_GlobalCanopyHeight_10m_2020_N51E006_Map_SD.tif",
    ]

    file_names = eth_canopy_height.get_filenames(bbox, sd_file=True)
    assert file_names == expected


def test_valid_filenames():
    """Test function to get valid filenames."""
    test_filenames = [
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        "ETH_GlobalCanopyHeight_10m_2020_N51E004_Map.tif",  # fake
        "ETH_GlobalCanopyHeight_10m_2020_N51E006_Map.tif",
    ]

    expected = [
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        "ETH_GlobalCanopyHeight_10m_2020_N51E006_Map.tif",
    ]

    file_names = eth_canopy_height.get_valid_filenames(test_filenames)
    assert file_names == expected


def test_parse_tiff_file():
    """Test tiff file parser."""
    dummy_ds = eth_canopy_height.parse_tiff_file(
        Path(
            data_folder,
            "eth-canopy-height",
            "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        )
    )
    assert isinstance(dummy_ds, xr.Dataset)


def test_convert_tiff_to_netcdf(dummy_dir):
    """Test tiff to netcdf conversion function."""
    dummy_data = Path(
        data_folder,
        "eth-canopy-height",
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )
    eth_canopy_height.convert_tiff_to_netcdf(
        ingest_folder=Path(dummy_dir),
        file=dummy_data,
    )

    ds = xr.open_dataset(
        Path(dummy_dir, "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.nc")
    )
    assert isinstance(ds, xr.Dataset)
