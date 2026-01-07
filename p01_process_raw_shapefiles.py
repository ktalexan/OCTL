# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: Orange County Tiger/Lines Processing (OCTL)
# Title: Part 1: Process Raw Shapefiles ----
# Author: Dr. Kostas Alexandridis, GISP
# Version: 2026.1, Date: January 2026
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOrange County Tiger/Lines Processing (OCTL): Part 1: Process Raw Shapefiles\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Preliminaries\n")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## 1.1. Referencing Libraries and Initialization ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.1. Referencing Libraries and Initialization\n")

import os, datetime
import arcpy
from arcpy import metadata as md
from arcpy import env
from octl import OCTL


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## 1.2. Basic Definitions ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.2. Basic Definitions\n")

# Main project path
prj_path = os.path.split(arcpy.env.workspace)[0]
print("\nMain project path: ", prj_path)

# Main project geodatabase
gdb_main = "octlAgp.gdb"
gdb_main_path = os.path.join(prj_path, gdb_main)
print("\nMain project geodatabase: ", gdb_main_path)

# List of project years
year_list = [*range(2010, 2025, 1)]
print("\nList of project years: ", year_list)

# Geodatabase name list construction from years
gdb_list = [f"octl{y}.gdb" for y in year_list]
gdb_path_list = [os.path.join(prj_path, f"octl{y}.gdb") for y in year_list]
print(gdb_path_list)

# US Congress years and their associated Congress Numbers
year_congress = [(2010, 111), (2011, 112), (2012, 112), (2013, 113), (2014, 114), (2015, 114), (2016, 115), (2017, 115), (2018, 116), (2019, 116), (2020, 116), (2021, 116), (2022, 118), (2023, 118), (2024, 119)]

for (y, c) in year_congress:
    print(f"Year: {y} | Congress: {c}th | Geodatabase: octl{y}.gdb")

# Initialize OCTL class
octl = OCTL()


### Metadata Icons ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Metadata icon logo paths
logo_icons = {
    "D": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/e2c4cd39783a4d1bb0925ead15a23cdc/data",
    "E": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/cc5efcd5c13d4025959c689a7f08e8cf/data",
    "H": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/412ef3a8487141dc8efbf7e2002cf695/data",
    "S": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/59662c66336141a4af9e888c10460905/data"
    }
