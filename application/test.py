import geopandas as gpd

# Loads the shape file in shapefiles
location = f'./shapeFiles/BON_Coastline.shp'

# Checks the crs file data of this shape file
coastline = gpd.read_file(location)

# Prints the crs data
print(coastline.crs)