"""This module contains all tests for datasets included in zampy."""

from pathlib import Path
from zampy.recipe import config_loader
from . import generate_test_data


test_folder = Path(__file__).resolve().parents[0]
data_folder = test_folder / "test_data"

ALL_DAYS = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31",
]  # fmt: skip

ALL_HOURS = [
    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00",
    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
    "21:00", "22:00", "23:00",
]  # fmt: skip


# Generate test data if it does not exist
# it assumes that the recipe
# zampy/recipes/STEMMUS_SCOPE_input.yml has been ran.
config = config_loader()
download_dir = Path(config["working_directory"]) / "download"

if not data_folder.exists():
   data_folder.mkdir(parents=True, exist_ok=True)
   generate_test_data.generate_test_data(download_dir, data_folder)
