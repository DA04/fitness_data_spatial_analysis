# Coordinates conversion
# Source for conversion rate https://gis.stackexchange.com/questions/122186/convert-garmin-or-iphone-weird-gps-coordinates/368905#368905

# import modules
import psycopg2
import pandas as pd

# create a new dataframe for the activity
activity_id = 100007015961
conn = psycopg2.connect(host="localhost", database="garmin_data", user="postgres", password="*****")
df = pd.read_sql_query("""select * from session
where activity_id ={}""".format(activity_id), conn)

# conversion rate
c_value = 1/((2**32) / 360)

# convert coordinates to new columns
df['start_latitude'] = df.start_position_lat*c_value
df['start_longitude'] = df.start_position_long*c_value
df['nec_latitude'] = df.nec_lat*c_value
df['nec_longitude'] = df.nec_long*c_value
df['swc_latitude'] = df.swc_lat*c_value
df['swc_longitude'] = df.swc_long*c_value