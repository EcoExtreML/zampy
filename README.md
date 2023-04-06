# lsmdata
Tool for downloading Land Surface Model input data


## Tool outline:

 - Goal is to retrieve data for LSM model input.
    1. First **download** the data for the specified location(s) / geographical area.
    2. Be able to **load** the variables in a standardized way (standardized names & standardized units).
    3. **Output** the data to standard formats:
       - ALMA / PLUMBER2's ALMA formatted netCDF.
       - *CMOR formatted netCDF*.
 - User-interaction should go through recipes. For example, see [springtime](https://github.com/phenology/springtime/blob/main/tests/recipes/daymet.yaml).
   - Recipes define:
     - data folder (where data should be downloaded to)
     - time extent.
     - spatial location / bounding box.
     - datasets to be used
       - variables within datasets
   - Load recipes using Pydantic ([for example](https://github.com/phenology/springtime/blob/main/src/springtime/datasets/daymet.py)).
 - Support both a CLI & Python API.

Note: items in *italic* will not be worked on for now/low priority, but we want to allow space for these in the future.