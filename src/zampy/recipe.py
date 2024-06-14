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
from zampy.datasets.validation import validate_download_request


def recipe_loader(recipe_path: Path) -> dict:
    """Load the yaml recipe into a dictionary, and do some validation."""
    with recipe_path.open() as f:
        recipe: dict = yaml.safe_load(f)

    if not all(key in recipe.keys() for key in ["name", "download", "convert"]):
        msg = (
            "One of the following items are missing from the recipe:\n"
            "name, download, convert."
        )
        raise ValueError(msg)

    if "datasets" not in recipe["download"].keys():
        msg = "No dataset entry found in the recipe."
        raise ValueError(msg)

    if not all(
        key in recipe["convert"].keys()
        for key in ["convention", "frequency", "resolution"]
    ):
        msg = (
            "One of the following 'convert' items are missing from the recipe:\n"
            "convention, frequency, resolution."
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

    if not isinstance(config, dict) or "working_directory" not in config.keys():
        msg = "No `working_directory` key found in the config file."
        raise ValueError(msg)

    return config


class RecipeManager:
    """The recipe manager is used to get the required info, and then run the recipe."""

    def __init__(self, recipe_path: Path) -> None:
        """Instantiate the recipe manager, using a prepared recipe."""
        # Load & parse recipe
        recipe = recipe_loader(recipe_path)

        self.start_time, self.end_time = recipe["download"]["time"]
        self.timebounds = TimeBounds(
            convert_time(f"{self.start_time}"),
            convert_time(f"{self.end_time}"),
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
        )

        # Create required directories if they do not exist yet:
        for dir in [self.data_dir, self.download_dir, self.ingest_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Run the full recipe."""
        # First validate all inputs (before downloading, processing...)
        for dataset_name in self.datasets:
            _dataset = DATASETS[dataset_name.lower()]
            dataset: Dataset = _dataset()

            validate_download_request(
                dataset,
                self.download_dir,
                self.timebounds,
                self.spatialbounds,
                self.datasets[dataset_name]["variables"],
            )

        for dataset_name in self.datasets:
            _dataset = DATASETS[dataset_name.lower()]
            dataset = _dataset()
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
            )

            ds = converter.convert(ds, dataset, convention=self.convention)

            if "time" in ds.dims:  # Dataset with only DEM (e.g.) has no time dim.
                ds = ds.resample(time=self.frequency).mean()

            comp = dict(zlib=True, complevel=5)
            encoding = {var: comp for var in ds.data_vars}
            time_start = str(self.timebounds.start.astype("datetime64[Y]"))
            time_end = str(self.timebounds.end.astype("datetime64[Y]"))
            # e.g. "era5_2010-2020.nc"
            fname = f"{dataset_name.lower()}_{time_start}-{time_end}.nc"
            ds.to_netcdf(path=self.data_dir / fname, encoding=encoding)
            del ds

        print(
            "Finished running the recipe. Output data can be found at:\n"
            f"    {self.data_dir}"
        )


def convert_time(time: str) -> np.datetime64:
    """Check input time and convert to np.datetime64."""
    try:
        timestamp = np.datetime64(time)
    except ValueError as err:
        msg = (
            "The input format of timestamp in the recipe is incorrect. \n Please"
            " follow the format of `numpy.datetime64` and update the input time,"
            " e.g. 'YYYY-MM-DD'."
        )
        raise ValueError(msg) from err

    return timestamp
