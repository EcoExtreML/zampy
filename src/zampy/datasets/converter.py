"""Dataset formatter for different conventions."""
import json
import warnings
from pathlib import Path
from typing import Union
import cf_xarray.units  # ruff: noqa: F401
import pint_xarray  # ruff: noqa: F401
import xarray as xr
from zampy.datasets.dataset_protocol import Dataset


CONVENTIONS = {
    "ALMA": "src/zampy/conventions/ALMA.json",
}


def check_convention(convention):
    """Check if the given convention is supported."""
    if convention.upper() not in CONVENTIONS:
        raise ValueError(
            f"The '{convention}' convention is not supported.\n"
            "Please check the available conventions in the `conventions` "
            "directory and choose one from there."
        )
    else:
        print(f"Start converting data to follow the '{convention}' convention.")


def convert(
    data: xr.Dataset, dataset: Dataset, convention: Union[str, Path]
) -> xr.Dataset:
    """Convert a loaded dataset to the specified convention."""
    converted = False
    convention_file = open(Path(CONVENTIONS[convention]), encoding="UTF8")
    convention_dict = json.load(convention_file)
    for var in data.data_vars:
        if var.lower() in convention_dict:
            convert_units = convention_dict[var.lower()]["units"]
            var_name = convention_dict[var.lower()]["variable"]
            var_units = data[var].attrs["units"]
            if var_units != convert_units:
                converted = True
                # lazy dask array
                data = _convert_var(data, var, convert_units)
            data = data.rename({var: var_name})
            print(f"{var} renamed to {var_name}.")

        else:
            print(f"Variable '{var}' is not included in '{convention}' convention.")

    convention_file.close()

    if converted:
        print(
            f"Conversion of dataset '{dataset.name}' following {convention} "
            "convention is complete!"
        )
    else:
        warnings.warn(
            f"All variables already follow the {convention} convention or "
            f"not included in the {convention} convention.\n"
            f"No conversion operation was performed on '{dataset.name}'."
        )

    return data


def _convert_var(
    data: xr.Dataset, var: str, new_units: str
) -> xr.Dataset:
    """Convert variable with given units.

    pint-xarray is used here for the unit conversion. It supports xarray and dask.
    We need to import `pint_xarray` for this.
    Note: `cf_xarray.units` is also needed to support units of latitude and longitude.
    """
    # make a copy to avoid in-place modification
    data = data.copy()
    data[var] = data[var].pint.quantify().pint.to(new_units)
    # convert pint arrays back into NumPy arrays, so the variable only contains numpy
    # array with units as xarray attributes (otherwise the variable is a pint array
    # object with unit) for more details, please check
    # https://xarray.dev/blog/introducing-pint-xarray#dequantifying
    data = data.pint.dequantify()

    return data
