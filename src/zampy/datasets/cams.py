"""CO2 dataset."""

from pathlib import Path
from typing import List
from typing import Union
import numpy as np
import xarray as xr
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


class CAMS(Dataset):  # noqa: D101
    name = "cams_co2"
    time_bounds = TimeBounds(np.datetime64("2003-01-01"), np.datetime64("2020-12-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    raw_variables = Variable(name="co2", unit=unit_registry.kilogram_per_kilogram)

    # variable names used in adsapi downloading request
    variable_names = ("carbon_dioxide",)

    # "https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf"
    license = "licence-to-use-copernicus-products"

    bib = """
    @article{agusti2023cams,
        title={The CAMS greenhouse gas reanalysis from 2003 to 2020},
        author={Agusti-Panareda, Anna et al.},
        journal={Atmospheric Chemistry and Physics},
        volume={23},
        number={6},
        pages={3829--3859},
        year={2023},
        publisher={Copernicus Publications G{\"o}ttingen, Germany}
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

        utils.ads_request(
            dataset="cams-global-ghg-reanalysis-egg4",
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

    def ingest(self):
        pass

    def load(self):
        pass

    def convert(self):
        pass
