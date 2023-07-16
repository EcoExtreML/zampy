"""Unit test for ERA5 dataset."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import era5
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


class TestERA5:
    """Test the ERA5 class."""

    @patch("cdsapi.Client.retrieve")
    def test_download(self, mock_retrieve, valid_path_cds):
        """Test download functionality.
        Here we mock the downloading and save property file to a fake path.
        """
        with TemporaryDirectory() as temp_dir:
            times = TimeBounds(np.datetime64("2010-01-01"), np.datetime64("2010-01-31"))
            bbox = SpatialBounds(54, 56, 1, 3)
            variable = ["10m_v_component_of_wind"]
            download_dir = Path(temp_dir, "download")

            era5_dataset = era5.ERA5()
            # create a dummy .cdsapirc
            patching = patch("zampy.datasets.utils.CDSAPI_CONFIG_PATH", valid_path_cds)
            with patching:
                era5_dataset.download(
                    download_dir=download_dir,
                    time_bounds=times,
                    spatial_bounds=bbox,
                    variable_names=variable,
                )

                # make sure that the download is called
                assert mock_retrieve.called

                # check property file
                with (download_dir / "era5" / "properties.json").open(
                    mode="r", encoding="utf-8"
                ) as file:
                    json_dict = json.load(file)
                    # check property
                    assert json_dict["variable_names"] == variable

    def ingest_dummy_data(self, temp_dir):
        """Ingest dummy tif data to nc for other tests."""
        era5_dataset = era5.ERA5()
        era5_dataset.ingest(download_dir=data_folder, ingest_dir=Path(temp_dir))
        ds = xr.load_dataset(
            Path(
                temp_dir,
                "era5",
                "era5_10m_v_component_of_wind_2010-1.nc",
            )
        )

        return ds, era5_dataset

    def test_ingest(self):
        """Test ingest function."""
        with TemporaryDirectory() as temp_dir:
            ds, _ = self.ingest_dummy_data(temp_dir)

            assert type(ds) == xr.Dataset

    def test_load(self):
        """Test load function."""
        times = TimeBounds(np.datetime64("2010-01-01"), np.datetime64("2010-01-31"))
        bbox = SpatialBounds(54, 6, 51, 3)
        variable = ["10m_v_component_of_wind"]

        era5_dataset = era5.ERA5()

        ds = era5_dataset.load(
            ingest_dir=Path(data_folder),
            time_bounds=times,
            spatial_bounds=bbox,
            variable_names=variable,
            resolution=1.0,
            regrid_method="flox",
        )

        # we assert the regridded coordinates
        expected_lat = [51.0, 52.0, 53.0, 54.0]
        expected_lon = [3.0, 4.0, 5.0, 6.0]

        np.testing.assert_allclose(ds.latitude.values, expected_lat)
        np.testing.assert_allclose(ds.longitude.values, expected_lon)

    def test_convert(self):
        """Test convert function."""
        with TemporaryDirectory() as temp_dir:
            _, era5_dataset = self.ingest_dummy_data(temp_dir)
            era5_dataset.convert(ingest_dir=Path(temp_dir), convention="ALMA")
            # TODO: finish this test when the function is complete.


def test_convert_to_zampy():
    """Test function for converting file to zampy format."""
    with TemporaryDirectory() as temp_dir:
        ingest_folder = Path(data_folder, "era5")
        era5.convert_to_zampy(
            ingest_folder=Path(temp_dir),
            file=Path(ingest_folder, "era5_10m_v_component_of_wind_2010-1.nc"),
            overwrite=True,
        )

        ds = xr.load_dataset(Path(temp_dir, "era5_10m_v_component_of_wind_2010-1.nc"))

        assert list(ds.data_vars)[0] == "10m_v_component_of_wind"


def test_parse_nc_file():
    """Test parsing netcdf file function."""
    ds = era5.parse_nc_file(
        data_folder / "era5" / "era5_10m_v_component_of_wind_2010-1.nc"
    )
    expected_var_name = "10m_v_component_of_wind"

    assert list(ds.data_vars)[0] == expected_var_name
    assert ds["10m_v_component_of_wind"].attrs["units"] == "meter_per_second"
