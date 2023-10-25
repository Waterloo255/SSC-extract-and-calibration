import re

import geopandas as gp
import pandas as pd
import xarray as xr
from pathlib import Path

from hat.validate.extract_value import extract
from hat.tools.raster_analysis import raster2array, raster_query
from hat.types.spatial import Mesh


def create_gdf(zone):
    station_files = r"D:\1027\points(1).xlsx"
    df = pd.read_excel(station_files, zone).drop(0)
    df['ID'] = df['ID'].apply(lambda x: "P{:.0f}".format(x))
    gdf = gp.GeoDataFrame(df, geometry=gp.points_from_xy(df['Lon'], df['Lat'], crs="epsg:4326"))

    return gdf


class Dataset(object):

    def __init__(self, name=None, path=None, file_filter=None, z_dim='time',
                 time_get_fun=None, time_format="%Y", dropna=True):
        self.name = name
        self.p = Path(path)
        self.ff = file_filter
        self.z_dim = z_dim
        self.tgf = time_get_fun
        self.dropna = dropna
        self.time_format = time_format
        self._files = None
        self._time_tags = []

    @property
    def files(self):
        if not self._files:
            self._files = [ifile.as_posix() for ifile in self.p.rglob(self.ff)]
        return self._files

    @property
    def time_tags(self):
        if not self._time_tags:
            self._time_tags = [self.tgf(ifile) for ifile in self.files]
        return self._time_tags

    def to_series(self):
        res = []
        rs_info = raster_query(self.files[0])
        my_mesh = Mesh(x_size=rs_info['xsize'], y_size=rs_info['ysize'], geo_transform=rs_info['geo_transform'])
        for i_file in self.files:
            res.append(raster2array(i_file))
        if len(res) > 1:
            my_datasets = xr.Dataset({self.name: (["time", "y", "x"], res)},
                                     coords={"x": (["x"], my_mesh.x_points),
                                             "y": (["y"], my_mesh.y_points[::-1]),
                                             "time": pd.to_datetime(self.time_tags, format=self.time_format),
                                             "reference_time": pd.Timestamp("2000-01-01")})
        elif len(res) == 1:
            my_datasets = xr.Dataset({self.name: (["y", "x"], res)},
                                     coords={"x": (["x"], my_mesh.x_points),
                                             "y": (["y"], my_mesh.y_points[::-1])})
        my_datasets.attrs['crs'] = rs_info["proj"]
        return my_datasets


class SoilTypeDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super(SoilTypeDataset, self).__init__(*args, **kwargs)
        self.z_dim = "depth"

    def to_series(self):
        res = []
        rs_info = raster_query(self.files[0])
        my_mesh = Mesh(x_size=rs_info['xsize'], y_size=rs_info['ysize'], geo_transform=rs_info['geo_transform'])
        for i_file in self.files:
            res.append(raster2array(i_file))
        my_datasets = xr.Dataset({self.name: (["depth", "y", "x"], res)},
                                 coords={"x": (["x"], my_mesh.x_points),
                                         "y": (["y"], my_mesh.y_points[::-1]),
                                         "depth": self.time_tags})
        my_datasets.attrs['crs'] = rs_info['proj']
        return my_datasets


class RunoffDataset(Dataset):

    def to_series(self, ):
        ds = xr.open_mfdataset(self.files)
        ds.attrs['crs'] = "epsg:4326"
        ds = ds.rename({"lon": "x", "lat": "y"})
        return ds


class SSCDataset(Dataset):
    def to_series(self):
        ds = xr.open_dataset(self.files)
        ds.attrs["crs"] = "epsg:4326"
        return ds


def main():
    ndvi = Dataset(name="GrNDVI", path=r"D:\1027\GrNDVI", file_filter="*.tif", time_get_fun=lambda x: x[-8:-4])
    # ssc = SSCDataset(name="SSC", path=r"D:\1027\SSC-年", file_filter="*.nc", time_get_fun=lambda x: x[-8:-4],
    #                  dropna=False)
    frozen_alt = Dataset(name="frozen_alt", path=r"D:\1027\冻土", file_filter="alt*s",
                         time_get_fun=lambda x: x[-5:-1])
    frozen_mean = Dataset(name="frozen_mean", path=r"D:\1027\冻土", file_filter="mean*s",
                          time_get_fun=lambda x: x[-5:-1])
    # sonw_depth = Dataset(name="sdp", path=r"D:\1027\积雪深度", file_filter="*.tif",
    #                      time_get_fun=lambda x: x[-11:-4],
    #                      time_format="%Y%j")
    # runoff = RunoffDataset(name="runoff", path=r"D:\1027\runoff", file_filter="*.nc",
    #                        time_get_fun=lambda x: x[-10: -3],
    #                        time_format="%Y-%m")
    soc = SoilTypeDataset(name="soc", path=r"D:\1027\土壤", file_filter="soc[!d]*.tif",
                          time_get_fun=lambda x: re.findall(r"soc(\d+)", x)[0])

    bd = SoilTypeDataset(name="bd", path=r"D:\1027\土壤", file_filter="bd*.tif",
                         time_get_fun=lambda x: re.findall(r"bd(\d+)", x)[0])
    btcly = SoilTypeDataset(name="btcly", path=r"D:\1027\土壤", file_filter="btcly*.tif",
                            time_get_fun=lambda x: re.findall(r"btcly(\d+)", x)[0])
    btslt = SoilTypeDataset(name="btslt", path=r"D:\1027\土壤", file_filter="btslt*.tif",
                            time_get_fun=lambda x: re.findall(r"btslt(\d+)", x)[0])
    btsnd = SoilTypeDataset(name="btsnd", path=r"D:\1027\土壤", file_filter="btsnd*.tif",
                            time_get_fun=lambda x: re.findall(r"btsnd(\d+)", x)[0])

    for ids in [soc, bd, btcly, btslt, btsnd]:
        ds = ids.to_series()
        basin1 = ["金沙江", '支流总', "澜沧江", "雅砻江"]
        basin2 = ["雅砻江支流", "黄河", "柴达木", "柴达木盆地右", "内陆河",
                  "Amu Darya", "河西走廊", "塔里木", "Ganges恒河",
                  "印度河Indus", "怒江", "雅鲁藏布江"]
        for ibasin in basin1:
            points = create_gdf(ibasin)
            points.to_file(r"output\shp\{}.shp".format(ibasin), encoding='utf-8')
            if ibasin == "Amu Daraya" and ids.name in ["GrNDVI", 'soc', 'bd', 'btcly', 'btslt', 'btsnd']:
                res = extract(ds, points, 'ID', raster_crs=ds.crs, find_no_nan=False, z_dim=ids.z_dim)
                outname = r"output\{}_{}.csv".format(ibasin, ids.name)
                df = res[list(res.keys())[0]]
                df.to_csv(outname)
            else:
                res = extract(ds, points, 'ID', raster_crs=ds.crs, z_dim=ids.z_dim, find_no_nan=True, search_radius=30)
                outname = r"output\{}_{}.csv".format(ibasin, ids.name)
                df = res[list(res.keys())[0]]
                df.to_csv(outname)

            print("{} done".format(outname))


if __name__ == "__main__":
    main()
