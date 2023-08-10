"""ERA5 land dataset."""

import numpy as np
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.ecmwf_dataset import ECMWFDataset
from zampy.reference.variables import unit_registry


class ERA5Land(ECMWFDataset):  # noqa: D101
    name = "era5-land"
    time_bounds = TimeBounds(np.datetime64("1950-01-01"), np.datetime64("2023-07-31"))

    raw_variables = (
        Variable(name="t2m", unit=unit_registry.kelvin),
        Variable(name="d2m", unit=unit_registry.kelvin),
    )

    # variable names used in cdsapi downloading request
    variable_names = (
        "2m_temperature",
        "2m_dewpoint_temperature",
    )

    cds_dataset = "reanalysis-era5-land"
