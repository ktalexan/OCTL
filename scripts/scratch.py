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

#tl_folder = Path(os.path.join(octl.prj_dirs["data_raw"], f"tl_{year}"))

tl_folder = Path(os.path.join(octl.prj_dirs["data_raw"], f"tl_{year}"))


# Create a new file geodatabase
# Define where the GDB will be stored
out_folder_path = prj_dirs["gis"]
gdb_name = f"TL{year}.gdb"

# Execute CreateFileGDB
if not arcpy.Exists(os.path.join(out_folder_path, gdb_name)):
    # Create a new file geodatabase
    arcpy.management.CreateFileGDB(out_folder_path, gdb_name)
    print(f"Geodatabase {gdb_name} created successfully.")
else:
    # Delete the existing geodatabase
    arcpy.management.Delete(os.path.join(out_folder_path, gdb_name))
    # Create a new file geodatabase
    arcpy.management.CreateFileGDB(out_folder_path, gdb_name)
    print("Geodatabase already exists. Deleted and recreated.")



# Process the folder and create the spatial data frames
sdfs = octl.process_folder(tl_files, tl_folder, year)


# For each key and contents of the sdfs dictionary, create a feature class in the geodatabase
for key, sdf in sdfs.items():
    # Create a feature class in the geodatabase and replace if it already exists
    sdf.spatial.to_featureclass(os.path.join(out_folder_path, gdb_name, key))
    print(f"Feature class {key} created successfully.")




# Delete the raw data folder
if tl_folder.exists() and tl_folder.is_dir():
    shutil.rmtree(tl_folder)
    print(f"Folder {tl_folder} deleted successfully.")
else:
    print(f"Folder {tl_folder} does not exist.")







# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import shutil
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL

pd.options.mode.copy_on_write = True

# Initialize the OCTL class object
octl = OCTL(part = 0, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the codebook from the OCTL class object
cb = octl.cb
cbdf = octl.cbdf

# Get the raw data from the OCTL class object
tl_data = octl.tl_data

# Create a geodatabase for the year
gdb_name = octl.create_gdb()

# Process the county
sdf_co = octl.process_county()
