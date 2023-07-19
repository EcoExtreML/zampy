"""ERA5 dataset."""

from pathlib import Path
from typing import List
from typing import Union
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
from zampy.utils import regrid


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class ERA5(Dataset):  # noqa: D101
    name = "era5"
    time_bounds = TimeBounds(np.datetime64("1940-01-01"), np.datetime64("2023-06-30"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    raw_variables = (
        Variable(name="mtpr", unit=unit_registry.kilogram_per_square_meter_second),
        Variable(name="strd", unit=unit_registry.watt_per_square_meter),
        Variable(name="ssrd", unit=unit_registry.watt_per_square_meter),
        Variable(name="sp", unit=unit_registry.pascal),
        Variable(name="u10", unit=unit_registry.meter_per_second),
        Variable(name="v10", unit=unit_registry.meter_per_second),
    )

    # variable names used in cdsapi downloading request
    variable_names = (
        "mean_total_precipitation_rate",
        "surface_thermal_radiation_downwards",
        "surface_solar_radiation_downwards",
        "surface_pressure",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
    )

    license = "cc-by-4.0"
    bib = """
    @article{hersbach2020era5,
        title={The ERA5 global reanalysis},
        author={Hersbach, Hans et al.},
        journal={Quarterly Journal of the Royal Meteorological Society},
        volume={146},
        number={730},
        pages={1999--2049},
        year={2020},
        publisher={Wiley Online Library}
        }
    """

    def download(
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
        download_folder.mkdir(parents=True, exist_ok=True)

        utils.cds_request(
            dataset="reanalysis-era5-single-levels",
            variables=variable_names,
            time_bounds=time_bounds,
            spatial_bounds=spatial_bounds,
            path=download_folder,
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

        data_file_pattern = "era5_*.nc"
        data_files = list(download_folder.glob(data_file_pattern))

        for file in data_files:
            convert_to_zampy(
                ingest_folder,
                file=file,
                overwrite=overwrite,
            )

        copy_properties_file(download_folder, ingest_folder)

        return True

    def load(
        self,
        ingest_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        resolution: float,
        regrid_method: str,
        variable_names: List[str],
    ) -> xr.Dataset:
        files: List[Path] = []
        for var in self.variable_names:
            if var in variable_names:
                files += (ingest_dir / self.name).glob(f"era5_{var}*.nc")

        ds = xr.open_mfdataset(files, chunks={"latitude": 200, "longitude": 200})
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

        data_file_pattern = "era5_*.nc"

        data_files = list(ingest_folder.glob(data_file_pattern))

        for file in data_files:
            # start conversion process
            print(f"Start processing file `{file.name}`.")
            ds = xr.open_dataset(file, chunks={"x": 50, "y": 50})
            ds = converter.convert(ds, dataset=self, convention=convention)
            # TODO: support derived variables
            # TODO: other calculations
            # call ds.compute()

        return True


def convert_to_zampy(
    ingest_folder: Path,
    file: Path,
    overwrite: bool = False,
) -> None:
    """Convert the downloaded nc files to standard CF/Zampy netCDF files.

    The downloaded ERA5 data already follows CF1.6 convention. However, it uses
    (abbreviated) variable name instead of standard name, which prohibits the format
    conversion. Therefore we need to ingest the downloaded files and rename all
    variables to standard names.

    Args:
        ingest_folder: Folder where the files have to be written to.
        file: Path to the ERA5 nc file.
        overwrite: Overwrite all existing files. If False, file that already exist will
            be skipped.
    """
    ncfile = ingest_folder / file.with_suffix(".nc").name
    if ncfile.exists() and not overwrite:
        print(f"File '{ncfile.name}' already exists, skipping...")
    else:
        ds = parse_nc_file(file)

        ds.to_netcdf(path=ncfile)


var_reference_era5_to_zampy = {
    "mtpr": "mean_total_precipitation_rate",
    "strd": "surface_thermal_radiation",
    "ssrd": "surface_solar_radiation",
    "sp": "surface_pressure",
    "u10": "10m_u_component_of_wind",
    "v10": "10m_v_component_of_wind",
}


def parse_nc_file(file: Path) -> xr.Dataset:
    """Parse the downloaded ERA5 nc files, to CF/Zampy standard dataset.

    Args:
        file: Path to the ERA5 nc file.

    Returns:
        CF/Zampy formatted xarray Dataset
    """
    # Open chunked: will be dask array -> file writing can be parallelized.
    ds = xr.open_dataset(file, chunks={"x": 50, "y": 50})

    for variable in ds.variables:
        if variable in var_reference_era5_to_zampy:
            var = str(variable)  # Cast to string to please mypy
            variable_name = var_reference_era5_to_zampy[var]
            # if statement variable name
            # conversion for radiation (to flux) & precipitation (/ rho water)
            # https://confluence.ecmwf.int/pages/viewpage.action?pageId=155337784
            ds = ds.rename({var: variable_name})
            ds[variable_name].attrs["units"] = str(
                VARIABLE_REFERENCE_LOOKUP[variable_name].unit
            )
            ds[variable_name].attrs["description"] = VARIABLE_REFERENCE_LOOKUP[
                variable_name
            ].desc

    # TODO: add dataset attributes.

    return ds
