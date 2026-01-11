# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import shutil
import pandas as pd
import arcpy
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



def process_metadata():
    fc_metadata = {
        "us_aitsn": {
            "abbrev": "AITSN",
            "alias": f"OCTL {tl_data['year']} Tribal Subdivisions",
            "type": "Shapefile",
            "fcname": "TS",
            "group": "Geographic Areas",
            "category": "American Indian Area Geography",
            "label": "American Indian Tribal Subdivision",
            "title": f"OCTL {tl_data['year']} Tribal Subdivisions Feature Class",
            "tags": "Orange County, California, OCTL, TigerLines, Tribal Subdivisions, American Indian Area Geography",
            "summary": f"Orange County Tiger Lines {tl_data['year']} Tribal Subdivisions Feature Class",
            "description" f"Orange County Tiger Lines {tl_data['year']} Tribal Subdivisions Feature Class",
            "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
            "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
            "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data",
        }
    }



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