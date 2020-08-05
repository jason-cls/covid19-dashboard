from geojson_rewind import rewind
import json
import pandas as pd
import os


def get_data():
    df_can, df_world = process_data()

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
    for region in pd.unique(df_can['prname']):
        if region != 'Canada':
            df_region = df_can.loc[df_can['prname'] == region]
            df_timeorder = df_timeorder.merge(df_region, on='date', how='outer', suffixes=[None, '_' + region])

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
            map_info_world['Country'].append(
                df_loc['location'].values[-1])  # index latest value (already sorted by date)
            map_info_world['Total Cases'].append(df_loc['total_cases'].values[-1])
            map_info_world['Death Toll'].append(df_loc['total_deaths'].values[-1])
            map_info_world['Test Count'].append(df_loc['total_tests'].values[-1])

    df_map_world = pd.DataFrame(map_info_world)
    world_locations = list(pd.unique(df_world['location']))

    # Timeseries data
    df_timeorder_world = df_world.loc[df_world['location'] == 'World']
    for loc in pd.unique(df_world['location']):
        if loc != 'World':
            df_country = df_world.loc[df_world['location'] == loc]
            df_timeorder_world = df_timeorder_world.merge(df_country, on='date', how='outer',
                                                          suffixes=[None, '_' + loc])

    return df_can, df_map_CA, df_timeorder, jdataNo, df_world, df_map_world, df_timeorder_world, world_locations


def process_data():
    # ### Canada COVID data processing ####
    url = 'https://health-infobase.canada.ca/src/data/covidLive/covid19.csv'
    response_CA = pd.read_csv(url)

    response_CA = response_CA.drop(columns=['pruid', 'prnameFR', 'percentoday',
                                            'ratetested', 'ratetotal', 'ratedeaths',
                                            'percentdeath', 'percentactive', 'numtotal_last14',
                                            'ratetotal_last14', 'numdeaths_last14', 'ratedeaths_last14'])

    response_CA['date'] = pd.to_datetime(response_CA['date'], dayfirst=True)
    response_CA = response_CA.sort_values(by=['prname', 'date'])

    # Impute missing values
    provinces = response_CA['prname'].value_counts().index
    impute_cols = ['numdeaths', 'numtested', 'numdeathstoday',
                   'numtestedtoday', 'numrecoveredtoday', 'numrecover', 'percentrecover']

    for p in provinces:
        for colname in impute_cols:
            response_CA.loc[response_CA['prname'] == p, colname] = response_CA.loc[
                response_CA['prname'] == p, colname].ffill().fillna(0)

    # ### World COVID data processing ####
    url_world = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
    response_world = pd.read_csv(url_world)

    # Drop unneeded info
    response_world = response_world.drop(
        columns=['new_tests_smoothed', 'new_tests_smoothed_per_thousand', 'tests_units',
                 'stringency_index', 'population', 'population_density', 'median_age',
                 'aged_65_older', 'aged_70_older', 'gdp_per_capita', 'extreme_poverty',
                 'cardiovasc_death_rate', 'diabetes_prevalence', 'female_smokers',
                 'male_smokers', 'handwashing_facilities', 'life_expectancy']
    )

    response_world = response_world.loc[response_world['location'] != 'International']
    response_world['date'] = pd.to_datetime(response_world['date'], yearfirst=True)
    response_world = response_world.sort_values(by=['location', 'date'])

    # Impute missing values
    locations = pd.unique(response_world['location'])
    impute_cols = ['new_tests', 'total_tests', 'total_tests_per_thousand', 'new_tests_per_thousand']

    for loc in locations:
        for colname in impute_cols:
            response_world.loc[response_world['location'] == loc, colname] = \
                response_world.loc[response_world['location'] == loc, colname].ffill()

    return response_CA, response_world