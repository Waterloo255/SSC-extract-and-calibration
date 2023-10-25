from pathlib import Path
import xarray as xr
import pandas as pd
import numpy as np

p = Path(r"D:\1027\runoff")
for ifile in p.glob("*new.nc"):
    ds = xr.open_dataset(ifile)
    z = pd.to_datetime(ds['dateT'][0].values)
    start_time = z+pd.tseries.offsets.DateOffset(days=1-z.day)
    end_time = z+pd.tseries.offsets.DateOffset(months=1, days=-z.day)
    time_index = pd.date_range(start_time, end_time)
    ds['dateT'] = time_index
    ds = ds.rename({"dateT": "time"})
    ds["lat"] = ds.lat[::-1]
    ds['RS'] = xr.where(ds['RS'] == -9999, np.nan, ds['RS'])
    out_name = ifile.parent / "{}_update.nc".format(ifile.stem)
    ds.to_netcdf(out_name.as_posix())
    print("{} done".format(ifile))