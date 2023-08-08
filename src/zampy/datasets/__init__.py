"""Datasets implementations."""
from zampy.datasets import dataset_protocol
from zampy.datasets import validation
from zampy.datasets.era5 import ERA5
from zampy.datasets.era5_land import ERA5Land
from zampy.datasets.eth_canopy_height import EthCanopyHeight


__all__ = ["dataset_protocol", "validation", "EthCanopyHeight", "ERA5", "ERA5Land"]


# This object tracks which datasets are available.
DATASETS: dict[str, type[dataset_protocol.Dataset]] = {
    # All lowercase key.
    "era5": ERA5,
    "era5_land": ERA5Land,
    "eth_canopy_height": EthCanopyHeight,
}
