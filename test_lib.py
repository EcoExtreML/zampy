import zampy
from pathlib import Path
 
bounds = zampy.datasets.eth_canopy_height.SpatialBounds(60, 10, 50, 0)

dataset = zampy.datasets.EthCanopyHeight()

dataset.download(
    download_dir=Path("/home/bart/Zampy"),
    spatial_bounds=bounds,
    temporal_bounds=None,
    variables=None,
)
