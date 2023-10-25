
from pathlib import Path

import xarray as xr
import geopandas as gp
from shapely.geometry import mapping

era5 = xr.open_dataset(
    r"F:\long\1027\ERA5\adaptor.mars.internal-1667291753.760688-6304-4-f19300ba-e1b4-4ed1-93da-4f11bb01b192.nc")
basins = gp.read_file(r"F:\long\1027\3_TP_basin_boundary_New_20190827\Union\TP_basins.shp")
era5.rio.write_crs("epsg:4326", inplace=True)
out_path = Path(r"output\basin_stat")
for name in basins['BasinName']:
    era5_sub = era5.rio.clip(basins[basins['BasinName'] == name].geometry.apply(mapping),
                             "epsg:4326", drop=False)
    df_t2m = era5_sub['t2m'].mean(dim=['longitude', 'latitude']).resample(time='Y').mean()
    df_ro = era5_sub['ro'].mean(dim=['longitude', 'latitude']).resample(time='Y').mean()
    df_sde = era5_sub['sde'].mean(dim=['longitude', 'latitude']).resample(time='Y').mean()
    df_tp = era5_sub['tp'].mean(dim=['longitude', 'latitude']).resample(time='Y').sum()

    df_t2m = df_t2m.to_dataframe().loc[:, 't2m'] - 273.15
    df_ro = df_ro.to_dataframe().loc[:, 'ro'] * 1000
    df_sde = df_sde.to_dataframe().loc[:, 'sde'] * 1000
    df_tp = df_tp.to_dataframe().loc[:, 'tp'] * 3.04e4

    df_t2m.to_excel(out_path / "{}-temperature.xlsx".format(name))
    df_ro.to_excel(out_path / "{}-runoff.xlsx".format(name))
    df_sde.to_excel(out_path / "{}-snow_depth.xlsx".format(name))
    df_tp.to_excel(out_path / "{}-total_precipitation.xlsx".format(name))