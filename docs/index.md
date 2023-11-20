# Zampy

A tool for downloading Land Surface Model (LSM) input data.

Named after *Zam*; [the Avestan language term for the Zoroastrian concept of "earth"](https://en.wikipedia.org/wiki/Zam).

## Why using Zampy
`zampy` is designed to retrieve data for LSM model input. It can help you prepare the data within the following steps:
1. **Download** the data for the specified location(s) / geographical area.
2. **Ingest** data into unified (zampy) format.
3. **Load** the variables in a standardized way (standardized names & standardized units).
4. **Convert** the data to standard formats:
    - ALMA / PLUMBER2's ALMA formatted netCDF.
    - *CMOR formatted netCDF*.

(Note: items in *italic* will not be worked on for now/low priority, but we want to allow space for these in the future.)

## How to use Zampy

To install `zampy`, check [this guide](configuration.md). Please also make sure that you have it properly configured following the guidelines.

We recommend our users to use `zampy` with recipes.

A "recipe" is a file with yml extension, it defines:
- data downloading
  - time extent.
  - spatial location / bounding box.
  - datasets to be downloaded
    - variables within datasets
- data conversion
  - convert to desired [conventions](https://github.com/EcoExtreML/zampy/tree/main/src/zampy/conventions)
  - output frequency
  - output resolution

A sample recipe is shown below:

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

You can specify multiple datasets and multiple variables per dataset. Information on the available datasets and their variables is shown [here](available_datasets.md).

When you have your reciped created and saved on your disk, you can execute your recipe by running the following code in your shell:

```py
zampy /path_to_recipe/sample_recipe.yml
```

### Interact with `zampy` in notebooks

Although it is not recommended, you could intereact with `zampy` via Python APIs. You can find the example notebooks for each supported dataset [here](https://github.com/EcoExtreML/zampy/tree/main/demo).

## Acknowledgements

This package was developed by the Netherlands eScience Center. Development was supported by the Netherlands eScience Center under grant number NLESC.ASDI.2020.026.