"""Unit test for land cover dataset."""

import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
import zampy.datasets.land_cover
from tests import data_folder
from zampy.datasets.catalog import LandCover
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


class TestLandCover:
    """Test the LandCover class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_config, dummy_dir):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-31"))
        bbox = SpatialBounds(60, 10, 50, 0)
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
                    "year": "2020",
                    "version": "v2_1_1",
                    "area": [60, 0, 50, 10],
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
                "land-cover_LCCS_MAP_300m_2020.nc",
            )
        )

        return ds, land_cover_dataset

    @pytest.mark.slow
    def test_ingest(self, dummy_dir):
        """Test ingest function."""
        ds, _ = self.ingest_dummy_data(dummy_dir)
        assert isinstance(ds, xr.Dataset)

    @pytest.mark.slow
    def test_load(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(60.0, 0.3, 59.7, 0.0)
        variable = ["land_cover"]

        ingest_ds, land_cover_dataset = self.ingest_dummy_data(dummy_dir)

        ds = land_cover_dataset.load(
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

        # check if unique values of ds are a subset of ingest_ds
        assert np.all(
            np.isin(
                np.unique(ds.land_cover.values),
                ingest_ds["land_cover"].attrs["flag_values"],
            )
        )

    def test_land_cover_without_flag_values(self, dummy_dir):
        """Test load function."""
        times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-01-04"))
        bbox = SpatialBounds(60.0, 0.3, 59.7, 0.0)
        variable = ["land_cover"]

        ingest_ds, land_cover_dataset = self.ingest_dummy_data(dummy_dir)

        # store unique values
        unique_values = ingest_ds["land_cover"].attrs["flag_values"]

        # remove flag_values
        ingest_ds["land_cover"].attrs.pop("flag_values")

        ds = land_cover_dataset.load(
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

        # check if unique values of ds are a subset of ingest_ds
        assert np.all(
            np.isin(
                np.unique(ds.land_cover.values),
                unique_values,
            )
        )

    @pytest.mark.slow
    def test_convert(self, dummy_dir):
        """Test convert function."""
        _, land_cover_dataset = self.ingest_dummy_data(dummy_dir)
        land_cover_dataset.convert(ingest_dir=Path(dummy_dir), convention="ALMA")
        # TODO: finish this test when the function is complete.


@pytest.mark.slow
def test_unzip_raw_to_netcdf():
    ds = zampy.datasets.land_cover.extract_netcdf_to_zampy(
        data_folder / "land-cover/land-cover_LCCS_MAP_300m_2020.zip"
    )
    assert isinstance(ds, xr.Dataset)


@pytest.mark.slow
def test_extract_netcdf_to_zampy(dummy_dir):
    zampy.datasets.land_cover.unzip_raw_to_netcdf(
        Path(dummy_dir),
        data_folder / "land-cover/land-cover_LCCS_MAP_300m_2020.zip",
    )
    dataset_path = Path(dummy_dir) / "land-cover_LCCS_MAP_300m_2020.nc"
    assert dataset_path.exists()
