"""Catalog of datasets."""

from zampy.datasets import dataset_protocol
from zampy.datasets.cams import CAMS
from zampy.datasets.era5 import ERA5
from zampy.datasets.era5 import ERA5Land
from zampy.datasets.eth_canopy_height import EthCanopyHeight
from zampy.datasets.fapar_lai import FaparLAI
from zampy.datasets.land_cover import LandCover
from zampy.datasets.prism_dem import PrismDEM30
from zampy.datasets.prism_dem import PrismDEM90


# This object tracks which datasets are available.
DATASETS: dict[str, type[dataset_protocol.Dataset]] = {
    # All lowercase key.
    "era5": ERA5,
    "era5_land": ERA5Land,
    "cams": CAMS,
    "eth_canopy_height": EthCanopyHeight,
    "prism_dem_30": PrismDEM30,
    "prism_dem_90": PrismDEM90,
    "fapar_lai": FaparLAI,
    "land_cover": LandCover,
}
