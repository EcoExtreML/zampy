"""ETH canopy height dataset."""
import gzip
from pathlib import Path
from typing import List
import numpy as np
import xarray as xr
from dask.delayed import Delayed
from zampy.datasets import utils
from zampy.datasets import validation
from zampy.datasets.dataset_protocol import Dataset
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.dataset_protocol import copy_properties_file
from zampy.datasets.dataset_protocol import write_properties_file
from zampy.reference.variables import VARIABLE_REFERENCE_LOOKUP
from zampy.reference.variables import unit_registry


VALID_NAME_FILE = (
    Path(__file__).parent / "assets" / "h_canopy_filenames_compressed.txt.gz"
)


class EthCanopyHeight(Dataset):
    """The ETH canopy height dataset."""

    name = "eth-canopy-height"
    time_bounds = TimeBounds(np.datetime64("2020-01-01"), np.datetime64("2020-12-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)
    crs = "EPSG:4326"

    raw_variables = (
        Variable(name="h_canopy", unit=unit_registry.meter),
        Variable(name="h_canopy_SD", unit=unit_registry.meter),
    )
    variable_names = ("canopy-height", "canopy-height-standard-deviation")
    variables = (
        VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names
    )  #  type: ignore

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
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        variable_names: List[str],
        overwrite: bool = False,
    ) -> bool:
        """Download the ETH tiles to the download directory."""
        validation.validate_download_request(
            self,
            download_dir,
            time_bounds,
            spatial_bounds,
            variable_names,
        )

        download_folder = download_dir / self.name
        download_files = []
        if self.variable_names[0] in variable_names:
            download_files += get_filenames(spatial_bounds)
        if self.variable_names[1] in variable_names:
            download_files += get_filenames(spatial_bounds, sd_file=True)

        download_folder.mkdir(parents=True, exist_ok=True)
        for fname in download_files:
            utils.download_url(
                url=self.data_url + fname,
                fpath=download_folder / fname,
                overwrite=overwrite,
            )

        write_properties_file(
            download_folder, spatial_bounds, time_bounds, variable_names
        )

        return True

    def ingest(  # noqa: PLR0913
        self,
        download_dir: Path,
        ingest_dir: Path,
    ) -> bool:
        """Convert the downloaded data to the CF-like Zampy convention."""
        download_folder = download_dir / self.name
        ingest_folder = ingest_dir / self.name
        ingest_folder.mkdir(parents=True, exist_ok=True)

        data_file_pattern = "ETH_GlobalCanopyHeight_10m_2020_*_Map.tif"
        sd_file_pattern = "ETH_GlobalCanopyHeight_10m_2020_*_Map_SD.tif"

        data_files = list(download_folder.glob(data_file_pattern))
        sd_files = list(download_folder.glob(sd_file_pattern))
        is_sd_file = len(data_files) * [False] + len(sd_files) * [True]

        for file, sd_file in zip(data_files + sd_files, is_sd_file):
            convert_tiff_to_netcdf(
                ingest_folder,
                file=file,
                sd_file=sd_file,
            )

        copy_properties_file(download_folder, ingest_folder)

        return True


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
        if fname.replace("_SD", "") in valid_filenames:
            valid_names.append(fname)
    return valid_names


def convert_tiff_to_netcdf(
    ingest_folder: Path,
    file: Path,
    sd_file: bool = False,
) -> Delayed:
    """Convert the downloaded tiff files to standard CF/Zampy netCDF files.

    Args:
        ingest_folder: Folder where the files have to be written to.
        file: Path to the ETH canopy height tiff file.
        sd_file: If the file contains the standard deviation values.
    """
    ds = parse_tiff_file(file, sd_file)
    return ds.to_netcdf(
        path=ingest_folder / file.with_suffix(".nc").name,
        encoding=ds.encoding,
        compute=False,
    )


def parse_tiff_file(file: Path, sd_file: bool = False) -> xr.Dataset:
    """Parse the downloaded canopy height tiff files, to CF/Zampy standard dataset.

    Args:
        file: Path to the ETH canopy height tiff file.
        sd_file: If the file contains the standard deviation values.

    Returns:
        CF/Zampy formatted xarray Dataset
    """
    # Open chunked: will be dask array -> file writing can be parallelized.
    da = xr.open_dataarray(file, engine="rasterio", chunks={"x": 6000, "y": 6000})
    da = da.sortby(["x", "y"])  # sort the dims ascending
    da = da.isel(band=0)  # get rid of band dim
    da = da.drop_vars(["band", "spatial_ref"])  # drop unnecessary coords
    ds = da.to_dataset()
    ds = ds.rename(
        {
            "band_data": "canopy-height-standard-deviation"
            if sd_file
            else "canopy-height",
            "x": "longitude",
            "y": "latitude",
        }
    )

    # All eth variables & coords already follow the CF/Zampy convention
    for variable in ds.variables:
        variable_name = str(variable)  # Cast to string to please mypy.
        ds[variable_name].attrs["units"] = str(
            VARIABLE_REFERENCE_LOOKUP[variable_name].unit
        )
        ds[variable_name].attrs["description"] = VARIABLE_REFERENCE_LOOKUP[
            variable_name
        ].desc

    # TODO: add dataset attributes.
    ds.encoding = {
        "canopy-height-standard-deviation"
        if sd_file
        else "canopy-height": {
            "zlib": True,
            "complevel": 5,
        }
    }
    return ds
