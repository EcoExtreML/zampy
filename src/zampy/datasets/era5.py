"""ERA5 dataset."""

import numpy as np
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.ecmwf_dataset import ECMWFDataset
from zampy.reference.variables import VARIABLE_REFERENCE_LOOKUP
from zampy.reference.variables import unit_registry


class ERA5(ECMWFDataset):  # noqa: D101
    name = "era5"
    time_bounds = TimeBounds(np.datetime64("1940-01-01"), np.datetime64("2023-07-31"))

    raw_variables = [
        Variable(name="mtpr", unit=unit_registry.kilogram_per_square_meter_second),
        Variable(name="strd", unit=unit_registry.joule_per_square_meter),
        Variable(name="ssrd", unit=unit_registry.joule_per_square_meter),
        Variable(name="sp", unit=unit_registry.pascal),
        Variable(name="u10", unit=unit_registry.meter_per_second),
        Variable(name="v10", unit=unit_registry.meter_per_second),
    ]

    # variable names used in cdsapi downloading request
    cds_var_names = {
        "total_precipitation": "mean_total_precipitation_rate",
        "surface_thermal_radiation_downwards": "surface_thermal_radiation_downwards",
        "surface_solar_radiation_downwards": "surface_solar_radiation_downwards",
        "surface_pressure": "surface_pressure",
        "eastward_component_of_wind": "10m_u_component_of_wind",
        "northward_component_of_wind": "10m_v_component_of_wind",
    }

    variable_names = list(cds_var_names.keys())

    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    data_url = "https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form"

    cds_dataset = "reanalysis-era5-single-levels"


class ERA5Land(ECMWFDataset):  # noqa: D101
    name = "era5-land"
    time_bounds = TimeBounds(np.datetime64("1950-01-01"), np.datetime64("2023-07-31"))

    raw_variables = [
        Variable(name="t2m", unit=unit_registry.kelvin),
        Variable(name="d2m", unit=unit_registry.kelvin),
        Variable(name="st", unit=unit_registry.kelvin),
        Variable(name="swvl", unit=unit_registry.fraction),
    ]

    # variable names used in cdsapi downloading request
    cds_var_names = {
        "air_temperature": "2m_temperature",
        "dewpoint_temperature": "2m_dewpoint_temperature",
        "soil_temperature_level_1": "soil_temperature_level_1",  # Note: split variables
        "soil_temperature_level_2": "soil_temperature_level_2",
        "soil_temperature_level_3": "soil_temperature_level_3",
        "soil_temperature_level_4": "soil_temperature_level_4",
        "volumetric_soil_water_layer_1": "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2": "volumetric_soil_water_layer_2",
        "volumetric_soil_water_layer_3": "volumetric_soil_water_layer_3",
        "volumetric_soil_water_layer_4": "volumetric_soil_water_layer_4",
    }

    variable_names = [
        "air_temperature",
        "dewpoint_temperature",
        "soil_temperature",
        "soil_moisture",
    ]

    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    data_url = "https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=form"

    cds_dataset = "reanalysis-era5-land"
