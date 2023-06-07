"""Dataset formatter for different conventions."""
import json
from pathlib import Path
import xarray as xr
from pint import UnitRegistry


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


def convert(dataset: xr.Dataset, fname: str, output_path: Path, convention: Union[str, Path]):
    """Convert ETH Canopy Height dataset to follow the specified convention."""
    # checker of conversion
    if_convert = False
    # Load convention file
    with Path(CONVENTIONS[convention]).open(
        mode="r", encoding="utf-8"
    ) as convention_file:
        convention_dict = json.load(convention_file)
        for var in dataset.data_vars:
            if var in convention_dict:
                convert_units = convention_dict[var]["units"]
                var_units = dataset[var].attrs["units"]
                if var_units != convert_units:
                    if_convert = True
                    # save converted dataset
                    _convert_var(dataset, var, var_units, convert_units).to_netcdf(
                        output_path / fname, format="NETCDF4"
                    )
            else:
                print(f"Variable '{var}' is not included in '{convention}' convention.")

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


def _convert_var(
    dataset: xr.Dataset, var: str, old_units: str, new_units: str
) -> xr.Dataset:
    """Convert variable with given units."""
    # create unit registry
    ureg = UnitRegistry()
    # assign values with old units
    var_old = dataset[var].values * ureg(old_units)
    # convert to new units
    var_convert = var_old.to(ureg(new_units)).magnitude
    # assign converted values to dataset and update units
    dataset[var][:] = var_convert
    dataset[var].attrs["units"] = new_units

    return dataset
