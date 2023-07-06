"""Unit test for regridding functions with xesmf."""

import pytest


XESMF_INSTALLED = True
try:
    import xesmf as _  # noqa: F401 (unused import)
except ImportError:
    XESMF_INSTALLED = False


@pytest.mark.skipif(not XESMF_INSTALLED, reason="xesmf is not installed")
def test_create_new_grid():
    pass


@pytest.mark.skipif(not XESMF_INSTALLED, reason="xesmf is not installed")
def test_xesfm_regrid():
    pass
