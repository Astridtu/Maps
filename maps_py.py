# -*- coding: utf-8 -*-
"""Maps.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/gist/Astridtu/85fab87d27c3ebd9ffa99f77780b2e62/untitled0.ipynb
"""

import folium
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
import ee
from google.colab import auth
from google.colab import files
files.download('requirements.txt')

# Create and save requirements.txt in Colab environment
with open('requirements.txt', 'w') as f:
    f.write('streamlit\n')
    f.write('folium\n')
    f.write('pandas\n')
    f.write('geopy\n')
    f.write('earthengine-api\n')
    f.write('streamlit-folium\n')

# Verify the file is created
!cat requirements.txt


# Authenticate and initialize Earth Engine
auth.authenticate_user()
ee.Initialize(project='otgongunj')

# Define the mining locations data (International)
mining_data = pd.DataFrame({
    'name': ['Kounrad', 'Aktogai', 'Kal’makyr', 'Oyu Tolgoi', 'Chalukou'],
    'latitude': [49.8000, 48.2217, 40.8000, 43.0183, 49.3000],
    'longitude': [73.1170, 82.6681, 70.2000, 106.8626, 120.8000],
    'country': ['Kazakhstan', 'Kazakhstan', 'Uzbekistan', 'Mongolia', 'China'],
    'resource': ['Cu', 'Cu', 'Cu', 'Cu-Au', 'Cu-Mo']
})

# Define Mongolian provinces data with their coordinates and resources
mongolian_provinces = pd.DataFrame({
    'province_name': ['Ulaanbaatar', 'Bulgan', 'Darkhan-Uul', 'Dornod', 'Davaa', 'Selenge', 'Khentii', 'Orkhon', 'Uvurkhangai', 'Dundgovi', 'Govi-Altai', 'Khovd', 'Bayankhongor', 'Zavkhan', 'Sukhbaatar', 'Uvs'],
    'latitude': [47.8864, 49.0511, 49.4753, 43.4361, 43.7020, 49.2161, 46.9461, 49.2982, 44.0553, 42.9344, 46.1000, 48.5152, 43.5847, 48.0353, 48.1571, 48.1503],
    'longitude': [106.9057, 104.3195, 105.9400, 113.1573, 103.9627, 105.5850, 110.3269, 105.4542, 102.8340, 104.0352, 91.8000, 91.7111, 100.0000, 91.0907, 92.0786, 92.2406],
    'mining_name': ['Oyu Tolgoi', 'Erdenet', 'Asgat', 'Tsagaan Suvarga', 'Tavan Tolgoi', 'Nariin Sukhait', 'Shuteen', 'Burenkhaan', 'Zuun Mod', 'Bayan Airag', 'Altan Tsagaan Ovoo', 'Tsenkher', 'Shariin Gol', 'Mandal Khairkhan', 'Bordkhonin', 'Tsav'],
    'resource': ['Cu-Au', 'Cu-Mo', 'Ag', 'Cu-Mo', 'Coal', 'Coal', 'Cu', 'Cu', 'Mo', 'Cu-Au', 'Mo', 'Cu', 'Cu', 'Au', 'Mo', 'Cu']
})

# Initialize a folium map centered on Central Asia
m = folium.Map(location=[45, 85], zoom_start=4)

# Add markers for each mining location (international)
for i, row in mining_data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(f"<b>Name:</b> {row['name']}<br>"
                           f"<b>Country:</b> {row['country']}<br>"
                           f"<b>Resource:</b> {row['resource']}", max_width=250),
        tooltip=row['name'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Add markers for each Mongolian province and associated mining locations with resources
for i, row in mongolian_provinces.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(f"<b>Province:</b> {row['province_name']}<br>"
                           f"<b>Mining Name:</b> {row['mining_name']}<br>"
                           f"<b>Resource:</b> {row['resource']}", max_width=200),
        tooltip=f"{row['province_name']} ({row['mining_name']} - {row['resource']})",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# Define a function to add Earth Engine layers to folium
def add_ee_layer(self, ee_object, vis_params, name):
    try:
        tiles = ee_object.getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=tiles['tile_fetcher'].url_format,
            attr='Google Earth Engine',
            name=name,
            overlay=True,
            control=True
        ).add_to(self)
    except Exception as e:
        print(f"Could not display {name}: {e}")

# Add EE drawing method to folium
folium.Map.add_ee_layer = add_ee_layer

# Add a satellite imagery layer from Earth Engine
# Use a global mosaic of Sentinel-2 imagery
sentinel2 = ee.ImageCollection('COPERNICUS/S2') \
    .filterDate('2020-06-01', '2020-09-30') \
    .filterBounds(ee.Geometry.Point([85, 45])) \
    .median() \
    .visualize(min=0, max=3000, bands=['B4', 'B3', 'B2'])

# Add the Sentinel-2 image to the map
m.add_ee_layer(sentinel2, {}, 'Sentinel-2 Imagery')

# Add a layer control panel
m.add_child(folium.LayerControl())

# Display the map
m