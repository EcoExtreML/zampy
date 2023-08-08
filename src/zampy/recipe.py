""""All functionality to read and execute Zampy recipes."""
from pathlib import Path
from typing import Any
import numpy as np
import yaml
from zampy.datasets import DATASETS
from zampy.datasets import converter
from zampy.datasets.dataset_protocol import Dataset
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds


def recipe_loader(recipe_filename: str) -> dict:
    """Load the yaml recipe into a dictionary, and do some validation."""
    with open(recipe_filename) as f:
        recipe: dict = yaml.safe_load(f)

    if not all(("name", "download", "convert" in recipe.keys())):
        msg = (
            "One of the following items are missing from the recipe:\n"
            "name, download, convert."
        )
        raise ValueError(msg)

    if "datasets" not in recipe["download"].keys():
        msg = "No dataset entry found in the recipe."
        raise ValueError(msg)

    if not all(("convention", "frequency", "resolution" in recipe["convert"].keys())):
        msg = (
            "One of the following items are missing from the recipe:\n"
            "name, download, convert."
        )
        raise ValueError(msg)

    return recipe


def config_loader() -> dict:
    """Load the zampty config and validate the contents."""
    config_path = Path.home() / ".config" / "zampy" / "zampy_config.yml"

    if not config_path.exists():
        msg = f"No config file was found at '{config_path}'"
        raise FileNotFoundError(msg)

    with config_path.open() as f:
        config: dict = yaml.safe_load(f)

    if "working_directory" not in config.keys():
        msg = "No `working_directory` key found in the config file."
        raise ValueError(msg)

    return config


class RecipeManager:
    """The recipe manager is used to get the required info, and then run the recipe."""

    def __init__(self, recipe_filename: str) -> None:
        """Instantiate the recipe manager, using a prepared recipe."""
        # Load & parse recipe
        recipe = recipe_loader(recipe_filename)

        self.start_year, self.end_year = recipe["download"]["years"]
        self.timebounds = TimeBounds(
            np.datetime64(f"{self.start_year}-01-01T00:00"),
            np.datetime64(f"{self.end_year}-12-13T23:59"),
        )
        self.spatialbounds = SpatialBounds(*recipe["download"]["bbox"])

        self.datasets: dict[str, Any] = recipe["download"]["datasets"]

        self.convention = recipe["convert"]["convention"]
        self.frequency = recipe["convert"]["frequency"]
        self.resolution = recipe["convert"]["resolution"]

        # Load & parse config
        config = config_loader()
        self.download_dir = Path(config["working_directory"]) / "download"
        self.ingest_dir = Path(config["working_directory"]) / "ingest"
        self.data_dir = (
            Path(config["working_directory"]) / "output" / str(recipe["name"])
        )  # TODO: strip illegal chars from name.

        # Create required directories if they do not exist yet:
        for dir in [self.data_dir, self.download_dir, self.ingest_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Run the full recipe."""
        for dataset_name in self.datasets:
            _dataset = DATASETS[dataset_name.lower()]
            dataset: Dataset = _dataset()
            variables: list[str] = self.datasets[dataset_name]["variables"]

            # Download datset
            dataset.download(
                download_dir=self.download_dir,
                time_bounds=self.timebounds,
                spatial_bounds=self.spatialbounds,
                variable_names=variables,
            )

            dataset.ingest(self.download_dir, self.ingest_dir)

            ds = dataset.load(
                ingest_dir=self.ingest_dir,
                time_bounds=self.timebounds,
                spatial_bounds=self.spatialbounds,
                variable_names=variables,
                resolution=self.resolution,
                regrid_method="flox",
            )

            ds = converter.convert(ds, dataset, convention=self.convention)

            ds = ds.resample(time=self.frequency).mean()

            comp = dict(zlib=True, complevel=5)
            encoding = {var: comp for var in ds.data_vars}
            fname = (  # e.g. "era5_2010-2020.nc"
                f"{dataset_name.lower()}_" f"{self.start_year}-{self.end_year}" ".nc"
            )
            ds.to_netcdf(path=self.data_dir / fname, encoding=encoding)

        print(
            "Finished running the recipe. Output data can be found at:\n"
            f"    {self.data_dir}"
        )
