# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL

octl = OCTL(part = 0, version = 2026.1)

prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

cb = octl.cb
cbdf = octl.cbdf


# Get the Path of the raw data directory
path = Path(prj_dirs["data_raw"])

# List only the folders of the path
folders = list(path.glob("tl_*"))

# Remove the "tl_" prefix from the folder names
folders = [f.name.replace("tl_", "") for f in folders]

# Check if there is only one folder
if len(folders) == 1:
    folder_name = folders[0]
elif len(folders) > 1:
    folder_name = folders
else:
    raise ValueError("There should be at least one folder under the 'data/raw' directory")

# Get the year by converting the folder_name to an integer
year = int(folder_name)
print(f"Year: {year}")

# Get the folder path
tl_folder = Path(os.path.join(os.getcwd(), "data", "raw", f"tl_{year}"))
print(tl_folder)

# Remove the year prefix, and the extension and obtain only the unique names
tl_files = list(set([f.replace(f"tl_{year}_", "").split(".")[0] for f in os.listdir(tl_folder)]))
print(f"There are {len(tl_files)} unique files in the Tiger/Line Folder")

# Temporarily process the county shapefile
name_co = f"tl_{year}_us_county.shp"
path_co = os.path.join(str(tl_folder), name_co)
sdf_co = GeoAccessor.from_featureclass(path_co)
sdf_co.spatial.project(3857, transformation_name = None)
sdf_co = sdf_co[(sdf_co["STATEFP"] == "06") & (sdf_co["COUNTYFP"] == "059")]

# Define an empty dictionary to hold the imported spatial data frames
sdfs = {}

