#%%
#Extracting CRU data for different regions (shapefiles)
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"

import pandas as pd
import geopandas as gpd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from glob import glob

list_nc = glob("Dados/CRU/*.nc")
list_shp = glob("Shapes/*.shp")

for dir_shp in list_shp:
    shp_basin = gpd.read_file(dir_shp)

    for dir_nc in list_nc:
        nc_data = xr.open_dataset(dir_nc)
        var = list(nc_data.data_vars)[0]

        lon, lat = np.meshgrid(nc_data.lon, nc_data.lat)
        df_point = pd.DataFrame({"lon": lon.flatten(), "lat": lat.flatten()})
        shp_point = gpd.GeoDataFrame(df_point,
                                    geometry = gpd.points_from_xy(df_point.lon, df_point.lat),
                                    crs = shp_basin.crs)
        #geometry = shp_basin.evelope caso queira que os dados 
        #sejam extraidos para a quadrícula que contém a shapefile
        #geometry = shp_basin.geometry caso queira que os dados
        #sejam extraidos para geometria exata da shapefile
        gdf_result = gpd.sjoin(shp_point,
                        gpd.GeoDataFrame(geometry = shp_basin.geometry),
                        how = "left")
        gdf_result = gdf_result.loc[~np.isnan(gdf_result["index_right"])]
        ins_point = gdf_result[["lon", "lat"]].values[:]
        ins_df = pd.DataFrame(ins_point, columns = ["lon", "lat"])

        var_ins = []

        for i in range(len(ins_df)):
                 var_ins.append(nc_data[var].sel(lat = ins_df["lat"][i], lon = ins_df["lon"][i]).values)
        
        var_df = ins_df[["lon", "lat"]].join(pd.DataFrame(var_ins, columns = nc_data.time))
        
        if dir_nc == list_nc[0]:
            merged_df = var_df
        else:
            merged_df = merged_df.merge(var_df, how = "inner", on = ("lon", "lat"))
        
    merged_df.to_csv("Dados/Extracted_Data/{}_{}_{}_{}.csv".format(
        dir_shp.split("\\")[-1].split(".")[0],
        var,
        merged_df.columns[2].year,
        merged_df.columns[-1].year),
        sep = ";", index = None, header = True)

    mean_df = merged_df.mean(axis = 0)
    mean_df.drop(["lon", "lat"], axis = 0, inplace = True)
    mean_df.to_csv("Dados/Extracted_Data/{}_Mean_{}_{}_{}.csv".format(
        dir_shp.split("\\")[-1].split(".")[0],
        var,
        merged_df.columns[2].year,
        merged_df.columns[-1].year),
    sep = ";", index = True, index_label = "Data", header = [var])   
#%%