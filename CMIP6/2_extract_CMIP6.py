#%%
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"

from netCDF4 import Dataset
import xarray as xr
import pandas as pd
import numpy as np
from glob import glob

#%%


list_nc = glob("raw_ncdf/*.nc")
for path_nc in list_nc:

    model_name = path_nc.split("\\")[-1].split(".")[0]

    nc_data = xr.open_dataset(path_nc)
    nc_data.coords["lon"] = (nc_data.coords["lon"] + 180) % 360 - 180
    nc_data = nc_data.sortby("lon")
    
    if ("KACE" in model_name) | ("HadGEM3-GC31-LL" in model_name) | ("UKESM1-0-LL" in model_name):
        nc_data = nc_data.convert_calendar("standard", align_on = "date")
    else:
        nc_data = nc_data.convert_calendar("standard")

    coords = np.meshgrid(nc_data.variables["lon"].values, nc_data.variables["lat"].values)
    lon = np.ravel(coords[0])
    lat = np.ravel(coords[1])
    df_coords = pd.DataFrame({"lon": lon, "lat": lat})

    index_list = pd.Index(nc_data.time.values)
    index_list = index_list.insert(0, "lat")
    index_list = index_list.insert(0, "lon")
    ts_df = pd.DataFrame(index = index_list)
    count = 0
        
    for i, j in zip(df_coords.lon, df_coords.lat):
        ts_var = nc_data[nc_data.variable_id].sel(lon = i, lat = j).to_dataframe()[nc_data.variable_id]
        if (nc_data.variable_id == "tasmax") or (nc_data.variable_id == "tasmin"):
            ts_var = ts_var - 273.156
        if (nc_data.variable_id == "pr"):
            ts_var = ts_var*86400
        ts = pd.Series([i,j], index = ["lon", "lat"])
        ts_df.insert(len(ts_df.columns), count, pd.concat([ts, ts_var]))
        count += 1         
        
    # ts_df.to_csv("Extracted_Data/{}.csv".format(model_name), sep = ";", index = True, header = None)
    ts_df.to_pickle("Extracted_Data/{}.pkl".format(model_name))
    # ts_df.to_parquet("Extracted_Data/{}.parquet", compression = "snappy")
    
#%%
