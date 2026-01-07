
import pandas as pd
from arcgis.geometry import Polygon, Geometry

# Create dummy geometries to check methods
p1 = Polygon({"rings": [[[-118, 34], [-117, 34], [-117, 35], [-118, 35], [-118, 34]]], "spatialReference": {"wkid": 4326}})

print("Methods of Polygon:")
for method in ['within', 'contains', 'intersects', 'intersect', 'disjoint', 'overlaps', 'touches', 'crosses']:
    print(f"{method}: {hasattr(p1, method)}")
