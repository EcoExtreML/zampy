"""Generates test data for running the recipe tests."""
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


def generate_era5_file(
    varname: str,
    time_bounds: TimeBounds,
    spatial_bounds: SpatialBounds,
    test_value: float,
    resolution: float,
    time_res="1H",
) -> xr.Dataset:
    time_coords = pd.date_range(
        start=time_bounds.start, end=time_bounds.end, freq=time_res, inclusive="left"
    )
    lat_coords = np.arange(
        start=np.round(spatial_bounds.south - 1),
        stop=np.round(spatial_bounds.north + 1),
        step=resolution,
    )
    lon_coords = np.arange(
        start=np.round(spatial_bounds.west - 1),
        stop=np.round(spatial_bounds.east + 1),
        step=resolution,
    )
    data = np.zeros((len(lon_coords), len(lat_coords), len(time_coords))) + test_value

    ds = xr.Dataset(
        data_vars={ERA5_LOOKUP[varname][1]: (("longitude", "latitude", "time"), data)},
        coords={
            "longitude": lon_coords,
            "latitude": lat_coords,
            "time": time_coords,
        },
    )
    ds[ERA5_LOOKUP[varname][1]].attrs["units"] = ERA5_LOOKUP[varname][0]
    ds["latitude"].attrs["units"] = "degrees_north"
    ds["longitude"].attrs["units"] = "degrees_east"

    return ds


ERA5_LOOKUP = {  # name: (unit, fname)
    "10m_u_component_of_wind": ("m s**-1", "u10"),
    "10m_v_component_of_wind": ("m s**-1", "v10"),
    "surface_pressure": ("Pa", "sp"),
}


def generate_era5_files(
    directory: Path,
    variables: list[str],
    spatial_bounds: SpatialBounds,
    time_bounds: TimeBounds,
) -> None:
    data_dir_era5 = directory / "era5"
    data_dir_era5.mkdir()

    for var in variables:
        ds = generate_era5_file(
            varname=var,
            time_bounds=time_bounds,
            spatial_bounds=spatial_bounds,
            test_value=1.0,
            resolution=0.25,
        )
        ds.to_netcdf(path=data_dir_era5 / f"era5_{var}.nc")
