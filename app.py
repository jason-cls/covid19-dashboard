import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from geojson_rewind import rewind
import numpy as np
import json
import plotly.express as px
import pandas as pd
import os

external_stylesheets = [dbc.themes.LUX,
                        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.2/css/font-awesome.min.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'COVID-19 Dashboard'

path_ca = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
df_can = pd.read_csv(path_ca)

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
    'Recovery Count': [],
    # 'Cases Today': [],
    # 'Deaths Today': [],
    # 'Tested Today': []
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
    # map_info_CA['Cases Today'].append(df_pr['numtoday'].values[-1])
    # map_info_CA['Deaths Today'].append(df_pr['deathstoday'].values[-1])
    # map_info_CA['Tested Today'].append(df_pr['testedtoday'].values[-1])

df_map_CA = pd.DataFrame(map_info_CA)

tab_canada = html.Div([
    dbc.Row(
        dbc.Col(
            [
                dbc.CardGroup(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2(id='case-count', className="card-title", style={'font-weight': 'bold',
                                                                                            'text-align': 'center'}),
                                    html.H5("cases", className="card-title", style={'font-weight': 'bold',
                                                                                    'text-align': 'center',
                                                                                    'margin-bottom': 0}),
                                    html.H5("today", className="card-title", style={'font-weight': 'bold',
                                                                                    'text-align': 'center'
                                                                                    }),
                                    html.Br(),
                                    html.P(
                                        id='total-cases-region',
                                        className="card-text"
                                    )
                                ]
                            ),
                            color='warning',
                            inverse=True
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2(id='death-count', className="card-title", style={'font-weight': 'bold',
                                                                                             'text-align': 'center'}),
                                    html.H5("deaths ", className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center',
                                                   'margin-bottom': 0}),
                                    html.H5("today", className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-deaths-region',
                                        className="card-text"
                                    )
                                ]
                            ),
                            color='danger',
                            inverse=True
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2(id='test-count', className="card-title", style={'font-weight': 'bold',
                                                                                            'text-align': 'center'}),
                                    html.H5("individuals tested today", className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-tests-region',
                                        className="card-text"
                                    )
                                ]
                            ),
                            color='info',
                            inverse=True
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2(id='recover-count', className="card-title", style={'font-weight': 'bold',
                                                                                               'text-align': 'center'}),
                                    html.H5("total recoveries today",
                                            className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-recoveries-region',
                                        className="card-text"
                                    )
                                ]
                            ),
                            color='success',
                            inverse=True
                        )
                    ]
                )
            ],
            width=12
        ),
        style={'margin-top': 15}
    ),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.Br(),
                    dcc.Dropdown(
                        id='stat-dropdown',
                        options=[
                            {'label': 'Total Cases', 'value': 'numtotal'},
                            {'label': 'Total Deaths', 'value': 'numdeaths'},
                            {'label': 'Individuals Tested', 'value': 'numtested'},
                            {'label': 'Cases Recovered', 'value': 'numrecovered'}
                        ],
                        value='numtotal'
                    )
                ],
                width=4
            ),
        ],
        style={'margin-bottom': 10}
    ),

    dbc.Row(
        html.Div(
            [
                dbc.Col(
                    dcc.Graph(id='choropleth-map', responsive=True, clear_on_unhover=True),
                    width=12
                )
            ],
            style={'width': '100%'}
        )
    )
])

tab_world = html.Div([
    html.P('PLACEHOLDER TEXT WORLD')
])

tab_ontario = html.Div([
    html.P('PLACEHOLDER TEXT ONTARIO')
])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1('COVID-19 Dashboard'),
                    width=6
                ),
                dbc.Col(
                    html.Div(
                        dcc.Tabs(id='tabs-granular', value='tab-ca', children=[
                            dcc.Tab(label='Canada', value='tab-ca'),
                            dcc.Tab(label='World', value='tab-int'),
                            dcc.Tab(label='Ontario', value='tab-on')
                        ]),
                    ),
                    width=6,
                    align='end'
                )
            ],
            style={'margin-top': 15}
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id='tabs-content'),
                    width=12
                )
            ],
            style={'margin-top': 15}
        )
    ]
)


