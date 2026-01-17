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
importlib.reload(sys.modules['octl'])
octl = OCTL(part = 1, version = 2026.1)

# Get the project metadata and directories from the OCTL class object
prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

# Get the raw metadata
tl_metadata = octl.get_raw_data(export = True)

# Get the codebook from the OCTL class object
cb, cb_df = octl.load_cb(tl_metadata["year"], cbdf = True)


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

# Define the input and output feature classes for the county feature class
in_oc = os.path.join(scratch_gdb, tl_metadata["layers"]["county"]["file"]
)
out_oc = os.path.join(tl_gdb, cb["county"]["code"])


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
    for message in arcpy.GetMessages().splitlines():
        print(f"- {message}")

# Check if the output feature class is empty
if int(arcpy.GetCount_management(out_oc).getOutput(0)) == 0:
    arcpy.management.Delete(out_oc)

# Create a list to store the final feature classes
final_list = dict()

# Create a list of feature classes to process and remove the us_county feature class
fc_list = list(cb.keys())
fc_list.remove("county")
final_list["CO"] = "county"

# Alter the alias name of the county feature class
arcpy.AlterAliasName(out_oc, cb["county"]["alias"])


# Loop through the feature classes in the fc_list
for f in fc_list:
    # Define the feature class name and code from the codebook
    fc = cb[f]["file"]
    code = cb[f]["code"]
    # Define the input and output feature classes
    in_fc = os.path.join(scratch_gdb, fc)
    out_fc = os.path.join(tl_gdb, code)
    method = cb[f]["method"]
    print(f"Processing {fc}...")

    # Match the method for executing geoprocessing operations
    match method:
        case "clip":
            # Clip the feature class to the extent of the county
            arcpy.analysis.Clip(
                in_features = in_fc,
                clip_features = out_oc,
                out_feature_class = out_fc,
                cluster_tolerance = None
            )
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
        case "copy":
            # Copy the feature class as is
            arcpy.management.Copy(
                in_data = in_fc,
                out_data = out_fc,
                data_type = "FeatureClass",
                associated_data = None
            )
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
        case "within":
            # Create a temporary layer (this stays in memory, not in your Pro Map)
            arcpy.management.MakeFeatureLayer(in_fc, "temp_lyr")
            # Check if the temp_lyr is empty
            if arcpy.management.GetCount("temp_lyr") == 0:
                arcpy.management.Delete("temp_lyr")
                print(f"- Deleted empty feature class: {out_fc}")
                continue
            # Apply your spatial selection with the negative distance
            arcpy.management.SelectLayerByLocation(
                in_layer = "temp_lyr",
                overlap_type = "WITHIN_A_DISTANCE",
                select_features = out_oc,
                search_distance = "-1000 Feet",
                selection_type = "NEW_SELECTION",
                invert_spatial_relationship = "NOT_INVERT"
            )
            # Export the selection to a new fc
            arcpy.conversion.FeatureClassToFeatureClass("temp_lyr", tl_gdb, code)
            # Delete the temporary layer
            arcpy.management.Delete("temp_lyr")
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
        case "query":
            # Get the field name from the arcpy.ListFields(in_fc) if field.name contains "STATEFP" and "COUNTYFP"
            state_field = ""
            county_field = ""
            for field in arcpy.ListFields(in_fc):
                if "STATEFP" in field.name:
                    state_field = field.name
                elif "COUNTYFP" in field.name:
                    county_field = field.name
            # Select rows with State and County FIPS codes
            arcpy.analysis.Select(
                in_features = in_fc,
                out_feature_class = out_fc,
                where_clause = f"{state_field} = '06' And {county_field} = '059'"
            )
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
        case _:
            print(f"- No valid method specified for {fc}. Skipping...")
            continue



# Get a list of all feature classes in the TL geodatabase
try:
    arcpy.env.workspace = tl_gdb
    tl_fcs = arcpy.ListFeatureClasses()
    tl_tbls = arcpy.ListTables()
    tl_features = sorted(tl_fcs + tl_tbls)
finally:
    arcpy.env.workspace = os.getcwd()

for fc in tl_features:
    # Select the key from the cb dictionary where the value of cb[key]["code"] matches fc
    key = next((k for k, v in cb.items() if v["code"] == fc), None)

    # Define a metadata object for the feature class
    mdo = md.Metadata()
    mdo.title = cb[key]["title"]
    mdo.tags = cb[key]["tags"]
    mdo.summary = cb[key]["summary"]
    mdo.description = cb[key]["description"]
    mdo.credits = cb[key]["credits"]
    mdo.accessConstraints = cb[key]["access"]
    mdo.thumbnailUri = cb[key]["uri"]

    # Apply the metadata to the feature class
    md_fc = md.Metadata(os.path.join(tl_gdb, fc))
    if not md_fc.isReadOnly:
        md_fc.copy(mdo)
        md_fc.save()
        print(f"- Metadata applied to {final_list[fc]} ({fc})")
    else:
        print(f"- Metadata is read-only for {final_list[fc]} ({fc})")

# Delete the scratch geodatabase
octl.scratch_gdb(method = "delete")

# Create a metadata object for the TL geodatabase
print(f"\nApplying metadata to the TL geodatabase:{tl_gdb}")
md_gdb = md.Metadata(tl_gdb)
md_gdb.title = f"TL{tl_metadata["year"]} TigerLine Geodatabase"
md_gdb.tags = "Orange County, California, OCTL, TigerLine, Geodatabase"
md_gdb.summary = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data"
md_gdb.description = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data. The data contains feature classes for all TigerLine data available for Orange County, California."
md_gdb.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
md_gdb.accessConstraints = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
md_gdb.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"
md_gdb.save()
