"""Implementation of the FAPAR LAI dataset."""

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union
import cdsapi
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from zampy.datasets import cds_utils
from zampy.datasets import converter
from zampy.datasets import validation
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.dataset_protocol import copy_properties_file
from zampy.datasets.dataset_protocol import write_properties_file
from zampy.reference.variables import VARIABLE_REFERENCE_LOOKUP
from zampy.reference.variables import unit_registry
from zampy.utils import regrid


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class FaparLAI:  # noqa: D101
    name = "fapar-lai"
    time_bounds = TimeBounds(np.datetime64("1998-04-10"), np.datetime64("2020-06-30"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)
    crs = "EPSG:4326"

    raw_variables = [Variable(name="lai", unit=unit_registry.fraction)]
    variable_names = ["leaf_area_index"]
    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    license = "non-standard"
    license_url = (
        "https://cds.climate.copernicus.eu/api/v2/terms/static/vito-proba-v.pdf"
    )

    bib = """
    @misc{https://doi.org/10.24381/cds.7e59b01a,
        doi = {10.24381/CDS.7E59B01A},
        url = {https://cds.climate.copernicus.eu/doi/10.24381/cds.7e59b01a},
        author = {{Copernicus Climate Change Service}},
        title = {Leaf area index and fraction absorbed of photosynthetically active radiation 10-daily gridded data from 1981 to present},
        publisher = {ECMWF},
        year = {2018}
    }
    """  # noqa: E501

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
        download_folder.mkdir(parents=True, exist_ok=True)

        url, api_key = cds_utils.cds_api_key("fapar-lai")

        client = cdsapi.Client(
            url=url,
            key=api_key,
            verify=True,
            quiet=True,
        )

        years_months = get_year_month_pairs(time_bounds)
        for year, month in tqdm(years_months):
            print(f"Downloading FAPAR LAI data for {year}-{month}...")
            download_fapar_lai(
                client, year, month, download_folder, spatial_bounds, overwrite
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

        zip_file_pattern = "*.zip"
        zip_files = sorted(download_folder.glob(zip_file_pattern))

        # Create tmp dir. See https://github.com/EcoExtreML/zampy/issues/36
        # TODO: Fix in a nice way.
        tmp_path = download_dir.parent / "tmp"
        tmp_path.mkdir(parents=True, exist_ok=True)

        # netCDF files follow CF-1.6, only unpacking the archives is required.
        for file in zip_files:
            with tempfile.TemporaryDirectory(dir=tmp_path) as _tmpdir:
                tmpdir = Path(_tmpdir)

                extract_fapar_zip(
                    zip_file=file,
                    ingest_folder=ingest_folder,
                    extract_dir=tmpdir,
                    overwrite=overwrite,
                )

                for ncfile in tmpdir.glob("*.nc"):
                    ingest_ncfile(ncfile, ingest_folder)

        copy_properties_file(download_folder, ingest_folder)

        return True

    def load(
        self,
        ingest_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        resolution: float,
        regrid_method: str,
        variable_names: list[str],
    ) -> xr.Dataset:
        files = list((ingest_dir / self.name).glob("*.nc"))

        ds = xr.open_mfdataset(files, chunks={"latitude": 2000, "longitude": 2000})
        ds = ds.sel(time=slice(time_bounds.start, time_bounds.end))
        ds = regrid.regrid_data(ds, spatial_bounds, resolution, regrid_method)

        return ds

    def convert(
        self,
        ingest_dir: Path,
        convention: Union[str, Path],
    ) -> bool:
        converter.check_convention(convention)
        ingest_folder = ingest_dir / self.name

        data_file_pattern = f"{self.name}_*.nc"

        data_files = list(ingest_folder.glob(data_file_pattern))

        for file in data_files:
            # start conversion process
            print(f"Start processing file `{file.name}`.")
            ds = xr.open_dataset(file, chunks={"x": 2000, "y": 2000})
            ds = converter.convert(ds, dataset=self, convention=convention)

        return True


def get_year_month_pairs(time_bounds: TimeBounds) -> list[tuple[int, int]]:
    """Get the year and month pairs covering the input time bounds."""
    start = pd.to_datetime(time_bounds.start)
    end = pd.to_datetime(time_bounds.end)

    year_month = []
    for year in range(start.year, end.year + 1):
        for month in range(1, 13):
            if year == start.year and month < start.month:
                pass
            elif year == end.year and month > end.month:
                pass
            else:
                year_month.append((year, month))

    return year_month


def get_lai_days(year: int, month: int) -> list[str]:
    """Get the days that the FAPAR LAI is available for a certain year and month."""
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return ["10", "20", "31"]
    if month == 2:
        if year in [2000, 2004, 2008, 2012, 2016, 2020]:
            return ["10", "20", "29"]
        else:
            return ["10", "20", "28"]
    return ["10", "20", "30"]


def download_fapar_lai(
    client: cdsapi.Client,
    year: int,
    month: int,
    download_dir: Path,
    spatial_bounds: Optional[SpatialBounds] = None,
    overwrite: bool = False,
) -> None:
    """Download the FAPAR LAI data from CDS."""
    request: dict[str, Any] = {
        "format": "zip",
        "variable": "lai",
        "horizontal_resolution": "1km",
        "product_version": "V3",
        "satellite": "spot" if year < 2014 else "proba",
        "sensor": "vgt",
        "month": f"{month:0>2}",
        "nominal_day": get_lai_days(year, month),
        "year": f"{year}",
    }

    if spatial_bounds is not None:
        request["area"] = [
            spatial_bounds.north,
            spatial_bounds.west,
            spatial_bounds.south,
            spatial_bounds.east,
        ]

    fpath = download_dir / f"satellite-lai-fapar_{year}-{month}.zip"

    retrieval = client.retrieve("satellite-lai-fapar", request)

    cds_utils._check_and_download(retrieval, fpath, overwrite)


def ingest_ncfile(ncfile: Path, ingest_folder: Path) -> None:
    """Ingest the 'raw' netCDF file to the Zampy standard format."""
    print(f"Converting file {ncfile.name}...")
    ds = xr.open_dataset(ncfile, decode_times=False)
    ds = ds.rename(
        {
            "LAI": "leaf_area_index",
            "lat": "latitude",
            "lon": "longitude",
        }
    )
    ds["leaf_area_index"].attrs["units"] = "fraction"
    ds[["leaf_area_index"]].to_netcdf(
        path=ingest_folder / ncfile.name,
        encoding={"leaf_area_index": {"zlib": True, "complevel": 3}},
    )


def extract_fapar_zip(
    zip_file: Path, ingest_folder: Path, extract_dir: Path, overwrite: bool
) -> None:
    """Extract the FAPAR LAI zip file, if not all files already exist."""
    with zipfile.ZipFile(zip_file, "r") as zf:
        file_list = zf.namelist()
    if all((ingest_folder / fname).exists() for fname in file_list) and not overwrite:
        print(f"Files '{file_list}' already exist, skipping...")
    else:
        shutil.unpack_archive(zip_file, extract_dir=extract_dir, format="zip")
