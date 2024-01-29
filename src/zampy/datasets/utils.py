"""Shared utilities from datasets."""
import urllib.request
from pathlib import Path
import requests
import xarray_regrid
from tqdm import tqdm
from zampy.datasets.dataset_protocol import SpatialBounds


class TqdmUpdate(tqdm):
    """Wrap a tqdm progress bar to be updateable by urllib.request.urlretrieve."""

    def update_to(
        self, b: int = 1, bsize: int = 1, tsize: int | None = None
    ) -> bool | None:
        """Update the progress bar.

        Args:
            b: Number of blocks transferred so far.
            bsize: Size of each block (in tqdm units).
            tsize: Total size (in tqdm units). If `None`, remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)


def download_url(url: str, fpath: Path, overwrite: bool) -> None:
    """Download a URL, and display a progress bar for that file.

    Args:
        url: URL to be downloaded.
        fpath: File path to which the URL should be saved.
        overwrite: If an existing file (of the same size!) should be overwritten.
    """
    if get_file_size(fpath) != get_url_size(url) or overwrite:
        with TqdmUpdate(
            unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
        ) as t:
            urllib.request.urlretrieve(url, filename=fpath, reporthook=t.update_to)
    else:
        print(f"File '{fpath.name}' already exists, skipping...")


def get_url_size(url: str) -> int:
    """Return the size (bytes) of a given URL."""
    response = requests.head(url)
    return int(response.headers["Content-Length"])


def get_file_size(fpath: Path) -> int:
    """Return the size (bytes) of a given Path."""
    if not fpath.exists():
        return 0
    else:
        return fpath.stat().st_size


def make_grid(spatial_bounds: SpatialBounds, resolution: float) -> xarray_regrid.Grid:
    """MAke a regridding grid for passing to xarray-regrid."""
    return xarray_regrid.Grid(
        north=spatial_bounds.north,
        east=spatial_bounds.east,
        south=spatial_bounds.south,
        west=spatial_bounds.west,
        resolution_lat=resolution,
        resolution_lon=resolution,
    )
