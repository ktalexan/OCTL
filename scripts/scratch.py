# Import necessary libraries
import os, sys, datetime
from pathlib import Path
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

# Get the codebook from the OCTL class object
cb = octl.cb
cb_df = octl.cb_df






# Get the raw data from the OCTL class object
tl_metadata = octl.get_raw_data(export = True)

# Create a scratch geodatabase
scratch_gdb = octl.scratch_gdb(method = "create")

# Set environment workspace to the folder containing shapefiles
arcpy.env.workspace = os.path.join(prj_dirs["root"], tl_metadata["path"])

# Get a list of all shapefiles in the folder
shapefiles = arcpy.ListFeatureClasses("*.shp")
tables = arcpy.ListTables("*.dbf")

if shapefiles:
    # FeatureClassToGeodatabase accepts a list of inputs
    arcpy.conversion.FeatureClassToGeodatabase(shapefiles, scratch_gdb)
    print(arcpy.GetMessages())
    print(f"\nSuccessfully imported {len(shapefiles)} shapefiles to {scratch_gdb}\n")
else:
    print("No shapefiles found in the specified directory.")


if tables:
    # FeatureClassToGeodatabase accepts a list of inputs
    arcpy.conversion.TableToGeodatabase(tables, scratch_gdb)
    print(arcpy.GetMessages())
    print(f"\nSuccessfully imported {len(tables)} tables to {scratch_gdb}\n")
else:
    print("No tables found in the specified directory.")

try:
    # Set environment workspace to the scratch geodatabase
    arcpy.env.workspace = scratch_gdb

    # List of all feature classes in the scratch geodatabase
    scratch_fcs = arcpy.ListFeatureClasses()
    #scratch_tbls = arcpy.ListTables()
finally:
    # Set environment workspace to the current working directory
    arcpy.env.workspace = os.getcwd()

# Create a geodatabase for the year
tl_gdb = octl.create_gdb(tl_metadata["year"])

tl_metadata["layers"]["county"]["file"]

# Define the input and output feature classes for the county feature class
in_oc = os.path.join(scratch_gdb, tl_metadata["layers"]["county"]["file"]
)
out_oc = os.path.join(tl_gdb, cb["us_county"]["code2"])


# Get the field name from the arcpy.ListFields(in_oc) if field.name contains "STATEFP" and "COUNTYFP"
state_field = ""
county_field = ""
for field in arcpy.ListFields(in_oc):
    if "STATEFP" in field.name:
        state_field = field.name
    elif "COUNTYFP" in field.name:
        county_field = field.name


if state_field and county_field:
    # Select rows with State and County FIPS codes
    arcpy.analysis.Select(
        in_features = in_oc,
        out_feature_class = out_oc,
        where_clause = f"{state_field} = '06' And {county_field} = '059'"
    )

# Check if the output feature class is empty
if int(arcpy.GetCount_management(out_oc).getOutput(0)) == 0:
    arcpy.management.Delete(out_oc)

# Create a list to store the final feature classes
final_list = dict()

# Create a list of feature classes to process and remove the us_county feature class
fc_list = [f.replace(f"tl_{tl_metadata["year"]}_", "") for f in scratch_fcs]

co_name = f"{tl_metadata["layers"]["county"]["spatial"]}_{tl_metadata["layers"]["county"]["abbrev"]}"
fc_list.remove(co_name)
final_list["CO"] = co_name

# Alter the alias name of the county feature class
arcpy.AlterAliasName(out_oc, cb[co_name]["alias"])

# Create a metadata dictionary for the feature classes
md_dict = self.process_metadata(tl_metadata["year"])


gdb_dict = octl.get_gdb_dict()


gdb_dict["2020"].keys()


for keys, g in gdb_dict.items():
    for k, v in g.items():
        path = os.path.join

for y, g in gdb_dict.items():
    print(f"\nAltering alias names in geodatabase for year {y}:")
    g_path = os.path.join(prj_dirs["gis"], f"TL{y}.gdb")
    for m, f in g.items():
        m_path = os.path.join(g_path, m)
        f_alias = f["alias"]
        arcpy.AlterAliasName(m_path, f_alias)
        print(f"- Altered alias name of {m} to {f_alias}")


for y, g in gdb_dict.items():
    print(g.keys())

g1 = list(gdb_dict["2020"].keys())
g2 = list(gdb_dict["2022"].keys())

# Compare the keys of the two dictionaries
g_diff = set(g1) - set(g2)

gdb_dict["2020"]["RL"]["alias"]

gdb_dict["2010"]["CD"]["alias"]
gdb_dict["2010"]["CD"]["title"]

gdb_dict["2025"]["CD"]["alias"]
gdb_dict["2025"]["CD"]["title"]

for i in ['RL', 'SC', 'SM', 'MD']:
    print(gdb_dict["2020"][i]["abbrev"])


    
# US Congress years and their associated Congress Numbers
year_congress = {"2010": "111", "2011": "112", "2012": "112", "2013": "113", "2014": "114", "2015": "114", "2016": "115", "2017": "115", "2018": "116", "2019": "116", "2020": "116", "2021": "116", "2022": "118", "2023": "118", "2024": "119", "2025": "119"}

for y, c in year_congress.items():
    print(f"Year: {y} | Congress: {c}th | Geodatabase: octl{y}.gdb")