# Loop through all files
for f in tl_files:
    # Proceed only if the file is a shapefile (from the codebook)
    if cb[f]["type"] == "Shapefile":
        print(f"\nReading {f} with ArcGIS SDF...")
        # Get the filename and file path to disk
        file_name = f"tl_{year}_{f}.shp"
        file_path = os.path.join(str(tl_folder), file_name)
        # Formulate the key for the dictionary
        f_key = cb[f]["code2"]

        # Import the shapefiles as a spatially enabled data frame (sdf) and add them to the spatial dictionary
        try:
            # Convert to spatial data frame from ArcGIS API for Python
            sdf = GeoAccessor.from_featureclass(str(file_path))
            
            # Get the original reference WKID
            ref = sdf.spatial.sr.wkid
            
            # Check the spatial refernce via the spatial accessor on the dataframe
            if ref != 102100:
                print(f"- {f_key} is not in Web Mercator (EPSG: 3857). Converting...")
                # Converting to ESPG 3857
                sdf.spatial.project(3857, transformation_name = None)
                # Update the reference WKID
                ref = sdf.spatial.sr.wkid
                print(f"- Updated CRS WKID: {ref}")
                print(f"- Original Shape: {sdf.shape[0]} rows x {sdf.shape[1]} cols")
            
            # Check method and clip to OC Extend:
            match cb[f]["method"]:
                case "query":
                    # Only keep rows where the value of the field "STATEFP" is 06 and "COUNTYFP" is 059
                    sdf = sdf[(sdf["STATEFP"] == "06") & (sdf["COUNTYFP"] == "059")]
                case "disjoint":
                    # Select the rows where they are inside the County Polygon
                    if not sdf_co.empty:
                        county_geom = sdf_co.iloc[0]['SHAPE']
                        sdf = sdf[sdf['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
                    else:
                        print("Warning: County DataFrame is empty. Cannot filter arealm.")
                case "none":
                    pass
                case "":
                    print("No method specified. Skipping...")
                    pass
                case _:
                    raise ValueError(f"Invalid method: {cb[f]['method']}")
            
            print(f"- Updated Shape: {sdf.shape[0]} rows x {sdf.shape[1]} cols")

            # Add the sdf data frame to the sdfs dictionary
            sdfs[f_key] = sdf
            
            # Get and report the number of rows and columns, and the WKID reference code
            print(f"- Loaded {f_key}: {sdfs[f_key].shape[0]} rows, {sdfs[f_key].shape[1]} columns")
            print(f"- CRS WKID: {sdfs[f_key].spatial.sr.wkid}")

        except Exception as e: # pylint: disable = broad-except
            print(f"- Error Loading {f}: {e}")


sdf_names = list(sdfs.keys())
print(sdf_names)

sdf_us = [f for f in sdf_names if "_us_" in f]
print(sdf_us)

sdf_ca = [f for f in sdf_names if "_06_" in f]
print(sdf_ca)

sdf_oc = [f for f in sdf_names if "_06059_" in f]
print(sdf_oc)

# List the fields of each dataframe
for name, sdf in sdfs.items():
    print(f"\nFields in {name}:")
    print(sdf.columns)

# Delete rows when the value of the field "STATEFP" is not 6
for name, sdf in sdfs.items():
    sdf = sdf[sdf["STATEFP"] == 6]
    sdfs[name] = sdf
    print(f"Updated {name}: {sdfs[name].shape[0]} rows")

def filter_oc_data(sdf):
    sdf = sdf[sdf["STATEFP"] == 6]
    return sdf


sdf_us[2]
sdfs[sdf_us[2]].columns

sdfs[sdf_us[2]]

test = sdfs[sdf_us[2]]


test[(test["STATEFP"] == "06") & (test["COUNTYFP"] == "059")]




# County (US Level)
county = sdfs[f"tl_{year}_us_county"]
# Only keep the rows where the value of the field "STATEFP" is 6 and "COUNTYFP" is 059
county = county[(county["STATEFP"] == "06") & (county["COUNTYFP"] == "059")]

# County Subdivision (CA Level)
cousub = sdfs[f"tl_{year}_06_cousub"]
# Only keep the rows where the value of the field "STATEFP" is 6 and "COUNTYFP" is 059
cousub = cousub[(cousub["STATEFP"] == "06") & (cousub["COUNTYFP"] == "059")]




# Area Landmark Feature (CA Level)
arealm = sdfs[f"tl_{year}_06_arealm"]
# Select the rows of arealm where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    arealm = arealm[arealm['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter arealm.")

# Block Group (CA Level)
bg = sdfs[f"tl_{year}_06_bg"]
# Only keep the rows where the value of the field "STATEFP" is 6 and "COUNTYFP" is 059
bg = bg[(bg["STATEFP"] == "06") & (bg["COUNTYFP"] == "059")]


# Congressional District (CA Level)
cd119 = sdfs[f"tl_{year}_06_cd119"]
# Only keep the rows where the value of the field "CD119FP" is in the list ["38", "40", "45", "46", "47", "49"]
oc_cd119 = ["38", "40", "45", "46", "47", "49"]
cd119 = cd119[cd119["CD119FP"].isin(oc_cd119)]



# Elementary School District (CA Level)
elsd = sdfs[f"tl_{year}_06_elsd"]
# Select the rows of elsd where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    elsd = elsd[elsd['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter elsd.")

# Place (CA Level)
place = sdfs[f"tl_{year}_06_place"]
# Select the rows of place where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    place = place[place['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter place.")

# Point Landmark (CA Level)
pointlm = sdfs[f"tl_{year}_06_pointlm"]
# Select the rows of pointlm where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    pointlm = pointlm[pointlm['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter pointlm.")


# All Road Features (OC Level)
roads = sdfs[f"tl_{year}_06059_roads"]

# Primary and Secondary Roads (CA Level)
prisecroads = sdfs[f"tl_{year}_06_prisecroads"]
# Select the rows of prisecroads where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    prisecroads = prisecroads[prisecroads['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter prisecroads.")

# Rails (US Level)
rails = sdfs[f"tl_{year}_us_rails"]
# Select the rows of rails where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    rails = rails[rails['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter rails.")


# PUMA (CA Level)
puma20 = sdfs[f"tl_{year}_06_puma20"]
# Select the rows of puma20 where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    puma20 = puma20[puma20['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter puma20.")

# Secondary School Districts (CA Level)
scsd = sdfs[f"tl_{year}_06_scsd"]
# Select the rows of scsd where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    scsd = scsd[scsd['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter scsd.")

# State Legislative District (Lower) (CA Level)
sldl = sdfs[f"tl_{year}_06_sldl"]
# Select the rows of sldl where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    sldl = sldl[sldl['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter sldl.")

# State Legislative District (Upper) (CA Level)
sldu = sdfs[f"tl_{year}_06_sldu"]
# Select the rows of sldu where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    sldu = sldu[sldu['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter sldu.")

# Tabulation Block (CA Level)
tabblock20 = sdfs[f"tl_{year}_06_tabblock20"]
# Only keep the rows where the value of the field "STATEFP" is 6 and "COUNTYFP" is 059
tabblock20 = tabblock20[(tabblock20["STATEFP20"] == "06") & (tabblock20["COUNTYFP20"] == "059")]

# Tract (CA Level)
tract = sdfs[f"tl_{year}_06_tract"]
# Only keep the rows where the value of the field "STATEFP" is 6 and "COUNTYFP" is 059
tract = tract[(tract["STATEFP"] == "06") & (tract["COUNTYFP"] == "059")]

# Unified School Districts (CA Level)
unsd = sdfs[f"tl_{year}_06_unsd"]
# Select the rows of unsd where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    unsd = unsd[unsd['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter unsd.")

# Core Based Statistical Area (US Level)
cbsa = sdfs[f"tl_{year}_us_cbsa"]
# Select the rows of cbsa where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    cbsa = cbsa[cbsa['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter cbsa.")

# Coastline (US Level)
coastline = sdfs[f"tl_{year}_us_coastline"]
# Select the rows of coastline where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    coastline = coastline[coastline['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter coastline.")


# Combined Statistical Area (US Level)
csa = sdfs[f"tl_{year}_us_csa"]
# Select the rows of csa where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    csa = csa[csa['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter csa.")

# International Boundary (US Level)
internationalboundary = sdfs[f"tl_{year}_us_internationalboundary"]
# Select the rows of internationalboundary where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    internationalboundary = internationalboundary[internationalboundary['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter internationalboundary.")

# Metropolitan Division (US Level)
metdiv = sdfs[f"tl_{year}_us_metdiv"]
# Select the rows of metdiv where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    metdiv = metdiv[metdiv['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter metdiv.")

# Military Installation (US Level)
mil = sdfs[f"tl_{year}_us_mil"]
# Select the rows of mil where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    mil = mil[mil['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter mil.")

# Urban Area (US Level)
uac20 = sdfs[f"tl_{year}_us_uac20"]
# Select the rows of uac20 where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    uac20 = uac20[uac20['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter uac20.")

# ZCTA (US Level)
zcta520 = sdfs[f"tl_{year}_us_zcta520"]
# Select the rows of zcta520 where they are inside the county polygon
if not county.empty:
    county_geom = county.iloc[0]['SHAPE']
    zcta520 = zcta520[zcta520['SHAPE'].apply(lambda x: not x.disjoint(county_geom))]
else:
    print("Warning: County DataFrame is empty. Cannot filter zcta520.")

# Address Range Feature (OC Level)
addrfeat = sdfs[f"tl_{year}_06059_addrfeat"]

# Area Hydrography Feature (OC Level)
areawater = sdfs[f"tl_{year}_06059_areawater"]

# All Lines Edges Feature (OC Level)
edges = sdfs[f"tl_{year}_06059_edges"]

# Topological Faces (polygons with all geocodes) (OC Level)
faces = sdfs[f"tl_{year}_06059_faces"]

# Linear Hydrography Features (OC Level)
linearwater = sdfs[f"tl_{year}_06059_linearwater"]
