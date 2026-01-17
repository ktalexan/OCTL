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
from datetime import datetime as dt
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
        self.data_date = dt.now().strftime("%B %Y")

        # Create a prj_meta variable calling the project_metadata function
        self.prj_meta = self.project_metadata(silent = False)

        # Create a prj_dirs variable calling the project_directories function
        self.prj_dirs = self.project_directories(silent = False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Print arcpy Messages ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def arcpy_messages(self, text = None) -> None:
        """Print arcpy messages."""
        for message in arcpy.GetMessages().splitlines():
            if text:
                print(f"{text} {message}")
            else:
                print(message)


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
                step = "Part 2: Part 2: ArcGis Pro Project Map Processing"
                desc = "Initialize the ArcGIS Pro Project with Maps and Layers, and process map layers from the TL Geodatabases"
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
            "date": self.data_date,
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
            "gis_agp": os.path.join(self.base_path, "gis", "octl"),
            "gis_aprx": os.path.join(self.base_path, "gis", "octl", "octl.aprx"),
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
    ## Fx: Codebook Metadata ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def codebook_metadata(self, year: int, layers_metadata: dict) -> dict:
        """
        Create a codebook dictionary for geographic layers based on provided metadata.
        Parameters:
            layers_metadata (dict): A dictionary containing metadata for each geographic layer.
        Returns:
            dict: A codebook dictionary with detailed information for each layer.
        Raises:
            None
        Example:
            >>> codebook = self.codebook_metadata(layers_metadata)
            >>> print(codebook)
        Note:
            This function assumes that the input dictionary contains all necessary keys for each layer.
        """
        # Create standard entry values
        entry_gdb = f"TL{year}.gdb"
        entry_tags = "Orange County, California, OCTL, TigerLines"
        entry_credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
        entry_access = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
        entry_uri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"
        
        # Create the codebook dictionary
        codebook = {
            "addr": {
                "type": layers_metadata["addr"]["type"],
                "file": layers_metadata["addr"]["file"],
                "scale": layers_metadata["addr"]["scale"],
                "spatial": layers_metadata["addr"]["spatial"],
                "abbrev": layers_metadata["addr"]["abbrev"],
                "postfix": layers_metadata["addr"]["postfix"],
                "postfix_desc": layers_metadata["addr"]["postfix_desc"],
                "alias": f"OCTL {year} Address Ranges",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Ranges Relationship File",
                "code": "AD",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Adress Ranges Relationship",
                "tags": f"{entry_tags}, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {year} Address Ranges Relationship Table",
                "description": f"Orange County Tiger Lines {year} Address Ranges Relationship Table. This table contains address range information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
                },
            "addrfeat": {
                "type": layers_metadata["addrfeat"]["type"],
                "file": layers_metadata["addrfeat"]["file"],
                "scale": layers_metadata["addrfeat"]["scale"],
                "spatial": layers_metadata["addrfeat"]["spatial"],
                "abbrev": layers_metadata["addrfeat"]["abbrev"],
                "postfix": layers_metadata["addrfeat"]["postfix"],
                "postfix_desc": layers_metadata["addrfeat"]["postfix_desc"],
                "alias": f"OCTL {year} Address Range Features",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Range Feature Shapefile",
                "code": "AF",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Address Range Features",
                "tags": f"{entry_tags}, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {year} Address Range Features",
                "description": f"Orange County Tiger Lines {year} Address Range Features. This shapefile contains address range feature information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "addrfn": {
                "type": layers_metadata["addrfn"]["type"],
                "file": layers_metadata["addrfn"]["file"],
                "scale": layers_metadata["addrfn"]["scale"],
                "spatial": layers_metadata["addrfn"]["spatial"],
                "abbrev": layers_metadata["addrfn"]["abbrev"],
                "postfix": layers_metadata["addrfn"]["postfix"],
                "postfix_desc": layers_metadata["addrfn"]["postfix_desc"],
                "alias": f"OCTL {year} Address Range Feature Names",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Address Range-Feature Name Relationship File",
                "code": "AN",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Address Range-Feature Name Relationship",
                "tags": f"{entry_tags}, Address, Relationships, Table",
                "summary": f"Orange County Tiger Lines {year} Address Range-Feature Name Relationship Table",
                "description": f"Orange County Tiger Lines {year} Address Range-Feature Name Relationship Table. This table contains address range-feature name information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "arealm": {
                "type": layers_metadata["arealm"]["type"],
                "file": layers_metadata["arealm"]["file"],
                "scale": layers_metadata["arealm"]["scale"],
                "spatial": layers_metadata["arealm"]["spatial"],
                "abbrev": layers_metadata["arealm"]["abbrev"],
                "postfix": layers_metadata["arealm"]["postfix"],
                "postfix_desc": layers_metadata["arealm"]["postfix_desc"],
                "alias": f"OCTL {year} Area Landmarks",
                "group": "Features",
                "category": "Landmarks",
                "label": "Area Landmarks",
                "code": "LA",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Area Landmarks",
                "tags": f"{entry_tags}, Area, Landmarks, Features",
                "summary": f"Orange County Tiger Lines {year} Area Landmarks",
                "description": f"Orange County Tiger Lines {year} Area Landmarks. This shapefile contains area landmark feature information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "areawater": {
                "type": layers_metadata["areawater"]["type"],
                "file": layers_metadata["areawater"]["file"],
                "scale": layers_metadata["areawater"]["scale"],
                "spatial": layers_metadata["areawater"]["spatial"],
                "abbrev": layers_metadata["areawater"]["abbrev"],
                "postfix": layers_metadata["areawater"]["postfix"],
                "postfix_desc": layers_metadata["areawater"]["postfix_desc"],
                "alias": f"OCTL {year} Area Hydrography",
                "group": "Features",
                "category": "Water",
                "label": "Area Hydrography",
                "code": "WA",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Area Hydrography",
                "tags": f"{entry_tags}, Water, Hydrography, Features",
                "summary": f"Orange County Tiger Lines {year} Area Hydrography",
                "description": f"Orange County Tiger Lines {year} Area Hydrography. This shapefile contains area hydrography feature information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "bg": {
                "type": layers_metadata["bg"]["type"],
                "file": layers_metadata["bg"]["file"],
                "scale": layers_metadata["bg"]["scale"],
                "spatial": layers_metadata["bg"]["spatial"],
                "abbrev": layers_metadata["bg"]["abbrev"],
                "postfix": layers_metadata["bg"]["postfix"],
                "postfix_desc": layers_metadata["bg"]["postfix_desc"],
                "alias": f"OCTL {year} Block Groups",
                "group": "Geographic Areas",
                "category": "Block Groups",
                "label": "Block Group",
                "code": "BG",
                "method": "query",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Block Groups",
                "tags": f"{entry_tags}, US Census, Block Groups",
                "summary": f"Orange County Tiger Lines {year} Block Groups",
                "description": f"Orange County Tiger Lines {year} Block Groups. This shapefile contains block group geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "cbsa": {
                "type": layers_metadata["cbsa"]["type"],
                "file": layers_metadata["cbsa"]["file"],
                "scale": layers_metadata["cbsa"]["scale"],
                "spatial": layers_metadata["cbsa"]["spatial"],
                "abbrev": layers_metadata["cbsa"]["abbrev"],
                "postfix": layers_metadata["cbsa"]["postfix"],
                "postfix_desc": layers_metadata["cbsa"]["postfix_desc"],
                "alias": f"OCTL {year} Metropolitan Statistical Areas",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Metropolitan/Micropolitan Statistical Area",
                "code": "SM",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Metropolitan Statistical Areas",
                "tags": f"{entry_tags}, US Census, Metropolitan Statistical Areas",
                "summary": f"Orange County Tiger Lines {year} Metropolitan Statistical Areas",
                "description": f"Orange County Tiger Lines {year} Metropolitan Statistical Areas. This shapefile contains metropolitan statistical area geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "coastline": {
                "type": layers_metadata["coastline"]["type"],
                "file": layers_metadata["coastline"]["file"],
                "scale": layers_metadata["coastline"]["scale"],
                "spatial": layers_metadata["coastline"]["spatial"],
                "abbrev": layers_metadata["coastline"]["abbrev"],
                "postfix": layers_metadata["coastline"]["postfix"],
                "postfix_desc": layers_metadata["coastline"]["postfix_desc"],
                "alias": f"OCTL {year} Coastlines",
                "group": "Features",
                "category": "Coastlines",
                "label": "Coastline",
                "code": "CL",
                "method": "clip",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Coastlines",
                "tags": f"{entry_tags}, Coastlines",
                "summary": f"Orange County Tiger Lines {year} Coastlines",
                "description": f"Orange County Tiger Lines {year} Coastlines. This shapefile contains coastline geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "county": {
                "type": layers_metadata["county"]["type"],
                "file": layers_metadata["county"]["file"],
                "scale": layers_metadata["county"]["scale"],
                "spatial": layers_metadata["county"]["spatial"],
                "abbrev": layers_metadata["county"]["abbrev"],
                "postfix": layers_metadata["county"]["postfix"],
                "postfix_desc": layers_metadata["county"]["postfix_desc"],
                "alias": f"OCTL {year} Counties",
                "group": "Geographic Areas",
                "category": "Counties",
                "label": "County and Equivalent",
                "code": "CO",
                "method": "query",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Orange County",
                "tags": f"{entry_tags}, Counties",
                "summary": f"Orange County Tiger Lines {year} Orange County",
                "description": f"Orange County Tiger Lines {year} Orange County. This shapefile contains county geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "csa": {
                "type": layers_metadata["csa"]["type"],
                "file": layers_metadata["csa"]["file"],
                "scale": layers_metadata["csa"]["scale"],
                "spatial": layers_metadata["csa"]["spatial"],
                "abbrev": layers_metadata["csa"]["abbrev"],
                "postfix": layers_metadata["csa"]["postfix"],
                "postfix_desc": layers_metadata["csa"]["postfix_desc"],
                "alias": f"OCTL {year} Combined Statistical Areas",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Combined Statistical Area",
                "code": "SC",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Combined Statistical Areas",
                "tags": f"{entry_tags}, US Census, Statistical Areas",
                "summary": f"Orange County Tiger Lines {year} Combined Statistical Areas",
                "description": f"Orange County Tiger Lines {year} Combined Statistical Areas. This shapefile contains combined statistical area geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "cd": {
                "type": layers_metadata["cd"]["type"],
                "file": layers_metadata["cd"]["file"],
                "scale": layers_metadata["cd"]["scale"],
                "spatial": layers_metadata["cd"]["spatial"],
                "abbrev": layers_metadata["cd"]["abbrev"],
                "postfix": layers_metadata["cd"]["postfix"],
                "postfix_desc": layers_metadata["cd"]["postfix_desc"],
                "alias": f"OCTL {year} Congressional Districts",
                "group": "Geographic Areas",
                "category": "Congressional Districts",
                "label": f"Congressional Districts of the {layers_metadata["cd"]["postfix_desc"]}",
                "code": "CD",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Congressional Districts",
                "tags": f"{entry_tags}, Congressional Districts",
                "summary": f"Orange County Tiger Lines {year} Congressional Districts of the {layers_metadata["cd"]["postfix_desc"]}",
                "description": f"Orange County Tiger Lines {year} Congressional Districts of the {layers_metadata["cd"]["postfix_desc"]}. This shapefile contains congressional district geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "cousub": {
                "type": layers_metadata["cousub"]["type"],
                "file": layers_metadata["cousub"]["file"],
                "scale": layers_metadata["cousub"]["scale"],
                "spatial": layers_metadata["cousub"]["spatial"],
                "abbrev": layers_metadata["cousub"]["abbrev"],
                "postfix": layers_metadata["cousub"]["postfix"],
                "postfix_desc": layers_metadata["cousub"]["postfix_desc"],
                "alias": f"OCTL {year} County Subdivisions",
                "group": "Geographic Areas",
                "category": "County Subdivisions",
                "label": "County Subdivisions",
                "code": "CS",
                "method": "query",
                "gdb": entry_gdb,
                "title": f"OCTL {year} County Subdivisions",
                "tags": f"{entry_tags}, counties, subdivisions",
                "summary": f"Orange County Tiger Lines {year} County Subdivisions",
                "description": f"Orange County Tiger Lines {year} County Subdivisions. This shapefile contains county subdivision geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "edges": {
                "type": layers_metadata["edges"]["type"],
                "file": layers_metadata["edges"]["file"],
                "scale": layers_metadata["edges"]["scale"],
                "spatial": layers_metadata["edges"]["spatial"],
                "abbrev": layers_metadata["edges"]["abbrev"],
                "postfix": layers_metadata["edges"]["postfix"],
                "postfix_desc": layers_metadata["edges"]["postfix_desc"],
                "alias": f"OCTL {year} All Lines",
                "group": "Features",
                "category": "All Lines",
                "label": "All Lines",
                "code": "ED",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} All Lines",
                "tags": f"{entry_tags}, all lines",
                "summary": f"Orange County Tiger Lines {year} All Lines",
                "description": f"Orange County Tiger Lines {year} All Lines. This shapefile contains all line features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "elsd": {
                "type": layers_metadata["elsd"]["type"],
                "file": layers_metadata["elsd"]["file"],
                "scale": layers_metadata["elsd"]["scale"],
                "spatial": layers_metadata["elsd"]["spatial"],
                "abbrev": layers_metadata["elsd"]["abbrev"],
                "postfix": layers_metadata["elsd"]["postfix"],
                "postfix_desc": layers_metadata["elsd"]["postfix_desc"],
                "alias": f"OCTL {year} Elementary School Districts",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Elementary School Districts",
                "code": "SE",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Elementary School Districts",
                "tags": f"{entry_tags}, schools, school districts, elementary schools",
                "summary": f"Orange County Tiger Lines {year} Elementary School Districts",
                "description": f"Orange County Tiger Lines {year} Elementary School Districts. This shapefile contains elementary school district geographic area information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "facesmil": {
                "type": layers_metadata["facesmil"]["type"],
                "file": layers_metadata["facesmil"]["file"],
                "scale": layers_metadata["facesmil"]["scale"],
                "spatial": layers_metadata["facesmil"]["spatial"],
                "abbrev": layers_metadata["facesmil"]["abbrev"],
                "postfix": layers_metadata["facesmil"]["postfix"],
                "postfix_desc": layers_metadata["facesmil"]["postfix_desc"],
                "alias": f"OCTL {year} Topological Faces-Military Installations",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Military Installations Relationship File",
                "code": "FM",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Topological Faces-Military Installations",
                "tags": f"{entry_tags}, military installations",
                "summary": f"Orange County Tiger Lines {year} Topological Faces-Military Installations Table",
                "description": f"Orange County Tiger Lines {year} Topological Faces-Military Installations. This shapefile contains topological faces and military installations relationship information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "faces": {
                "type": layers_metadata["faces"]["type"],
                "file": layers_metadata["faces"]["file"],
                "scale": layers_metadata["faces"]["scale"],
                "spatial": layers_metadata["faces"]["spatial"],
                "abbrev": layers_metadata["faces"]["abbrev"],
                "postfix": layers_metadata["faces"]["postfix"],
                "postfix_desc": layers_metadata["faces"]["postfix_desc"],
                "alias": f"OCTL {year} Topological Faces",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces (Polygons with all Geocodes) Shapefile",
                "code": "FC",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Topological Faces",
                "tags": f"{entry_tags}, faces, relationships",
                "summary": f"Orange County Tiger Lines {year} Topological Faces",
                "description": f"Orange County Tiger Lines {year} Topological Faces. This shapefile contains topological faces (polygons with all geocodes) information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "facesah": {
                "type": layers_metadata["facesah"]["type"],
                "file": layers_metadata["facesah"]["file"],
                "scale": layers_metadata["facesah"]["scale"],
                "spatial": layers_metadata["facesah"]["spatial"],
                "abbrev": layers_metadata["facesah"]["abbrev"],
                "postfix": layers_metadata["facesah"]["postfix"],
                "postfix_desc": layers_metadata["facesah"]["postfix_desc"],
                "alias": f"OCTL {year} Topological Faces-Area Hydrography",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Area Hydrography Relationship File",
                "code": "FH",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Topological Faces-Area Hydrography",
                "tags": f"{entry_tags}, feces, water, hydrography",
                "summary": f"Orange County Tiger Lines {year} Topological Faces-Area Hydrography",
                "description": f"Orange County Tiger Lines {year} Topological Faces-Area Hydrography. This shapefile contains topological faces and area hydrography relationship information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "facesal": {
                "type": layers_metadata["facesal"]["type"],
                "file": layers_metadata["facesal"]["file"],
                "scale": layers_metadata["facesal"]["scale"],
                "spatial": layers_metadata["facesal"]["spatial"],
                "abbrev": layers_metadata["facesal"]["abbrev"],
                "postfix": layers_metadata["facesal"]["postfix"],
                "postfix_desc": layers_metadata["facesal"]["postfix_desc"],
                "alias": f"OCTL {year} Topological Faces-Area Landmark",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Topological Faces-Area Landmark Relationship File",
                "code": "FL",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Topological Faces-Area Landmark",
                "tags": f"{entry_tags}, faces, landmarks",
                "summary": f"Orange County Tiger Lines {year} Topological Faces-Area Landmark",
                "description": f"Orange County Tiger Lines {year} Topological Faces-Area Landmark. This shapefile contains topological faces and area landmark relationship information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "featnames": {
                "type": layers_metadata["featnames"]["type"],
                "file": layers_metadata["featnames"]["file"],
                "scale": layers_metadata["featnames"]["scale"],
                "spatial": layers_metadata["featnames"]["spatial"],
                "abbrev": layers_metadata["featnames"]["abbrev"],
                "postfix": layers_metadata["featnames"]["postfix"],
                "postfix_desc": layers_metadata["featnames"]["postfix_desc"],
                "alias": f"OCTL {year} Feature Names",
                "group": "Feature Relationships",
                "category": "Relationship Files",
                "label": "Feature Names Relationship File",
                "code": "FN",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Feature Names",
                "tags": f"{entry_tags}, names, relationships",
                "summary": f"Orange County Tiger Lines {year} Feature Names Table",
                "description": f"Orange County Tiger Lines {year} Feature Names. This shapefile contains feature names relationship information for features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "linearwater": {
                "type": layers_metadata["linearwater"]["type"],
                "file": layers_metadata["linearwater"]["file"],
                "scale": layers_metadata["linearwater"]["scale"],
                "spatial": layers_metadata["linearwater"]["spatial"],
                "abbrev": layers_metadata["linearwater"]["abbrev"],
                "postfix": layers_metadata["linearwater"]["postfix"],
                "postfix_desc": layers_metadata["linearwater"]["postfix_desc"],
                "alias": f"OCTL {year} Linear Hydrography",
                "group": "Features",
                "category": "Water",
                "label": "Linear Hydrography",
                "code": "WL",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Linear Hydrography",
                "tags": f"{entry_tags}, water, hydrography",
                "summary": f"Orange County Tiger Lines {year} Linear Hydrography",
                "description": f"Orange County Tiger Lines {year} Linear Hydrography. This shapefile contains linear hydrography features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "metdiv": {
                "type": layers_metadata["metdiv"]["type"],
                "file": layers_metadata["metdiv"]["file"],
                "scale": layers_metadata["metdiv"]["scale"],
                "spatial": layers_metadata["metdiv"]["spatial"],
                "abbrev": layers_metadata["metdiv"]["abbrev"],
                "postfix": layers_metadata["metdiv"]["postfix"],
                "postfix_desc": layers_metadata["metdiv"]["postfix_desc"],
                "alias": f"OCTL {year} Metropolitan Divisions",
                "group": "Geographic Areas",
                "category": "Core Based Statistical Areas",
                "label": "Metropolitan Division",
                "code": "MD",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Metropolitan Divisions",
                "tags": f"{entry_tags}, metropolitan divisions",
                "summary": f"Orange County Tiger Lines {year} Metropolitan Divisions",
                "description": f"Orange County Tiger Lines {year} Metropolitan Divisions. This shapefile contains metropolitan division features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "mil": {
                "type": layers_metadata["mil"]["type"],
                "file": layers_metadata["mil"]["file"],
                "scale": layers_metadata["mil"]["scale"],
                "spatial": layers_metadata["mil"]["spatial"],
                "abbrev": layers_metadata["mil"]["abbrev"],
                "postfix": layers_metadata["mil"]["postfix"],
                "postfix_desc": layers_metadata["mil"]["postfix_desc"],
                "alias": f"OCTL {year} Military Installations",
                "group": "Features",
                "category": "Military Installations",
                "label": "Military Installations",
                "code": "ML",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Military Installations",
                "tags": f"{entry_tags}, military installations",
                "summary": f"Orange County Tiger Lines {year} Military Installations",
                "description": f"Orange County Tiger Lines {year} Military Installations. This shapefile contains military installation features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "place": {
                "type": layers_metadata["place"]["type"],
                "file": layers_metadata["place"]["file"],
                "scale": layers_metadata["place"]["scale"],
                "spatial": layers_metadata["place"]["spatial"],
                "abbrev": layers_metadata["place"]["abbrev"],
                "postfix": layers_metadata["place"]["postfix"],
                "postfix_desc": layers_metadata["place"]["postfix_desc"],
                "alias": f"OCTL {year} Cities or Places",
                "group": "Geographic Areas",
                "category": "Places",
                "label": "Place (Cities or Unincorporated)",
                "code": "PL",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Cities or Places",
                "tags": f"{entry_tags}, places, cities",
                "summary": f"Orange County Tiger Lines {year} Cities or Places",
                "description": f"Orange County Tiger Lines {year} Cities or Places. This shapefile contains city and place features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "pointlm": {
                "type": layers_metadata["pointlm"]["type"],
                "file": layers_metadata["pointlm"]["file"],
                "scale": layers_metadata["pointlm"]["scale"],
                "spatial": layers_metadata["pointlm"]["spatial"],
                "abbrev": layers_metadata["pointlm"]["abbrev"],
                "postfix": layers_metadata["pointlm"]["postfix"],
                "postfix_desc": layers_metadata["pointlm"]["postfix_desc"],
                "alias": f"OCTL {year} Point Landmarks",
                "group": "Features",
                "category": "Landmarks",
                "label": "Point Landmarks",
                "code": "LP",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Point Landmarks",
                "tags": f"{entry_tags}, points, landmarks",
                "summary": f"Orange County Tiger Lines {year} Point Landmarks",
                "description": f"Orange County Tiger Lines {year} Point Landmarks. This shapefile contains point landmark features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "primaryroads": {
                "type": layers_metadata["primaryroads"]["type"],
                "file": layers_metadata["primaryroads"]["file"],
                "scale": layers_metadata["primaryroads"]["scale"],
                "spatial": layers_metadata["primaryroads"]["spatial"],
                "abbrev": layers_metadata["primaryroads"]["abbrev"],
                "postfix": layers_metadata["primaryroads"]["postfix"],
                "postfix_desc": layers_metadata["primaryroads"]["postfix_desc"],
                "alias": f"OCTL {year} Primary Roads",
                "group": "Features",
                "category": "Roads",
                "label": "Primary Roads",
                "code": "RP",
                "method": "clip",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Primary Roads",
                "tags": f"{entry_tags}, roads, primary",
                "summary": f"Orange County Tiger Lines {year} Primary Roads",
                "description": f"Orange County Tiger Lines {year} Primary Roads. This shapefile contains primary road features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "prisecroads": {
                "type": layers_metadata["prisecroads"]["type"],
                "file": layers_metadata["prisecroads"]["file"],
                "scale": layers_metadata["prisecroads"]["scale"],
                "spatial": layers_metadata["prisecroads"]["spatial"],
                "abbrev": layers_metadata["prisecroads"]["abbrev"],
                "postfix": layers_metadata["prisecroads"]["postfix"],
                "postfix_desc": layers_metadata["prisecroads"]["postfix_desc"],
                "alias": f"OCTL {year} Primary and Secondary Roads",
                "group": "Features",
                "category": "Roads",
                "label": "Primary and Secondary Roads",
                "code": "RS",
                "method": "clip",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Primary and Secondary Roads",
                "tags": f"{entry_tags}, roads, primary, secondary",
                "summary": f"Orange County Tiger Lines {year} Primary and Secondary Roads",
                "description": f"Orange County Tiger Lines {year} Primary and Secondary Roads. This shapefile contains primary and secondary road features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "puma": {
                "type": layers_metadata["puma"]["type"],
                "file": layers_metadata["puma"]["file"],
                "scale": layers_metadata["puma"]["scale"],
                "spatial": layers_metadata["puma"]["spatial"],
                "abbrev": layers_metadata["puma"]["abbrev"],
                "postfix": layers_metadata["puma"]["postfix"],
                "postfix_desc": layers_metadata["puma"]["postfix_desc"],
                "alias": f"OCTL {year} Public Use Microdata Areas",
                "group": "Geographic Areas",
                "category": "Public Use Microdata Areas",
                "label": "Public Use Microdata Areas",
                "code": "PU",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Public Use Microdata Areas",
                "tags": f"{entry_tags}, public use microdata areas",
                "summary": f"Orange County Tiger Lines {year} Public Use Microdata Areas",
                "description": f"Orange County Tiger Lines {year} Public Use Microdata Areas. This shapefile contains public use microdata area features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "rails": {
                "type": layers_metadata["rails"]["type"],
                "file": layers_metadata["rails"]["file"],
                "scale": layers_metadata["rails"]["scale"],
                "spatial": layers_metadata["rails"]["spatial"],
                "abbrev": layers_metadata["rails"]["abbrev"],
                "postfix": layers_metadata["rails"]["postfix"],
                "postfix_desc": layers_metadata["rails"]["postfix_desc"],
                "alias": f"OCTL {year} Rails",
                "group": "Features",
                "category": "Rails",
                "label": "Rails",
                "code": "RL",
                "method": "clip",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Rails",
                "tags": f"{entry_tags}, rails, railroads",
                "summary": f"Orange County Tiger Lines {year} Rails",
                "description": f"Orange County Tiger Lines {year} Rails. This shapefile contains rail features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "roads": {
                "type": layers_metadata["roads"]["type"],
                "file": layers_metadata["roads"]["file"],
                "scale": layers_metadata["roads"]["scale"],
                "spatial": layers_metadata["roads"]["spatial"],
                "abbrev": layers_metadata["roads"]["abbrev"],
                "postfix": layers_metadata["roads"]["postfix"],
                "postfix_desc": layers_metadata["roads"]["postfix_desc"],
                "alias": f"OCTL {year} All Roads",
                "group": "Features",
                "category": "Roads",
                "label": "All Roads",
                "code": "RD",
                "method": "copy",
                "gdb": entry_gdb,
                "title": f"OCTL {year} All Roads",
                "tags": f"{entry_tags}, roads",
                "summary": f"Orange County Tiger Lines {year} All Roads",
                "description": f"Orange County Tiger Lines {year} All Roads. This shapefile contains road features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "scsd": {
                "type": layers_metadata["scsd"]["type"],
                "file": layers_metadata["scsd"]["file"],
                "scale": layers_metadata["scsd"]["scale"],
                "spatial": layers_metadata["scsd"]["spatial"],
                "abbrev": layers_metadata["scsd"]["abbrev"],
                "postfix": layers_metadata["scsd"]["postfix"],
                "postfix_desc": layers_metadata["scsd"]["postfix_desc"],
                "alias": f"OCTL {year} Secondary School Districts",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Secondary School Districts",
                "code": "SS",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Secondary School Districts",
                "tags": f"{entry_tags}, schools, school districts, secondary schools",
                "summary": f"Orange County Tiger Lines {year} Secondary School Districts",
                "description": f"Orange County Tiger Lines {year} Secondary School Districts. This shapefile contains secondary school district features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "sldl": {
                "type": layers_metadata["sldl"]["type"],
                "file": layers_metadata["sldl"]["file"],
                "scale": layers_metadata["sldl"]["scale"],
                "spatial": layers_metadata["sldl"]["spatial"],
                "abbrev": layers_metadata["sldl"]["abbrev"],
                "postfix": layers_metadata["sldl"]["postfix"],
                "postfix_desc": layers_metadata["sldl"]["postfix_desc"],
                "alias": f"OCTL {year} State Assembly Legislative Districts",
                "group": "Geographic Areas",
                "category": "State Legislative Districts",
                "label": "State Legislative District - Lower Chamber (Assembly)",
                "code": "LL",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} State Assembly Legislative Districts",
                "tags": f"{entry_tags}, legislative districts, state assembly",
                "summary": f"Orange County Tiger Lines {year} State Assembly Legislative Districts",
                "description": f"Orange County Tiger Lines {year} State Assembly Legislative Districts. This shapefile contains state assembly legislative district (lower chamber) features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "sldu": {
                "type": layers_metadata["sldu"]["type"],
                "file": layers_metadata["sldu"]["file"],
                "scale": layers_metadata["sldu"]["scale"],
                "spatial": layers_metadata["sldu"]["spatial"],
                "abbrev": layers_metadata["sldu"]["abbrev"],
                "postfix": layers_metadata["sldu"]["postfix"],
                "postfix_desc": layers_metadata["sldu"]["postfix_desc"],
                "alias": f"OCTL {year} State Senate Legislative Districts",
                "group": "Geographic Areas",
                "category": "State Legislative Districts",
                "label": "State Legislative District - Upper Chamber (Senate)",
                "code": "LU",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} State Senate Legislative Districts",
                "tags": f"{entry_tags}, legislative districts, state senate",
                "summary": f"Orange County Tiger Lines {year} State Senate Legislative Districts",
                "description": f"Orange County Tiger Lines {year} State Senate Legislative Districts. This shapefile contains state senate legislative district (upper chamber) features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "tabblock": {
                "type": layers_metadata["tabblock"]["type"],
                "file": layers_metadata["tabblock"]["file"],
                "scale": layers_metadata["tabblock"]["scale"],
                "spatial": layers_metadata["tabblock"]["spatial"],
                "abbrev": layers_metadata["tabblock"]["abbrev"],
                "postfix": layers_metadata["tabblock"]["postfix"],
                "postfix_desc": layers_metadata["tabblock"]["postfix_desc"],
                "alias": f"OCTL {year} Blocks",
                "group": "Geographic Areas",
                "category": "Blocks",
                "label": "Block",
                "code": "BL",
                "method": "query",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Blocks",
                "tags": f"{entry_tags}, US Census, blocks",
                "summary": f"Orange County Tiger Lines {year} Blocks",
                "description": f"Orange County Tiger Lines {year} Blocks. This shapefile contains block features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "tract": {
                "type": layers_metadata["tract"]["type"],
                "file": layers_metadata["tract"]["file"],
                "scale": layers_metadata["tract"]["scale"],
                "spatial": layers_metadata["tract"]["spatial"],
                "abbrev": layers_metadata["tract"]["abbrev"],
                "postfix": layers_metadata["tract"]["postfix"],
                "postfix_desc": layers_metadata["tract"]["postfix_desc"],
                "alias": f"OCTL {year} Census Tracts",
                "group": "Geographic Areas",
                "category": "Census Tracts",
                "label": "Census Tract",
                "code": "TR",
                "method": "query",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Census Tracts",
                "tags": f"{entry_tags}, US Census, census tracts",
                "summary": f"Orange County Tiger Lines {year} Census Tracts",
                "description": f"Orange County Tiger Lines {year} Census Tracts. This shapefile contains census tract features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "unsd": {
                "type": layers_metadata["unsd"]["type"],
                "file": layers_metadata["unsd"]["file"],
                "scale": layers_metadata["unsd"]["scale"],
                "spatial": layers_metadata["unsd"]["spatial"],
                "abbrev": layers_metadata["unsd"]["abbrev"],
                "postfix": layers_metadata["unsd"]["postfix"],
                "postfix_desc": layers_metadata["unsd"]["postfix_desc"],
                "alias": f"OCTL {year} Unified School Districts",
                "group": "Geographic Areas",
                "category": "School Districts",
                "label": "Unified School Districts",
                "code": "SU",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Unified School Districts",
                "tags": f"{entry_tags}, schools, school districts, unified schools",
                "summary": f"Orange County Tiger Lines {year} Unified School Districts",
                "description": f"Orange County Tiger Lines {year} Unified School Districts. This shapefile contains unified school district features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "uac": {
                "type": layers_metadata["uac"]["type"],
                "file": layers_metadata["uac"]["file"],
                "scale": layers_metadata["uac"]["scale"],
                "spatial": layers_metadata["uac"]["spatial"],
                "abbrev": layers_metadata["uac"]["abbrev"],
                "postfix": layers_metadata["uac"]["postfix"],
                "postfix_desc": layers_metadata["uac"]["postfix_desc"],
                "alias": f"OCTL {year} Urban Areas",
                "group": "Geographic Areas",
                "category": "Urban Areas",
                "label": "Urban Areas",
                "code": "UA",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} Urban Areas",
                "tags": f"{entry_tags}, urban areas",
                "summary": f"Orange County Tiger Lines {year} Urban Areas",
                "description": f"Orange County Tiger Lines {year} Urban Areas. This shapefile contains urban area features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            },
            "zcta5": {
                "type": layers_metadata["zcta5"]["type"],
                "file": layers_metadata["zcta5"]["file"],
                "scale": layers_metadata["zcta5"]["scale"],
                "spatial": layers_metadata["zcta5"]["spatial"],
                "abbrev": layers_metadata["zcta5"]["abbrev"],
                "postfix": layers_metadata["zcta5"]["postfix"],
                "postfix_desc": layers_metadata["zcta5"]["postfix_desc"],
                "alias": f"OCTL {year} ZIP Code Tabulation Areas",
                "group": "Geographic Areas",
                "category": "ZIP Code Tabulation Areas",
                "label": "ZIP Code Tabulation Areas",
                "code": "ZC",
                "method": "within",
                "gdb": entry_gdb,
                "title": f"OCTL {year} ZIP Code Tabulation Areas",
                "tags": f"{entry_tags}, ZIP Codes, ZCTA",
                "summary": f"Orange County Tiger Lines {year} ZIP Code Tabulation Areas",
                "description": f"Orange County Tiger Lines {year} ZIP Code Tabulation Areas. This shapefile contains ZIP Code Tabulation Area features in the Tiger/Line shapefiles. Version {self.version}, Last Updated: {self.data_date}.",
                "credits": entry_credits,
                "access": entry_access,
                "uri": entry_uri
            }
        }

        # Define the codebook path
        cb_path = os.path.join(self.prj_dirs["codebook"], f"cb_{year}.json")
        
        # Export the codebook to a JSON file
        with open(cb_path, "w", encoding = "utf-8") as json_file:
            json.dump(codebook, json_file, indent = 4)
            print(f"Codebook exported to {cb_path}")

        # Return the constructed codebook
        return codebook


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Get Raw Data Dictionary ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_raw_data(self, export: bool = False) -> dict:
        """
        Get the raw data.
        Args:
            export (bool): If True, exports the metadata to a JSON file. Default is False.
        Returns:
            tl_metadata (dict): The raw data metadata.
        Raises:
            ValueError: if there is no folder under the 'data/raw' directory
        Example:
            >>>tl_metadata = get_raw_data()
        Notes:
            This function gets the raw data from the raw data directory.
        """ 
        # Initialize metadata dictionary
        metadata = {}

        # Read all directories in the path
        folder = [d for d in os.listdir(self.prj_dirs["data_raw"]) if os.path.isdir(os.path.join(self.prj_dirs["data_raw"], d))][0]

        # Set the directory path
        folder_path = os.path.join(self.prj_dirs["data_raw"], folder)

        # Relative folder path
        relative_folder_path = os.path.relpath(folder_path, self.prj_dirs["root"])

        # Extract year from directory name
        year = folder.removeprefix("tl_")

        # Create metadata dictionary folder data
        metadata = {"version": self.version, "date": self.data_date, "year": int(year), "folder": folder, "path": relative_folder_path, "layers": {}}

        # Define the layers to be checked
        layers = ["addr", "addrfeat", "addrfn", "arealm", "areawater", "bg", "cbsa", "cd", "coastline", "county", "cousub", "csa", "edges", "elsd", "faces", "facesah", "facesal", "facesmil", "featnames", "linearwater", "metdiv", "mil", "place", "pointlm", "primaryroads", "prisecroads", "puma", "rails", "roads", "scsd", "sldl", "sldu", "tabblock", "tract", "uac", "unsd", "zcta5"]

        try:
            # Set environment workspace to the folder path
            arcpy.env.workspace = folder_path

            # Get the shapefiles in the folder
            shp_files = sorted([os.path.splitext(s)[0] for s in arcpy.ListFeatureClasses()])

            # Get the list of tables in the folder
            dbf_files = sorted([os.path.splitext(s)[0] for s in arcpy.ListTables()])
        finally:
            # Set environment workspace to the current working directory
            arcpy.env.workspace = os.getcwd()

        # Combine shapefiles and tables
        files = sorted(list(set(shp_files + dbf_files)))

        # Print the count of files by type
        print(f"Year: {year}\n- Total Files: {len(files)}\n- Shapefiles: {len(shp_files)}\n- Tables: {len(dbf_files)}")

        # Create an intermediary layers dictionary
        layers_metadata = {}

        # Loop through each file
        for f in files:
            # Split the file name into components
            file_components = f.split("_")
            # Extract the year, spatial level, and abbreviation
            file_spatial = file_components[2]
            file_abbrev = file_components[3]

            # Check if the file is a shapefile or table
            if f in shp_files:
                file_type = "Shapefile"
            elif f in dbf_files:
                file_type = "Table"
            else:
                file_type = "Unknown"

            # Check if the file layer is in the defined layers
            if file_abbrev in layers:
                file_layer = file_abbrev
                file_postfix = ""
            else:
                # Find all the matches in file_abbrev that start with the layer
                matches = [layer for layer in layers if file_abbrev.startswith(layer)]
                # Check if any matches were found
                if matches:
                    # Get the match with the longest length
                    file_layer = max(matches, key = len)
                    # Extract the postfix from the file_abbrev
                    file_postfix = file_abbrev.removeprefix(file_layer)
                else:
                    file_layer = "Unknown"
                    file_postfix = ""

            # Determine spatial level description
            match file_spatial:
                case "us":
                    spatial_level = "US"
                case "06":
                    spatial_level = "CA"
                case "06059":
                    spatial_level = "OC"
                case _:
                    spatial_level = "Unknown"

            # Calculate the length of the postfix
            len_postfix = len(file_postfix)

            # Determine postfix description
            if len_postfix == 2:
                file_postfix_desc = f"20{file_postfix} US Census"
            elif len_postfix == 3:
                file_postfix_desc = f"{file_postfix}th US Congress"
            else:
                file_postfix_desc = ""

            # Populate the metadata dictionary
            layers_metadata[file_layer] = {
                "type": file_type,
                "file": f,
                "scale": spatial_level,
                "spatial": file_spatial,
                "abbrev": file_abbrev,
                "postfix": file_postfix,
                "postfix_desc": file_postfix_desc
            }

        # Sort the metadata dictionary by file_layer
        layers_metadata = dict(sorted(layers_metadata.items()))

        # Add layers metadata to the main metadata dictionary
        metadata["layers"] = self.codebook_metadata(int(year), layers_metadata)

        if export:
            # Export metadata to JSON file
            json_path = os.path.join(self.prj_dirs["metadata"], f"raw_metadata_tl_{year}.json")
            with open(json_path, "w", encoding = "utf-8") as json_file:
                json.dump(metadata, json_file, indent=4)
                print(f"Metadata exported to {json_path}")
        
        # Return the populated metadata dictionary
        return metadata


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Load Codebook Function ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def load_cb(self, year: int, cbdf: bool = False) -> tuple:
        """
        Load the codebook.
        Args:
            cbdf (bool): If True, returns the codebook as a DataFrame. Default is False.
        Returns:
            cb (dict): The codebook.
            df_cb (pd.DataFrame): The codebook data frame.
        Raises:
            Nothing
        Example:
            >>>cb, df_cb = load_cb(year, cbdf = True)
        Notes:
            This function loads the codebook from the codebook path.
        """

        # Set the codebook from the JSON file
        cb_path = os.path.join(self.prj_dirs["codebook"], f"cb_{year}.json")
        with open(cb_path, "r", encoding = "utf-8") as json_file:
            cb = json.load(json_file)
        
        if cbdf:
            # Create a codebook data frame
            cbdf = pd.DataFrame(cb).transpose()
            # Add attributes to the codebook data frame
            cbdf.attrs["name"] = "Codebook"        
            print("\nCodebook:\n", cbdf)
            return cb, cbdf
        else:
            return cb


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Create Scratch Geodatabase ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    def create_gdb(self, year: int) -> str:
        """
        Create a geodatabase.
        Args:
            year (int): The year of the geodatabase.
        Returns:
            gdb_path (str): The path to the geodatabase.
        Raises:
            Nothing
        Example:
            >>>create_gdb()
        Notes:
            This function creates a geodatabase.
        """
        gdb_name = f"TL{year}.gdb"
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

        if shapefiles:
            # FeatureClassToGeodatabase accepts a list of inputs
            arcpy.conversion.FeatureClassToGeodatabase(shapefiles, scratch_gdb)
            self.arcpy_messages()
            print(f"\nSuccessfully imported {len(shapefiles)} shapefiles to {scratch_gdb}\n")
        else:
            print("No shapefiles found in the specified directory.")

        if tables:
            # FeatureClassToGeodatabase accepts a list of inputs
            arcpy.conversion.TableToGeodatabase(tables, scratch_gdb)
            self.arcpy_messages()
            print(f"\nSuccessfully imported {len(tables)} tables to {scratch_gdb}\n")
        else:
            print("No tables found in the specified directory.")

        # Create a geodatabase for the year
        tl_gdb = self.create_gdb(tl_metadata["year"])

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
            self.arcpy_messages()

        # Check if the output feature class is empty
        if int(arcpy.GetCount_management(out_oc).getOutput(0)) == 0:
            arcpy.management.Delete(out_oc)
            self.arcpy_messages("-")
            print(f"- Deleted empty feature class: {out_oc}")


        # Create a list to store the final feature classes
        final_list = dict()

        # Create a list of feature classes to process and remove the us_county feature class
        fc_list = list(cb.keys())
        fc_list.remove("county")
        final_list["CO"] = "county"
        
        # Alter the alias name of the county feature class
        arcpy.AlterAliasName(out_oc, cb["county"]["alias"])
        self.arcpy_messages()

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
                    self.arcpy_messages("-")
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        self.arcpy_messages("-")
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                        self.arcpy_messages("-")
                case "copy":
                    # Copy the feature class as is
                    arcpy.management.Copy(
                        in_data = in_fc,
                        out_data = out_fc,
                        data_type = "FeatureClass",
                        associated_data = None
                    )
                    self.arcpy_messages("-")
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        self.arcpy_messages("-")
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                        self.arcpy_messages("-")
                case "within":
                    # Create a temporary layer (this stays in memory, not in your Pro Map)
                    arcpy.management.MakeFeatureLayer(in_fc, "temp_lyr")
                    self.arcpy_messages("-")
                    # Check if the temp_lyr is empty
                    if arcpy.management.GetCount("temp_lyr") == 0:
                        arcpy.management.Delete("temp_lyr")
                        self.arcpy_messages("-")
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
                    self.arcpy_messages("-")
                    # Export the selection to a new fc
                    arcpy.conversion.FeatureClassToFeatureClass("temp_lyr", tl_gdb, code)
                    self.arcpy_messages("-")
                    # Delete the temporary layer
                    arcpy.management.Delete("temp_lyr")
                    self.arcpy_messages("-")
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        self.arcpy_messages("-")
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                        self.arcpy_messages("-")
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
                    self.arcpy_messages("-")
                    # Check if the output feature class is empty
                    if int(arcpy.GetCount_management(out_fc).getOutput(0)) == 0:
                        arcpy.management.Delete(out_fc)
                        self.arcpy_messages("-")
                        print(f"- Deleted empty feature class: {out_fc}")
                    else:
                        final_list[code] = f
                        # Alter the alias name of the feature class
                        arcpy.AlterAliasName(out_fc, cb[f]["alias"])
                        self.arcpy_messages("-")
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
        self.scratch_gdb(method = "delete")

        # Create a metadata object for the TL geodatabase
        print(f"\nApplying metadata to the TL geodatabase:{tl_gdb}")
        md_gdb = md.Metadata(tl_gdb)
        md_gdb.title = f"TL{tl_metadata["year"]} TigerLine Geodatabase"
        md_gdb.tags = "Orange County, California, OCTL, TigerLine, Geodatabase"
        md_gdb.summary = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data"
        md_gdb.description = f"Orange County TigerLine Geodatabase for the {tl_metadata["year"]} year data. The data contains feature classes for all TigerLine data available for Orange County, California. Version: {self.version}, last updated on {self.data_date}."
        md_gdb.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
        md_gdb.accessConstraints = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
        md_gdb.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"
        md_gdb.save()

        # Print the list of feature classes in the TL geodatabase
        print(f"\nSuccessfully processed shapefiles:\n{tl_fcs}")

        # Return the list of feature classes in the TL geodatabase
        return final_list

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Get GDB Dictionary ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_gdb_dict(self) -> dict:
        """
        Function to get the gdb dictionary from the project directories.
        Args:
            Nothing
        Returns:
            gdb_dict (dict): The gdb dictionary.
        Raises:
            Nothing
        Example:
            >>> gdb_dict = get_gdb_dict()
        Notes:
            This function gets the gdb dictionary from the project directories.
        """
        # US Congress dictionary mapping years to Congress Numbers
        congress_dict = {"2010": "111", "2011": "112", "2012": "112", "2013": "113", "2014": "114", "2015": "114", "2016": "115", "2017": "115", "2018": "116", "2019": "116", "2020": "116", "2021": "116", "2022": "118", "2023": "118", "2024": "119", "2025": "119"}

        # Get the list of gdb files in the gis directory
        gdb_list = [f for f in os.listdir(self.prj_dirs["gis"]) if f.endswith(".gdb")]
        
        # Initialize the gdb dictionary
        gdb_dict = {}
        
        # Loop through the gdb files
        for gdb in gdb_list:
            year = int(gdb.split(".")[0].replace("TL", ""))
            path = os.path.join(self.prj_dirs["gis"], gdb)
            arcpy.env.workspace = path
            fc_list =arcpy.ListFeatureClasses()
            fc_dict = self.process_metadata(year)
            
            # Initialize the gdb dictionary for the year
            gdb_dict[str(year)] = {}
            
            # Loop through the feature classes
            for fc in fc_list:
                if fc == ["CD"]:
                    # get the congress number from the congress_dict
                    congress_number = congress_dict[str(year)]
                    for value in fc_dict.values():
                        value["alias"] = f"OCTL {year} Congressional Districts {congress_number}th Congress"
                        value["label"] = f"Congressional Districts of the {congress_number}th US Congress"
                        value["title"] = f"OCTL {year} Congressional Districts of the {congress_number}th US Congress"
                        value["description"] = f"Orange County Tiger Lines {year} Congressional Districts of the {congress_number}th US Congress"
                        gdb_dict[str(year)][fc] = value
                    continue
                else:
                    # get the fc_dict key that matches the fc name and update the value
                    for value in fc_dict.values():
                        if value["fcname"] == fc:
                            gdb_dict[str(year)][fc] = value
            
            # Reset the workspace
            arcpy.env.workspace = os.getcwd()
        
        # Return the gdb dictionary
        return gdb_dict

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Map Metadata ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def map_metadata(self, year: int) -> dict:
        """Function to get the map metadata for a given year.
        Args:
            year (int): The year for which to get the map metadata.
        Returns:
            dict: A dictionary containing the map metadata for the given year.
        Raises:
            Nothing
        Example:
            >>> map_metadata(2020)
        Notes:
            This function gets the map metadata for a given year.
        """
        # Convert year to string
        year = str(year)

        # Create the map metadata dictionary
        md_map = {
            "title": f"OCTL {year} Map",
            "tags": f"Orange County, California, Tiger/Line, OCTL, TL{year}",
            "summary": f"Orange County Tiger Lines Map for {year}",
            "description": f"Orange County Tiger Lines {year} Map containing the most up-to-date spatial data for Orange County, California. This map is part of the Orange County Tiger Lines (OCTL) project, which provides comprehensive geospatial data for the county. The data includes roads, boundaries, hydrography, and other essential features derived from the U.S. Census Bureau's Tiger/Line shapefiles for {year}.",
            "credits": "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services",
            "access": """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>""",
            "uri": "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"
        }

        # Return the map metadata dictionary
        return md_map


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fx: Write Dictionary to JSON ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def write_dict_to_json(self, data: dict, dict_type: str) -> str:
        """
        Write a dictionary to a JSON file.
        Args:
            data (dict): The dictionary to write to a JSON file.
            dict_type (str): The type of dictionary to determine the filename.
        Returns:
            str: The filename of the written JSON file.
        Raises:
            Nothing
        Example:
            >>> write_dict_to_json(data, "gdbs")
        Notes:
            This function writes a dictionary to a JSON file.
        """
        # Determine the filename based on the dict_type
        match dict_type:
            case "gdbs":
                dict_name = "gdb_dict.json"
            case "layers":
                dict_name = "layers_dict.json"
        
        # Create the full file path
        filename = os.path.join(self.prj_dirs["metadata"], dict_name)

        # Write the dictionary to a JSON file
        with open(filename, "w", encoding = "utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Dictionary written to {filename}")

        # Return the filename
        return filename


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
