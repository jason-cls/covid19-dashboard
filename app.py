import dash
import dash_bootstrap_components as dbc
from geojson_rewind import rewind
import json
import pandas as pd
import os

external_stylesheets = [dbc.themes.LUX,
                        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.2/css/font-awesome.min.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'COVID-19 Dashboard'

path_ca = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
df_can = pd.read_csv(path_ca, parse_dates=['date'])

# Process geodata for Canada choropleth map
path_geo_ca = os.path.join(os.getcwd(), 'data', 'ca_geodata', 'canada-geo-simple.json')
with open(path_geo_ca) as geofile:
    jdataNo = json.load(geofile)

jdataNo = rewind(jdataNo, rfc7946=False)  # geojson formatting

map_info_CA = {
    'pr-id': [],
    'province': [],
    'Total Cases': [],
    'Death Toll': [],
    'Test Count': [],
    'Recovery Count': []
}
for k in range(len(jdataNo['features'])):
    jdataNo['features'][k]['properties']['id'] = k
    name = jdataNo['features'][k]['properties']['NAME_1']
    if name.startswith('Qu'):
        name = 'Quebec'  # Remove french accents in text
    map_info_CA['pr-id'].append(k)
    map_info_CA['province'].append(name)
    df_pr = df_can.loc[df_can['prname'] == name]
    map_info_CA['Total Cases'].append(df_pr['numtotal'].values[-1])  # index latest value (already sorted by date)
    map_info_CA['Death Toll'].append(df_pr['numdeaths'].values[-1])
    map_info_CA['Test Count'].append(df_pr['numtested'].values[-1])
    map_info_CA['Recovery Count'].append(df_pr['numrecover'].values[-1])

df_map_CA = pd.DataFrame(map_info_CA)

# Timeseries data
df_timeorder = df_can.loc[df_can['prname'] == 'Canada']
last_loc = 'Canada'
for region in pd.unique(df_can['prname']):
    if region != 'Canada':
        df_region = df_can.loc[df_can['prname'] == region]
        df_timeorder = df_timeorder.merge(df_region, on='date', how='outer', suffixes=[None, '_' + region])
        last_loc = region


#### World Geo Data ####
path_world = os.path.join(os.getcwd(), 'data', 'covid19world.csv')
df_world = pd.read_csv(path_world, parse_dates=['date'])

map_info_world = {
    'iso_code': [],
    'Country': [],
    'Total Cases': [],
    'Death Toll': [],
    'Test Count': []
}

for iso in pd.unique(df_world['iso_code']):
    if iso != 'OWID_WRL':
        map_info_world['iso_code'].append(iso)
        df_loc = df_world.loc[df_world['iso_code'] == iso]
        map_info_world['Country'].append(df_loc['location'].values[-1])  # index latest value (already sorted by date)
        map_info_world['Total Cases'].append(df_loc['total_cases'].values[-1])
        map_info_world['Death Toll'].append(df_loc['total_deaths'].values[-1])
        map_info_world['Test Count'].append(df_loc['total_tests'].values[-1])

df_map_world = pd.DataFrame(map_info_world)

# Timeseries data
df_timeorder_world = df_world.loc[df_world['location'] == 'World']
last_loc = 'World'
for loc in pd.unique(df_world['location']):
    if loc != 'World':
        df_country = df_world.loc[df_world['location'] == loc]
        df_timeorder_world = df_timeorder_world.merge(df_country, on='date', how='outer', suffixes=[None, '_' + loc])
        last_loc = loc
