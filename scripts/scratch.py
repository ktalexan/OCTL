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









#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Fx: Process Shapefiles ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def process_shapefiles(self) -> dict:
#     """
#     Process shapefiles from the raw data directory and create a geodatabase.
#     Args:
#         Nothing
#     Returns:
#         final_list (dict): A dictionary of feature classes and their codes.
#     Raises:
#         Nothing
#     Example:
#         >>>process_shapefiles()
#     Notes:
#         This function processes shapefiles from the raw data directory and creates a geodatabase.
#     """

# Get the raw data from the OCTL class object
tl_metadata = octl.get_raw_data(export = True)

# Load the codebook for the specified year
cb = octl.load_cb(tl_metadata["year"], cbdf = False)

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
    arcpy_messages()
    print(f"\nSuccessfully imported {len(shapefiles)} shapefiles to {scratch_gdb}\n")
else:
    print("No shapefiles found in the specified directory.")

if tables:
    # FeatureClassToGeodatabase accepts a list of inputs
    arcpy.conversion.TableToGeodatabase(tables, scratch_gdb)
    arcpy_messages()
    print(f"\nSuccessfully imported {len(tables)} tables to {scratch_gdb}\n")
else:
    print("No tables found in the specified directory.")

# Create a geodatabase for the year
tl_gdb = create_gdb(tl_metadata["year"])

print(f"Processing {cb['county']['file']}...")

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

# Select rows with State and County FIPS codes
if state_field and county_field:
    # Select rows with State and County FIPS codes
    arcpy.analysis.Select(
        in_features = in_oc,
        out_feature_class = out_oc,
        where_clause = f"{state_field} = '06' And {county_field} = '059'"
    )
    arcpy_messages()

# Check if the output feature class is empty
if int(arcpy.GetCount_management(out_oc).getOutput(0)) == 0:
    arcpy.management.Delete(out_oc)
    arcpy_messages("-")
    print(f"- Deleted empty feature class: {out_oc}")


# Create a list to store the final feature classes
final_list = dict()

# Create a list of feature classes to process and remove the us_county feature class
fc_list = list(cb.keys())
fc_list.remove("county")
final_list["CO"] = "county"

# Alter the alias name of the county feature class
arcpy.AlterAliasName(out_oc, cb["county"]["alias"])
arcpy_messages()

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
            arcpy_messages("-")
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                arcpy_messages("-")
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                arcpy_messages("-")
        case "copy":
            # Copy the feature class as is
            arcpy.management.Copy(
                in_data = in_fc,
                out_data = out_fc,
                data_type = "FeatureClass",
                associated_data = None
            )
            arcpy_messages("-")
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                arcpy_messages("-")
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                arcpy_messages("-")
        case "within":
            # Create a temporary layer (this stays in memory, not in your Pro Map)
            arcpy.management.MakeFeatureLayer(in_fc, "temp_lyr")
            arcpy_messages("-")
            # Check if the temp_lyr is empty
            if arcpy.management.GetCount("temp_lyr") == 0:
                arcpy.management.Delete("temp_lyr")
                arcpy_messages("-")
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
            arcpy_messages("-")
            # Export the selection to a new fc
            arcpy.conversion.FeatureClassToFeatureClass("temp_lyr", tl_gdb, code)
            arcpy_messages("-")
            # Delete the temporary layer
            arcpy.management.Delete("temp_lyr")
            arcpy_messages("-")
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                arcpy_messages("-")
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                arcpy_messages("-")
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
            arcpy_messages("-")
            # Check if the output feature class is empty
            if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                arcpy.management.Delete(out_fc)
                arcpy_messages("-")
                print(f"- Deleted empty feature class: {out_fc}")
            else:
                final_list[code] = f
                # Alter the alias name of the feature class
                arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                arcpy_messages("-")
        case _:
            print(f"- No valid method specified for {fc}. Skipping...")
            continue

# Get a list of all feature classes in the TL geodatabase
try:
    arcpy.env.workspace = tl_gdb
    tl_fcs = arcpy.ListFeatureClasses()
    tl_tables = arcpy.ListTables()
    tl_features = sorted(tl_fcs) + sorted(tl_tables)
finally:
    arcpy.env.workspace = os.getcwd()

# Apply metadata to the TL geodatabase
print(f"\nApplying metadata to the TL geodatabase: {tl_gdb}")
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
scratch_gdb(method = "delete")

# Create a metadata object for the TL geodatabase
print(f"\nApplying metadata to the TL geodatabase:{tl_gdb}")
md_gdb = md.Metadata(tl_gdb)
md_gdb.title = f"TL{tl_metadata["year"]} TigerLine Geodatabase"
md_gdb.tags = "Orange County, California, OCTL, TigerLine, Geodatabase"
md_gdb.summary = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data"
md_gdb.description = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data. The data contains feature classes for all TigerLine data available for Orange County, California. Version: {version}, last updated on {data_date}."
md_gdb.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
md_gdb.accessConstraints = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
md_gdb.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"
md_gdb.save()

# Print the list of feature classes in the TL geodatabase
print(f"\nSuccessfully processed shapefiles:\n{tl_fcs}")

    # Return the list of feature classes in the TL geodatabase
    # return final_list























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