"""Dataset formatter for different conventions."""
from pathlib import Path
import xarray as xr


def convert(
        dataset: xr.DataArray,
        fname: str,
        output_path: Path,
        convention: str="ALMA"):
    """Convert ETH Canopy Height dataset to follow the specified convention."""
    # change the extension from "tif" to "nc"
    if convention == "ALMA":
        # question: drop "spatial_ref"?
        dataset.to_netcdf(output_path / fname, format="NETCDF4")
    else:
        raise ValueError(f"The {convention} convention is not supported."
                         "Please use another convention.")
