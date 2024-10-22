"""Testing a simple recipe."""

from pathlib import Path
from unittest.mock import patch
import dask.distributed
import generate_test_data
import numpy as np
import pytest
import xarray as xr
from zampy.datasets import DATASETS
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import write_properties_file
from zampy.recipe import RecipeManager
from zampy.recipe import convert_time


RECIPE_FILE = Path(__file__).parent / "recipes" / "era5_recipe.yml"


def test_recipe(tmp_path: Path, mocker):
    with (
        patch.object(DATASETS["era5"], "download"),
    ):
        dask.distributed.Client()

        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-12-31T23:59")
        )
        variables = ["northward_component_of_wind", "surface_pressure"]

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
        # Check if time frequency is correct
        assert ds.time.diff("time").min() == np.timedelta64(1, "h")

def test_recipe_with_lower_frequency(tmp_path: Path, mocker):
    with (
        patch.object(DATASETS["era5"], "download"),
    ):
        dask.distributed.Client()

        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())
        rm.frequency = "6h"  # change the frequency of the recipe

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-01-01T23:59")
        )
        variables = ["northward_component_of_wind", "surface_pressure"]

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
        # check the lenght of the time dimension, mean values are used
        assert len(ds.time) == 4

def test_recipe_with_higher_frequency(tmp_path: Path, mocker):
    with (
        patch.object(DATASETS["era5"], "download"),
    ):
        dask.distributed.Client()

        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())
        rm.frequency = "30min"  # change the frequency of the recipe

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-01-01T23:59")
        )
        variables = ["northward_component_of_wind", "surface_pressure"]

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
        # check the lenght of the time dimension, data is interpolated
        assert len(ds.time) == 47

def test_recipe_with_two_time_values(tmp_path: Path, mocker):
    with (
        patch.object(DATASETS["era5"], "download"),
    ):
        dask.distributed.Client()

        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-01-01T02:00")
        )
        variables = ["northward_component_of_wind", "surface_pressure"]

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
        # check the lenght of the time dimension
        assert len(ds.time) == 2


def test_recipe_with_one_time_values(tmp_path: Path, mocker):
    with (
        patch.object(DATASETS["era5"], "download"),
    ):
        dask.distributed.Client()

        mocker.patch(
            "zampy.recipe.config_loader",
            return_value={"working_directory": str(tmp_path.absolute())},
        )
        rm = RecipeManager(RECIPE_FILE.absolute())

        spatial_bounds = SpatialBounds(51, 4, 50, 3)
        time_bounds = TimeBounds(
            np.datetime64("2020-01-01T00:00"), np.datetime64("2020-01-01T00:00")
        )
        variables = ["northward_component_of_wind", "surface_pressure"]

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
        # check the lenght of the time dimension, should not do interpolation or
        # extrapolation in time
        assert len(ds.time) == 1


def test_invalid_time_format():
    time_from_recipe = "2020-1-01"
    with pytest.raises(ValueError, match="The input format of timestamp"):
        convert_time(time_from_recipe)
