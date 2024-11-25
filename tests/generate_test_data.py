"""Generates test data for running the tests.

The recipe zampy/recipes/STEMMUS_SCOPE_input.yml should be used to download the
data before running this script.
"""

import shutil
import xarray as xr


TEST_DATA_NAME = {
    "cams": "cams_co2_concentration_2020_01_01-2020_02_15.nc",
    "era5": [
        "era5_northward_component_of_wind_2020-1.nc",
        "era5_eastward_component_of_wind_2020-1.nc",
        "era5_total_precipitation_2020-1.nc",
        "era5_surface_pressure_2020-1.nc",
        "era5_surface_solar_radiation_downwards_2020-1.nc",
        "era5_surface_thermal_radiation_downwards_2020-1.nc",
    ],
    "era5-land": [
        "era5-land_dewpoint_temperature_2020-1.nc",
        "era5-land_air_temperature_2020-1.nc",
    ],
    "eth-canopy-height": "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif",
    "fapar-lai": "satellite-lai-fapar_2020-1.zip",
    "land-cover": "land-cover_LCCS_MAP_300m_2020.zip",
    "prism-dem-90": "Copernicus_DSM_30_N50_00_E000_00.tar",
}


def _subset_ncfile(input_file, output_file):
    ds = xr.open_dataset(input_file)
    subset = ds.isel(
        valid_time=slice(0, min(4, ds.valid_time.size)),
        latitude=slice(0, min(4, ds.latitude.size)),
        longitude=slice(0, min(4, ds.longitude.size)),
    )
    subset.to_netcdf(output_file)


def _subset_tiffile(input_file, output_file):
    da = xr.open_dataarray(input_file, engine="rasterio", chunks={"x": 200, "y": 200})
    subset = da.isel(
        x=slice(0, min(4, da.x.size)),
        y=slice(0, min(4, da.y.size)),
    )
    subset.rio.to_raster(output_file)


def _subset_zipfile_include_ncfiles(input_file, output_dir):
    format = input_file.suffix.lstrip(".")
    zip_file_name = input_file.stem
    temp_dir = output_dir / zip_file_name
    temp_dir.mkdir(parents=True, exist_ok=True)

    shutil.unpack_archive(input_file, extract_dir=output_dir, format=format)
    ncfiles = output_dir.glob("*.nc")

    for ncfile in ncfiles:
        ds = xr.open_dataset(ncfile)
        # select a subset of the data
        subset = ds.isel(
            time=slice(0, min(100, ds.time.size)),
            lat=slice(0, min(100, ds.lat.size)),
            lon=slice(0, min(100, ds.lon.size)),
        )

        # remove the original file
        ncfile.unlink()

        # Save back to the original format
        subset.to_netcdf(temp_dir / ncfile.name)

    # archive back to zip
    base_name = output_dir / zip_file_name
    shutil.make_archive(base_name, format, temp_dir)

    # remove the temp_dir
    shutil.rmtree(temp_dir)


def _subset_tarfile_include_tiffiles(input_file, output_dir):
    format = input_file.suffix.lstrip(".")
    zip_file_name = input_file.stem
    temp_dir = output_dir / zip_file_name
    temp_dir.mkdir(parents=True, exist_ok=True)

    shutil.unpack_archive(input_file, extract_dir=temp_dir, format=format)
    tifffile = list((temp_dir / zip_file_name / "DEM").glob("*.tif"))[0]

    da = xr.open_dataarray(tifffile, engine="rasterio", chunks={"x": 200, "y": 200})

    # select a subset of the data
    subset = da.isel(
        x=slice(0, min(100, da.x.size)),
        y=slice(0, min(100, da.y.size)),
    )

    # remove the original file
    tifffile.unlink()

    # Save back to the original format as a tif
    subset.rio.to_raster(tifffile)

    # archive back to zip
    base_name = output_dir / zip_file_name
    root_dir = output_dir / zip_file_name
    shutil.make_archive(base_name, format, root_dir, zip_file_name)

    # remove the temp_dir
    shutil.rmtree(root_dir)


def prepare_dataset(path, data_name, output_dir):
    """Open a dataset as an xarray dataset."""
    if data_name in {"cams", "era5", "era5-land"}:
        _subset_ncfile(path, output_dir / path.name)

    if data_name in {"eth-canopy-height"}:
        _subset_tiffile(path, output_dir / path.name)

    if data_name in {"fapar-lai", "land-cover"}:
        _subset_zipfile_include_ncfiles(path, output_dir)

    if data_name == "prism-dem-90":
        _subset_tarfile_include_tiffiles(path, output_dir)


def generate_test_data(data_dir, test_dir):
    """Generate test data for the recipe tests."""

    for data_name in TEST_DATA_NAME.keys():
        output_dir = test_dir / data_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # copy properties.json
        shutil.copy(data_dir / data_name / "properties.json", output_dir)

        # subset data
        if isinstance(TEST_DATA_NAME[data_name], list):
            for file_name in TEST_DATA_NAME[data_name]:
                path = data_dir / data_name / file_name
                prepare_dataset(path, data_name, output_dir)
        else:
            path = data_dir / data_name / TEST_DATA_NAME[data_name]
            prepare_dataset(path, data_name, output_dir)

        print(f"Generated test data for {data_name} in {output_dir}")

    print("Done generating test data.")
