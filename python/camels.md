# CAMELS Forcing Ensemble

The [CAMELS](https://gdex.ucar.edu/dataset/camels.html) dataset
provides a large ensemble of hydrologic model simulations for 671
basins across the contiguous United States. However, the forcing data
is not well-structured and can be difficult to work with. This
code snippet demonstrates how to process the forcing data into a
single NetCDF file by taking the mean of the ensemble members.

First, download the Daymet forcing data from
[here](https://gdex.ucar.edu/dataset/camels/file/basin_timeseries_v1p2_modelOutput_daymet.zip).
Then, extract the contents of the zip file into a directory called
`data`. Then, install `cytoolz`, `pandas`, and `xarray` and run the
following code:

```python
from collections.abc import Generator
from pathlib import Path

import cytoolz.curried as tlz
import pandas as pd
import xarray as xr


def read_camels(filename: Path) -> pd.DataFrame:
    try:
        forcing = pd.read_csv(filename, usecols=[0, 1, 2, 4, 5, 6, 7, 8, 9], sep=r"\s+")
    except pd.errors.EmptyDataError:
        print(f"{filename} is empty")
        return pd.DataFrame()
    forcing = forcing.rename(
        columns={
            "YR": "year",
            "MNTH": "month",
            "DY": "day",
            "SWE": "swe",
            "PRCP": "prcp",
            "RAIM": "liquid",
            "TAIR": "tas",
            "PET": "pet",
            "ET": "et",
        }
    )
    date_cols = ["year", "month", "day"]
    forcing.index = pd.to_datetime(forcing[date_cols])
    return forcing.drop(columns=date_cols)


def ensemble_mean(
    df_list: Generator[pd.DataFrame, None, None], station_id: str
) -> xr.Dataset:
    ensemble = xr.concat(
        (df.to_xarray() for df in df_list if len(df) > 0), dim="ensemble"
    ).mean("ensemble")
    ensemble = ensemble.rename({"index": "time"}).expand_dims(
        {"station_id": [station_id]}
    )
    ensemble["swe"].attrs = {"units": "kg/m2", "long_name": "Snow Water Equivalent"}
    ensemble["prcp"].attrs = {"units": "mm", "long_name": "Precipitation"}
    ensemble["liquid"].attrs = {"units": "mm", "long_name": "Liquid Precipitation"}
    ensemble["tas"].attrs = {"units": "C", "long_name": "Air Temperature"}
    ensemble["pet"].attrs = {"units": "mm", "long_name": "Potential Evapotranspiration"}
    ensemble["et"].attrs = {"units": "mm", "long_name": "Evapotranspiration"}
    return ensemble


data_dir = Path("data")
files = Path(data_dir, "model_output_daymet/model_output/flow_timeseries/daymet").glob(
    "*/*model_output.txt"
)
station_files = tlz.groupby(lambda x: x.stem.split("_")[0], files)
counter = 1
for parts in tlz.partition_all(100, station_files.items()):
    clm = xr.merge(
        ensemble_mean((read_camels(f) for f in flist), sid) for sid, flist in parts
    )
    clm.to_netcdf(Path(data_dir, f"camels_daymet_ensemble_{counter}.nc"))
    counter += 1
clm = xr.merge(
    (xr.open_dataset(f) for f in data_dir.glob("camels_daymet_ensemble_*.nc"))
)
clm.transpose("time", "station_id").to_netcdf(
    Path(data_dir, "camels_daymet_ensemble.nc")
)
_ = [f.unlink() for f in data_dir.glob("camels_daymet_ensemble_*.nc")]
```
