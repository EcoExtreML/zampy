# Using Zampy

## Installing Zampy
Zampy can be installed by doing:
```bash
pip install zampy git+https://github.com/EcoExtreML/zampy
```

## Configuration
Zampy needs to be configured with a simple configuration file.

You need to create this file under your -*user's home*-/.config directory: `~/.config/zampy/zampy_config.yml`, and should contain the following:

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

## Formulating a recipe
A "recipe" is a file with `yml` extension and has the following structure:

```yaml
name: "test_recipe"

download:
  time: [2020-01-01, 2020-01-31] # must follow the numpy.datetime64 format.
  bbox: [54, 6, 50, 3] # NESW

  datasets:
    era5:
      variables:
        - eastward_component_of_wind
        - surface_pressure

    cams:
      variables:
        - co2_concentration
    
convert:
  convention: ALMA
  frequency: 1H  # outputs at 1 hour frequency. Pandas-like freq-keyword.
  resolution: 0.5  # output resolution in degrees.
```

You can specify multiple datasets and multiple variables per dataset.

## Running a recipe
Save this recipe to disk and run the following code in your shell:

```bash
zampy /home/username/path_to_file/simple_recipe.yml
```

This will execute the recipe (i.e. download, ingest, convert, resample and save the data).
