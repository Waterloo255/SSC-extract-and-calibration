import numpy as np
import pandas as pd
from scipy.stats import mode
import geopandas as gpd
import xarray as xr
import rioxarray as rxr
from rioxarray.exceptions import NoDataInBounds

import matplotlib.pyplot as plt

# 读取shapefile和栅格文件
shapefile_path = r"F:\long\HMA_roi\roi.shp"
pet = xr.open_dataset(r"F:\公共数据\era5_month\EAR5-Land-Monthly-Global_05deg_1950-2020_PET_yearsum.nc",
					  engine="h5netcdf")
sw = xr.open_dataset(r"F:\公共数据\era5_month\ERA5-Land-Monthly_Global_05deg_1980-2020_SoilWater.nc", engine="h5netcdf")
ai = xr.open_dataset(r"F:\干旱变化研究\数据合并\merge_ai_yearmean.nc", engine="h5netcdf")
vpd = xr.open_dataset(r"F:\干旱变化研究\数据合并\merge_vpd_yearmean.nc", engine="h5netcdf")
era5 = xr.open_dataset(r"F:\公共数据\era5_month\ERA5-Land-Monthly-Global_05deg_1950-2022.nc", engine="h5netcdf")

stat_dict = {"PET": pet['pet'], "SW1": sw["swvl1"].resample(time='Y').mean(),
			 "SW2": sw["swvl2"].resample(time='Y').mean(),
			 "AI": ai["AI"], "VPD": vpd["vpd"], "T2": era5["2t"].resample(time='Y').mean(),
			 "TP": era5["tp"].resample(time='Y').sum()}

gdf = gpd.read_file(shapefile_path)

# 定义函数来进行分区统计
def zonal_statistics(zone_geometry, raster_data: xr.Dataset):
	# 利用rasterio.mask模块裁剪栅格数据，以匹配每个分区的边界
	raster_data = raster_data.mean(dim='time')
	raster_data.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
	masked_data = raster_data.rio.clip([zone_geometry])

	# 计算栅格数据中非nan值的统计信息（平均值、最大值、最小值等）
	statistics = {
		'mean': masked_data.mean().values,
		'max': masked_data.max().values,
		'min': masked_data.min().values,
	}

	return statistics


# 对每个分区进行统计
df = pd.DataFrame(index=gdf['HYBAS_ID'], columns=stat_dict.keys())
for name, dataset in stat_dict.items():
	dataset.rio.write_crs("epsg:4326", inplace=True)
	for idx, zone_geometry in zip(gdf['HYBAS_ID'], gdf.geometry):
		try:
			stats = zonal_statistics(zone_geometry, dataset)
			df.loc[idx, name] = stats.get('mean')
			print("{} {} done.".format(name, idx))
		except NoDataInBounds as e:
			print("{} {} error".format(name, idx))

df.to_excel("basin_statistic_yearmean.xlsx")
