#%%
#Extracting Xavier data for different regions (shapefiles)
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"
import xarray as xr
import numpy as np
import pandas as pd 
import geopandas as gpd
from glob import glob
#%%
list_shp = glob("Shapes/*.shp")
list_nc = glob("*.nc")

list_ETP = [x for x in list_nc if "ETo" in x]
list_pr = [x for x in list_nc if "pr" in x]
path_shp = list_shp[0]
path_nc = list_nc[0]


#%%
for path_shp in list_shp:
    
    shp_buffer = gpd.read_file(path_shp)


    for list_nc in [list_ETP]:

        merged_df = None

        for path_nc in list_nc:

            nc_data = xr.open_dataset(path_nc, engine = "netcdf4")

            var_label = list(nc_data.keys())[0]

            coords = np.meshgrid(nc_data.variables["longitude"].values, nc_data.variables["latitude"].values)


            df_coords = pd.DataFrame({"lon": np.ravel(coords[0]), "lat": np.ravel(coords[1])})
            gdf_grid = gpd.GeoDataFrame(
                    df_coords,
                    geometry = gpd.points_from_xy(df_coords.lon, df_coords.lat),
                    crs = shp_buffer.crs
                )

            gdf_ins = gpd.sjoin(gdf_grid, shp_buffer, how = "left")
            gdf_ins = gdf_ins.loc[~np.isnan(gdf_ins.index_right)]
            coords_ins = gdf_ins[["lon", "lat"]]

            index_list = pd.Index(nc_data.time.values)
            index_list = index_list.insert(0, "lat")
            index_list = index_list.insert(0, "lon")

            ts_dict = {}

            count = 0
            for i, j in zip(coords_ins.lon, coords_ins.lat):
                ts = nc_data[var_label].sel(longitude = i, latitude = j).to_dataframe()[var_label]

                ts = pd.concat([pd.Series([i,j], index = ["lon", "lat"]), ts])
                ts_dict[count] = ts
                count += 1

            ts_df = pd.DataFrame(ts_dict).T

            if merged_df is None:

                merged_df = ts_df
            
            else:
                merged_df = merged_df.merge(ts_df, on = ["lon", "lat"])

        if merged_df is not None:       
            merged_df = merged_df.T

        merged_df.to_csv("{}_{}.csv".format(var_label, path_shp.split("\\")[-1].split(".")[0]))
    
#%%