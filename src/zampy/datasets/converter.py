"""Dataset formatter for different conventions."""
import json
from pathlib import Path
from pint import UnitRegistry
import xarray as xr


CONVENTIONS = {
    "ALMA": "src/zampy/conventions/ALMA.json",
}


def convert(
        dataset: xr.Dataset,
        fname: str,
        output_path: Path,
        convention: str):
    """Convert ETH Canopy Height dataset to follow the specified convention."""
    # create unit registry
    ureg = UnitRegistry()
    # Load convention file
    with open(CONVENTIONS[convention], 'r') as convention_file:
        convention_dict = json.load(convention_file)
        for var in dataset.data_vars:
            if var in convention_dict:
                convert_units = convention_dict[var]["units"]
                var_units = dataset[var].attrs["units"]
                if  var_units != convert_units:
                    var_old = dataset[var].values * ureg(var_units)
                    var_convert = var_old.to(ureg(convert_units)).magnitude
                    # assign converted values to dataset
                    dataset[var][:] = var_convert
                    dataset[var].attrs["units"] = convert_units
                    # save converted dataset
                    dataset.to_netcdf(output_path / fname, format="NETCDF4")

            else:
                print(f"Variable {var} is not included in {convention} convention.")
