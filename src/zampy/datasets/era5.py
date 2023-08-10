"""ERA5 dataset."""

import numpy as np
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.ecmwf_dataset import ECMWFDataset
from zampy.reference.variables import unit_registry


class ERA5(ECMWFDataset):  # noqa: D101
    name = "era5"
    time_bounds = TimeBounds(np.datetime64("1940-01-01"), np.datetime64("2023-07-31"))

    raw_variables = (
        Variable(name="mtpr", unit=unit_registry.kilogram_per_square_meter_second),
        Variable(name="strd", unit=unit_registry.joule_per_square_meter),
        Variable(name="ssrd", unit=unit_registry.joule_per_square_meter),
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

    cds_dataset = "reanalysis-era5-single-levels"
