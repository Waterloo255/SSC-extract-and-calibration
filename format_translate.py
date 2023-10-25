import pandas as pd

areas = {'金沙江': 251978.7, '澜沧江': 90441.1, '雅砻江': 110153.3, '雅砻江支流': 110153.3,
         '黄河': 254191.0, '柴达木': 253252.0, '柴达木盆地右': 253252.0,
         '内陆河': 708282.0, 'Amu Darya': 125633.0, '河西走廊': 61699.9,
         '塔里木': 190669.0, 'Ganges恒河': 121321.0, '印度河Indus': 319123.0,
         '怒江': 130172.0, '雅鲁藏布江': 347506.0}


def surface_runoff():
    for basin_name, area in areas.items():
        file = r"output\era5\{}_sro.csv".format(basin_name)
        df = pd.read_csv(file, parse_dates=[0], index_col=0)
        df = df.apply(lambda x: x * 1e-3 * area).groupby(df.index.year).sum()
        # m -> km3/yr
        out_name = r"output\era5_translate\{}_sro.csv".format(basin_name)
        df.to_csv(out_name)


def surface_temperature():
    for basin_name, area in areas.items():
        file = r"output\era5\{}_t2m.csv".format(basin_name)
        df = pd.read_csv(file, parse_dates=[0], index_col=0)
        df = df.apply(lambda x: x - 273.15).groupby(df.index.year).mean()
        # K -> C
        out_name = r"output\era5_translate\{}_t2m.csv".format(basin_name)
        df.to_csv(out_name)


def total_precipitation():
    for basin_name, area in areas.items():
        file = r"output\era5\{}_tp.csv".format(basin_name)
        df = pd.read_csv(file, parse_dates=[0], index_col=0)
        df = df.apply(lambda x: x * 3.04e4).groupby(df.index.year).sum()
        # m/d -> mm
        out_name = r"output\era5_translate\{}_tp.csv".format(basin_name)
        df.to_csv(out_name)


def snow_depth():
    for basin_name, area in areas.items():
        file = r"output\era5\{}_sde.csv".format(basin_name)
        df = pd.read_csv(file, parse_dates=[0], index_col=0)
        df = df.apply(lambda x: x * 1000).groupby(df.index.year).median()
        # m -> mm
        out_name = r"output\era5_translate\{}_sde.csv".format(basin_name)
        df.to_csv(out_name)


if __name__ == "__main__":
    surface_runoff()
    surface_temperature()
    total_precipitation()
    snow_depth()
