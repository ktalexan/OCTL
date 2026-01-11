# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: Orange County Tiger Lines (OCTL)
# Title: Main Processing Script ----
# Author: Dr. Kostas Alexandridis, GISP
# Version: 2025.2, Date: December 2025
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import necessary libraries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, sys
import json
from pathlib import Path
import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Class Containing the OCTL Processing Workflow Functions ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OCTL:
    """Class Containing the OCTL Processing Workflow Functions.

    This class encapsulates the workflow for processing Orange County Tiger Lines (OCTL)
    data. It includes methods for initialization, main execution, and retrieving
    metadata for various feature classes.
    """
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Initialize the OCTL Class ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, part: int, version: float):
        """Initialize the OCTL class."""
        self.part = part
        self.version = version
        self.base_path = os.getcwd()

        # Create a prj_meta variable calling the project_metadata function
        self.prj_meta = self.project_metadata(silent = False)

        # Create a prj_dirs variable calling the project_directories function
        self.prj_dirs = self.project_directories(silent = False)

        # Load the codebook
        self.cb_path = os.path.join(self.prj_dirs["codebook"], "cb.json")
        self.cb, self.cbdf = self.load_cb(silent = False)

        # Get the raw data
        self.tl_data = self.get_raw_data()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Obtain the US Congress Number ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_congress_number(self, census_year: int) -> int:
        """
        Returns the US Congress Number given a year.
        Args:
            census_year (int): The year of the US Congress
        Returns:
            congress_no (int): The US Congress number for the year.
        Raises:
            ValueError: if the census_year is not integer, or if it is not numeric.
        Example:
            >>> congress_number = self.congress_number(census_year = 2020)
        Notes:
            This function queries the congress dictionary using the US Congress year, and obtains (and returns) the US Congress Number for that year.
        """
        # US Congress Number by Year Dictionary
        congress_dict = {
            2010: 111,
            2011: 112,
            2012: 112,
            2013: 113,
            2014: 114,
            2015: 114,
            2016: 115,
            2017: 115,
            2018: 116,
            2019: 116,
            2020: 116,
            2021: 116,
            2022: 118,
            2023: 118,
            2024: 119,
            2025: 119
        }

        # Get the Congress number from the dictionary
        congress_no = int(congress_dict.get(census_year))

        # Return the Congress Number
        return congress_no


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Create Project Metadata ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def project_metadata(self, silent: bool = False) -> dict:
        """
        Function to generate project metadata for the OCTL data processing object.
        Args:
            silent (bool): If True, suppresses the print output. Default is False.
        Returns:
            metadata (dict): A dictionary containing the project metadata. The dictionary includes: name, title, description, version, author, years, date_start, date_end, date_updated, and TIMS metadata.
        Raises:
            ValueError: If part is not an integer, or if version is not numeric.
        Example:
            >>> metadata = self.project_metadata()
        Notes:
            This function generates a dictionary with project metadata based on the provided part and version.
            The function also checks if the TIMS metadata file exists and raises an error if it does not.
        """
        
        # Match the part to a specific step and description (with default case)
        match self.part:
            case 0:
                step = "Part 0: General Data Updating"
                desc = "General Data Updating and Mentenance"
            case 1:
                step = "Part 1: Raw Data Processing"
                desc = "Processing Raw Tiger/Line Shapefiles Folder"
            case 2:
                step = "Part 2: Geodatabase Data Processing"
                desc = "Processing Spatial Data Frame Data to Yearly Geodatabase Feature Classes"
            case 3:
                step = "Part 3: Sharing and Publishing Feature Classes"
                desc = "Sharing and Publishing Feature Classes to ArcGIS Online"
            case _:
                step = "Part 0: General Data Updating"
                desc = "General Data Updating and Maintenance (default)"
        
        # Create a dictionary to hold the metadata
        metadata = {
            "name": "OCTL Tiger/Line Data Processing",
            "title": step,
            "description": desc,
            "version": self.version,
            "author": "Dr. Kostas Alexandridis, GISP",
            "years": "",
        }

        # If not silent, print the metadata
        if not silent:
            print(
                f"\nProject Metadata:\n- Name: {metadata["name"]}\n- Title: {metadata["title"]}\n- Description: {metadata["description"]}\n- Version: {metadata["version"]}\n- Author: {metadata["author"]}"
            )
        
        # Return the metadata
        return metadata


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Create Project Directories ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        
    def project_directories(self, silent: bool = False) -> dict:
        """
        Function to generate project directories for the OCTL data processing project.
        Args:
            silent (bool): If True, suppresses the print output. Default is False.
        Returns:
            prj_dirs (dict): A dictionary containing the project directories.
        Raises:
            ValueError: if base_path is not a string
        Example:
            >>> prj_dirs = self.project_directories()
        Notes:
            This function creates a dictionary of project directories based on the base path.
            The function also checks if the base path exists and raises an error if it does not.
        """
        prj_dirs = {
            "root": self.base_path,
            "admin": os.path.join(self.base_path, "admin"),
            "analysis": os.path.join(self.base_path, "analysis"),
            "codebook": os.path.join(self.base_path, "codebook"),
            "data": os.path.join(self.base_path, "data"),
            "data_archived": os.path.join(self.base_path, "data", "archived"),
            "data_processed": os.path.join(self.base_path, "data", "processed"),
            "data_raw": os.path.join(self.base_path, "data", "raw"),
            "gis": os.path.join(self.base_path, "gis"),
            "graphics": os.path.join(self.base_path, "graphics"),
            "metadata": os.path.join(self.base_path, "metadata"),
            "notebooks": os.path.join(self.base_path, "notebooks"),
            "scripts": os.path.join(self.base_path, "scripts")
        }

        # Print the project directories
        if not silent:
            print("\nProject Directories:")
            for key, value in prj_dirs.items():
                print(f"- {key}: {value}")
        
        # Return the project directories
        return prj_dirs


    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Load Codebook Function ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def load_cb(self, silent: bool = False) -> tuple:
        """
        Load the codebook.
        Args:
            silent (bool): If True, suppresses the print output. Default is False.
        Returns:
            cb (dict): The codebook.
            df_cb (pd.DataFrame): The codebook data frame.
        Raises:
            Nothing
        Example:
            >>>cb, df_cb = load_cb()
        Notes:
            This function loads the codebook from the codebook path.
        """
        with open(self.cb_path, encoding = "utf-8") as json_file:
            cb = json.load(json_file)
        
        # Create a codebook data frame
        cbdf = pd.DataFrame(cb).transpose()
        # Add attributes to the codebook data frame
        cbdf.attrs["name"] = "Codebook"
        
        if not silent:
            print("\nCodebook:\n", cbdf)
        return cb, cbdf


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Get Raw Data Function ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_raw_data(self) -> dict:
        """
        Get the raw data.
        Args:
            Nothing
        Returns:
            tl_data (dict): The raw data dictionary.
        Raises:
            ValueError: if there is no folder under the 'data/raw' directory
        Example:
            >>>tl_data = get_raw_data()
        Notes:
            This function gets the raw data from the raw data directory.
        """ 
        # Get the folder name of the raw data
        tl_folder = [d for d in os.listdir(self.prj_dirs["data_raw"]) if os.path.isdir(os.path.join(self.prj_dirs["data_raw"], d))][0]
        
        # Get the folder path
        tl_path = os.path.join(self.prj_dirs["data_raw"], tl_folder)
        
        # Get the year from the folder name
        tl_year = int(tl_folder.replace("tl_", ""))
        print(f"Year: {tl_year}")
        
        # Get the raw data from the folder: Remove the year prefix, and the extension and obtain only the unique names
        tl_files = sorted(list({f.replace(f"tl_{tl_year}_", "").split(".")[0] for f in os.listdir(tl_path)}))

        # Combine the obtained variables into a data dictionary
        tl_data = {
            "folder": tl_folder,
            "path": tl_path,
            "year": tl_year,
            "files": tl_files,
            "count": len(tl_files)
        }
        print(f"There are {tl_data["count"]} unique files in the {tl_data["year"]} Tiger/Line raw data folder.")

        # Return the data dictionary
        return tl_data


    def scratch_gdb(self, method: str = "create"):
        """
        Create a scratch geodatabase.
        Args:
            method (str): The method to use. Default is "create".
        Returns:
            gdb_path (str): The path to the scratch geodatabase.
        Raises:
            Nothing
        Example:
            >>>scratch_gdb(method = "create")
        Notes:
            This function creates a scratch geodatabase.
        """
        # Get the path to the scratch geodatabase
        gdb_path = os.path.join(self.prj_dirs["gis"], "scratch.gdb")

        if method == "create":
            # Check if the geodatabase exists
            if arcpy.Exists(gdb_path):
                # Delete the geodatabase
                arcpy.management.Delete(gdb_path)
                print("Scratch geodatabase deleted successfully.")
            # Create a scratch geodatabase
            arcpy.management.CreateFileGDB(self.prj_dirs["gis"], "scratch.gdb")
            print("Scratch geodatabase created successfully.")
        elif method == "delete":
            if not arcpy.Exists(gdb_path):
                print("Scratch geodatabase does not exist.")
                return
            # Delete the scratch geodatabase
            arcpy.management.Delete(gdb_path)
            print("Scratch geodatabase deleted successfully.")
        else:
            print("Invalid method. Please choose 'create' or 'delete'.")
        
        # Return the path to the scratch geodatabase
        return gdb_path


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Create Geodatabase ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_gdb(self):
        """
        Create a geodatabase.
        Args:
            Nothing
        Returns:
            Nothing
        Raises:
            Nothing
        Example:
            >>>create_gdb()
        Notes:
            This function creates a geodatabase.
        """
        gdb_name = f"TL{self.tl_data["year"]}.gdb"
        gdb_path = os.path.join(self.prj_dirs["gis"], gdb_name)

        if not arcpy.Exists(gdb_path):
            # Create a new file geodatabase
            arcpy.management.CreateFileGDB(self.prj_dirs["gis"], gdb_name)
            print(f"Geodatabase {gdb_name} created successfully.")
            return gdb_path
        else:
            # Delete the existing geodatabase
            arcpy.management.Delete(gdb_path)
            # Create a new file geodatabase
            arcpy.management.CreateFileGDB(self.prj_dirs["gis"], gdb_name)
            print("Geodatabase already exists. Deleted and recreated.")
            return gdb_path


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Process Shapefiles ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def process_shapefiles(self) -> dict:
        """
        Process shapefiles from the raw data directory and create a geodatabase.
        Args:
            Nothing
        Returns:
            final_list (dict): A dictionary of feature classes and their codes.
        Raises:
            Nothing
        Example:
            >>>process_shapefiles()
        Notes:
            This function processes shapefiles from the raw data directory and creates a geodatabase.
        """
        # Get the raw data from the OCTL class object
        tl_data = self.tl_data

        # Create a scratch geodatabase
        scratch_gdb = self.scratch_gdb(method = "create")

        # Set environment workspace to the folder containing shapefiles
        arcpy.env.workspace = tl_data["path"]

        # Get a list of all shapefiles in the folder
        shapefiles = arcpy.ListFeatureClasses("*.shp")
        tables = arcpy.ListTables("*.dbf")

        if shapefiles:
            # FeatureClassToGeodatabase accepts a list of inputs
            arcpy.conversion.FeatureClassToGeodatabase(shapefiles, scratch_gdb)
            print(f"\nSuccessfully imported {len(shapefiles)} shapefiles to {scratch_gdb}\n")
        else:
            print("No shapefiles found in the specified directory.")

        if tables:
            # FeatureClassToGeodatabase accepts a list of inputs
            arcpy.conversion.TableToGeodatabase(tables, scratch_gdb)
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
        tl_gdb = self.create_gdb()

        # Define the input and output feature classes for the county feature class
        in_oc = os.path.join(scratch_gdb, f"tl_{tl_data["year"]}_us_county")
        out_oc = os.path.join(tl_gdb, self.cb["us_county"]["code2"])

        # Select rows with State and County FIPS codes
        arcpy.analysis.Select(
            in_features = in_oc,
            out_feature_class = out_oc,
            where_clause = "STATEFP = '06' And COUNTYFP = '059'"
        )
        # Check if the output feature class is empty
        if int(arcpy.GetCount_management(out_oc).getOutput(0)) == 0:
            arcpy.management.Delete(out_oc)

        # Create a list to store the final feature classes
        final_list = dict()

        # Create a list of feature classes to process and remove the us_county feature class
        fc_list = [f.replace(f"tl_{tl_data["year"]}_", "") for f in scratch_fcs]
        fc_list.remove("us_county")
        final_list["CO"] = "us_county"


        # Loop through the feature classes in the fc_list
        for f in fc_list:
            # Define the feature class name and code from the codebook
            fc = f"tl_{tl_data["year"]}_{f}"
            code = self.cb[f]["code2"]
            # Define the input and output feature classes
            in_fc = os.path.join(scratch_gdb, fc)
            out_fc = os.path.join(tl_gdb, code)
            method = self.cb[f]["method"]
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
                case "query":
                    # Select rows with State and County FIPS codes
                    arcpy.analysis.Select(
                        in_features = in_fc,
                        out_feature_class = out_fc,
                        where_clause = "STATEFP = '06' And COUNTYFP = '059'"
                    )
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                case "query20":
                    # Select rows with State and County FIPS codes
                    arcpy.analysis.Select(
                        in_features = in_fc,
                        out_feature_class = out_fc,
                        where_clause = "STATEFP20 = '06' And COUNTYFP20 = '059'"
                    )
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                case "none":
                    pass

        # Get a list of all feature classes in the TL geodatabase
        try:
            arcpy.env.workspace = tl_gdb
            tl_fcs = arcpy.ListFeatureClasses()
        finally:
            arcpy.env.workspace = os.getcwd()
        
        # Delete the scratch geodatabase
        self.scratch_gdb(method = "delete")

        # Print the list of feature classes in the TL geodatabase
        print(f"\nSuccessfully processed shapefiles:\n{tl_fcs}")

        # Return the list of feature classes in the TL geodatabase
        return final_list


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Get Metadata for Feature Classes ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_metadata(self, census_year, no_congress):
        fc_metadata = {
            "ADDR": {
                "name": "Address Range Relationship File",
                "alias": f"OCTL {census_year} Address Relationship",
                "fcname": f"octl{census_year}addr",
                "category": "relationship",
                "type": "table",
                "subtype": "",
                "title": f"OCTL{census_year} Address Range Relationship File Table",
                "tags": "Orange County, California, OCTL, TigerLines, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {census_year} Address Range Relationship File Table",
                "description": f"Orange County Tiger Lines {census_year} Address Range Relationship File Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "ADDRFEAT": {
                "name": "Address Range Feature",
                "alias": f"OCTL {census_year} Address Feature",
                "fcname": f"octl{census_year}addrfeat",
                "category": "relationship",
                "type": "table",
                "subtype": "",
                "title": f"OCTL{census_year} Address Range Feature Table",
                "tags": "Orange County, California, OCTL, TigerLines, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {census_year} Address Range Feature Table",
                "description": f"Orange County Tiger Lines {census_year} Address Range Feature Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "ADDRFN": {
                "name": "Address Range-Feature Name Relationship",
                "alias": f"OCTL {census_year} Address Feature Name",
                "fcname": f"octl{census_year}addrfn",
                "category": "relationship",
                "type": "table",
                "subtype": "",
                "title": f"OCTL{census_year} Address Range-Feature Name Relationship Table",
                "tags": "Orange County, California, OCTL, TigerLines, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {census_year} Address Range-Feature Name Relationship Table",
                "description": f"Orange County Tiger Lines {census_year} Address Range-Feature Name Relationship Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "AREALM": {
                "name": "Area Landmark",
                "alias": f"OCTL {census_year} Area Landmark",
                "fcname": f"octl{census_year}arealm",
                "category": "landmark",
                "type": "feature",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Area Landmark",
                "tags": "Orange County, California, OCTL, TigerLines, Landmarks",
                "summary": f"Orange County Tiger Lines {census_year} Area Landmark Features",
                "description": f"Orange County Tiger Lines {census_year} Area Landmark Features",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "AREAWATER": {
                "name": "Area Hydrography",
                "alias": f"OCTL {census_year} Area Hydrography",
                "fcname": f"octl{census_year}areawater",
                "category": "hydrography",
                "type": "feature",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Area Hydrography",
                "tags": "Orange County, California, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {census_year} Area Hydrography Features",
                "description": f"Orange County Tiger Lines {census_year} Area Hydrography Features",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "BG": {
                "name": "Block Group",
                "alias": f"OCTL {census_year} Block Group",
                "fcname": f"octl{census_year}bg",
                "category": "census geography",
                "type": "statistical area",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Block Group",
                "tags": "Orange County, California, OCTL, TigerLines, Census, Block Groups",
                "summary": f"Orange County Tiger Lines {census_year} Census Block Groups",
                "description": f"Orange County Tiger Lines {census_year} Census Block Group Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "CBSA": {
                "name": "Core Based Statistical Area",
                "alias": f"OCTL {census_year} Statistical Areas",
                "fcname": f"octl{census_year}cbsa",
                "category": "census geography",
                "type": "statistical area",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Core Based Statistical Area",
                "tags": "Orange County, California, OCTL, TigerLines, Census, Statistical Area",
                "summary": f"Orange County Tiger Lines {census_year} Core Based Statistical Area",
                "description": f"Orange County Tiger Lines {census_year} Core Based Statistical Area",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "CD": {
                "name": f"Congressional Districts of the {no_congress}th US Congress",
                "alias": f"OCTL {census_year} Congressional Districts",
                "fcname": f"octl{census_year}cd",
                "category": "legislative",
                "type": "legislative areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Congressional Districts of the {no_congress}th US Congress",
                "tags": "Orange County, California, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {census_year} for the Congessional Districts of the {no_congress}th US Congress",
                "description": f"Orange County Tiger Lines {census_year} for the Congressional Districts of the {no_congress}th US Congress",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "COUNTY": {
                "name": "Orange County",
                "alias": f"OCTL {census_year} County",
                "fcname": f"octl{census_year}county",
                "category": "administrative",
                "type": "administrative boundaries",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Orange County Boundaries",
                "tags": "Orange County, California, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {census_year} for Orange County",
                "description": f"Orange County Tiger Lines {census_year} for Orange County",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "COUSUB": {
                "name": "County Subdivisions",
                "alias": f"OCTL {census_year} County Subdivisions",
                "fcname": f"octl{census_year}cousub",
                "category": "administrative",
                "type": "administrative boundaries",
                "subtype": "polygon",
                "title": f"OCTL{census_year} County Subdivisions",
                "tags": "Orange County, California, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {census_year} Orange County Subdivisions",
                "description": f"Orange County Tiger Lines {census_year} Orange County Subdivisions",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "CSA": {
                "name": "Combined Statistical Areas",
                "alias": f"OCTL {census_year} Combined Statistical Areas",
                "fcname": f"octl{census_year}csa",
                "category": "census geographies",
                "type": "statistical areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Combined Statistical Areas",
                "tags": "Orange County, California, OCTL, TigerLines, Statistical Areas",
                "summary": f"Orange County Tiger Lines {census_year} Combined Statistical Areas",
                "description": f"Orange County Tiger Lines {census_year} Combined Statistical Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "EDGES": {
                "name": "All Lines",
                "alias": f"OCTL {census_year} Line Edges",
                "fcname": f"octl{census_year}edges",
                "category": "features",
                "type": "line features",
                "subtype": "lines",
                "title": f"OCTL{census_year} Line Edges",
                "tags": "Orange County, California, OCTL, TigerLines, Edges",
                "summary": f"Orange County Tiger Lines {census_year} Line Edges",
                "description": f"Orange County Tiger Lines {census_year} Line Edges",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "ELSD": {
                "name": "Elementary School Districts",
                "alias": f"OCTL {census_year} Elementary School Districts",
                "fcname": f"octl{census_year}elsd",
                "category": "school districts",
                "type": "administrative boundaries",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Elementary School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Schools, Elementary Schools",
                "summary": f"Orange County Tiger Lines {census_year} Elementary School Districts",
                "description": f"Orange County Tiger Lines {census_year} Elementary School Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "FACES": {
                "name": "Topological Faces (polygons with all geocodes)",
                "alias": f"OCTL {census_year} Topological Faces",
                "fcname": f"octl{census_year}faces",
                "category": "topologies",
                "type": "topological features",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Topological Faces",
                "tags": "Orange County, California, OCTL, TigerLines, Topology, Faces",
                "summary": f"Orange County Tiger Lines {census_year} Topological Faces",
                "description": f"Orange County Tiger Lines {census_year} Topological Faces (polygons with all geocodes)",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },    
            "FACESAH": {
                "name": "Topological Faces-Area Hydrography Relationship File",
                "alias": f"OCTL {census_year} Topological Faces-Area Hydrography Relationships",
                "fcname": f"octl{census_year}facesah",
                "category": "relationships",
                "type": "table",
                "subtype": "topologies",
                "title": f"OCTL{census_year} Topological Faces-Area Hydrography Relationships",
                "tags": "Orange County, California, OCTL, TigerLines, Topology, Faces, Relationships, Hydrology",
                "summary": f"Orange County Tiger Lines {census_year} Topological Faces-Area Hydrography Relationships",
                "description": f"Orange County Tiger Lines {census_year} Topological Faces-Area Hydrography Relationships Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "FACESAL": {
                "name": "Topological Faces-Area Landmark Relationship Fle",
                "alias": f"OCTL {census_year} Topological Faces-Area Landmark Relationships",
                "fcname": f"octl{census_year}facesal",
                "category": "relationships",
                "type": "table",
                "subtype": "topologies",
                "title": f"OCTL{census_year} Topological Faces-Area Landmark Relationships",
                "tags": "Orange County, California, OCTL, TigerLines, Topology, Faces, Relationships, Landmarks",
                "summary": f"Orange County Tiger Lines {census_year} Topological Faces-Area Landmark Relationships",
                "description": f"Orange County Tiger Lines {census_year} Topological Faces-Area Landmark Relationships Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "FACESMIL": {
                "name": "Topological Faces-Military Installation Relationship File",
                "alias": f"OCTL {census_year} Topological Faces-Military Installation Relationships",
                "fcname": f"octl{census_year}facesmil",
                "category": "relationships",
                "type": "table",
                "subtype": "topologies",
                "title": f"OCTL{census_year} Topological Faces-Military Installation Relationships",
                "tags": "Orange County, California, OCTL, TigerLines, Topology, Faces, Military, Relationships",
                "summary": f"Orange County Tiger Lines {census_year} Topological Faces-Military Installation Relationships",
                "description": f"Orange County Tiger Lines {census_year} Topological Faces-Military Installation Relationships Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "FEATNAMES": {
                "name": "Feature Names Relationship File",
                "alias": f"OCTL {census_year} Feature Names Relationship",
                "fcname": f"octl{census_year}featnames",
                "category": "relationships",
                "type": "table",
                "subtype": "features",
                "title": f"OCTL{census_year} Feature Names Relationship File",
                "tags": "Orange County, California, OCTL, TigerLines, Features, Relationships",
                "summary": f"Orange County Tiger Lines {census_year} Feature Names Relationship File",
                "description": f"Orange County Tiger Lines {census_year} Feature Names Relationship File Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "LINEARWATER": {
                "name": "Linear Hydrography",
                "alias": f"OCTL {census_year} Linear Hydrography",
                "fcname": f"octl{census_year}linearwater",
                "category": "hydrography",
                "type": "hydrographic areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Linear Hydrography",
                "tags": "Orange County, California, OCTL, TigerLines, Hydrography",
                "summary": f"Orange County Tiger Lines {census_year} Linear Hydrography",
                "description": f"Orange County Tiger Lines {census_year} Linear Hydrography Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "METDIV": {
                "name": "Metropolital Divisions",
                "alias": f"OCTL {census_year} Metropolitan Divisions",
                "fcname": f"octl{census_year}metdiv",
                "category": "administrative",
                "type": "administrative boundaries",
                "subtype": "divisions",
                "title": f"OCTL{census_year} Metropolitan Divisions",
                "tags": "Orange County, California, OCTL, TigerLines, Metropolitan",
                "summary": f"Orange County Tiger Lines {census_year} Metropolitan Divisions",
                "description": f"Orange County Tiger Lines {census_year} Metropolitan Division Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "MIL": {
                "name": "Military Installations",
                "alias": f"OCTL {census_year} Military Installations",
                "fcname": f"octl{census_year}mil",
                "category": "military",
                "type": "administrative areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Military Installations",
                "tags": "Orange County, California, OCTL, TigerLines, Military",
                "summary": f"Orange County Tiger Lines {census_year} Military Installations",
                "description": f"Orange County Tiger Lines {census_year} Military Installation Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "PLACE": {
                "name": "Place or Cities",
                "alias": f"OCTL {census_year} Place or Cities",
                "fcname": f"octl{census_year}place",
                "category": "cities",
                "type": "administrative boundaries",
                "subtype": "polygons",
                "title": f"OCTL{census_year} Place or Cities",
                "tags": "Orange County, California, OCTL, TigerLines, Places, Cities",
                "summary": f"Orange County Tiger Lines {census_year} Place or Cities",
                "description": f"Orange County Tiger Lines {census_year} Place or City Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "POINTLM": {
                "name": "Point Landmark",
                "alias": f"OCTL {census_year} Point Landmark",
                "fcname": f"octl{census_year}pointlm",
                "category": "landmark",
                "type": "landmark areas",
                "subtype": "points",
                "title": f"OCTL{census_year} Point Landmark",
                "tags": "Orange County, California, OCTL, TigerLines, Landmarks",
                "summary": f"Orange County Tiger Lines {census_year} Point Landmarks",
                "description": f"Orange County Tiger Lines {census_year} Point Landmarks",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "PRIMARYROADS": {
                "name": "Primary Roads",
                "alias": f"OCTL {census_year} Primary Roads",
                "fcname": f"octl{census_year}primaryroads",
                "category": "roads",
                "type": "primary",
                "subtype": "lines",
                "title": f"OCTL{census_year} Primary Roads",
                "tags": "Orange County, California, OCTL, TigerLines, Roads, Primary Roads",
                "summary": f"Orange County Tiger Lines {census_year} Primary Roads",
                "description": f"Orange County Tiger Lines {census_year} Primary Road Lines",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "PRISECROADS": {
                "name": "Primary and Secondary Roads",
                "alias": f"OCTL {census_year} Primary and Secondary Roads",
                "fcname": f"octl{census_year}prisecroads",
                "category": "roads",
                "type": "primary secondary",
                "subtype": "lines",
                "title": f"OCTL{census_year} Primary and Secondary Roads",
                "tags": "Orange County, California, OCTL, TigerLines, Roads, Primary Roads, Secondary Roads",
                "summary": f"Orange County Tiger Lines {census_year} Primary and Secondary Roads",
                "description": f"Orange County Tiger Lines {census_year} Primary and Secondary Road Lines",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "PUMA": {
                "name": "Public Use Microdata Areas",
                "alias": f"OCTL {census_year} PUMA",
                "fcname": f"octl{census_year}puma",
                "category": "statistical",
                "type": "statistical areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Public Use Microdata Areas",
                "tags": "Orange County, California, OCTL, TigerLines, PUMA",
                "summary": f"Orange County Tiger Lines {census_year} Public Use Microdata Areas",
                "description": f"Orange County Tiger Lines {census_year} Public Use Microdata Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "RAILS": {
                "name": "Rail Lines",
                "alias": f"OCTL {census_year} Railroads",
                "fcname": f"octl{census_year}rails",
                "category": "railroads",
                "type": "rail lines",
                "subtype": "lines",
                "title": f"OCTL{census_year} Rail Lines",
                "tags": "Orange County, California, OCTL, TigerLines, Rail, Railroads",
                "summary": f"Orange County Tiger Lines {census_year} Rail Lines",
                "description": f"Orange County Tiger Lines {census_year} Railroad Lines",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "ROADS": {
                "name": "All Roads",
                "alias": f"OCTL {census_year} All Roads",
                "fcname": f"octl{census_year}roads",
                "category": "roads",
                "type": "mixed",
                "subtype": "lines",
                "title": f"OCTL{census_year} All Roads",
                "tags": "Orange County, California, OCTL, TigerLines, Roads",
                "summary": f"Orange County Tiger Lines {census_year} All Roads",
                "description": f"Orange County Tiger Lines {census_year} All Road Lines",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "SCSD": {
                "name": "Secondary School Districts",
                "alias": f"OCTL {census_year} Secondary School Districts",
                "fcname": f"octl{census_year}scsd",
                "category": "schools",
                "type": "school districts",
                "subtype": "polygons",
                "title": f"OCTL{census_year} Secondary School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Schools, School Districts, Secondary Schools",
                "summary": f"Orange County Tiger Lines {census_year} Secondary School Districts",
                "description": f"Orange County Tiger Lines {census_year} Secondary School District Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "SLDL": {
                "name": "State Legislative Districts - Lower Level",
                "alias": f"OCTL {census_year} State Assembly Legislative Districts",
                "fcname": f"octl{census_year}sldl",
                "category": "legislative",
                "type": "legislative districts",
                "subtype": "polygons",
                "title": f"OCTL{census_year} State Assembly Legislative Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Legislative Districts, State Assembly",
                "summary": f"Orange County Tiger Lines {census_year} State Assembly Legislative Districts",
                "description": f"Orange County Tiger Lines {census_year} State Assembly Legislative District Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "SLDU": {
                "name": "State Legislative Districts - Upper Level",
                "alias": f"OCTL {census_year} State Senate Legislative Districts",
                "fcname": f"octl{census_year}sldu",
                "category": "legislative",
                "type": "legislative districts",
                "subtype": "polygons",
                "title": f"OCTL{census_year} State Senate Legislative Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Legislative Districts, State Senate",
                "summary": f"Orange County Tiger Lines {census_year} State Senate Legislative Districts",
                "description": f"Orange County Tiger Lines {census_year} State Senate Legislative District Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "TABBLOCK": {
                "name": "Tabulation (Census) Block",
                "alias": f"OCTL {census_year} Census Blocks",
                "fcname": f"octl{census_year}tabblock",
                "category": "census blocks",
                "type": "statistical areas",
                "subtype": "polygons",
                "title": f"OCTL{census_year} Census Blocks",
                "tags": "Orange County, California, OCTL, TigerLines, Census Blocks",
                "summary": f"Orange County Tiger Lines {census_year} Census Blocks",
                "description": f"Orange County Tiger Lines {census_year} Census Block Tabulation Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "TRACT": {
                "name": "Census Tract",
                "alias": f"OCTL {census_year} Census Tracts",
                "fcname": f"octl{census_year}tract",
                "category": "census tracts",
                "type": "statistical areas",
                "subtype": "polygons",
                "title": f"OCTL{census_year} Census Tracts",
                "tags": "Orange County, California, OCTL, TigerLines, Census Tracts",
                "summary": f"Orange County Tiger Lines {census_year} Census Tracts",
                "description": f"Orange County Tiger Lines {census_year} Census Tract Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "UAC": {
                "name": "Urban Area or Cluster",
                "alias": f"OCTL {census_year} Urban Areas",
                "fcname": f"octl{census_year}uac",
                "category": "urban",
                "type": "urban areas",
                "subtype": "polygon",
                "title": f"OCTL{census_year} Urban Areas",
                "tags": "Orange County, California, OCTL, TigerLines, Urban Areas",
                "summary": f"Orange County Tiger Lines {census_year} Urban Areas or Clusters",
                "description": f"Orange County Tiger Lines {census_year} Urban or Cluster Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "UNSD": {
                "name": "Unified School Districs",
                "alias": f"OCTL {census_year} Unified School Districts",
                "fcname": f"octl{census_year}unsd",
                "category": "schools",
                "type": "unified districts",
                "subtype": "polygons",
                "title": f"OCTL{census_year} Unified School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Schools, School Districts, Unified Schools",
                "summary": f"Orange County Tiger Lines {census_year} Unified School Districts",
                "description": f"Orange County Tiger Lines {census_year} Unified School Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },        
            "ZCTA": {
                "name": "ZIP Code Tabulation Areas",
                "alias": f"OCTL {census_year} ZIP Codes",
                "fcname": f"octl{census_year}zcta",
                "category": "zip codes",
                "type": "administrative areas",
                "subtype": "polygons",
                "title": f"OCTL{census_year} ZIP Code Tabulation Areas",
                "tags": "Orange County, California, OCTL, TigerLines, ZIP Codes",
                "summary": f"Orange County Tiger Lines {census_year} ZIP Code Tabulation Areas",
                "description": f"Orange County Tiger Lines {census_year} ZIP Code Tabulation Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            }
        }
        return fc_metadata


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
