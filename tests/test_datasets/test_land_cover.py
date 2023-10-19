"""Unit test for land cover dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
import zampy.datasets.land_cover
from zampy.datasets.catalog import LandCover
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


class TestLandCover:
    """Test the LandCover class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_config, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("1996-01-01"), np.datetime64("1996-12-31"))
        bbox = SpatialBounds(54, 56, 1, 3)
        variable = ["land_cover"]
        download_dir = Path(dummy_dir, "download")

        land_cover_dataset = LandCover()
        # create a dummy .cdsapirc
        patching = patch("zampy.datasets.cds_utils.CONFIG_PATH", valid_path_config)
        with patching:
            land_cover_dataset.download(
                download_dir=download_dir,
                time_bounds=times,
                spatial_bounds=bbox,
                variable_names=variable,
                overwrite=True,
            )

            # make sure that the download is called
            mock_retrieve.assert_called_once_with(
                "satellite-land-cover",
                {
                    "variable": "all",
                    "format": "zip",
                    "year": "1996",
                    "version": "v2.0.7cds",
                },
            )

            # check property file
            with (download_dir / "land-cover" / "properties.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                json_dict = json.load(file)
                # check property
                assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy zip data to nc for other tests."""
        land_cover_dataset = LandCover()
        land_cover_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "land-cover",
                "land-cover_LCCS_MAP_300m_1996.nc",
            )
        )

        return ds, land_cover_dataset

    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert isinstance(ds, xr.Dataset)

    def test_load(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("1996-01-01"), np.datetime64("1996-12-31"))
        bbox = SpatialBounds(39, -107, 37, -109)
        variable = ["land_cover"]

        _, land_cover_dataset = self.ingest_dummy_data(dummy_dir)

        ds = land_cover_dataset.load(
            ingest_dir=Path(dummy_dir),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=1.0,
            regrid_method="most_common",
        )

        # we assert the regridded coordinates
        expected_lat = [37.0, 38.0, 39.0]
        expected_lon = [-109.0, -108.0, -107.0]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, land_cover_dataset = self.ingest_dummy_data(dummy_dir)
        land_cover_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.


def test_unzip_raw_to_netcdf():
    ds = zampy.datasets.land_cover.extract_netcdf_to_zampy(
        data_folder / "land-cover/land-cover_LCCS_MAP_300m_1996.zip"
    )
    assert isinstance(ds, xr.Dataset)


def test_extract_netcdf_to_zampy(dummy_dir):
    zampy.datasets.land_cover.unzip_raw_to_netcdf(
        Path(dummy_dir),
        data_folder / "land-cover/land-cover_LCCS_MAP_300m_1996.zip",
    )
    dataset_path = Path(dummy_dir) / "land-cover_LCCS_MAP_300m_1996.nc"
    assert dataset_path.exists()
