"""Generate fake data for the fapar-lai tests."""
import zipfile
from pathlib import Path
import numpy as np
import xarray as xr


if __name__ == "__main__":
    download_path = Path("download")
    ingest_path = Path("ingest")
    download_path.mkdir(exist_ok=True)
    ingest_path.mkdir(exist_ok=True)

    # Generate raw NC files:
    latitude = np.linspace(80, -59.99107142876241, num=15680, endpoint=True)
    longitude = np.linspace(-180, 180, num=40320, endpoint=True)
    dummy_data = np.ones((1, len(latitude), len(longitude)))
    encoding = {"LAI": {"zlib": True, "complevel": 8}}
    days = [10, 20, 31]

    fnames: list[Path] = []
    for day in days:
        time = np.array([np.datetime64(f"2019-01-{day}")])

        da = xr.DataArray(
            data=dummy_data,
            dims=[
                "time",
                "lat",
                "lon",
            ],
            coords={"time": time, "lat": latitude, "lon": longitude},
        )

        da.name = "LAI"
        da.attrs = {
            "long_name": "Effective Leaf Area Index 1km",
            "grid_mapping": "crs",
            "standard_name": "leaf_area_index",
            "units": "fraction",
            "valid_range": np.array([0, 65534], dtype=np.uint16),
        }
        ds = da.to_dataset()

        fname = f"c3s_LAI_201901{day}000000_GLOBE_PROBAV_V3.0.1.nc"

        ds.to_netcdf(fname, encoding=encoding)
        fnames.append(Path(fname))

    # Zip em up
    zip_fname = "satellite-lai-fapar_2019-1.zip"
    with zipfile.ZipFile(download_path / zip_fname, mode="w") as zipf:
        for fname in fnames:
            zipf.write(fname)

    # Clean up raw nc files
    for fname in fnames:
        fname.unlink()

    # Generate ingested nc files:
    encoding = {"leaf_area_index": {"zlib": True, "complevel": 8}}
    for day in days:
        time = np.array([np.datetime64(f"2019-01-{day}")])

        da = xr.DataArray(
            data=dummy_data,
            dims=[
                "time",
                "latitude",
                "longitude",
            ],
            coords={"time": time, "latitude": latitude, "longitude": longitude},
        )

        da.name = "leaf_area_index"
        da.attrs = {
            "long_name": "Effective Leaf Area Index 1km",
            "grid_mapping": "crs",
            "standard_name": "leaf_area_index",
            "units": "fraction",
            "valid_range": np.array([0, 65534], dtype=np.uint16),
        }
        ds = da.to_dataset()

        fname = f"c3s_LAI_201901{day}000000_GLOBE_PROBAV_V3.0.1.nc"
        ds.to_netcdf(ingest_path / fname, encoding=encoding)
