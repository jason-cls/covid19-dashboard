#### Canada COVID data processing ####
import pandas as pd
import os


path_canada = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
url = 'https://health-infobase.canada.ca/src/data/covidLive/covid19.csv'
response = pd.read_csv(url)

# - `pruid`: province id
# - **`prname`: (English )province name
# - `prnameFR`: (French) province name
# - **`date`: date reported
# - **`numconf`: number of confirmed cases
# - **`numprob`: number of probable cases
# - **`numdeaths`: number of deaths
# - **`numtotal`: total # of confirmed and probable cases
# - **`numtested`: number of people tested
# - **`numrecover`: number of people recovered
# - **`percentrecover`: numrecover / numtotal
# - `ratetested`:
# - **`numtoday`: number of new cases relative to yesterday
# - `percentoday`:  percent change of new cases relative to yesterday
# - `ratetotal`:
# - `ratedeaths`:
# - **`deathstoday`: number of deaths reported today
# - `percentdeath`:
# - **`testedtoday`: number of people tested today
# - `recoveredtoday`: number of people who have recovered today
# - `percentactive`:

response = response.drop(columns=['pruid', 'prnameFR', 'percentoday',
                                  'ratetested', 'ratetotal', 'ratedeaths',
                                  'percentdeath', 'percentactive'])

response['date'] = pd.to_datetime(response['date'], dayfirst=True)
response = response.sort_values(by=['prname', 'date'])

# Impute missing values
provinces = response['prname'].value_counts().index
impute_cols = ['numdeaths', 'numtested', 'deathstoday',
               'testedtoday', 'recoveredtoday', 'numrecover', 'percentrecover']

for p in provinces:
    for colname in impute_cols:
        response.loc[response['prname'] == p, colname] = response.loc[response['prname'] == p, colname].ffill().fillna(0)

# Save local copy
response.to_csv(path_canada, index=False)
