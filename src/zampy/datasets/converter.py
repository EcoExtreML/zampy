"""Dataset formatter for different conventions."""
import json
from pathlib import Path
from typing import Union
import cf_xarray.units  # ruff: noqa: F401
import pint_xarray  # ruff: noqa: F401
import xarray as xr


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
    dataset: xr.Dataset, fname: str, convention: Union[str, Path]
) -> xr.Dataset:
    """Convert a loaded dataset to the specified convention."""
    converted = False
    convention_file = open(Path(CONVENTIONS[convention]), encoding="UTF8")
    convention_dict = json.load(convention_file)
    for var in dataset.data_vars:
        if var.lower() in convention_dict:
            convert_units = convention_dict[var.lower()]["units"]
            var_units = dataset[var].attrs["units"]
            if var_units != convert_units:
                if_convert = True
                # lazy dask array
                dataset = _convert_var(dataset, var, convert_units)

        else:
            print(f"Variable '{var}' is not included in '{convention}' convention.")

    convention_file.close()

    if if_convert:
        print(
            f"Conversion of dataset '{fname}' following {convention} "
            "convention is complete!"
        )
    else:
        print(
            f"All variables already follow the {convention} convention or "
            f"not included in the {convention} convention.\n"
            f"No conversion operation was performed on '{fname}'."
        )

    return dataset


def _convert_var(
    dataset: xr.Dataset, var: str, new_units: str
) -> xr.Dataset:
    """Convert variable with given units.

    pint-xarray is used here for the unit conversion. It supports xarray and dask.
    We need to import `pint_xarray` for this.
    Note: `cf_xarray.units` is also needed to support units of latitude and longitude.
    """
    # make a copy to avoid in-place modification
    dataset = dataset.copy()
    dataset[var] = dataset[var].pint.quantify().pint.to(new_units)
    # convert pint arrays back into NumPy arrays
    dataset = dataset.pint.dequantify()

    return dataset
