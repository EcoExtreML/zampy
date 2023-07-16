"""Shared utilities from datasets."""
import itertools
import urllib.request
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
import cdsapi
import pandas as pd
import requests
from tqdm import tqdm
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


PRODUCT_FNAME = {
    "reanalysis-era5-single-levels": "era5",
    "reanalysis-era5-land": "era5-land",
}
CDSAPI_CONFIG_PATH = Path.home() / ".cdsapirc"


class TqdmUpdate(tqdm):
    """Wrap a tqdm progress bar to be updateable by urllib.request.urlretrieve."""

    def update_to(
        self, b: int = 1, bsize: int = 1, tsize: Optional[int] = None
    ) -> Union[bool, None]:
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
    response = requests.head(url, timeout=30)
    return int(response.headers["Content-Length"])


def get_file_size(fpath: Path) -> int:
    """Return the size (bytes) of a given Path."""
    if not fpath.exists():
        return 0
    else:
        return fpath.stat().st_size


def cds_request(  # noqa: PLR0913
    product: str,
    variables: List[str],
    time_bounds: TimeBounds,
    spatial_bounds: SpatialBounds,
    path: Path,
    overwrite: bool,
) -> None:
    """Download data via CDS API.

    To raise a request via CDS API, the user needs to set up the
    configuration file `.cdsapirc` following the instructions on
    https://cds.climate.copernicus.eu/api-how-to.

    Following the efficiency tips of request,
    https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+documentation
    The downloading is organized by asking for one month of data per request.

    Args:
        product: Dataset name for retrieval via `cdsapi`.
        variables: Zampy variable.
        time_bounds: Zampy time bounds object.
        spatial_bounds: Zampy spatial bounds object.
        path: File path to which the data should be saved.
        overwrite: If an existing file (of the same size!) should be overwritten.
    """
    fname = PRODUCT_FNAME[product]

    with CDSAPI_CONFIG_PATH.open(encoding="utf8") as f:
        url = f.readline().split(":", 1)[1].strip()
        api_key = f.readline().split(":", 1)[1].strip()

    c = cdsapi.Client(
        url=url,
        key=api_key,
        verify=True,
        quiet=True,
    )

    # create list of year/month pairs
    year_month_pairs = time_bounds_to_year_month(time_bounds)

    for (year, month), variable in itertools.product(year_month_pairs, variables):
        # check existence and overwrite
        fpath = path / f"{fname}_{variable}_{year}-{month}.nc"
        if fpath.exists() and not overwrite:
            print(f"File '{fpath.name}' already exists, skipping...")
            continue
        # raise download request
        c.retrieve(
            product,
            {
                "product_type": "reanalysis",
                "variable": [variable],
                "year": year,
                "month": month,
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": [
                    "00:00",
                    "01:00",
                    "02:00",
                    "03:00",
                    "04:00",
                    "05:00",
                    "06:00",
                    "07:00",
                    "08:00",
                    "09:00",
                    "10:00",
                    "11:00",
                    "12:00",
                    "13:00",
                    "14:00",
                    "15:00",
                    "16:00",
                    "17:00",
                    "18:00",
                    "19:00",
                    "20:00",
                    "21:00",
                    "22:00",
                    "23:00",
                ],
                "area": [
                    spatial_bounds.north,
                    spatial_bounds.west,
                    spatial_bounds.south,
                    spatial_bounds.east,
                ],
                "format": "netcdf",
            },
            fpath,
        )


def time_bounds_to_year_month(time_bounds: TimeBounds) -> List[Tuple[str, str]]:
    """Return year/month pairs."""
    date_range = pd.date_range(start=time_bounds.start, end=time_bounds.end, freq="M")
    year_month_pairs = [(str(date.year), str(date.month)) for date in date_range]
    return year_month_pairs
