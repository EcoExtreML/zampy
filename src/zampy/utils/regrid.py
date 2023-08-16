"""Zampy regridding functions."""
import numpy as np
import pandas as pd
import xarray as xr
from flox import xarray as floxarray
from zampy.datasets.dataset_protocol import SpatialBounds


def assert_xesmf_available() -> None:
    """Util that attempts to load the optional module xesmf."""
    try:
        import xesmf as _  # noqa: F401 (unused import)

    except ImportError as e:
        raise ImportError(
            "Could not import the `xesmf` module.\nPlease install this"
            " before continuing, with either `pip` or `conda`."
        ) from e


def infer_resolution(dataset: xr.Dataset) -> tuple[float, float]:
    """Infer the resolution of a dataset's latitude and longitude coordinates.

    Args:
        dataset: dataset with latitude and longitude coordinates.

    Returns:
        The latitude and longitude resolution.
    """
    resolution_lat = np.median(
        np.diff(
            dataset["latitude"].to_numpy(),
            n=1,
        )
    )
    resolution_lon = np.median(
        np.diff(
            dataset["longitude"].to_numpy(),
            n=1,
        )
    )

    return (resolution_lat, resolution_lon)


def _groupby_regrid(
    data: xr.Dataset,
    spatial_bounds: SpatialBounds,
    resolution: float,
) -> xr.Dataset:
    """Coarsen a dataset using xrarray's groupby method.

    Args:
        data: Input dataset.
        spatial_bounds: Spatial bounds of the new grid.
        resolution: Resolution of the new grid.

    Returns:
        Regridded input dataset
    """
    # Determine the minumum number of datapoints per group. Simulates xesmf's na_thres.
    na_thres = 0.10
    data_resolution = infer_resolution(data)
    n_points = (resolution / data_resolution[0]) * (resolution / data_resolution[1])
    min_points = int(n_points * (1 - na_thres))

    # Create bins to group by. Offset by 0.5*resolution, so bins are centered.
    lat_bins = pd.interval_range(
        start=spatial_bounds.south - 0.5 * resolution,
        end=spatial_bounds.north + 0.5 * resolution,
        periods=np.round((spatial_bounds.north - spatial_bounds.south) / resolution)
        + 1,
        closed="left",  # Closed "both" is not implemented (yet) in Flox
    )
    lon_bins = pd.interval_range(
        spatial_bounds.west - 0.5 * resolution,
        spatial_bounds.east + 0.5 * resolution,
        periods=np.round((spatial_bounds.east - spatial_bounds.west) / resolution) + 1,
        closed="left",  # Closed "both" is not implemented (yet) in Flox
    )

    # Group by the bins and reduce w/ mean
    ds_out = floxarray.xarray_reduce(
        data,
        "latitude",
        "longitude",
        func="mean",
        expected_groups=(lat_bins, lon_bins),
        isbin=True,
        skipna=True,
        min_count=min_points,
    )

    # Convert *_bins dimensions back to latitude and longitude
    ds_out["latitude"] = (
        "latitude_bins",
        [v.mid for v in ds_out["latitude_bins"].values],
    )
    ds_out["longitude"] = (
        "longitude_bins",
        [v.mid for v in ds_out["longitude_bins"].values],
    )
    ds_out = ds_out.set_coords(["latitude", "longitude"])
    ds_out = ds_out.swap_dims(
        {"latitude_bins": "latitude", "longitude_bins": "longitude"}
    )
    ds_out = ds_out.drop_vars(["latitude_bins", "longitude_bins"])
    if "time" in ds_out.dims:
        return ds_out.transpose("time", "latitude", "longitude", ...)
    else:
        return ds_out.transpose("latitude", "longitude", ...)


def _interp_regrid(
    data: xr.Dataset,
    spatial_bounds: SpatialBounds,
    resolution: float,
) -> xr.Dataset:
    """Refine a dataset using xrarray's interp method.

    Args:
        data: Input dataset.
        spatial_bounds: Spatial bounds of the new grid.
        resolution: Resolution of the new grid.

    Returns:
        Regridded input dataset
    """
    lat_coords = np.arange(
        spatial_bounds.south, spatial_bounds.north + resolution, resolution
    )
    lon_coords = np.arange(
        spatial_bounds.west, spatial_bounds.east + resolution, resolution
    )

    return data.interp(
        coords={
            "latitude": lat_coords,
            "longitude": lon_coords,
        },
        method="linear",
    )


def flox_regrid(
    data: xr.Dataset,
    spatial_bounds: SpatialBounds,
    resolution: float,
) -> xr.Dataset:
    """Regrid a dataset to a new grid, using xarray + flox methods.

    Data will be regridded using groupby and/or linear interpolation, depending on the
    ratio between the old and new resolution.

    This regridding method is a rough approximation that will work fine in most cases,
    but can struggle in some areas:
        - There is no weighted averaging performed: areas near the poles will
            incorrectly contribute more to the total average.
        - To achieve a conservative regrid-like method, data of a resolution close to
            the new resolution is first interpolated (to a finer resolution), and then
            regridded to the intended resolution. This will lead to small
            inconsistencies with NaN thresholds.

    For a more robust method use the xesmf regridding option, however this does require
    installation through conda/mamba, and is not available on Windows.

    Args:
        data: Input dataset.
        spatial_bounds: Spatial bounds of the new grid.
        resolution: Resolution of the new grid.

    Returns:
        Regridded input dataset
    """
    data_resolution = infer_resolution(data)
    old_resolution = min(data_resolution)

    # # Use Nyquist-like criterion to avoid aliasing.
    # # At a 4x courser resolution, no issues: just groupy-regrid.
    if resolution >= 4 * old_resolution:
        return _groupby_regrid(data, spatial_bounds, resolution)

    # At a 4x finer resolution: no issues: just interpolate.
    if resolution <= 0.25 * old_resolution:
        return _interp_regrid(data, spatial_bounds, resolution)

    # Otherwise we first regrid to a finer grid, and then reduce:
    else:
        ds_in_interp = _interp_regrid(data, spatial_bounds, old_resolution / 4)
        return _groupby_regrid(ds_in_interp, spatial_bounds, resolution)


def regrid_data(
    data: xr.Dataset,
    spatial_bounds: SpatialBounds,
    resolution: float,
    method: str = "flox",
) -> xr.Dataset:
    """Regrid a dataset to a new grid.

    Args:
        data: Input dataset.
        spatial_bounds: Spatial bounds of the new grid.
        resolution: Resolution of the new grid.
        method: Which routines to use to resample. Either "flox" (default) or "esmf".
            Of these two, esmf is the more robust and accurate regridding method,
            however it can be difficult to install.

    Returns:
        Regridded input dataset
    """
    if method == "flox":
        return flox_regrid(data, spatial_bounds, resolution)

    elif method == "esmf":
        assert_xesmf_available()
        from zampy.utils.xesmf_regrid import xesfm_regrid

        return xesfm_regrid(data, spatial_bounds, resolution)

    else:
        raise ValueError(f"Unknown regridding method '{method}'")
