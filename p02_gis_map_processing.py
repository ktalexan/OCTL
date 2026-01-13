# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: Orange County Tiger/Lines Processing (OCTL)
# Title: Part 2: ArcGis Pro Project Map Processing ----
# Author: Dr. Kostas Alexandridis, GISP
# Version: 2026.1, Date: January 2026
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOrange County Tiger/Lines Processing (OCTL): Part 2: ArcGis Pro Project Map Processing\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Preliminaries\n")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## 1.1. Referencing Libraries and Initialization ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.1. Referencing Libraries and Initialization\n")

# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import shutil
import pandas as pd
import arcpy
from arcpy import metadata as md
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## 1.2. Basic Definitions ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.2. Basic Definitions\n")

# Set pandas options
pd.options.mode.copy_on_write = True

# Set environment workspace to the current working directory
arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True

# Initialize the OCTL class object
octl = OCTL(part = 2, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the codebook from the OCTL class object
cb = octl.cb
cbdf = octl.cb_df


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. ArcGIS Pro Project Map Processing ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. ArcGIS Pro Project Map Processing\n")



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## 2.1. Create Maps in ArcGIS Pro Project ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.1. Create Maps in ArcGIS Pro Project\n")

# Get the geodatabase dictionary from the OCTL class object
gdb_dict = octl.get_gdb_dict()

# Get the list of years from the geodatabase dictionary keys
year_list = [int(y) for y in gdb_dict.keys()]

# Load the ArcGIS Pro project
aprx_path = prj_dirs['gis_aprx']
aprx = arcpy.mp.ArcGISProject(aprx_path)

# Create the list of map names based on the years
map_list = [f"TL{year}" for year in year_list]


### Delete Maps ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n- Delete Maps")

# Clean up the maps in the project structure
if aprx.listMaps():
    for m in aprx.listMaps():
        print(f"- Removing {m.name} map from the project...")
        aprx.deleteItem(m)
else:
    print("- No maps to remove from the project.")


### Create New Maps ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create New Maps")

# Create new raw data maps in current ArcGIS Pro project
# for each of the maps in the list, if it exists, delete it
for m in map_list:
    for i in aprx.listMaps():
        if i.name == m:
            print(f"Deleting map: {m}")
            aprx.deleteItem(i)
    # Create new maps
    print(f"Creating map: {m}")
    aprx.createMap(m)


# Store the map objects in a dictionary
map_dict = {}
for m in aprx.listMaps():
    map_dict[m.name] = m


### Change Basemap to "Light Gray Canvas" ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n- Change Basemap to 'Light Gray Canvas'")

# Change the Map Base Map to "Light Gray Canvas"
for m in map_dict.values():
    for l in m.listLayers():
        if l.isBasemapLayer:
            print(f"- Removing existing basemap layer from {m.name}...")
            m.removeLayer(l)
    print(f"- Setting {m.name} basemap to 'Light Gray Canvas'...")
    m.addBasemap("Light Gray Canvas")

# Turn off the basemap layer visibility
for m in map_dict.values():
    print(f"- Turning off basemap layer visibility in {m.name}...")
    for l in m.listLayers():
        if l.isBasemapLayer and l.name == "Light Gray Reference":
            l.visible = False
    

### Save the ArcGIS Pro Project ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n- Save the ArcGIS Pro Project")

# Save the changes to the ArcGIS Pro project
aprx.save()
