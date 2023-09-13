"""Land cover classification dataset."""

from pathlib import Path
import numpy as np
from zampy.datasets import cds_utils
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


class LandCover:  # noqa: D101
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
