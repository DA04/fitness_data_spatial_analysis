# Creating Routes Density Map

# import modules
import geopandas as gpd
import h3pandas
import pandas as pd
import osmnx as ox

# loading the spatial datasets (city polygon, routes layer, drawing h3 hexagons)
moscow = ox.geocode_to_gdf('Москва', which_result=2) # Old Moscow + New Moscow polygon
routes = gpd.read_file("geodata/cycling_routes.geojson")
moscow_hex = moscow.h3.polyfill_resample(9)
moscow_hex = moscow_hex.reset_index()
moscow_hex = moscow_hex[['h3_polyfill', 'geometry']]

# spatial join for routes and hexagons
sjoin = moscow_hex.sjoin(routes, how='left')
sjoin = sjoin[['h3_polyfill', 'activity_id']]
sjoin = pd.pivot_table(sjoin, values ='activity_id', index='h3_polyfill', aggfunc='count')
sjoin = sjoin.reset_index()
moscow_hex = moscow_hex.merge(sjoin, how='left', on=['h3_polyfill'])

# function to colorize hexagons based on aggregated value
def colorcode(x):
    if x == 0:
        return 'whitesmoke'
    elif x == 1:
        return 'lightgray'
    elif x in [2,3]:
        return 'sandybrown'
    elif x in range(4,21):
        return 'chocolate'
    else:
        return 'darkred'

# display the map
import folium
import branca
m = folium.Map([moscow.centroid.y, moscow.centroid.x], tiles='cartodbpositron')

# Leaflet map manual legend addition sourced from here https://nbviewer.org/gist/talbertc-usgs/18f8901fc98f109f2b71156cf3ac81cd
from branca.element import Template, MacroElement
template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Number of cycling visits per Hexangon (h3:9)</div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:darkred;opacity:0.7;'></span>Very Often (> 20 times)</li>
    <li><span style='background:chocolate;opacity:0.7;'></span>Often (4-20 times)</li>
    <li><span style='background:sandybrown;opacity:0.7;'></span>Rarely (2-3 times)</li>
    <li><span style='background:lightgray;opacity:0.7;'></span>Very Rarely (1 time)</li>
    <li><span style='background:whitesmoke;opacity:0.7;'></span>Never (0 time)</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)


folium.GeoJson(moscow_hex, 
               style_function=lambda x:{'fillColor': colorcode(x['properties']['activity_id']),
                                       'color': colorcode(x['properties']['activity_id'])}).add_to(m)
folium.FitBounds([[moscow.bounds.miny[0], moscow.bounds.minx[0]],[moscow.bounds.maxy[0], moscow.bounds.maxx[0]]]).add_to(m)
m