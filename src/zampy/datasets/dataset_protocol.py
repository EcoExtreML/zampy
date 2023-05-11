"""Outline of the dataset protocol."""
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional
from typing import Protocol
from typing import Tuple
import numpy as np
import xarray as xr


@dataclass
class Variable:
    """zampy variable."""

    name: str
    unit: str
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

    def preprocess(
        self,
        download_dir: Path,
        spatial_bounds: SpatialBounds,
        time_bounds: TimeBounds,
        variable_names: List[str],
    ) -> bool:
        """Preprocess the downloaded data to the CF-like Zampy convention."""
        ...

    def load(self) -> xr.Dataset:
        """Get the dataset as an xarray Dataset."""
        ...
