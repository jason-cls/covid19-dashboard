import pandas as pd
import os

#### Canada COVID data processing ####
path_canada = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
url = 'https://health-infobase.canada.ca/src/data/covidLive/covid19.csv'
response = pd.read_csv(url)

response = response.drop(columns=['pruid', 'prnameFR', 'percentoday',
                                  'ratetested', 'ratetotal', 'ratedeaths',
                                  'percentdeath', 'percentactive','numtotal_last14',
                                  'ratetotal_last14', 'numdeaths_last14', 'ratedeaths_last14'])

response['date'] = pd.to_datetime(response['date'], dayfirst=True)
response = response.sort_values(by=['prname', 'date'])

# Impute missing values
provinces = response['prname'].value_counts().index
impute_cols = ['numdeaths', 'numtested', 'deathstoday',
               'testedtoday', 'recoveredtoday', 'numrecover', 'percentrecover']

for p in provinces:
    for colname in impute_cols:
        response.loc[response['prname'] == p, colname] = response.loc[response['prname'] == p, colname].ffill().fillna(0)

# Save data
response.to_csv(path_canada, index=False)


#### World COVID data processing ####
path_world = os.path.join(os.getcwd(), 'data', 'covid19world.csv')
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

response_world['date'] = pd.to_datetime(response_world['date'], yearfirst=True)
response_world = response_world.sort_values(by=['location', 'date'])
# Save data
response_world.to_csv(path_world, index=False)
