"""ERA5 dataset."""

from pathlib import Path
from typing import List
from typing import Union
import numpy as np
import xarray as xr
# from zampy.datasets import converter
from zampy.datasets import utils
# from zampy.datasets import validation
from zampy.datasets.dataset_protocol import Dataset
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
# from zampy.datasets.dataset_protocol import Variable
# from zampy.datasets.dataset_protocol import copy_properties_file
from zampy.datasets.dataset_protocol import write_properties_file


class ERA5(Dataset):  # noqa: D101
    name = "era5"
    time_bounds = TimeBounds(np.datetime64("1940-01-01"), np.datetime64("2023-06-30"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    license = "cc-by-4.0"

    def download(  # noqa: PLR0913
        self,
        download_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        variable_names: List[str],
        overwrite: bool = False,
    ) -> bool:
        # validation.validate_download_request(
        #     self,
        #     download_dir,
        #     time_bounds,
        #     spatial_bounds,
        #     variable_names,
        # )
        # call the cds_request function

        download_folder = download_dir / self.name
        download_folder.mkdir(parents=True, exist_ok=True)

        utils.cds_request(
            product="reanalysis-era5-single-levels",
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
        return True

    def load( # noqa: PLR0913
        self,
        ingest_dir: Path,
        time_bounds: TimeBounds,
        spatial_bounds: SpatialBounds,
        resolution: float,
        regrid_method: str,
        variable_names: List[str],
    ):
        pass

    def convert(
        self,
        ingest_dir: Path,
        convention: Union[str, Path],
    ) -> bool:
        return True
