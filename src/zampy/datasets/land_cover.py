"""Land cover classification dataset."""

import numpy as np
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
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
    author={Buchhorn, Marcel and Lesiv, Myroslava and Tsendbazar, Nandin-Erdene and Herold, Martin and Bertels, Luc and Smets, Bruno},
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