@app.callback([Output('case-count', 'children'),
               Output('total-cases-region', 'children'),
               Output('death-count', 'children'),
               Output('total-deaths-region', 'children'),
               Output('test-count', 'children'),
               Output('total-tests-region', 'children'),
               Output('recover-count', 'children'),
               Output('total-recoveries-region', 'children')],
              [Input('choropleth-map', 'hoverData')])
def show_daily_counts(hoverData):
    if hoverData:
        region_name = hoverData['points'][0]['customdata'][0]
    else:
        region_name = 'Canada'

    case_count = str(int(df_can.loc[df_can['prname'] == region_name, 'numtoday'].values[-1]))
    death_count = str(int(df_can.loc[df_can['prname'] == region_name, 'deathstoday'].values[-1]))
    test_count = str(int(df_can.loc[df_can['prname'] == region_name, 'testedtoday'].values[-1]))
    recovery_count = str(int(df_can.loc[df_can['prname'] == region_name, 'recoveredtoday'].values[-1]))

    total_cases = str(df_can.loc[df_can['prname'] == region_name, 'numtotal'].values[-1])
    total_deaths = str(int(df_can.loc[df_can['prname'] == region_name, 'numdeaths'].values[-1]))
    total_tests = str(int(df_can.loc[df_can['prname'] == region_name, 'numtested'].values[-1]))
    total_recoveries = str(int(df_can.loc[df_can['prname'] == region_name, 'numrecover'].values[-1]))

    total_cases_region = [total_cases + " total cases in ", html.Br(), region_name]
    total_deaths_region = [total_deaths + " total deaths in ", html.Br(), region_name]
    total_tests_region = [total_tests + " total tested in ", html.Br(), region_name]
    total_recoveries_region = [total_recoveries + " total recoveries in ", html.Br(), region_name]

    return (case_count, total_cases_region, death_count, total_deaths_region, test_count, total_tests_region,
            recovery_count, total_recoveries_region)


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-granular', 'value')])
def render_tab_content(tab):
    if tab == 'tab-ca':
        return tab_canada
    elif tab == 'tab-int':
        return tab_world
    elif tab == 'tab-on':
        return tab_ontario


@app.callback(Output('choropleth-map', 'figure'),
              [Input('stat-dropdown', 'value')])
def render_map_canada(dropdown):
    hovertemplate = (
            "<b>%{customdata[0]}</b><br>" +
            "Count: %{customdata[1]}"
    )
    fig_choropleth = px.choropleth_mapbox()
    if dropdown == 'numtotal':
        fig_choropleth = px.choropleth_mapbox(
            df_map_CA,
            geojson=jdataNo,
            featureidkey='properties.id',
            locations='pr-id',
            color='Total Cases',
            center={"lat": 59, "lon": -95.34},
            mapbox_style='carto-positron',
            color_continuous_scale='emrld',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':.0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Total Cases']), axis=-1),
            hovertemplate=hovertemplate
        )
    elif dropdown == 'numdeaths':
        fig_choropleth = px.choropleth_mapbox(
            df_map_CA,
            geojson=jdataNo,
            featureidkey='properties.id',
            locations='pr-id',
            color='Death Toll',
            center={"lat": 59, "lon": -95.34},
            mapbox_style='carto-positron',
            color_continuous_scale='emrld',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':.0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Death Toll']), axis=-1),
            hovertemplate=hovertemplate
        )
    elif dropdown == 'numtested':
        fig_choropleth = px.choropleth_mapbox(
            df_map_CA,
            geojson=jdataNo,
            featureidkey='properties.id',
            locations='pr-id',
            color='Test Count',
            center={"lat": 59, "lon": -95.34},
            mapbox_style='carto-positron',
            color_continuous_scale='emrld',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':.0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Test Count']), axis=-1),
            hovertemplate=hovertemplate
        )
    elif dropdown == 'numrecovered':
        fig_choropleth = px.choropleth_mapbox(
            df_map_CA,
            geojson=jdataNo,
            featureidkey='properties.id',
            locations='pr-id',
            color='Recovery Count',
            center={"lat": 59, "lon": -95.34},
            mapbox_style='carto-positron',
            color_continuous_scale='emrld',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':.0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Recovery Count']), axis=-1),
            hovertemplate=hovertemplate
        )
    fig_choropleth.update_layout(margin={'r': 0, 'l': 0, 'b': 0, 't': 0})
    return fig_choropleth


if __name__ == '__main__':
    app.run_server(debug=True)
