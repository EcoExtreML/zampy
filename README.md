# zampy
Tool for downloading Land Surface Model input data

[![github license badge](https://img.shields.io/github/license/EcoExtreML/zampy)](https://github.com/EcoExtreML/zampy)
[![build](https://github.com/EcoExtreML/zampy/actions/workflows/build.yml/badge.svg)](https://github.com/EcoExtreML/zampy/actions/workflows/build.yml)
[![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=EcoExtreML_zampy&metric=coverage)](https://sonarcloud.io/dashboard?id=EcoExtreML_zampy)


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

## Instructions for CDS datasets (e.g. ERA5)
To download the following datasets, users need access to CDS via cdsapi:

- ERA5
- ERA5 land
- LAI

First, you need to be a registered user on CDS via the [registration page](https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome).

Before submitting any request with `zampy`, please configure your `.cdsapirc` file following the instructions on https://cds.climate.copernicus.eu/api-how-to.

## Instructions for ADS datasets (e.g. CAMS)
To download the following datasets, users need access to ADS via cdsapi:

- CAMS (e.g. co2)

First, you need to be a registered user on ADS via the [registration page](https://ads.atmosphere.copernicus.eu/user/register?destination=%2F%23!%2Fhome).

Before submitting any request with `zampy`, please configure your `.adsapirc` file following the instructions on https://cds.climate.copernicus.eu/api-how-to.

### Agree to the Terms of Use on CDS/ADS

When downloading a dataset for the first time, it is **necessary to agree to the Terms of Use of every datasets that you intend to download**. This can only be done via the CDS website. When you try to download these datasets, you will be prompted to go to the terms of use and accept them.