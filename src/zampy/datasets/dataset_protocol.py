"""Outline of the dataset protocol."""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from typing import List
from typing import Tuple
import numpy as np
import xarray as xr


@dataclass
class Variable:
    """zampy variable."""

    name: str
    unit: str


@dataclass
class SpatialBounds:
    """zampy spatial bounds object."""

    north: float
    east: float
    south: float
    west: float


class Dataset(Protocol):
    """Dataset."""

    name: str
    start_time: np.datetime64
    end_time: np.datetime64
    bounds: SpatialBounds
    crs: str
    license: str
    bib: str

    def __init__(self) -> None:
        """Init."""
        ...

    def download(
        self,
        download_dir: Path,
        spatial_bounds: SpatialBounds,
        temporal_bounds: Tuple[np.datetime64, np.datetime64],
        variables: List[Variable],
    ) -> bool:
        """Download the data.

        Returns:
            Download success
        """
        ...

    def load(self) -> xr.Dataset:
        """Get the dataset as an xarray Dataset."""
        ...
