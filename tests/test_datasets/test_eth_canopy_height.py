"""Unit test for ETH canopy height dataset."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pytest
from unittest.mock import patch
import xarray as xr
from zampy.datasets import eth_canopy_height
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from . import data_folder


class TestEthCanopyHeight:
    """Test the EthCanopyHeight class."""

    @patch("urllib.request.urlretrieve")
    def test_download(self, mock_urlretrieve):
        """Test download functionality.

        Here we mock the downloading and save property file to a fake path.
        """
        with TemporaryDirectory() as temp_dir:
            times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
            bbox = SpatialBounds(54, 6, 51, 3)
            variable = ["height_of_vegetation"]
            download_dir = Path(temp_dir, "download")

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

    def test_ingest(self):
        # with TemporaryDirectory() as temp_dir:
            # canopy_height_dataset = eth_canopy_height.EthCanopyHeight()
            # canopy_height_dataset.ingest(download_dir=data_folder, ingest_dir=temp_dir)
        pass

    def test_load(self):
        pass

    def test_convert(self):
        pass


def test_get_filenames():
    """Test file names generator."""
    bbox = SpatialBounds(54, 8, 51, 3)
    expected = [
        "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        "ETH_GlobalCanopyHeight_10m_2020_N51E006_Map.tif",
    ]

    file_names = eth_canopy_height.get_filenames(bbox)
    assert file_names == expected


def test_get_filenames_SD():
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
        Path(data_folder, "eth-canopy-height", "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif")
    )
    assert type(dummy_ds) == xr.Dataset


def test_convert_tiff_to_netcdf():
    """Test tiff to netcdf conversion function."""
    with TemporaryDirectory() as temp_dir:
        dummy_data = Path(
            data_folder,
            "eth-canopy-height",
            "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
        )
        eth_canopy_height.convert_tiff_to_netcdf(
            ingest_folder=Path(temp_dir),
            file=dummy_data,
        )

        ds = xr.load_dataset(
            Path(temp_dir, "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.nc")
        )
        assert type(ds) == xr.Dataset
