"""Base module for datasets available on CDS."""

from pathlib import Path
from typing import List
from typing import Tuple
from typing import Union
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
from zampy.utils import regrid


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class ECMWFDataset(Dataset):  # noqa: D101
    name: str
    time_bounds: TimeBounds
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    raw_variables: Tuple[Variable, ...]
    variable_names: Tuple[str, ...]
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
    cds_dataset: str

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
            dataset=self.cds_dataset,
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

        data_file_pattern = f"{self.name}_*.nc"
        data_files = list(download_folder.glob(data_file_pattern))

        for file in data_files:
            utils.convert_to_zampy(
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
                files += (ingest_dir / self.name).glob(f"{self.name}_{var}*.nc")

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

        data_file_pattern = f"{self.name}_*.nc"

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
