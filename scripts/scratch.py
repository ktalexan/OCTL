# Import necessary libraries
import os, sys, datetime
from pathlib import Path
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from octl import OCTL

pd.options.mode.copy_on_write = True

octl = OCTL(part = 0, version = 2026.1)

prj_meta = octl.prj_meta
prj_dirs = octl.prj_dirs

cb = octl.cb
cbdf = octl.cbdf



# Get the raw data from the OCTL class object
tl_files, year = octl.get_raw_data()

tl_folder = Path(os.path.join(octl.prj_dirs["data_raw"], f"tl_{year}"))

sdfs = octl.process_folder(tl_files, tl_folder, year)
