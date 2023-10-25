import xarray as xr
import geopandas as gp
import pandas as pd

ds = xr.open_dataset(r"F:\long\1027\ERA5\adaptor.mars.internal-1667291753.760688-6304-4-f19300ba-e1b4-4ed1-93da-4f11bb01b192.nc")
df = pd.read_csv(r"F:\long\1127\Snow.csv")
df['id'] = df['id'].apply(lambda x: "P{}".format(x))

t2m = pd.DataFrame(index=ds.time, columns=df['id'])
ro = pd.DataFrame(index=ds.time, columns=df['id'])
tp = pd.DataFrame(index=ds.time, columns=df['id'])
sde = pd.DataFrame(index=ds.time, columns=df['id'])

for idx, lon, lat in zip(df.id, df.lon, df.lat):
    t2m.loc[:, idx] = ds['t2m'].sel(longitude=lon, latitude=lat, method="nearest").values - 273.15
    ro.loc[:, idx] = ds['ro'].sel(longitude=lon, latitude=lat, method="nearest").values
    tp.loc[:, idx] = ds['tp'].sel(longitude=lon, latitude=lat, method="nearest").values * 3.04e4
    sde.loc[:, idx] = ds['sde'].sel(longitude=lon, latitude=lat, method="nearest").values * 1e3

t2m.to_excel(r"F:\long\1127\output\temperature.xlsx")
ro.to_excel(r"F:\long\1127\output\runoff.xlsx")
tp.to_excel(r"F:\long\1127\output\precipitation.xlsx")
sde.to_excel(r"F:\long\1127\output\snow_depth.xlsx")
