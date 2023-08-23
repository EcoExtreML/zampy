"""CO2 dataset."""

import numpy as np
from zampy.datasets.dataset_protocol import SpatialBounds
from zampy.datasets.dataset_protocol import TimeBounds
from zampy.datasets.dataset_protocol import Variable
from zampy.datasets.ecmwf_dataset import ECMWFDataset
from zampy.reference.variables import VARIABLE_REFERENCE_LOOKUP
from zampy.reference.variables import unit_registry


class CAMS(ECMWFDataset):  # noqa: D101
    name = "cams"
    time_bounds = TimeBounds(np.datetime64("2003-01-01"), np.datetime64("2020-12-31"))
    spatial_bounds = SpatialBounds(90, 180, -90, -180)

    raw_variables = [Variable(name="co2", unit=unit_registry.kilogram_per_kilogram)]

    # variable names used in adsapi downloading request
    cds_var_names = {"co2_concentration": "carbon_dioxide"}
    variable_names = list(cds_var_names.keys())

    variables = [VARIABLE_REFERENCE_LOOKUP[var] for var in variable_names]

    # "https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf"
    license = "licence-to-use-copernicus-products"

    bib = """
    @article{agusti2023cams,
        title={The CAMS greenhouse gas reanalysis from 2003 to 2020},
        author={Agusti-Panareda, Anna et al.},
        journal={Atmospheric Chemistry and Physics},
        volume={23},
        number={6},
        pages={3829--3859},
        year={2023},
        publisher={Copernicus Publications G{\"o}ttingen, Germany}
        }
    """

    data_url = "https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-ghg-reanalysis-egg4?tab=form"

    cds_dataset = "cams-global-ghg-reanalysis-egg4"
