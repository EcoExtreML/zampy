Currently, the following datasets are available. Note that not all variables from each dataset might be supported.

You can add these yourself by creating a pull request, or open an issue to request a new feature.

=== "ERA5"
    - `mean_total_precipitation_rate`
    - `surface_thermal_radiation_downwards`
    - `surface_solar_radiation_downwards`
    - `surface_pressure`
    - `10m_u_component_of_wind`
    - `10m_v_component_of_wind`

    Note: all hours in a day are covered and all days for the given month are included for downloading.

    Fore more information, see [the ECMWF website](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels).

=== "ERA5-land"
    - `2m_temperature`
    - `2m_dewpoint_temperature`

    Note: all hours in a day are covered and all days for the given month are included for downloading.

    Fore more information, see [the ECMWF website](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land).

=== "ETH canopy height"
    - `height_of_vegetation`
    - `height_of_vegetation_standard_deviation`

    For more information, see [their webpage](https://langnico.github.io/globalcanopyheight/).

=== "PRISM DEM"
    - `elevation`

    For more information, see [their webpage](https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model).

=== "CAMS EGG4"
    - `carbon_dioxide`

    Note: model level is set to "60" and all steps are included for downloading.

    For more information, see [their webpage](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-ghg-reanalysis-egg4).

=== "Land cover classification gridded maps"
    - `land_cover`

    For more information, see [their webpage](https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover).

=== FAPAR Leaf Area Index
    - `leaf_area_index`

    For more info see [their webpage](https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-lai-fapar).
