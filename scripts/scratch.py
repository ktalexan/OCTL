# Import necessary libraries
import os, sys
from datetime import datetime as dt
from pathlib import Path
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