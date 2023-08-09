"""ERA5 land dataset."""

import numpy as np
from zampy.datasets import ERA5
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.reference.variables import unit_registry


## Ignore missing class/method docstrings: they are implemented in the Dataset class.
# ruff: noqa: D102


class ERA5Land(ERA5):  # noqa: D101
    name = "era5-land"
    time_bounds = TimeBounds(np.datetime64("1950-01-01"), np.datetime64("2023-07-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    raw_variables = (
        Variable(name="t2m", unit=unit_registry.kelvin),
        Variable(name="d2m", unit=unit_registry.kelvin),
    )

    # variable names used in cdsapi downloading request
    variable_names = (
        "2m_temperature",
        "2m_dewpoint_temperature",
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

    cds_dataset = "reanalysis-era5-land"
