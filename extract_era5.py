import xarray as xr

from hat.validate.extract_value import extract
from extract_all import create_gdf

ds_era5 = xr.open_dataset(
    r"D:\1027\ERA5\adaptor.mars.internal-1667291753.760688-6304-4-f19300ba-e1b4-4ed1-93da-4f11bb01b192.nc")


def main():
    basin1 = ["金沙江", '支流总', "澜沧江", "雅砻江"]
    basin2 = ["雅砻江支流", "黄河", "柴达木", "柴达木盆地右", "内陆河",
              "Amu Darya", "河西走廊", "塔里木", "Ganges恒河",
              "印度河Indus", "怒江", "雅鲁藏布江"]
    basin1.extend(basin2)
    for ibasin in basin1:
        points = create_gdf(ibasin)
        res = extract(ds_era5, points, 'ID', raster_crs="epsg:4326", find_no_nan=False, search_radius=30,
                      target_var=['tp', 't2m', 'sro', 'sde'])
        for k, df in res.items():
            outname = r"output\era5\{}_{}.csv".format(ibasin, k)
            df.to_csv(outname)
        print("{} done".format(ibasin))


if __name__ == "__main__":
    main()
