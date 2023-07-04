"""Checks for user input validation."""
from pathlib import Path
from typing import List
from zampy.datasets.dataset_protocol import Dataset
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


class InvalidTimeBoundsError(Exception):
    """Error raised when the time bounds of a dataset is insufficient for a request."""

    ...


class InvalidVariableError(Exception):
    """Error raised when a variable is requested which is not in the dataset."""

    ...


def validate_download_request(
    dataset: Dataset,
    download_dir: Path,
    time_bounds: TimeBounds,
    spatial_bounds: SpatialBounds,
    variable_names: List[str],
) -> None:
    """Validate the user's download request against the dataset.

    Args:
        dataset: Zampy Dataset definition.
        download_dir: Path to the download directory.
        time_bounds: Time bounds of the user's download request.
        spatial_bounds: Spatial bounds of the user's download request.
        variable_names: User requested variables.
    """
    compare_variables(dataset, variable_names)
    compare_time_bounds(dataset, time_bounds)
    # TODO: check spatial bounds
    # TODO: check download dir


def compare_variables(
    dataset: Dataset,
    variable_names: List[str],
) -> None:
    """Compare the user's requested variables to the dataset's variables.

    Args:
        dataset: Zampy Dataset definition.
        variable_names: User requested variables.

    Raises:
        InvalidVariableError: If the variables are not available in the dataset
    """
    if not all(var in dataset.variable_names for var in variable_names):
        raise InvalidVariableError(
            f"Input variable and/or units does not match the {dataset.name} dataset."
        )


def compare_time_bounds(
    dataset: Dataset,
    request_bounds: TimeBounds,
) -> None:
    """Compare the requested time bounds with the dataset time bounds.

    Args:
        dataset: Zampy Dataset definition.
        request_bounds: Time bounds requested by the user/recipe.

    Raises:
        InvalidTimeBoundsError: If the dataset bounds are not sufficient.
    """
    error_message = ""
    if dataset.time_bounds.start > request_bounds.start:
        error_message += (
            f"\nThe '{dataset.name}' data could not cover the start of requested range:"
            f"\n    data start: {dataset.time_bounds.start}"
            f"\n    requested start: {request_bounds.start}"
        )
    if dataset.time_bounds.end < request_bounds.end:
        error_message += (
            f"\nThe '{dataset.name}' data could not cover the end of requested range:"
            f"\n    data end: {dataset.time_bounds.end}"
            f"\n    requested end: {request_bounds.end}"
        )
    if len(error_message) > 0:
        raise InvalidTimeBoundsError(error_message)
