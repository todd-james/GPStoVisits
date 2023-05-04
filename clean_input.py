# BW GPS Data Cleaning 
# Prep for Gibbs/lachesis visit detection 
# Remove all unnecessary columns, reformat time/coordinates, remove column headings
# James Todd - Apr '23

import sys
import pandas as pd 
import pyproj
import numpy as np

# Set Directories
input_file = sys.argv[1]
output_file = sys.argv[2]

# Load in Data
data = pd.read_csv(input_file,  names=['uuid', 'datetime', 'lat', 'long', 'accuracy'], usecols=[0,2,3,4,5] )

# Remove points with low accuracy (more than 100m)
data = data[data['accuracy'] < 100]

# Transform coodinates to JGD2011 / Japan Plan Rectangular CS IX (EPSG:6677)
wgs2jdg = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:6677")
data['y'], data['x'] = wgs2jdg.transform(data['lat'] , data['long'])

# Subset the data
data = data[['uuid', 'datetime', 'x', 'y']]

# Remove Inf values from data 
data = data.replace([np.inf, -np.inf], np.nan).dropna()

# Write the CSV
data.to_csv(output_file, header=False, index=False)