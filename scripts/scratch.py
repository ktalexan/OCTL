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
octl = OCTL(part = 0, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the codebook from the OCTL class object
cb = octl.cb
cbdf = octl.cbdf

# Get the raw data
tl_data = octl.tl_data

# Process the shapefiles and get the dictionary of feature classes and codes
tl_dict = octl.process_shapefiles()




list(cb.keys())


scratch_query_fcs = [f for f in scratch_fcs if cb[f.replace(f"tl_{tl_data['year']}_", "").replace(".shp", "")]["method"] == "query"]

for fc in scratch_query_fcs:
    code2 = cb[fc.replace(f"tl_{tl_data['year']}_", "").replace(".shp", "")]["code2"]
    arcpy.analysis.Select(
            in_features = os.path.join(scratch_gdb, fc),
            out_feature_class = os.path.join(tl_gdb, code2),
        where_clause = "STATEFP = '06' And COUNTYFP = '059'"
    )

arcpy.management.Copy(
    in_data=os.path.join(scratch_gdb, fc),
    out_data=os.path.join(tl_gdb, code),
    data_type="FeatureClass",
    associated_data=None
)


arcpy.ListFeatureClasses(tl_gdb)