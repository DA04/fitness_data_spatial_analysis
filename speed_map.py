# Attribute visualization on the route - Option with CircleMarker
# Source https://plugins.qgis.org/planet/tag/folium/

# import modules
import psycopg2
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import branca

# create a new dataframe for the activity
activity_id = 97199718403
conn = psycopg2.connect(host="localhost", database="garmin_data", user="postgres", password="afande")
df = pd.read_sql_query("""select * from record
where activity_id ={} order by timestamp asc""".format(activity_id), conn)

# create geodataframes for the map extent and for the speed points
line = gpd.GeoDataFrame(index=[0], crs = 'EPSG:4326', geometry=[LineString(zip(df.longitude, df.latitude))])    
gdf = gpd.GeoDataFrame(df[['speed', 'latitude', 'longitude']], crs='EPSG:4326',geometry=gpd.points_from_xy(df.longitude, df.latitude))

# assign speed values to linear gradient colors
colormap = branca.colormap.LinearColormap(colors=['cyan', 'green','yellow', 'orange', 'red'],
                             index=[0, 10, 20, 30, 40], vmin=0, vmax=40,
                             caption='Average Speed, km/h')

# display the map
import folium
m = folium.Map([line.centroid.y, line.centroid.x], tiles='cartodbpositron')
for point, alt in gdf[['geometry', 'speed']].values:
    folium.CircleMarker([point.y, point.x], radius=6, fill=True, color='r', fill_color=colormap(alt), fill_opacity=1.0).add_to(m)
m.add_child(colormap)
folium.FitBounds([[line.bounds.miny[0], line.bounds.minx[0]],[line.bounds.maxy[0], line.bounds.maxx[0]]]).add_to(m)
m