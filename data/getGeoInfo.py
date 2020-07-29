import geopandas as gpd
import os


# Canada Geographic info - converts .shp to GeoJSON data
geo_path_ca = os.path.join(os.getcwd(), 'ca_geodata')
gdf = gpd.read_file(os.path.join(geo_path_ca, 'gadm36_CAN_1.shp'), encoding='utf-8')
print(gdf.crs)
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(os.path.join(geo_path_ca, 'canada-geo.json'), driver='GeoJSON')
