# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import shutil
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
octl = OCTL(part = 1, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the codebook from the OCTL class object
cb = octl.cb
cb_df = octl.cb_df



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
