# zampy
Tool for downloading Land Surface Model (LSM) input data.

Named after *Zam*; [the Avestan language term for the Zoroastrian concept of "earth"](https://en.wikipedia.org/wiki/Zam).

[![github license badge](https://img.shields.io/github/license/EcoExtreML/zampy)](https://github.com/EcoExtreML/zampy)
[![Documentation Status](https://readthedocs.org/projects/zampy/badge/?version=latest)](https://zampy.readthedocs.io/en/latest/?badge=latest)
[![build](https://github.com/EcoExtreML/zampy/actions/workflows/build.yml/badge.svg)](https://github.com/EcoExtreML/zampy/actions/workflows/build.yml)
[![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=EcoExtreML_zampy&metric=coverage)](https://sonarcloud.io/dashboard?id=EcoExtreML_zampy)


## Outline
`zampy` is designed to retrieve data for LSM model input. It can help you prepare the data within the following steps:
1. **Download** the data for the specified location(s) / geographical area.
2. **Ingest** data into unified (zampy) format.
3. **Load** the variables in a standardized way (standardized names & standardized units).
4. **Convert** the data to standard formats:
    - ALMA / PLUMBER2's ALMA formatted netCDF.
    - *CMOR formatted netCDF*.

(Note: items in *italic* will not be worked on for now/low priority, but we want to allow space for these in the future.)

## Getting start

### Installation
[![workflow pypi badge](https://img.shields.io/pypi/v/zampy.svg?colorB=blue)](https://pypi.python.org/project/zampy/)
[![supported python versions](https://img.shields.io/pypi/pyversions/zampy)](https://pypi.python.org/project/zampy/)

To install the latest release of `zampy`, do:
```console
python3 -m pip install zampy
```

To install the in-development version from the GitHub repository, do:

```console
python3 -m pip install git+https://github.com/EcoExtreML/zampy.git
```

### Configuration
`Zampy` needs to be configured with a simple configuration file.

You need to create this file under your user home directory:

`~/.config/zampy/zampy_config.yml`

The configuration file should contain the `working_directory`, for instance:
```yaml
working_directory: /path_to_a_working_directory/  #for example: /home/bart/Zampy
```

If you need access to data on CDS or ADS server, you should add your CDS or ADS credentials to `zampy_config.yml`:

```yaml
cdsapi:
  url:  # for example https://cds.climate.copernicus.eu/api/v2
  key:  # for example 12345:xhashd-232jcsha-dsaj429-cdjajd29319
adsapi:
  url:  # for example https://ads.atmosphere.copernicus.eu/api/v2
  key:  # for example 12345:xhashd-232jcsha-dsaj429-cdjajd29319
```

About how to create CDS or ADS credentials, check the section below.

### How to use `zampy`

We recommend our users to use `zampy` with recipes.

A "recipe" is a file with yml extension, it defines:
- data downloading
  - time extent.
  - spatial location / bounding box.
  - datasets to be downloaded
    - variables within datasets
- data conversion
  - convert to desired [conventions](./src/zampy/conventions/)
  - output frequency
  - output resolution

A sample recipe can be found in the [documentation](https://zampy.readthedocs.io/en/latest/#how-to-use-zampy).

When you have your reciped created and saved on your disk, you can execute your recipe by running the following code in your shell:

```py
zampy /path_to_recipe/sample_recipe.yml
```

We also provide python API for you to intereact with `zampy`. You can find the example notebooks for each supported dataset [here](./demo/).

## Instructions for CDS/ADS datasets

To download the following datasets, users need access to CDS/ADS via `cdsapi`/`adsapi`:
- CDS
  - ERA5
  - ERA5 land
  - LAI
  - land cover
- ADS
  - CAMS EGG4 (e.g. co2)

To generate these API keys, you need to be a registered user on *CDS* via the [registration page](https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome), or on *ADS* via the [registration page](https://ads.atmosphere.copernicus.eu/user/register?destination=%2F%23!%2Fhome).

Before submitting any request with `zampy`, please put your `cdsapi`/`adsapi` credentials in `zampy_config.yml`. Here is a short [instruction](https://cds.climate.copernicus.eu/api-how-to) about how to find your CDS/ADS API key. You can skip the steps related to `.cdsapirc` and simply add the key to `zampy_config.yml`.

### Agree to the Terms of Use on CDS/ADS

When downloading a dataset for the first time, it is **necessary to agree to the Terms of Use of every datasets that you intend to download**. This can only be done via the CDS/ADS website. When you try to download these datasets, you will be prompted to go to the terms of use and accept them.


## Acknowledgements

This package was developed by the Netherlands eScience Center. Development was supported by the Netherlands eScience Center under grant number NLESC.ASDI.2020.026.