"""Unit test for regridding functions with xesmf."""

import pytest


try:
    import xesmf as _  # noqa: F401 (unused import)
except ImportError:
    xesmf_installed = False


@pytest.mark.skipif(not xesmf_installed, reason="xesmf is not installed")
def test_create_new_grid():
    pass


@pytest.mark.skipif(not xesmf_installed, reason="xesmf is not installed")
def test_xesfm_regrid():
    pass