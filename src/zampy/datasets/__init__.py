"""Datasets implementations."""
from zampy.datasets import dataset_protocol
from zampy.datasets import validation
from zampy.datasets.era5 import ERA5
from zampy.datasets.eth_canopy_height import EthCanopyHeight


__all__ = ["dataset_protocol", "validation", "EthCanopyHeight", "ERA5"]


# This object tracks which datasets are available.
DATASETS: dict[str, type[dataset_protocol.Dataset]] = {
    # All lowercase key.
    "era5": ERA5,
    "eth_canopy_height": EthCanopyHeight,
}
