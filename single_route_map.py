# Creating a single map for a training route

# import modules
import psycopg2
import pandas as pd
from pyproj import CRS
import geopandas as gpd
from shapely.geometry import LineString

# create a new dataframe for the activity
activity_id = 100007015961
conn = psycopg2.connect(host="localhost", database="garmin_data", user="postgres", password="*****")
df = pd.read_sql_query("""select * from record
where activity_id ={} order by timestamp asc""".format(activity_id), conn)

# create a geodataframe from the dataframe
line = gpd.GeoDataFrame(crs = CRS('EPSG:4326'), geometry=[LineString(zip(df.longitude, df.latitude))])

# calculate centroid and bounds coordinates
line_centroid = line.centroid
line_bounds = line.bounds

# display the map with route layer
import folium
m = folium.Map([line_centroid.y, line_centroid.x], tiles='Stamen Terrain')
folium.GeoJson(line).add_to(m)
folium.FitBounds([[line_bounds.miny[0], line_bounds.minx[0]],[line_bounds.maxy[0], t_bounds.maxx[0]]]).add_to(m)
m