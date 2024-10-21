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

To install and configure`zampy`, fist check [this guide](configuration.md) before continuing. Please also make sure that you have properly configured it following the guidelines.

We recommend our users to use `zampy` with recipes.

A "recipe" is a file with yml extension, it defines:

- which data to download:
  - the time extent
  - a spatial bounding box
  - the datasets to be downloaded
    - the variables within each dataset
- and data conversion to the desired:
  - [convention](https://github.com/EcoExtreML/zampy/tree/main/src/zampy/conventions)
  - time frequency
  - spatial resolution

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

>NOTE: You may recieve an error message from CDS/ADS if not all the required
>licences have been accepted. Follow the instructions in the error message to
>accept the licences and run the recipe again.

When downloading process starts, you can also check the status of your requests
in your CDS/ADS profile.


### Interact with `zampy` in notebooks

It is possible to use `zampy` directly in Python via its Python API. This is not recommended, as it is more difficult to reproduce the workflow if there is no recipe.
As it is an internal API, python code can break without warning on new versions of Zampy.
An example notebooks for each supported dataset is available [here](https://github.com/EcoExtreML/zampy/tree/main/demo).

## Acknowledgements

This package was developed by the Netherlands eScience Center. Development was supported by the Netherlands eScience Center under grant number NLESC.ASDI.2020.026.