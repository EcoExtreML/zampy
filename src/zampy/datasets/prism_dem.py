"""Prism DEM dataset."""
import gzip
import tarfile
from pathlib import Path
from typing import Literal
import numpy as np
import xarray as xr
from rasterio.io import MemoryFile
from zampy.datasets import converter
from zampy.datasets import utils
from zampy.datasets import validation
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.dataset_protocol import copy_properties_file
from zampy.datasets.dataset_protocol import write_properties_file
from zampy.reference.variables import VARIABLE_REFERENCE_LOOKUP
from zampy.reference.variables import unit_registry
from zampy.utils import regrid


VALID_NAME_FILES = [
    Path(__file__).parent / "assets" / "dem_filenames_glo30.txt.gz",
    Path(__file__).parent / "assets" / "dem_filenames_glo90.txt.gz",
]


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class PrismDEM:
    """The Prism Digital Elevation Model."""

    name: str
    data_url: str
    _glob_code: Literal["30", "90"]

    # DEM does not change a lot, so use wide valid bounds:
    time_bounds = TimeBounds(np.datetime64("1900-01-01"), np.datetime64("2100-12-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)
    crs = "EPSG:4326"

    raw_variables = [
        Variable(name="elevation", unit=unit_registry.meter),
    ]
    variable_names = ["elevation"]
    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    license = "free"
    bib = """
    @misc{2022,
    doi = {10.5270/esa-c5d3d65},
    url = {https://doi.org/10.5270/esa-c5d3d65},
    year = {2022},
    publisher = {European Space Agency},
    author = {European Space Agency and Copernicus},
    title = {Copernicus Prism DEM}
    }
    """
    data_url = "https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model#anchor"

    def __init__(self) -> None:
        """Init."""
        pass

    def download(
        self,
        download_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        variable_names: list[str],
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
        filenames = get_archive_filenames(spatial_bounds, self._glob_code)

        download_folder.mkdir(parents=True, exist_ok=True)
        for fname in filenames:
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

        archive_file_pattern = "Copernicus_DSM_*_00.tar"
        archive_files = list(download_folder.glob(archive_file_pattern))

        for file in archive_files:
            convert_raw_dem_to_netcdf(
                ingest_folder,
                file=file,
                overwrite=overwrite,
            )

        copy_properties_file(download_folder, ingest_folder)

        return True

    def load(
        self,
        ingest_dir: Path,
        time_bounds: TimeBounds,  # Unused in PrismDEM
        spatial_bounds: SpatialBounds,
        resolution: float,
        regrid_method: str,
        variable_names: list[str],
    ) -> xr.Dataset:
        for var in variable_names:
            if var not in self.variable_names:
                msg = (
                    "One or more variables are not in this dataset.\n"
                    f"Please check input. Dataset: '{self.name}'\n"
                    f"Variables: '{variable_names}'"
                )
                raise ValueError(msg)
        files = list((ingest_dir / self.name).glob("*.nc"))

        def preproc(ds: xr.Dataset) -> xr.Dataset:
            """Remove overlapping coordinates on the edges."""
            return ds.isel(latitude=slice(None, -1), longitude=slice(None, -1))

        ds = xr.open_mfdataset(files, preprocess=preproc)
        ds = regrid.regrid_data(ds, spatial_bounds, resolution, regrid_method)

        return ds

    def convert(
        self,
        ingest_dir: Path,
        convention: str | Path,
    ) -> bool:
        converter.check_convention(convention)
        ingest_folder = ingest_dir / self.name

        data_file_pattern = "Copernicus_DSM_*_00_DEM.nc"

        data_files = list(ingest_folder.glob(data_file_pattern))

        for file in data_files:
            # start conversion process
            print(f"Start processing file `{file.name}`.")
            ds = xr.open_dataset(file)
            ds = converter.convert(ds, dataset=self, convention=convention)

        return True


class PrismDEM30(PrismDEM):
    """The Prism Digital Elevation Model, GLO-30 version."""

    name = "prism-dem-30"
    note = "Armenia and Azerbaijan are not in this dataset."

    _glob_code = "30"

    data_url = "https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-30-DGED__2021_1/"


class PrismDEM90(PrismDEM):
    """The Prism Digital Elevation Model, GLO-90 version."""

    name = "prism-dem-90"

    _glob_code = "90"

    data_url = "https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-90-DGED__2021_1/"


def convert_raw_dem_to_netcdf(
    ingest_folder: Path,
    file: Path,
    overwrite: bool = False,
) -> None:
    """Convert a downloaded archived tiff file to a standard CF/Zampy netCDF file.

    Args:
        ingest_folder: Folder where the files have to be written to.
        file: Path to the Prism DEM .tar archive.
        overwrite: Overwrite all existing files. If False, file that already exist will
            be skipped.
    """
    ncfile = ingest_folder / file.with_suffix(".nc").name
    if ncfile.exists() and not overwrite:
        print(f"File '{ncfile.name}' already exists, skipping...")
    else:
        ds = read_raw_dem(file)
        ds.to_netcdf(
            path=ncfile,
            encoding=ds.encoding,
        )


def read_raw_dem(file: Path) -> xr.Dataset:
    """Parse the downloaded DEM compressed tif files, to CF/Zampy standard dataset.

    Args:
        file: Path to the Prism DEM .tar archive.

    Returns:
        CF/Zampy formatted xarray Dataset
    """
    basename = file.with_suffix("").name

    tf = tarfile.open(file)
    tfdata = tf.extractfile(f"{basename}/DEM/{basename}_DEM.tif")

    if tfdata is None:
        raise ValueError(f"File {file} contains no data")

    # Reading bytestream is flakey. rasterio has a MemoryFile module to allow reading
    # in-memory GeoTIFF file data:
    da = xr.open_dataarray(MemoryFile(tfdata), engine="rasterio")  # type: ignore

    da = da.sortby(["x", "y"])  # sort the dims ascending
    da = da.isel(band=0)  # get rid of band dim
    da = da.drop_vars(["band", "spatial_ref"])  # drop unnecessary coords
    ds = da.to_dataset()
    ds = ds.rename(
        {
            "band_data": "elevation",
            "x": "longitude",
            "y": "latitude",
        }
    )
    ds["elevation"].attrs.pop("AREA_OR_POINT")  # Remove tif leftover attr

    # The prism DEM variable & coords already follow the CF/Zampy convention
    for variable in ds.variables:
        variable_name = str(variable)  # Cast to string to please mypy.
        if variable_name != "time":
            ds[variable_name].attrs["units"] = str(
                VARIABLE_REFERENCE_LOOKUP[variable_name].unit
            )
            ds[variable_name].attrs["description"] = VARIABLE_REFERENCE_LOOKUP[
                variable_name
            ].desc

    ds.encoding = {
        "elevation": {
            "zlib": True,
            "complevel": 5,
        }
    }
    return ds


def get_archive_filenames(
    bounds: SpatialBounds, glo_number: Literal["30", "90"]
) -> list[str]:
    """Get all valid Prism dataset archive filenames within given spatial bounds.

    Args:
        bounds: Spatial bounds to be used to determine which tiles need to be
            downloaded.
        glo_number: Number code of GLO. Either 30 or 90.

    Returns:
        List of filenames.
    """
    step = 1

    locs = np.meshgrid(
        np.arange(start=bounds.south, stop=bounds.north, step=step),
        np.arange(start=bounds.west, stop=bounds.east, step=step),
    )
    lats = locs[0].flatten()
    lons = locs[1].flatten()

    fnames = [""] * len(lats)

    if glo_number == "30":
        file_code_number = 10
    elif glo_number == "90":
        file_code_number = 30
    else:
        raise ValueError("Unknown glo_number.")

    for i, (lat, lon) in enumerate(zip(lats, lons, strict=True)):
        lat_ = int(lat // step * step)
        lon_ = int(lon // step * step)

        latstr = str(abs(lat_)).rjust(2, "0")
        lonstr = str(abs(lon_)).rjust(3, "0")
        latstr = f"N{latstr}" if lat_ >= 0 else f"S{latstr}"
        lonstr = f"E{lonstr}" if lon_ >= 0 else f"W{lonstr}"
        fnames[i] = f"Copernicus_DSM_{file_code_number}_{latstr}_00_{lonstr}_00.tar"

    return get_valid_filenames(fnames)


def get_valid_filenames(filenames: list[str]) -> list[str]:
    """Return a new list with only the valid filenames."""
    valid_filenames = ""

    for valid_name_file in VALID_NAME_FILES:
        with gzip.open(valid_name_file, "rb") as f:
            valid_filenames += f.read().decode("utf-8")

    valid_names = []
    for fname in filenames:
        if fname in valid_filenames:
            valid_names.append(fname)
    return valid_names
