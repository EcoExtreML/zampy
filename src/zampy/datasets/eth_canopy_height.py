"""ETH canopy height dataset."""
import gzip
from pathlib import Path
from typing import List
from typing import Tuple
import numpy as np
import xarray as xr
from zampy.datasets import converter
from zampy.datasets import utils
from .dataset_protocol import Dataset
from .dataset_protocol import SpatialBounds
from .dataset_protocol import Variable


VALID_NAME_FILE = (
    Path(__file__).parent / "assets" / "h_canopy_filenames_compressed.txt.gz"
)


class EthCanopyHeight(Dataset):
    """The ETH canopy height dataset."""

    name = "ETH_canopy_height"
    start_time = np.datetime64("2020-01-01")
    end_time = np.datetime64("2020-12-31")
    bounds = SpatialBounds(90, 180, -90, -180)
    crs = "EPSG:4326"

    variables = (
        Variable(name="h_canopy", unit="m"),
        Variable(name="h_canopy_SD", unit="m"),
    )

    download_files: list

    license = "cc-by-4.0"
    bib = """
    @article{lang2022,
        title={A high-resolution canopy height model of the Earth},
        author={Lang, Nico and Jetz, Walter and Schindler, Konrad and Wegner, Jan Dirk},
        journal={arXiv preprint arXiv:2204.08322},
        doi={10.48550/arXiv.2204.08322}
        year={2022}
    }
    """

    data_url = "https://share.phys.ethz.ch/~pf/nlangdata/ETH_GlobalCanopyHeight_10m_2020_version1/3deg_cogs/"

    def download(  # noqa: PLR0913
        self,
        download_dir: Path,
        spatial_bounds: SpatialBounds,
        temporal_bounds: Tuple[np.datetime64, np.datetime64],
        variables: List[Variable],
        overwrite: bool = False,
    ) -> bool:
        """Download the ETH tiles to the download directory."""
        if not all(var in self.variables for var in variables):
            raise ValueError(
                f"Input variable and/or units does not match the {self.name} dataset."
            )

        download_folder = download_dir / self.name
        self.download_files = []
        if self.variables[0] in variables:
            self.download_files += get_filenames(spatial_bounds)
        if self.variables[1] in variables:
            self.download_files += get_filenames(spatial_bounds, sd_file=True)

        download_folder.mkdir(parents=True, exist_ok=True)
        for fname in self.download_files:
            utils.download_url(
                url=self.data_url + fname,
                fpath=download_folder / fname,
                overwrite=overwrite,
            )
        return True
    
    def raw_load(
        self,
        download_dir: Path,
        spatial_bounds: SpatialBounds,
        temporal_bounds: Tuple[np.datetime64, np.datetime64],
        variables: List[Variable],
    ):
        pass

    def convert(self,
               download_dir: Path,
               convention: str="ALMA"):
        """Format dataset following the given convention."""
        # questions:
        # - is there site selection?
        # - do we combine files or keep files site-based?
        #   （code in pystemmusscope process data site-by-site)
        preprocess_folder = download_dir / self.name / "preprocess_data"
        preprocess_folder.mkdir(parents=True, exist_ok=True)
        for fname in self.download_files:
            data = xr.open_dataarray(download_dir / self.name / fname,
                                     engine="rasterio")
            converter.eth_canopy_height(data, fname, preprocess_folder, convention)
        print(f"Dataset conversion following {convention} convention is complet!")


def get_filenames(bounds: SpatialBounds, sd_file: bool = False) -> List[str]:
    """Get all valid ETH canopy height dataset filenames within given spatial bounds.

    Args:
        bounds: Spatial bounds to be used to determine which tiles need to be
            downloaded.
        sd_file: If the SD (standard deviation) files should be returned, or the actual
            height values.

    Returns:
        List of filenames (not checked for validity).
    """
    step = 3

    locs = np.meshgrid(
        np.arange(start=bounds.south, stop=bounds.north + step, step=step),
        np.arange(start=bounds.west, stop=bounds.east + step, step=step),
    )
    lats = locs[0].flatten()
    lons = locs[1].flatten()

    fnames = [""] * len(lats)

    for i, (lat, lon) in enumerate(zip(lats, lons)):
        lat_ = int(lat // step * step)
        lon_ = int(lon // step * step)

        latstr = str(abs(lat_)).rjust(2, "0")
        lonstr = str(abs(lon_)).rjust(3, "0")
        latstr = f"N{latstr}" if lat_ >= 0 else f"S{latstr}"
        lonstr = f"E{lonstr}" if lon_ >= 0 else f"W{lonstr}"

        sd_str = "_SD" if sd_file else ""
        fnames[i] = f"ETH_GlobalCanopyHeight_10m_2020_{latstr}{lonstr}_Map{sd_str}.tif"
    return get_valid_filenames(fnames)


def get_valid_filenames(filenames: List[str]) -> List[str]:
    """Returns a new list with only the valid filenames."""
    valid_name_file = (
        Path(__file__).parent / "assets" / "h_canopy_filenames_compressed.txt.gz"
    )

    with gzip.open(valid_name_file, "rb") as f:
        valid_filenames = f.read().decode("utf-8")

    valid_names = []
    for fname in filenames:
        if fname.replace("_SD","") in valid_filenames:
            valid_names.append(fname)
    return valid_names
