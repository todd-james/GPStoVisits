# BW GPS Data Cleaning 
# Cleaning Gibbs Lachesis Output 
# Reformat Coordinates, Duration in Minutes, Remove Columns 
# James Todd - Apr '23

import sys
import pandas as pd
import pyproj
import geopandas as gpd 
from shapely.geometry import Point

input_file = sys.argv[1]
cleaned_visits = sys.argv[2]
hourly_user_mesh = sys.argv[3]

# Load in Data
try: 
    data = pd.read_csv(input_file)
except pd.errors.EmptyDataError: 
    #If input data is empty then touch output files 
    open(cleaned_visits, 'w').close()
    open(hourly_user_mesh, 'w').close()
    exit()

# Transform coodinates to JGD2011 EPSG:6677
jdg2wgs = pyproj.Transformer.from_crs("EPSG:6677","EPSG:4326")
data['lat'], data['long'] = jdg2wgs.transform(data['y'], data['x'])

# Get Duration in Minutes
data['duration'] = data['duration']/60

# Remove Columns
data = data[['id', 'start', 'end', 'duration', 'long', 'lat']]
data = data.rename(columns ={'id': 'uuid'})

# Write the cleaned vists to CSV
data.to_csv(cleaned_visits, index=False)

grid6 = gpd.read_file("/Volumes/kyotogps-db/meshall/GRID6.shp").to_crs('EPSG:4326')

data_geom = [Point(xy) for xy in zip(data['long'], data['lat'])]

data_points = gpd.GeoDataFrame(data, crs='EPSG:4326', geometry=data_geom)

joined = gpd.sjoin(data_points, grid6, how = 'left', op = 'within')

joined = joined.drop(['geometry',  'index_right',  'OBJECTID',  'GRID_LEVEL', 'Shape_Leng', 'Shape_Area', 'mesh6'], axis = 1).dropna(subset=['GRID_CODE'])

# Convert the start and end columns to datetime format
joined['start'] = pd.to_datetime(joined['start'])
joined['end'] = pd.to_datetime(joined['end'])

# Create a new dataframe to store the hourly data
HUM = pd.DataFrame()

for index, row in joined.iterrows():
    # Round start and end times to the nearest hour
    start_hour = row['start'].floor('H')
    end_hour = row['end'].ceil('H')

    # Generate a range of hourly timestamps for this row
    hourly_range = pd.date_range(start=start_hour, end=end_hour, freq='H')

    # Calculate the duration in each hour
    total_duration = row['duration']
    hour_durations = []
    for i in range(len(hourly_range)-1):
        duration = (min(hourly_range[i+1], row['end']) - max(hourly_range[i], row['start'])).seconds // 60
        hour_durations.append(duration)

    # Create a new dataframe for this row
    uuid_df = pd.DataFrame({'uuid': row['uuid'], 'GRID_CODE': row['GRID_CODE'], 'time': hourly_range[:-1], 'duration': hour_durations, 'total_duration': [total_duration] * len(hour_durations)})

    # Append this dataframe to the HUM
    HUM = pd.concat([HUM, uuid_df])

HUM.to_csv(hourly_user_mesh, index = False, header = False)