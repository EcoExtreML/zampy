"""Testing a simple recipe."""
from pathlib import Path
from unittest.mock import patch
import generate_test_data
import numpy as np
import xarray as xr
from zampy.datasets import DATASETS
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import write_properties_file
from zampy.recipe import RecipeManager


RECIPE_FILE = Path(__file__).parent / "recipes" / "era5_recipe.yml"


def test_recipe(tmp_path: Path, mocker):
    with (patch.object(DATASETS["era5"], "download"),):
        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-12-31T23:59")
        )
        variables = ["10m_v_component_of_wind", "surface_pressure"]

        generate_test_data.generate_era5_files(
            directory=tmp_path / "download",
            variables=variables,
            spatial_bounds=spatial_bounds,
            time_bounds=time_bounds,
        )
        write_properties_file(
            tmp_path / "download" / "era5", spatial_bounds, time_bounds, variables
        )

        rm.run()

        ds = xr.open_mfdataset(str(tmp_path / "output" / "era5_recipe" / "*.nc"))
        assert all(var in ds.data_vars for var in ["Psurf", "Wind_N"])
