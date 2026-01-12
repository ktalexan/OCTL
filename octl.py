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
from arcpy import metadata as md
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
    ## Fx: Get Metadata for Feature Classes ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def process_metadata(self):
        """
        Process metadata for feature classes.
        Args:
            Nothing
        Returns:
            Nothing
        """
        
        # Initialize an empty dictionary to store metadata for feature classes
        fc_metadata = {
            "06059_addr": {
                "abbrev": "ADDR",
                "alias":  f"OCTL {self.tl_data["year"]} Address Ranges",
                "type": "Table",
                "fcname": "AD",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Ranges Relationship File",
                "title": f"OCTL {self.tl_data["year"]} Address Ranges Relationship File Table",
                "tags": "Orange County, California, OCTL, TigerLines, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Address Ranges Relationship File Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Address Ranges Relationship File Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"            
            },
            "06059_addrfeat": {
                "abbrev": "ADDRFEAT",
                "alias": f"OCTL {self.tl_data["year"]} Address Range Features",
                "type": "Feature Class",
                "fcname": "AF",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Range Feature Table",
                "title": f"OCTL {self.tl_data["year"]} Address Range Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Address, Relationships, Feature Class",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Address Range Feature Class",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Address Range Feature Class",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_addrfn": {
                "abbrev": "ADDRFN",
                "alias": f"OCTL {self.tl_data["year"]} Address Range Feature Names",
                "type": "Table",
                "fcname": "AN",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Range-Feature Name Relationship Table",
                "title": f"OCTL {self.tl_data["year"]} Address Range Feature Names Table",
                "tags": "Orange County, California, OCTL, TigerLines, Address Range, Feature Names, Relationship Files, Table",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Address Range Feature Names Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Address Range Feature Names Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_areawater": {
                "abbrev": "AREAWATER",
                "alias": f"OCTL {self.tl_data["year"]} Area Hydrography",
                "type": "Feature Class",
                "fcname": "WA",
                "group": "Features",
                "category": "Water",
                "label": "Area Hydrography",
                "title": f"OCTL {self.tl_data["year"]} Area Hydrography Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Area Hydrography, Water, Feature Class",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Area Hydrography Feature Class",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Area Hydrography Feature Class",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_edges": {
                "abbrev": "EDGES",
                "alias": f"OCTL {self.tl_data["year"]} All Lines",
                "type": "Feature Class",
                "fcname": "ED",
                "group": "Features",
                "category": "All Lines",
                "label": "All Lines",
                "title": f"OCTL {self.tl_data["year"]} All Lines Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, All Lines, Feature Class",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} All Lines Feature Class",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} All Lines Feature Class",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_faces": {
                "abbrev": "FACES",
                "alias": f"OCTL {self.tl_data["year"]} Topological Faces",
                "type": "Feature Class",
                "fcname": "FC",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces (Polygons with all Geocodes) Feature Class",
                "title": f"OCTL {self.tl_data["year"]} Topological Faces Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Topological Faces, Feature Class",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces Feature Class",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces Feature Class",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_facesah": {
                "abbrev": "FACESAH",
                "alias": f"OCTL {self.tl_data["year"]} Topological Faces-Area Hydrography",
                "type": "Table",
                "fcname": "FH",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Area Hydrography Relationship Table",
                "title": f"OCTL {self.tl_data["year"]} Topological Faces-Area Hydrography Relationship Table",
                "tags": "Orange County, California, OCTL, TigerLines, Topological Faces-Area Hydrography, Relationship Table",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Area Hydrography Relationship Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Area Hydrography Relationship Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_featnames": {
                "abbrev": "FEATNAMES",
                "alias": f"OCTL {self.tl_data["year"]} Feature Names",
                "type": "Table",
                "fcname": "FN",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Feature Names Relationship Table",
                "title": f"OCTL {self.tl_data["year"]} Feature Names Relationship Table",
                "tags": "Orange County, California, OCTL, TigerLines, Feature Names, Relationship Table",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Feature Names Relationship Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Feature Names Relationship Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_linearwater": {
                "abbrev": "LINEARWATER",
                "alias": f"OCTL {self.tl_data["year"]} Linear Hydrography",
                "type": "Feature Class",
                "fcname": "WL",
                "group": "Features",
                "category": "Water",
                "label": "Linear Hydrography",
                "title": f"OCTL {self.tl_data["year"]} Linear Hydrography Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Linear Hydrography",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Linear Hydrography",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Linear Hydrography",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06059_roads": {
                "abbrev": "ROADS",
                "alias": f"OCTL {self.tl_data["year"]} All Roads",
                "type": "Feature Class",
                "fcname": "RD",
                "group": "Feature",
                "category": "Roads",
                "label": "All Roads",
                "title": f"OCTL {self.tl_data["year"]} All Roads Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Roads, Transportation",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} All Roads",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} All Roads",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_arealm": {
                "abbrev": "AREALM",
                "alias": f"OCTL {self.tl_data["year"]} Area Landmarks",
                "type": "Feature Class",
                "fcname": "LA",
                "group": "Features",
                "category": "Landmarks",
                "label": "Area Landmarks",
                "title": f"OCTL {self.tl_data["year"]} Area Landmarks Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Landmarks",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Area Landmarks",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Area Landmarks",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_bg": {
                "abbrev": "BG",
                "alias": f"OCTL {self.tl_data["year"]} Block Groups",
                "type": "Feature Class",
                "fcname": "BG",
                "group": "Geographic Areas",
                "category": "Block Groups",
                "label": "Block Groups",
                "title": f"OCTL {self.tl_data["year"]} Block Groups Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Block Groups",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Block Groups",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Block Groups",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_cd118": {
                "abbrev": "CD118",
                "alias": f"OCTL {self.tl_data["year"]} Congressional Districts 118th",
                "type": "Feature Class",
                "fcname": "CD",
                "group": "Geographic Areas",
                "category": "Congressional Districts",
                "label": "Congressional Districts of the 118th US Congress",
                "title": f"OCTL {self.tl_data["year"]} Congressional Districts 118th",
                "tags": "Orange County, California, OCTL, TigerLines, Congressional Districts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 118th US Congress",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 118th US Congress",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_cd119": {
                "abbrev": "CD119",
                "alias": f"OCTL {self.tl_data["year"]} Congressional Districts 119th",
                "type": "Feature Class",
                "fcname": "CD",
                "group": "Geographic Areas",
                "category": "Congressional Districts",
                "label": "Congressional Districts of the 119th US Congress",
                "title": f"OCTL {self.tl_data["year"]} Congressional Districts 119th",
                "tags": "Orange County, California, OCTL, TigerLines, Congressional Districts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 119th US Congress",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 119th US Congress",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_cousub": {
                "abbrev": "COUSUB",
                "alias": f"OCTL {self.tl_data["year"]} County Subdivisions",
                "type": "Feature Class",
                "fcname": "CS",
                "group": "Geographic Areas",
                "category": "County Subdivisions",
                "label": "County Subdivisions",
                "title": f"OCTL {self.tl_data["year"]} County Subdivisions",
                "tags": "Orange County, California, OCTL, TigerLines, County Subdivisions",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} County Subdivisions",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} County Subdivisions",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_elsd": {
                "abbrev": "ELSD",
                "alias": f"OCTL {self.tl_data["year"]} Elementary School Districts",
                "type": "Feature Class",
                "fcname": "SE",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Elementary School Districts",
                "title": f"OCTL {self.tl_data["year"]} Elementary School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Schools, School Districts, Elementary School Districts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Elementary School Districts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Elementary School Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_facesal": {
                "abbrev": "FACESAL",
                "alias": f"OCTL {self.tl_data["year"]} Topological Faces-Area Landmark",
                "type": "Table",
                "fcname": "FL",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Area Landmark Relationship Table",
                "title": f"OCTL {self.tl_data["year"]} Topological Faces-Area Landmark Relationship Table",
                "tags": "Orange County, California, OCTL, TigerLines, Topological Faces-Area Landmark, Relationship File, Feature Relationship",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Area Landmark Relationship Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Area Landmark Relationship Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_place": {
                "abbrev": "PLACE",
                "alias": f"OCTL {self.tl_data["year"]} Cities or Places",
                "type": "Feature Class",
                "fcname": "PL",
                "group": "Geographic Areas",
                "category": "Places",
                "label": "Place (Cities or Unincorporated Areas)",
                "title": f"OCTL {self.tl_data["year"]} Cities or Places",
                "tags": "Orange County, California, OCTL, TigerLines, Cities or Places, Place, Geographic Area, Cities, Unincorporated Areas",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Cities or Places",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Cities or Places",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_pointlm": {
                "abbrev": "POINTLM",
                "alias": f"OCTL {self.tl_data["year"]} Point Landmarks",
                "type": "Feature Class",
                "fcname": "LP",
                "group": "Features",
                "category": "Landmarks",
                "label": "Point Landmarks",
                "title": f"OCTL {self.tl_data["year"]} Point Landmarks",
                "tags": "Orange County, California, OCTL, TigerLines, Point Landmarks, Point, Landmarks, Features",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Point Landmarks",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Point Landmarks",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_prisecroads": {
                "abbrev": "PRISECROADS",
                "alias": f"OCTL {self.tl_data["year"]} Primary and Secondary Roads",
                "type": "Feature Class",
                "fcname": "RS",
                "group": "Features",
                "category": "Roads",
                "label": "Primary and Secondary Roads",
                "title": f"OCTL {self.tl_data["year"]} Primary and Secondary Roads",
                "tags": "Orange County, California, OCTL, TigerLines, Primary and Secondary Roads, Roads, Features, Transportation",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Primary and Secondary Roads",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Primary and Secondary Roads",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_puma20": {
                "abbrev": "PUMA",
                "alias": f"OCTL {self.tl_data["year"]} Public Use Microdata Areas",
                "type": "Feature Class",
                "fcname": "PU",
                "group": "Geographic Areas",
                "category": "Public Use Microdata Areas",
                "label": "Public Use Microdata Areas",
                "title": f"OCTL {self.tl_data["year"]} Public Use Microdata Areas",
                "tags": "Orange County, California, OCTL, TigerLines, Public Use Microdata Areas, PUMA, Geographic Areas, Features",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Public Use Microdata Areas",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Public Use Microdata Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_scsd": {
                "abbrev": "SCSD",
                "alias": f"OCTL {self.tl_data["year"]} Secondary School Districts",
                "type": "Feature Class",
                "fcname": "SS",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Secondary School Districts",
                "title": f"OCTL {self.tl_data["year"]} Secondary School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Secondary School Districts, SCSD, Geographic Areas, Schools, Secondary Schools",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Secondary School Districts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Secondary School Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_sldl": {
                "abbrev": "SLDL",
                "alias": f"OCTL {self.tl_data["year"]} State Assembly Legislative Districts",
                "type": "Feature Class",
                "fcname": "LL",
                "group": "Geographic Areas",
                "category": "State Legislative Districts",
                "label": "State Legislative District - Lower Chamber (Assembly)",
                "title": f"OCTL {self.tl_data["year"]} State Assembly Legislative Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Legislative Districts, State Assembly",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} State Assembly Legislative Districts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} State Assembly Legislative Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_sldu": {
                "abbrev": "SLDU",
                "alias": f"OCTL {self.tl_data["year"]} State Senate Legislative Districts",
                "type": "Feature Class",
                "fcname": "LU",
                "group": "Geographic Areas",
                "category": "State Legislative Districts",
                "label": "State Legislative District - Upper Chamber (Senate)",
                "title": f"OCTL {self.tl_data["year"]} State Senate Legislative Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Legislative Districts, State Senate",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} State Senate Legislative Districts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} State Senate Legislative Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_tabblock20": {
                "abbrev": "TABBLOCK",
                "alias": f"OCTL {self.tl_data["year"]} Blocks",
                "type": "Feature Class",
                "fcname": "BL",
                "group": "Geographic Areas",
                "category": "Blocks",
                "label": "Block",
                "title": f"OCTL {self.tl_data["year"]} Blocks",
                "tags": "Orange County, California, OCTL, TigerLines, Blocks",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Blocks",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Blocks",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_tract": {
                "abbrev": "TRACT",
                "alias": f"OCTL {self.tl_data["year"]} Census Tracts",
                "type": "Feature Class",
                "fcname": "TR",
                "group": "Geographic Areas",
                "category": "Census Tracts",
                "label": "Census Tract",
                "title": f"OCTL {self.tl_data["year"]} Census Tracts",
                "tags": "Orange County, California, OCTL, TigerLines, Census Tracts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Census Tracts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Census Tracts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "06_unsd": {
                "abbrev": "UNSD",
                "alias": f"OCTL {self.tl_data["year"]} Unified School Districts",
                "type": "Feature Class",
                "fcname": "SU",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Unified School District",
                "title": f"OCTL {self.tl_data["year"]} Unified School Districts",
                "tags": "Orange County, California, OCTL, TigerLines, Unified School Districts, Schools, School Districts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Unified School Districts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Unified School Districts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_aitsn": {
                "abbrev": "AITSN",
                "alias": f"OCTL {self.tl_data["year"]} Tribal Subdivisions",
                "type": "Feature Class",
                "fcname": "TS",
                "group": "Geographic Areas",
                "category": "American Indian Area Geography",
                "label": "American Indian Tribal Subdivision",
                "title": f"OCTL {self.tl_data["year"]} Tribal Subdivisions Feature Class",
                "tags": "Orange County, California, OCTL, TigerLines, Tribal Subdivisions, American Indian Area Geography",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Subdivisions Feature Class",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Subdivisions Feature Class",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data",
            },
            "us_cbsa": {
                "abbrev": "CBSA",
                "alias": f"OCTL {self.tl_data["year"]} Metropolitan Statistical Areas",
                "type": "Feature Class",
                "fcname": "SM",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Metropolitan/Micropolitan Statistical Area",
                "title": f"OCTL {self.tl_data["year"]} Metropolitan Statistical Areas",
                "tags": "Orange County, California, OCTL, TigerLines, Metropolitan Statistical Areas, Core Based Statistical Areas",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Metropolitan Statistical Areas",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Metropolitan Statistical Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            },
            "us_cd116": {
                "abbrev": "CD116",
                "alias": f"OCTL {self.tl_data["year"]} Congressional Districts 116th",
                "type": "Feature Class",
                "fcname": "CD",
                "group": "Geographic Areas",
                "category": "Congressional Districts",
                "label": "Congressional Districts of the 116th US Congress",
                "title": f"OCTL {self.tl_data["year"]} Congressional Districts of the 116th US Congress",
                "tags": "Orange County, California, OCTL, TigerLines, Congressional Districts, 116th US Congress",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 116th US Congress",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Congressional Districts of the 116th US Congress",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_coastline": {
                "abbrev": "COASTLINE",
                "alias": f"OCTL {self.tl_data["year"]} Coastlines",
                "type": "Feature Class",
                "fcname": "CL",
                "group": "Geographic Areas",
                "category": "Coastlines",
                "label": "Coastline",
                "title": f"OCTL {self.tl_data["year"]} Coastlines",
                "tags": "Orange County, California, Coastlines, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Coastlines",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Coastlines",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_county": {
                "abbrev": "COUNTY",
                "alias": f"OCTL {self.tl_data["year"]} Orange County",
                "type": "Feature Class",
                "fcname": "CO",
                "group": "Geographic Areas",
                "category": "Counties",
                "label": "County and Equivalent",
                "title": f"OCTL {self.tl_data["year"]} Orange County",
                "tags": "Orange County, California, Counties, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Orange County",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Orange County",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_csa": {
                "abbrev": "CSA",
                "alias": f"OCTL {self.tl_data["year"]} Combined Statistical Areas",
                "type": "Feature Class",
                "fcname": "SC",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Combined Statistical Area",
                "title": f"OCTL {self.tl_data["year"]} Combined Statistical Areas",
                "tags": "Orange County, California, Core Based Statistical Areas, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Combined Statistical Areas",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Combined Statistical Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_facesmil": {
                "abbrev": "FACEMIL",
                "alias": f"OCTL {self.tl_data["year"]} Topological Faces-Military Installations",
                "type": "Table",
                "fcname": "FM",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Military Installations Relationship Table",
                "title": f"OCTL {self.tl_data["year"]} Topological Faces-Military Installations Relationship Table",
                "tags": "Orange County, California, Military Installations, OCTL, TigerLines, Relationship Files, Topological Faces",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Military Installations Relationship Table",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Topological Faces-Military Installations Relationship Table",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_metdiv": {
                "abbrev": "METDIV",
                "alias": f"OCTL {self.tl_data["year"]} Metropolitan Divisions",
                "type": "Feature Class",
                "fcname": "MD",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Metropolitan Division",
                "title": f"OCTL {self.tl_data["year"]} Metropolitan Divisions",
                "tags": "Orange County, California, Metropolitan Divisions, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Metropolitan Divisions",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Metropolitan Divisions",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_mil": {
                "abbrev": "MIL",
                "alias": f"OCTL {self.tl_data["year"]} Military Installations",
                "type": "Feature Class",
                "fcname": "ML",
                "group": "Features",
                "category": "Military Installations",
                "label": "Military Installations",
                "title": f"OCTL {self.tl_data["year"]} Military Installations",
                "tags": "Orange County, California, Military Installations, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Military Installations",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Military Installations",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_primaryroads": {
                "abbrev": "PRIMARYROADS",
                "alias": f"OCTL {self.tl_data["year"]} Primary Roads",
                "type": "Feature Class",
                "fcname": "RP",
                "group": "Features",
                "category": "Roads",
                "label": "Primary Roads",
                "title": f"OCTL {self.tl_data["year"]} Primary Roads",
                "tags": "Orange County, California, Primary Roads, OCTL, TigerLines, Roads, Transportation",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Primary Roads",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Primary Roads",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_rails": {
                "abbrev": "RAILS",
                "alias": f"OCTL {self.tl_data["year"]} Rails",
                "type": "Feature Class",
                "fcname": "RL",
                "group": "Features",
                "category": "Rails",
                "label": "Rails",
                "title": f"OCTL {self.tl_data["year"]} Rails",
                "tags": "Orange County, California, Rails, OCTL, TigerLines, Transportation",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Rails",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Rails",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_tbg": {
                "abbrev": "TBG",
                "alias": f"OCTL {self.tl_data["year"]} Tribal Block Groups",
                "type": "Feature Class",
                "fcname": "TB",
                "group": "Geographic Areas",
                "category": "American Indian Area Geography",
                "label": "Tribal Block Groups",
                "title": f"OCTL {self.tl_data["year"]} Tribal Block Groups",
                "tags": "Orange County, California, Tribal Block Groups, OCTL, TigerLines, Geography, Block Groups",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Block Groups",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Block Groups",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_ttract": {
                "abbrev": "TTRACT",
                "alias": f"OCTL {self.tl_data["year"]} Tribal Census Tracts",
                "type": "Feature Class",
                "fcname": "TC",
                "group": "Geographic Areas",
                "category": "American Indian Area Geography",
                "label": "Tribal Census Tract",
                "title": f"OCTL {self.tl_data["year"]} Tribal Census Tracts",
                "tags": "Orange County, California, Tribal Census Tracts, OCTL, TigerLines, Geography, Census Tracts",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Census Tracts",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Tribal Census Tracts",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_uac20": {
                "abbrev": "UAC",
                "alias": f"OCTL {self.tl_data["year"]} Urban Areas",
                "type": "Feature Class",
                "fcname": "UA",
                "group": "Geographic Areas",
                "category": "Urban Areas",
                "label": "Urban Areas",
                "title": f"OCTL {self.tl_data["year"]} Urban Areas",
                "tags": "Orange County, California, Urban Areas, OCTL, TigerLines",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} Urban Areas",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} Urban Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"             
            },
            "us_zcta520": {
                "abbrev": "ZCTA",
                "alias": f"OCTL {self.tl_data["year"]} ZIP Code Tabulation Areas",
                "type": "Feature Class",
                "fcname": "ZC",
                "group": "Geographic Areas",
                "category": "ZIP Code Tabulation Areas",
                "label": "ZIP Code Tabulation Areas",
                "title": f"OCTL {self.tl_data["year"]} ZIP Code Tabulation Areas",
                "tags": "Orange County, California, ZIP Code Tabulation Areas, OCTL, TigerLines, ZIP codes",
                "summary": f"Orange County Tiger Lines {self.tl_data["year"]} ZIP Code Tabulation Areas",
                "description": f"Orange County Tiger Lines {self.tl_data["year"]} ZIP Code Tabulation Areas",
                "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
                "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
                "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
            }
        }

        # Return the metadata dictionary
        return fc_metadata


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

        # Create a metadata dictionary for the feature classes
        md_dict = self.process_metadata()

        # Loop through the feature classes in the fc_list
        for f in fc_list:
            # Define the feature class name and code from the codebook
            fc = f"tl_{self.tl_data["year"]}_{f}"
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
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, self.cb[f]["alias"])
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
                        arcpy.AlterAliasName(out_fc, self.cb[f]["alias"])
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
                        arcpy.AlterAliasName(out_fc, self.cb[f]["alias"])
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
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, self.cb[f]["alias"])
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
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, self.cb[f]["alias"])
                case "none":
                    pass
        
        # Get a list of all feature classes in the TL geodatabase
        try:
            arcpy.env.workspace = tl_gdb
            tl_fcs = arcpy.ListFeatureClasses()
        finally:
            arcpy.env.workspace = os.getcwd()
        
        # Apply metadata to the TL geodatabase
        print(f"\nApplying metadata to the TL geodatabase: {tl_gdb}")
        for fc in tl_fcs:
            # Define the feature class metadata
            fc_md = md_dict[final_list[fc]]
            mdo = md.Metadata()
            mdo.title = fc_md["title"]
            mdo.tags = fc_md["tags"]
            mdo.summary = fc_md["summary"]
            mdo.description = fc_md["description"]
            mdo.credits = fc_md["credits"]
            mdo.accessConstraints = fc_md["access"]
            mdo.thumbnailUri = fc_md["uri"]

            # Apply the metadata to the feature class
            md_fc = md.Metadata(tl_gdb)
            if not md_fc.isReadOnly:
                md_fc.copy(mdo)
                md_fc.save()
                print(f"- Metadata applied to {final_list[fc]} ({fc})")
            else:
                print(f"- Metadata is read-only for {final_list[fc]} ({fc})")
        
        # Delete the scratch geodatabase
        self.scratch_gdb(method = "delete")

        # Create a metadata object for the TL geodatabase
        print(f"\nApplying metadata to the TL geodatabase:{tl_gdb}")
        md_gdb = md.Metadata(tl_gdb)
        md_gdb.title = f"TL{self.tl_data["year"]} TigerLine Geodatabase"
        md_gdb.tags = "Orange County, California, OCTL, TigerLine, Geodatabase"
        md_gdb.summary = f"Orange County TigerLine Geodatabase for the {self.tl_data["year"]} year data"
        md_gdb.description = f"Orange County TigerLine Geodatabase for the {self.tl_data["year"]} year data. The data contains feature classes for all TigerLine data available for Orange County, California."
        md_gdb.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
        md_gdb.accessConstraints = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
        md_gdb.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/20c4b722b7d84db3a4e163fc0ce11102/data"
        md_gdb.save()

        # Print the list of feature classes in the TL geodatabase
        print(f"\nSuccessfully processed shapefiles:\n{tl_fcs}")

        # Return the list of feature classes in the TL geodatabase
        return final_list


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
