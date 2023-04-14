"""ETH canopy height dataset."""
import gzip
from pathlib import Path
from typing import List
from typing import Tuple
import numpy as np
import requests
from tqdm import tqdm
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
        Variable(name="LAI", unit="-"),
        Variable(name="LAI_SD", unit="-"),
    )

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

    def download(
        self,
        download_dir: Path,
        spatial_bounds: SpatialBounds,
        temporal_bounds: Tuple[np.datetime64, np.datetime64],
        variables: List[Variable],
    ) -> bool:
        """Download the ETH tiles to the download directory."""
        download_folder = download_dir / self.name
        download_files = get_filenames(spatial_bounds)

        download_folder.mkdir(parents=True, exist_ok=True)
        for fname in tqdm(
            download_files, desc="Downloading canopy height files", unit="files"
        ):
            file = requests.get(self.data_url + fname)
            (download_folder / fname).open(mode="wb").write(file.content)
        return True


def get_filenames(bounds: SpatialBounds) -> List[str]:
    """Get all valid ETH canopy height dataset filenames within given spatial bounds."""
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

        fnames[i] = f"ETH_GlobalCanopyHeight_10m_2020_{latstr}{lonstr}_Map.tif"
    return get_valid_filenames(fnames)


def get_valid_filenames(filenames: List[str]) -> List[str]:
    """Remove the invalid filenames from the list of tile names."""
    valid_name_file = (
        Path(__file__).parent / "assets" / "h_canopy_filenames_compressed.txt.gz"
    )

    with gzip.open(valid_name_file, "rb") as f:
        valid_filenames = f.read().decode("utf-8")

    valid_names = []
    for fname in filenames:
        if fname in valid_filenames:
            valid_names.append(fname)
    return valid_names
