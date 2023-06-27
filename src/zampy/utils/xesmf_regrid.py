"""xesmf specific regridding implementation."""
import numpy as np
import xarray as xr
import xesmf
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.utils import regrid


def create_new_grid(spatial_bounds: SpatialBounds, resolution: float) -> xr.Dataset:
    """Create a dataset describing the new grid."""
    return xr.Dataset(
        {
            "latitude": (
                ["latitude"],
                np.arange(
                    spatial_bounds.south,
                    spatial_bounds.north + 0.9 * resolution,
                    resolution,
                ),
            ),
            "longitude": (
                ["longitude"],
                np.arange(
                    spatial_bounds.west,
                    spatial_bounds.east + 0.9 * resolution,
                    resolution,
                ),
            ),
        }
    )


def xesfm_regrid(
    data: xr.Dataset, spatial_bounds: SpatialBounds, resolution: float
) -> xr.Dataset:
    """Regrid a dataset to a new grid, using the xESMF library.

    Args:
        data: Input dataset.
        spatial_bounds: Spatial bounds of the new grid.
        resolution: Resolution of the new grid.

    Returns:
        Regridded input dataset
    """
    data_resolution = regrid.infer_resolution(data)
    old_resolution = min(data_resolution)
    regrid_method = "bilinear" if resolution < old_resolution else "conservative"

    ds_grid = create_new_grid(spatial_bounds, resolution)

    regridder = xesmf.Regridder(
        data, ds_grid, method=regrid_method, unmapped_to_nan=True
    )
    return regridder(
        data.chunk({"latitude": -1, "longitude": -1}),
        keep_attrs=True,
        skipna=True,
        na_thres=0.1,  # max 10% NaN values
    )
