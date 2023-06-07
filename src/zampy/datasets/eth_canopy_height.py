"""ETH canopy height dataset."""
import gzip
from pathlib import Path
from typing import List
import numpy as np
import xarray as xr
from zampy.datasets import converter
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

## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class EthCanopyHeight(Dataset):  # noqa: D101
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
    )  # type: ignore

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

    def ingest(
        self,
        download_dir: Path,
        ingest_dir: Path,
        overwrite: bool = False,
    ) -> bool:
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
                overwrite=overwrite,
            )

        copy_properties_file(download_folder, ingest_folder)

        return True

    def load(
        self,
        ingest_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        variable_names: List[str],
    ) -> xr.Dataset:
        files: List[Path] = []
        if self.variable_names[0] in variable_names:
            files += (ingest_dir / self.name).glob("*Map.nc")
        if self.variable_names[1] in variable_names:
            files += (ingest_dir / self.name).glob("*Map_SD.nc")

        ds = xr.open_mfdataset(files, chunks={"latitude": 6000, "longitude": 6000})
        ds = ds.sel(
            latitude=slice(spatial_bounds.south, spatial_bounds.north),
            longitude=slice(spatial_bounds.west, spatial_bounds.east),
            time=slice(time_bounds.start, time_bounds.end),
        )
        return ds

    def convert(
        self,
        ingest_dir: Path,
        convert_dir: Path,
        convention: str,
        overwrite: bool = False,
    ) -> xr.Dataset:
        # check convention
        converter.check_convention(convention)
        # load files
        ingest_folder = ingest_dir / self.name
        convert_folder = convert_dir / self.name
        convert_folder.mkdir(parents=True, exist_ok=True)

        data_file_pattern = "ETH_GlobalCanopyHeight_10m_2020_*.nc"

        data_files = list(ingest_folder.glob(data_file_pattern))

        # convert variables
        for file in data_files:
            # check if the converted file already exists
            ncfile = convert_folder / file.with_suffix(".nc").name
            if ncfile.exists() and not overwrite:
                print(f"The converted file '{ncfile.name}' already exists, skipping...")
            else:
                # start conversion process
                print(f"Start processing file `{file.name}`.")
                ds = xr.open_dataset(file, chunks={"x": 6000, "y": 6000})
                converter.convert(
                    ds,
                    fname=file.name,
                    output_path=convert_folder,
                    convention=convention
                )


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
        np.arange(start=bounds.south, stop=bounds.north, step=step),
        np.arange(start=bounds.west, stop=bounds.east, step=step),
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
    overwrite: bool = False,
) -> None:
    """Convert the downloaded tiff files to standard CF/Zampy netCDF files.

    Args:
        ingest_folder: Folder where the files have to be written to.
        file: Path to the ETH canopy height tiff file.
        sd_file: If the file contains the standard deviation values.
        overwrite: Overwrite all existing files. If False, file that already exist will
            be skipped.
    """
    ncfile = ingest_folder / file.with_suffix(".nc").name
    if ncfile.exists() and not overwrite:
        print(f"File '{ncfile.name}' already exists, skipping...")
    else:
        ds = parse_tiff_file(file, sd_file)
        ds.to_netcdf(
            path=ncfile,
            encoding=ds.encoding,
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
    ds = ds.assign_coords({"time": np.datetime64("2020-07-01")})  # halfway in the year
    ds = ds.expand_dims("time")
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
        if variable_name != "time":  # TODO: Check how to write time attrs...
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
