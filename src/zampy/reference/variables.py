from pint import UnitRegistry
from zampy.datasets.dataset_protocol import Variable
from typing import Union, Literal
import pandas as pd
import numpy as np
import xarray  as xr

unit_registry = UnitRegistry()
unit_registry.define('fraction = [] = frac')
unit_registry.define('percent = 1e-2 frac = pct')
unit_registry.define('ppm = 1e-6 fraction')

# By default, we use the variable names and units following the CF convention:
# https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html


VARIABLE_REFERENCE = [
    Variable("air-temperature", unit_registry.kelvin),
    Variable("relative-humidity", unit_registry.percent),
    Variable("specific-humidity", unit_registry.fraction, description="Mass fraction of water in air."),
    Variable("altitude", unit_registry.meter),
    Variable("canopy-height", unit_registry.meter),
]


def convert_si_prefix(
    value: Union[np.ndarray, pd.DataFrame, xr.Dataset],
    from_prefix: str,
    to_prefix: str,
):
    """Convert a value between SI prefixes (e.g. from km to cm).

    Args:
        value
        from_prefix
        to_prefix

    Returns:
        Input value with the unit converted.
    """
    prefixes = {
        'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12,
        'G': 1e9, 'M': 1e6, 'k': 1e3, 'h': 1e2, 'da': 1e1,
        'd': 1e-1, 'c': 1e-2, 'm': 1e-3, 'µ': 1e-6, 'n': 1e-9,
        'p': 1e-12, 'f': 1e-15, 'a': 1e-18, 'z': 1e-21, 'y': 1e-24
    }

    if from_prefix not in prefixes or to_prefix not in prefixes:
        raise ValueError("Invalid prefix specified")
    from_factor = prefixes[from_prefix]
    to_factor = prefixes[to_prefix]
    return value * from_factor / to_factor

"kg/m3" -> "g/cm3"

def convert_temperature(
    value: Union[np.ndarray, pd.DataFrame, xr.Dataset],
    from_unit: Literal["K", "degC", "degF"],
    to_unit: Literal["K", "degC", "degF"],
):
    """
    Converts temperature from one unit to another.

    Parameters:
        value: The temperature value to convert.
        from_unit: The unit of the input temperature (e.g., 'degC', 'degF', 'K').
        to_unit: The desired unit for the converted temperature
            (e.g., 'degC', 'degF', 'K').

    Returns:
        float: The converted temperature value.
    """
    # Define conversion formulas
    conversion_table = {
        ('degC', 'degF'): lambda x: x * 9/5 + 32,
        ('degF', 'degC'): lambda x: (x - 32) * 5/9,
        ('degC', 'K'): lambda x: x + 273.15,
        ('K', 'degC'): lambda x: x - 273.15,
        ('degF', 'K'): lambda x: (x + 459.67) * 5/9,
        ('K', 'degF'): lambda x: x * 9/5 - 459.67
    }

    # Check if the conversion is possible
    if (from_unit, to_unit) not in conversion_table:
        raise ValueError(f"Cannot convert temperature from {from_unit} to {to_unit}")

    # Convert the temperature value
    conversion_func = conversion_table[(from_unit, to_unit)]
    converted_value = conversion_func(value)

    return converted_value


def convert_pressure(value, from_unit, to_unit):
    """
     Converts pressure from one unit to another.

     Parameters:
        value (float): The pressure value to convert.
        from_unit (str): The unit of the input pressure (e.g., 'Pa', 'atm', 'bar', 'psi').
        to_unit (str): The desired unit for the converted pressure (e.g., 'Pa', 'atm', 'bar', 'psi').

     Returns:
        The converted pressure value.
     """

    conversion_factors = {
        'Pa': {'Pa': 1, 'atm': 9.8692e-6, 'bar': 1e-5, 'psi': 0.000145038},
        'atm': {'Pa': 101325, 'atm': 1, 'bar': 1.01325, 'psi': 14.6959},
        'bar': {'Pa': 1e+5, 'atm': 0.986923, 'bar': 1, 'psi': 14.5038},
        'psi': {'Pa': 6894.76, 'atm': 0.0680459, 'bar': 0.0689476, 'psi': 1}
    }

    # Check if the conversion is possible
    if from_unit not in conversion_factors or to_unit not in conversion_factors:
        raise ValueError(f"Cannot convert pressure from {from_unit} to {to_unit}")

    # Convert the pressure value
    conversion_factor = conversion_factors[from_unit][to_unit]
    converted_value = value * conversion_factor
    return converted_value
