"""Unit test for utils functions."""

import tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
from zampy.datasets import utils
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


def test_tqdm_update():
    """Test tqdm function."""
    # Create an instance of TqdmUpdate
    progress_bar = utils.TqdmUpdate(total=100)
    progress_bar.update_to(10, 10)

    # Assert that the progress bar's value has been updated correctly
    assert progress_bar.n == 100


@patch("requests.head")
def test_get_url_size(mock_head):
    """Test url size function."""
    url = "https://example.com/test_file.txt"

    # Create a mock response object
    mock_response = mock_head.return_value
    mock_response.headers = {"Content-Length": "1024"}

    size = utils.get_url_size(url)

    # Assert that the mock head function was called with the correct URL
    mock_head.assert_called_once_with(url)

    # Assert that the returned size is correct
    assert size == 1024


def test_get_file_size():
    """Create a temporary file with a size of 1024 bytes."""
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(b"0" * 1024)
        temp_file.flush()

        # Call the get_file_size() function
        size = utils.get_file_size(temp_path)

        # Assert that the returned size is correct
        assert size == 1024


def test_get_file_size_not_exist():
    """Test with a non-existing file."""
    non_existing_path = Path("non_existing_file.txt")
    size = utils.get_file_size(non_existing_path)
    assert size == 0


@patch("urllib.request.urlretrieve")
def test_download_url(mock_urlretrieve):
    """Test download function."""
    # fake test data
    url = "https://example.com/test_file.txt"
    fpath = Path("test_file.txt")
    overwrite = True

    utils.download_url(url, fpath, overwrite)
    # assrt that the urlretrieve function is called.
    assert mock_urlretrieve.called


@pytest.fixture(scope="function")
def valid_path_cds(tmp_path_factory):
    """Create a dummy .cdsapirc file."""
    fn = tmp_path_factory.mktemp("usrhome") / ".cdsapirc"
    with open(fn, mode="w", encoding="utf-8") as f:
        f.write("url: a\nkey: 123:abc-def")
    return fn


@patch("cdsapi.Client.retrieve")
def test_cds_request(mock_retrieve, valid_path_cds):
    """ "Test cds request for downloading data from CDS server."""
    product = "reanalysis-era5-single-levels"
    variables = ["10m_v_component_of_wind"]
    time_bounds = TimeBounds(
        np.datetime64("2010-01-01T00:00:00"), np.datetime64("2010-01-31T23:00:00")
    )
    spatial_bounds = SpatialBounds(54, 56, 1, 3)
    path = Path(__file__).resolve().parent
    overwrite = True

    # create a dummy .cdsapirc
    patching = patch("zampy.datasets.utils.CDSAPI_CONFIG_PATH", valid_path_cds)
    with patching:
        utils.cds_request(
            product, variables, time_bounds, spatial_bounds, path, overwrite
        )

        mock_retrieve.assert_called_with(
            product,
            {
                "product_type": "reanalysis",
                "variable": variables,
                "year": "2010",
                "month": "1",
                # fmt: off
                "day": [
                    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                    "31",
                ],
                "time": [
                    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00",
                    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
                    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                    "21:00", "22:00", "23:00",
                ],
                # fmt: on
                "area": [
                    spatial_bounds.north,
                    spatial_bounds.west,
                    spatial_bounds.south,
                    spatial_bounds.east,
                ],
                "format": "netcdf",
            },
        )


def test_time_bounds_to_year_month():
    """Test year and month pair converter function."""
    times = TimeBounds(np.datetime64("2010-01-01"), np.datetime64("2010-01-31"))
    expected = [("2010", "1")]
    year_month_pairs = utils.time_bounds_to_year_month(times)
    assert expected == year_month_pairs
