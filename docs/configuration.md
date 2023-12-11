## Installation
Zampy can be installed by doing:

```console
python3 -m pip install zampy
```

To install the in-development version from the GitHub repository, do:

```console
python3 -m pip install git+https://github.com/EcoExtreML/zampy.git
```

## Configuration
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
