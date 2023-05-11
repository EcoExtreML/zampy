"""Outline of the dataset protocol."""
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Protocol
from typing import Tuple
import numpy as np
import xarray as xr


FNAME_PROPERTIES = "properties.json"


@dataclass
class Variable:
    """zampy variable."""

    name: str
    unit: Any  # pint unit. typing has issues with pint 0.21
    desc: Optional[str] = ""


@dataclass
class SpatialBounds:
    """zampy spatial bounds object."""

    north: float
    east: float
    south: float
    west: float


@dataclass
class TimeBounds:
    """zampy time bounds object.

    Note: the bounds are closed on both sides.
    """

    start: np.datetime64
    end: np.datetime64


class Dataset(Protocol):
    """Dataset."""

    name: str
    time_bounds: TimeBounds
    spatial_bounds: SpatialBounds
    crs: str
    license: str
    bib: str
    raw_variables: Tuple[Variable, ...]
    variable_names: Tuple[str, ...]
    variables: Tuple[Variable, ...]

    def __init__(self) -> None:
        """Init."""
        ...

    def download(  # noqa: PLR0913
        self,
        download_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        variable_names: List[str],
        overwrite: bool = False,
    ) -> bool:
        """Download the data.

        Returns:
            Download success
        """
        ...

    def preprocess(  # noqa: PLR0913
        self,
        download_dir: Path,
        preprocessed_dir: Path,
        spatial_bounds: SpatialBounds,
        time_bounds: TimeBounds,
        variable_names: List[str],
    ) -> bool:
        """Preprocess the downloaded data to the CF-like Zampy convention."""
        ...

    def load(self) -> xr.Dataset:
        """Get the dataset as an xarray Dataset."""
        ...


def write_properties_file(
    dataset_folder: Path,
    spatial_bounds: SpatialBounds,
    time_bounds: TimeBounds,
    variable_names: List[str],
) -> None:
    """Write the (serialized) spatial and time bounds to a json file.

    Args:
        dataset_folder: Path to the dataset folder (download/preprocessing).
        spatial_bounds: Spatial bounds of the data.
        time_bounds: Time bounds of the data.
        variable_names: The (standard) variable names of the data.
    """
    # Data to be written
    json_dict = {
        "start_time": str(time_bounds.start),
        "end_time": str(time_bounds.end),
        "north": spatial_bounds.north,
        "east": spatial_bounds.east,
        "south": spatial_bounds.south,
        "west": spatial_bounds.west,
        "variable_names": variable_names,
    }

    json_object = json.dumps(json_dict, indent=4)

    with (dataset_folder / FNAME_PROPERTIES).open(mode="w", encoding="utf-8") as file:
        file.write(json_object)


def read_properties_file(
    dataset_folder: Path,
) -> Tuple[SpatialBounds, TimeBounds, List[str]]:
    """Load the serialized spatial and time bounds from the json file.

    Args:
        dataset_folder: Path to the dataset folder (download/preprocessing).

    Returns:
        Tuple[SpatialBounds, TimeBounds]: The spatial and time bounds of the data.
    """
    with (dataset_folder / FNAME_PROPERTIES).open(mode="r", encoding="utf-8") as file:
        json_dict = json.load(file)

    return (
        SpatialBounds(
            json_dict["north"],
            json_dict["east"],
            json_dict["south"],
            json_dict["west"],
        ),
        TimeBounds(start=json_dict["start_time"], end=json_dict["end_time"]),
        json_dict["variable_names"],
    )


def copy_properties_file(
    source_folder: Path,
    target_folder: Path,
) -> None:
    """Copy the properties file from one folder to another.

    To be used when, for example, the downloaded data has been ingested.

    Args:
        source_folder: Source folder containing the properties file.
        target_folder: Destination folder where the file should be copied to.
    """
    shutil.copy(source_folder / FNAME_PROPERTIES, target_folder / FNAME_PROPERTIES)
