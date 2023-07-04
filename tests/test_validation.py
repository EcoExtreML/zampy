"""Unit test for validation."""

import numpy as np
import pytest
from zampy.datasets import EthCanopyHeight
from zampy.datasets import validation
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


def test_compare_variables_not_match():
    dummy_dataset = EthCanopyHeight()
    variables = ["fake_var"]
    with pytest.raises(validation.InvalidVariableError):
        validation.compare_variables(dummy_dataset, variables)


def test_compare_time_bounds_not_cover_start():
    dummy_dataset = EthCanopyHeight()
    times = TimeBounds(np.datetime64("1900-01-01"), np.datetime64("2020-12-31"))
    with pytest.raises(validation.InvalidTimeBoundsError, match="not cover the start"):
        validation.compare_time_bounds(dummy_dataset, times)


def test_compare_time_bounds_not_cover_end():
    dummy_dataset = EthCanopyHeight()
    times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2100-12-31"))
    with pytest.raises(validation.InvalidTimeBoundsError, match="not cover the end"):
        validation.compare_time_bounds(dummy_dataset, times)


def test_validate_download_request():
    """Check function validate download request.

    Note that all the cases with errors are tested separately in other functions.
    Here we make sure that the function can be called without error.
    """
    dummy_dataset = EthCanopyHeight()
    times = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
    bbox = SpatialBounds(54, 6, 51, 3)
    variables = ["height_of_vegetation"]
    validation.validate_download_request(dummy_dataset, "./", times, bbox, variables)
