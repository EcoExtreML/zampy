"""Test the recipe loader."""
import pytest
from zampy.recipe import recipe_loader


valid_recipe = """
name: "Test recipe 2"
download:
  years: [2020, 2020]
  bbox: [54, 6, 50, 3] # NESW
  datasets:
    era5:
      variables:
        - 10m_v_component_of_wind
        - surface_pressure
convert:
  convention: ALMA
  frequency: 1H
  resolution: 0.5
"""

recipe_missing_datasets = """
name: "Test recipe 2"
download:
  years: [2020, 2020]
  bbox: [54, 6, 50, 3] # NESW
convert:
  convention: ALMA
  frequency: 1H
  resolution: 0.5
"""

recipe_missing_name = """
download:
  years: [2020, 2020]
  bbox: [54, 6, 50, 3] # NESW
  datasets:
    era5:
      variables:
        - 10m_v_component_of_wind
        - surface_pressure
convert:
  convention: ALMA
  frequency: 1H
  resolution: 0.5
"""

recipe_missing_convention = """
name: "Test recipe 2"
download:
  years: [2020, 2020]
  bbox: [54, 6, 50, 3] # NESW
  datasets:
    era5:
      variables:
        - 10m_v_component_of_wind
        - surface_pressure
convert:
  frequency: 1H
  resolution: 0.5
"""


def test_valid_recipe(tmp_path):
    recipe_path = tmp_path / "valid_recipe.yml"
    with recipe_path.open("w") as f:
        f.write(valid_recipe)
    recipe_loader(recipe_path)


@pytest.mark.parametrize(
    "recipe", [recipe_missing_convention, recipe_missing_datasets, recipe_missing_name]
)
def test_invalid_recipes(tmp_path, recipe):
    recipe_path = tmp_path / "invalid_recipe.yml"
    with recipe_path.open("w") as f:
        f.write(recipe)

    with pytest.raises(ValueError):
        recipe_loader(recipe_path)
