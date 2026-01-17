# Import necessary libraries
import os, sys
from datetime import datetime as dt
from pathlib import Path
import wmi
import json
import shutil
import importlib
import pandas as pd
import arcpy
from arcpy import metadata as md
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL


# Set pandas options
pd.options.mode.copy_on_write = True

# Set environment workspace to the current working directory
arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True

# Initialize the OCTL class object
#importlib.reload(sys.modules['octl'])
octl = OCTL(part = 1, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the master codebook (load from JSON file)
cb = octl.master_codebook(create = False)



test = folder_metadata["2010"]

test["layers"]























# Add the layers to the maps in the ArcGIS Pro project
for key, m in map_dict.items():
    year = key.replace("TL", "")
    path = os.path.join(prj_dirs["gis"], key + ".gdb")
    lyr_dict[key] = {}
    print(f"\n- Map: {key} Layers:")
    for lyr in cb[year].values():
        # Get the layer path
        lyr_path = os.path.join(path, lyr["code"])
        # Add the layer to the map
        map_lyr = m.addDataFromPath(lyr_path)
        # Store the layer name in the dictionary
        lyr_dict[key][lyr["code"]] = map_lyr.name
        # Set the layer visibility to False
        map_lyr.visible = False
        print(f"- Added layer: {lyr['code']} to map: {key}")


# Add the layers to the maps in the ArcGIS Pro project
for key, m in map_dict.items():
    year = key.replace("TL", "")
    path = os.path.join(prj_dirs["gis"], key + ".gdb")
    lyr_dict[key] = {}
    print(f"\n- Map: {key} Layers:")
    for lyr in cb[year].values():
        # Get the layer path
        lyr_path = os.path.join(path, lyr["code"])
        print(f"- Layer path: {lyr_path}")


# Get the raw data from the OCTL class object
tl_metadata = self.get_raw_data(export = True)

# Load the codebook for the specified year
cb = self.load_cb(tl_metadata["year"], cbdf = False)

# Create a scratch geodatabase
scratch_gdb = self.scratch_gdb(method = "create")

# Set environment workspace to the folder containing shapefiles
arcpy.env.workspace = os.path.join(self.prj_dirs["root"], tl_metadata["path"])

# Get a list of all shapefiles in the folder
shapefiles = arcpy.ListFeatureClasses("*.shp")
tables = arcpy.ListTables("*.dbf")


def test_function(remote = False):
    if remote:
        # asl the user to provide remote path
        remote_path = Path(input("Please provide the remote path: "))
        # List all the folders in the remote path that begin with "TL"
        #tl_folders = [f for f in remote_path.iterdir() if f.is_dir() and f.name.startswith("tl")]
        tl_folders = [d.name for d in remote_path.iterdir() if d.is_dir() and d.name.startswith("tl")]

        for folder in tl_folders:
            #scratch_gdb = octl.scratch_gdb(method = "create")

            arcpy.env.workspace = os.path.join(remote_path.as_posix(), folder)
            #arcpy.env.workspace = .as_posix()
            shapefiles = arcpy.ListFeatureClasses("*.shp")
            tables = arcpy.ListTables("*.dbf")
            print(f"Folder: {folder} - Shapefiles: {len(shapefiles)} - Tables: {len(tables)}")

            

    else:
        print("Running in local mode")

test_function(remote = True)


remote_path = Path(r"d:\Professional\OCPW Projects\OCGD\OCTL\OCTLRaw")

remote_path.as_posix()