"""Unit test for dataset protocol."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
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
    """Test """
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
