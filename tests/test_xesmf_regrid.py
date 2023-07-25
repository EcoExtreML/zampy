"""Unit test for regridding functions with xesmf."""

from pathlib import Path
import numpy as np
import pytest
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.eth_canopy_height import parse_tiff_file


XESMF_INSTALLED = True
try:
    import xesmf as _  # noqa: F401 (unused import)
    from zampy.utils import xesmf_regrid
except ImportError:
    XESMF_INSTALLED = False


@pytest.mark.skipif(not XESMF_INSTALLED, reason="xesmf is not installed")
def test_create_new_grid():
    bbox = SpatialBounds(54, 6, 51, 3)
    ds = xesmf_regrid.create_new_grid(spatial_bounds=bbox, resolution=1.0)
    expected_lat = [51.0, 52.0, 53.0, 54.0]
    expected_lon = [3.0, 4.0, 5.0, 6.0]

    np.testing.assert_allclose(ds.latitude.values, expected_lat)
    np.testing.assert_allclose(ds.longitude.values, expected_lon)


@pytest.mark.skipif(not XESMF_INSTALLED, reason="xesmf is not installed")
def test_xesfm_regrid():
    # load dummy dataset
    path_dummy_data = (
        Path(__file__).resolve().parent / "test_data" / "eth-canopy-height"
    )
    dummy_dataset = parse_tiff_file(
        path_dummy_data / "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    )

    bbox = SpatialBounds(54, 6, 51, 3)
    ds = xesmf_regrid.xesfm_regrid(
        data=dummy_dataset, spatial_bounds=bbox, resolution=1.0
    )

    expected_lat = [51.0, 52.0, 53.0, 54.0]
    expected_lon = [3.0, 4.0, 5.0, 6.0]

    np.testing.assert_allclose(ds.latitude.values, expected_lat)
    np.testing.assert_allclose(ds.longitude.values, expected_lon)
