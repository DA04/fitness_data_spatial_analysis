# Attribute visualization on the route - Option with Gradient Line

# import modules
import psycopg2
import pandas as pd
from pyproj import Proj, CRS, transform
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon

# create a new dataframe for the activity
activity_id = 97199718403
conn = psycopg2.connect(host="localhost", database="garmin_data", user="postgres", password="afande")
df = pd.read_sql_query("""select * from record
where activity_id ={} order by timestamp asc""".format(activity_id), conn)

# create a geodataframe for the activity
line = gpd.GeoDataFrame(index=[0], crs = 'EPSG:4326', geometry=[LineString(zip(df.longitude, df.latitude))])    

# calculate average speed and ordered number for the segments (between two points)
df = df[['record_id','speed', 'latitude', 'longitude']]
df['avg_speed'], df['segment'] = 0, 0
df['prev_lat'] = df.latitude.shift(1)
df['prev_long'] = df.longitude.shift(1)

for row in range(1, len(df)):
    df.loc[row, 'avg_speed'] = round((df.loc[row-1, 'speed']+df.loc[row, 'speed'])/2)
for i in range(2, len(df)):
    df.loc[i, 'segment'] = [df.loc[i-1, 'segment'] if df.loc[i, 'avg_speed'] == df.loc[i-1, 'avg_speed'] else df.loc[i-1, 'segment']+1]
df = df.iloc[1:,:]

# create geometry for the segments
df['from'] = [Point(xy) for xy in zip(df.prev_long, df.prev_lat)]
df['to'] = [Point(xy) for xy in zip(df.longitude, df.latitude)]

df['polyline'] = df.apply(lambda row: LineString([row['from'], row['to']]), axis=1)
gdf = gpd.GeoDataFrame(df[['segment', 'avg_speed']], geometry=df.polyline, crs='EPSG:4326')

# group the segments
segments = gdf.dissolve(by=['segment', 'avg_speed'])
segments = segments.reset_index()

# display the map with speed line
import folium
import branca

# the linear gradient settings
colormap = branca.colormap.LinearColormap(colors=['cyan', 'green','yellow', 'orange', 'red'],
                             index=[0, 10, 20, 30, 40], vmin=0, vmax=40,
                             caption='Average Speed, km/h')
   
m = folium.Map([line.centroid.y, line.centroid.x], tiles='cartodbpositron')
folium.GeoJson(segments, style_function=lambda x:{'color': colormap(x['properties']['avg_speed'])}).add_to(m)
folium.FitBounds([[line.bounds.miny[0], line.bounds.minx[0]],[line.bounds.maxy[0], line.bounds.maxx[0]]]).add_to(m)
m.add_child(colormap)
m