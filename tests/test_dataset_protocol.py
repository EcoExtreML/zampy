"""Unit test for dataset protocol."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pytest
from zampy.datasets import dataset_protocol
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


def dummy_property_file(dataset_folder):
    """Write a dummy property file for testing."""
    times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
    bbox = SpatialBounds(54, 6, 51, 3)
    variables = ["Hveg", "SWnet"]

    dataset_protocol.write_properties_file(
        dataset_folder=dataset_folder,
        spatial_bounds=bbox,
        time_bounds=times,
        variable_names=variables,
    )


def test_write_properties():
    """Test write properties function."""
    with TemporaryDirectory() as temp_dir:
        dataset_folder = Path(temp_dir)
        dummy_property_file(dataset_folder)

        json_file_path = dataset_folder / "properties.json"
        with json_file_path.open(mode="r", encoding="utf-8") as file:
            properties = json.load(file)

        # Verify the written data
        assert properties["start_time"] == "2020-01-01"
        assert properties["end_time"] == "2020-12-31"
        assert properties["north"] == 54
        assert properties["east"] == 6
        assert properties["south"] == 51
        assert properties["west"] == 3
        assert properties["variable_names"] == ["Hveg", "SWnet"]


def test_read_properties():
    """Test read properties function."""
    with TemporaryDirectory() as temp_dir:
        dataset_folder = Path(temp_dir)
        dummy_property_file(dataset_folder)

        (
            spatial_bounds,
            time_bounds,
            variable_names,
        ) = dataset_protocol.read_properties_file(dataset_folder)

        # Verify the returned values
        assert spatial_bounds.north == 54
        assert spatial_bounds.east == 6
        assert spatial_bounds.south == 51
        assert spatial_bounds.west == 3
        assert time_bounds.start == "2020-01-01"
        assert time_bounds.end == "2020-12-31"
        assert variable_names == ["Hveg", "SWnet"]


def test_copy_properties_file():
    """Test copy properties file function."""
    # Create temporary directories
    with TemporaryDirectory() as temp_dir1, TemporaryDirectory() as temp_dir2:
        source_folder = Path(temp_dir1)
        target_folder = Path(temp_dir2)

        # Create a properties.json file in the source folder
        dummy_property_file(source_folder)

        # Call the function
        dataset_protocol.copy_properties_file(source_folder, target_folder)

        # Verify that the file has been copied
        target_file_path = target_folder / "properties.json"
        assert target_file_path.exists()


def test_invalid_spatial_bounds_north_south():
    with pytest.raises(ValueError, match="greater than norther bound"):
        SpatialBounds(51, 6, 54, 3)


def test_invalid_spatial_bounds_east_west():
    with pytest.raises(ValueError, match="greater than east bound"):
        SpatialBounds(54, 6, 51, 20)


def test_invalid_time_bounds():
    with pytest.raises(ValueError):
        TimeBounds(np.datetime64("2021-01-01"), np.datetime64("2020-12-31"))
