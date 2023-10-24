"""Land cover classification dataset."""

from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import numpy as np
import xarray as xr
import xarray_regrid
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


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class LandCover:
    """Land cover classification gridded maps."""

    name = "land-cover"
    time_bounds = TimeBounds(np.datetime64("1992-01-01"), np.datetime64("2020-12-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)
    crs = "EPSG:4326"

    raw_variables = [
        Variable(name="lccs_class", unit=unit_registry.dimensionless),
    ]
    variable_names = ["land_cover"]
    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    license = "ESA CCI licence; licence-to-use-copernicus-products; VITO licence"

    bib = """
    @article{buchhorn2020copernicus,
    title={Copernicus global land cover layers—collection 2},
    author={Buchhorn, Marcel et al.},
    journal={Remote Sensing},
    volume={12},
    number={6},
    pages={1044},
    year={2020},
    publisher={MDPI}
    }
    """

    data_url = "https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=overview"

    cds_dataset = "satellite-land-cover"

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

        cds_utils.cds_request_land_cover(
            dataset=self.cds_dataset,
            time_bounds=time_bounds,
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

        archive_file_pattern = f"{self.name}_*.zip"
        archive_files = list(download_folder.glob(archive_file_pattern))

        for file in archive_files:
            unzip_raw_to_netcdf(
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
        regrid_method: str,  # Unused in land-cover dataset
        variable_names: list[str],
    ) -> xr.Dataset:
        files: list[Path] = []
        for var in variable_names:
            if var not in self.variable_names:
                msg = (
                    "One or more variables are not in this dataset.\n"
                    f"Please check input. Dataset: '{self.name}'\n"
                    f"Variables: '{variable_names}'"
                )
                raise ValueError(msg)
        files = list((ingest_dir / self.name).glob(f"{self.name}_*.nc"))

        ds = xr.open_mfdataset(files, chunks={"latitude": 200, "longitude": 200})
        ds = ds.sel(time=slice(time_bounds.start, time_bounds.end))
        new_grid = xarray_regrid.Grid(
            north=spatial_bounds.north,
            east=spatial_bounds.east,
            south=spatial_bounds.south,
            west=spatial_bounds.west,
            resolution_lat=resolution,
            resolution_lon=resolution,
        )
        target_dataset = xarray_regrid.create_regridding_dataset(new_grid)

        ds_regrid = ds.regrid.most_common(target_dataset, time_dim="time", max_mem=1e9)

        return ds_regrid

    def convert(
        self,
        ingest_dir: Path,
        convention: str | Path,
    ) -> bool:
        converter.check_convention(convention)
        ingest_folder = ingest_dir / self.name

        data_file_pattern = "land-cover_LCCS_MAP_*.nc"

        data_files = list(ingest_folder.glob(data_file_pattern))

        for file in data_files:
            # start conversion process
            print(f"Start processing file `{file.name}`.")
            ds = xr.open_dataset(file)
            ds = converter.convert(ds, dataset=self, convention=convention)
            # TODO: support derived variables
            # TODO: other calculations
            # call ds.compute()

        return True


def unzip_raw_to_netcdf(
    ingest_folder: Path,
    file: Path,
    overwrite: bool = False,
) -> None:
    """Convert a downloaded zip netcdf file to a standard CF/Zampy netCDF file.

    Args:
        ingest_folder: Folder where the files have to be written to.
        file: Path to the land cover .zip archive.
        overwrite: Overwrite all existing files. If False, file that already exist will
            be skipped.
    """
    ncfile = ingest_folder / file.with_suffix(".nc").name
    if ncfile.exists() and not overwrite:
        print(f"File '{ncfile.name}' already exists, skipping...")
    else:
        ds = extract_netcdf_to_zampy(file)
        ds.to_netcdf(path=ncfile)


def extract_netcdf_to_zampy(file: Path) -> xr.Dataset:
    """Extract zipped data and convert to zampy format.

    Since the original land cover field is too large to fit into
    the memory in general, in this function the loaded land cover
    data are regridded. They are regrid to a resoltuion of 0.25
    degree, same as the native resolution of ERA5 data.

    Args:
        file: Path to the land cover .zip archive.

    Returns:
        Coarse land cover data in zampy format.
    """
    with TemporaryDirectory() as temp_dir:
        unzip_folder = Path(temp_dir)
        with ZipFile(file, "r") as zip_object:
            zipped_file_name = zip_object.namelist()[0]
            zip_object.extract(zipped_file_name, path=unzip_folder)

        # only keep land cover class variable
        with xr.open_dataset(unzip_folder / zipped_file_name) as ds:
            var_list = [var for var in ds.data_vars]
            raw_variable = "lccs_class"
            var_list.remove(raw_variable)
            ds = ds.drop_vars(var_list)  # noqa: PLW2901

            # coarsen to fit into memory
            ds = ds.sortby(["lat", "lon"])  # noqa: PLW2901
            ds = ds.rename({"lat": "latitude", "lon": "longitude"})  # noqa: PLW2901
            new_grid = xarray_regrid.Grid(
                north=90,
                east=180,
                south=-90,
                west=-180,
                resolution_lat=0.25,  # same as resolution of ERA5
                resolution_lon=0.25,
            )

            target_dataset = xarray_regrid.create_regridding_dataset(new_grid)

            ds_regrid = ds.regrid.most_common(
                target_dataset, time_dim="time", max_mem=1e9
            )

        # rename variable to follow the zampy convention
        variable_name = "land_cover"
        ds_regrid = ds_regrid.rename({raw_variable: variable_name})
        ds_regrid[variable_name].attrs["units"] = str(
            VARIABLE_REFERENCE_LOOKUP[variable_name].unit
        )
        ds_regrid[variable_name].attrs["description"] = VARIABLE_REFERENCE_LOOKUP[
            variable_name
        ].desc

    return ds_regrid
