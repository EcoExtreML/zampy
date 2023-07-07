"""Unit test for utils functions."""

import tempfile
from pathlib import Path
from unittest.mock import patch
from zampy.datasets import utils


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
