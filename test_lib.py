import zampy
from pathlib import Path
from zampy.datasets.dataset_protocol import Variable
 
bounds = zampy.datasets.eth_canopy_height.SpatialBounds(54, 6, 50, 3)

dataset = zampy.datasets.EthCanopyHeight()

varbs = [Variable("h_canopy", unit="m"), Variable("h_canopy_SD", unit="m")]

dataset.download(
    download_dir=Path("/home/bart/Zampy"),
    spatial_bounds=bounds,
    temporal_bounds=None,
    variables=varbs,
)
