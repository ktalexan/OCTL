# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL

octl = OCTL()
octl.main()

# List the folders under the "data/raw" directory
raw_dir = Path(os.path.join(os.getcwd(), "data", "raw"))
# List only the folders in the raw_dir
folders = list(raw_dir.glob("tl_*"))
# remove the "tl_" prefix from the folder names
folders = [f.name.replace("tl_", "") for f in folders]
# Make sure there is only one folder
if len(folders) != 1:
    raise ValueError("There should be only one folder under the 'data/raw' directory")
folder_name = folders[0]
# Remove the "tl_" prefix from the folder name and convert to integer
year = int(folder_name.replace("tl_", ""))
print("Year: ", year)

# Get the folder path
folder_path = Path(os.path.join(os.getcwd(), "data", "raw", f"tl_{year}"))
print(folder_path)
# List the shapefiles in the folder
shapefiles = list(folder_path.glob("*.shp"))
# Print the shapefiles
print(shapefiles)

# Using ArcGIS API for Python (Spatially Enabled DataFrame)
sdfs = {}
for shp in shapefiles:
    layer_name = shp.stem
    print(f"Reading {layer_name} with ArcGIS SEDF...")
    try:
        # from_featureclass can read shapefiles if passed as path
        sdfs[layer_name] = GeoAccessor.from_featureclass(str(shp))
        print(f"  - Loaded {layer_name}: {sdfs[layer_name].shape[0]} rows, {sdfs[layer_name].shape[1]} columns")
        print(f"  - CRS WKID: {sdfs[layer_name].spatial.sr.wkid}")
    except Exception as e:
        print(f"  - Error loading {layer_name}: {e}")


for name, sdf in sdfs.items():
    # Access the spatial reference via the spatial accessor on the dataframe
    if sdf.spatial.sr.wkid == 4269:
        print(f"\n{name} is in NAD 1983 (EPSG:4269). Converting to Web Mercator (EPSG:3857)...")
        sdf.spatial.project(3857, transformation_name = None)
        print(f"  - Updated CRS WKID: {sdf.spatial.sr.wkid}")
        # Update the dictionary with the projected dataframe
        print(f"Updating the dictionary for {name} with the projected dataframe...")
        sdfs[name] = sdf # Update the dictionary with the projected dataframe


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


