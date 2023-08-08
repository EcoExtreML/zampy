# Using Zampy

## Installing Zampy
Zampy can be installed by doing:
```bash
pip install zampy git+https://github.com/EcoExtreML/zampy
```

## Configuration
Zampy needs to be configured with a simple configuration file.

This file is created under your -*user's home*-/.config directory:

`~/.config/zampy/zampy_config.yml`

```yaml
working_directory: /home/bart/Zampy
```

## Formulating a recipe
Recipes have the following structure:

```yaml
name: "test_recipe"

download:
  years: [2020, 2020]
  bbox: [54, 6, 50, 3] # NESW

  datasets:
    era5:
      variables:
        - 10m_v_component_of_wind
        - surface_pressure
    eth_canopy_height:
      variables:
        - height_of_vegetation

convert:
  convention: ALMA
  frequency: 1H  # outputs at 1 hour frequency. Pandas-like freq-keyword.
  resolution: 0.5  # output resolution in degrees.
```

You can specify multiple datasets and multiple variables per dataset.

## Running a recipe
Save this recipe to disk and run the following code in your shell:

```bash
zampy --filename /home/username/path_to_file/simple_recipe.yml
```

This will execute the recipe (i.e. download, ingest, convert, resample and save the data).
