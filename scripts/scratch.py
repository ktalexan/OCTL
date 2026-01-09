# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import shutil
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL

pd.options.mode.copy_on_write = True

octl = OCTL(part = 0, version = 2026.1)

prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

cb = octl.cb
cbdf = octl.cbdf



# Get the raw data from the OCTL class object
tl_files, year = octl.get_raw_data()

tl_folder = Path(os.path.join(octl.prj_dirs["data_raw"], f"tl_{year}"))

sdfs = octl.process_folder(tl_files, tl_folder, year)











# Create a new file geodatabase
# Define where the GDB will be stored
out_folder_path = prj_dirs["gis"]
gdb_name = f"TL{year}.gdb"

# Execute CreateFileGDB
if not arcpy.Exists(os.path.join(out_folder_path, gdb_name)):
    arcpy.management.CreateFileGDB(out_folder_path, gdb_name)
    print(f"Geodatabase {gdb_name} created successfully.")
else:
    print("Geodatabase already exists.")


# For each spatial data frame in the sdfs dictionary, create a feature class in the geodatabase
for sdf in sdfs:
    sdf.to_featureclass(os.path.join(out_folder_path, gdb_name), sdf.name)
    print(f"Feature class {sdf.name} created successfully.")
else:
    print("Geodatabase does not exist.")





# Delete the raw data folder
if tl_folder.exists() and tl_folder.is_dir():
    shutil.rmtree(tl_folder)
    print(f"Folder {tl_folder} deleted successfully.")
else:
    print(f"Folder {tl_folder} does not exist.")
