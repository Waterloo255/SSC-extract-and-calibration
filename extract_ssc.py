from pathlib import Path

import pandas as pd
import xarray as xr

from hat.validate.extract_value import extract
from extract_all import create_gdf


def main():
    basin1 = ["金沙江", "澜沧江", "雅砻江", "雅砻江支流", "黄河", "柴达木", "柴达木盆地右", "内陆河",
              "河西走廊", "塔里木", "Ganges恒河", "印度河Indus", "怒江", "雅鲁藏布江"]
    path1 = ['Yangtze', 'mekong', 'Yangtze', 'Yangtze', 'Yellow', 'qidamu', 'qidamu', 'inner',
             'hexi', 'Tarim', 'Ganges', 'indus', 'Salween', 'Brahmaputra']

    for ibasin, path in zip(basin1, path1):
        points = create_gdf(ibasin)
        p = Path(r"H:\TIF\{}".format(path))
        df = pd.DataFrame()
        ssc_out_name = r"output\ssc\{}_ssc.xlsx".format(ibasin)
        flux_out_name = r"output\ssc\{}_flux.xlsx".format(ibasin)
        for ifile in p.glob("*.tif"):
            ds = xr.open_dataset(ifile.as_posix()).sel(band=1)
            year = ifile.as_posix()[-8:-4]
            res = extract(ds, points, 'ID', raster_crs="epsg:4326", find_no_nan=False)['res']
            res.index = [year]
            df = pd.concat([df, res])

        rf = pd.read_csv(r"D:\code\li_extract\output\era5_translate\{}_sro.csv".format(ibasin),
                         parse_dates=[0], index_col=0)
        rf.index = rf.index.year.astype('str')
        flux = df*rf.loc['1986':'2021', :]*1e-3
        flux.to_excel(flux_out_name)
        df.to_excel(ssc_out_name)
        print("{} done.".format(ibasin))


if __name__ == "__main__":
    main()
