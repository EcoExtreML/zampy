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

The old Climate Data Store (CDS) is shut down on 3 September 2024. For more
information see:
[the-new-climate-data-store-beta](https://forum.ecmwf.int/t/the-new-climate-data-store-beta-cds-beta-is-now-live/3315).
To use the new CDS/ADS, you need to have an ECMWF account, your existing CDS/ADS
credentials does not work.

If you need access to data on CDS or ADS server, you should add your CDS/ADS
credentials to `zampy_config.yml`. To find your key, go to [CDS how to
api](https://cds.climate.copernicus.eu/how-to-api), or [ADS how to
api](https://ads.atmosphere.copernicus.eu/how-to-api). You can skip the steps
related to `.cdsapirc` and simply add the key to `zampy_config.yml`:

```yaml
cdsapi:
  url:  # for example https://cds.climate.copernicus.eu/api
  key:  # for example xhashd-232jcsha-dsaj429-cdjajd29319
adsapi:
  url:  # for example https://ads.atmosphere.copernicus.eu/api
  key:  # for example xhashd-232jcsha-dsaj429-cdjajd29319
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


### Agree to the Terms of Use on CDS/ADS

When downloading a dataset for the first time, it is **necessary to agree to the Terms of Use of every datasets that you intend to download**. This can only be done via the CDS/ADS website. When you try to download these datasets, you will be prompted to go to the terms of use and accept them.
