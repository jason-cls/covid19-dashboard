import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64
import flask
import numpy as np
import pandas as pd
import plotly.express as px
from random import randint
import os
import json
from collect.collect import pull_db_data
from geojson_rewind import rewind
import pymongo


external_stylesheets = [dbc.themes.LUX,
                        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.2/css/font-awesome.min.css"]

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.config['suppress_callback_exceptions'] = True
app.title = 'COVID-19 Dashboard'

svg_file = os.path.join(os.getcwd(), 'misc', 'github.svg')
encoded = base64.b64encode(open(svg_file, 'rb').read())
github_svg = 'data:image/svg+xml;base64,{}'.format(encoded.decode())

connectionURL = os.getenv('MONGO_URL').strip("\"")
db_client = pymongo.MongoClient(connectionURL)

# Process geodata for Canada choropleth map
path_geo_ca = os.path.join(os.getcwd(), 'data', 'ca_geodata', 'canada-geo-simple.json')
with open(path_geo_ca) as geofile:
    jdataNo = json.load(geofile)

jdataNo = rewind(jdataNo, rfc7946=False)  # geojson formatting
for k in range(len(jdataNo['features'])):
    jdataNo['features'][k]['properties']['id'] = k  # assign province ID

# Initialize global variables
df_can, df_map_CA, df_timeorder, df_world, df_map_world, df_timeorder_world, lastUpdate_utc = pull_db_data(db_client)

world_locations = list(pd.unique(df_world['location']))

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

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.H3('Overview of Canada')
                ]
            ),
            dbc.Col(
                [
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
        style={'margin-bottom': 10, 'margin-top': 20}
    ),

    dbc.Row([
        html.Div(
            [
                dbc.Col(
                    dcc.Graph(id='choropleth-map', clear_on_unhover=True),
                    width=12
                )
            ],
            style={'width': '100%', 'margin-bottom': 5, 'margin-top': 5}
        )
    ]),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                html.H3('COVID-19 Canadian Timeline'),
                width=9
            ),
            dbc.Col(
                html.Div(
                    [
                        dcc.RadioItems(
                            id='yaxis-scale',
                            options=[
                                {'label': ' Linear   ', 'value': 'Linear'},
                                {'label': ' Log', 'value': 'log'}
                            ],
                            value='Linear',
                            labelStyle={'display': 'block'}
                        )
                    ],
                    style={'text-align': 'left'}
                ),
                width=3
            )
        ]
    ),

    dbc.Row(
        html.Div(
            [
                dbc.Col(
                    dcc.Graph(id='timeseries', responsive=True),
                    width=12
                )
            ],
            style={'width': '100%', 'height': '100%', 'margin-bottom': 50}
        )
    ),

])

tab_world = html.Div([
    dbc.Row(
        dbc.Col(
            [
                dbc.CardGroup(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2(id='case-count-country', className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.H5("cases today", className="card-title", style={'font-weight': 'bold',
                                                                                          'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-cases-country',
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
                                    html.H2(id='death-count-country', className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.H5("deaths today", className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-deaths-country',
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
                                    html.H2(id='test-count-country', className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.H5("individuals tested today", className="card-title",
                                            style={'font-weight': 'bold', 'text-align': 'center'}),
                                    html.Br(),
                                    html.P(
                                        id='total-tests-country',
                                        className="card-text"
                                    )
                                ]
                            ),
                            color='info',
                            inverse=True
                        )
                    ]
                )
            ],
            width=12
        ),
        style={'margin-top': 15}
    ),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.H3('Global Overview')
                ]
            ),
            dbc.Col(
                [
                    dcc.Dropdown(
                        id='world-stat-dropdown',
                        options=[
                            {'label': 'Total Cases', 'value': 'numtotalWorld'},
                            {'label': 'Total Deaths', 'value': 'numdeathsWorld'},
                            {'label': 'Individuals Tested', 'value': 'numtestedWorld'}
                        ],
                        value='numtotalWorld'
                    )
                ],
                width=4
            ),
        ],
        style={'margin-bottom': 10, 'margin-top': 20}
    ),

    dbc.Row([
        html.Div(
            [
                dbc.Col(
                    dcc.Graph(id='choropleth-map-world', clear_on_unhover=True),
                    width=12
                )
            ],
            style={'width': '100%', 'margin-bottom': 5, 'margin-top': 5}
        )
    ]),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                html.H3('COVID-19 Global Timeline'),
                width=10
            ),

            dbc.Col(
                html.Div(
                    [
                        dcc.RadioItems(
                            id='yaxis-scale-world-timeline',
                            options=[
                                {'label': ' Linear   ', 'value': 'Linear'},
                                {'label': ' Log', 'value': 'log'}
                            ],
                            value='Linear',
                            labelStyle={'display': 'block'}
                        )
                    ],
                    style={'text-align': 'left'}
                ),
                width=2
            )
        ]
    ),

    dbc.Row(
        dbc.Col(
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': loc, 'value': loc} for loc in world_locations],
                value=['World', 'United States', 'Canada', 'China', 'United Kingdom',
                       'Italy', 'Russia', 'South Korea', 'Japan'],
                multi=True
            )
        ),
        style={'margin-bottom': 15}
    ),

    dbc.Row(
        html.Div(
            [
                dbc.Col(
                    dcc.Graph(id='timeseries-world', responsive=True),
                    width=12
                )
            ],
            style={'width': '100%', 'height': '100%', 'margin-bottom': 50}
        )
    ),
])


def serve_layout():
    # Update latest data on refresh
    df_can, df_map_CA, df_timeorder, df_world, df_map_world, df_timeorder_world, lastUpdate_utc = pull_db_data(db_client)
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1('COVID-19 Dashboard'),
                            html.P(['Last Update: ' + lastUpdate_utc['utc_datetime'] + ' UTC',
                                    html.A(dbc.Button([html.Img(src=github_svg, height='20'), " Follow @jason-cls"],
                                                      color="light", size="sm", style={'margin-left': 10, 'margin-bottom': 0}),
                                           href="https://github.com/jason-cls", target="_blank")
                                    ]),
                        ],

                        width=6
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Tabs(id='tabs-granular', value='tab-ca', children=[
                                dcc.Tab(label='Canada', value='tab-ca'),
                                dcc.Tab(label='World', value='tab-int')
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


app.layout = serve_layout


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-granular', 'value')])
def render_tab_content(tab):
    if tab == 'tab-ca':
        return tab_canada
    elif tab == 'tab-int':
        return tab_world


# ------------------------- CANADA ------------------------------
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

    case_count = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numtoday'].values[-1]))
    death_count = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numdeathstoday'].values[-1]))
    test_count = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numtestedtoday'].values[-1]))
    recovery_count = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numrecoveredtoday'].values[-1]))

    total_cases = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numtotal'].values[-1]))
    total_deaths = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numdeaths'].values[-1]))
    total_tests = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numtested'].values[-1]))
    total_recoveries = '{:,}'.format(int(df_can.loc[df_can['prname'] == region_name, 'numrecover'].values[-1]))

    total_cases_region = [total_cases + " total cases in ", html.Br(), region_name]
    total_deaths_region = [total_deaths + " total deaths in ", html.Br(), region_name]
    total_tests_region = [total_tests + " total tested in ", html.Br(), region_name]
    total_recoveries_region = [total_recoveries + " total recoveries in ", html.Br(), region_name]

    return (case_count, total_cases_region, death_count, total_deaths_region, test_count, total_tests_region,
            recovery_count, total_recoveries_region)


@app.callback([Output('choropleth-map', 'figure'),
               Output('timeseries', 'figure')],
              [Input('stat-dropdown', 'value'),
               Input('yaxis-scale', 'value')])
def render_plots_canada(dropdown, yaxis_scale):
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
            color_continuous_scale='reds',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':,0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Total Cases']), axis=-1),
            hovertemplate=hovertemplate
        )
        renamed_timeorder = df_timeorder.rename(
            columns={'numtotal': 'Canada',
                     'numtotal_Alberta': 'Alberta',
                     'numtotal_British Columbia': 'British Columbia',
                     'numtotal_Manitoba': 'Manitoba',
                     'numtotal_New Brunswick': 'New Brunswick',
                     'numtotal_Newfoundland and Labrador': 'Newfoundland and Labrador',
                     'numtotal_Northwest Territories': 'Northwest Territories',
                     'numtotal_Nova Scotia': 'Nova Scotia',
                     'numtotal_Nunavut': 'Nunavut',
                     'numtotal_Ontario': 'Ontario',
                     'numtotal_Prince Edward Island': 'Prince Edward Island',
                     'numtotal_Quebec': 'Quebec',
                     'numtotal_Repatriated travellers': 'Repatriated travellers',
                     'numtotal_Saskatchewan': 'Saskatchewan',
                     'numtotal_Yukon': 'Yukon'}
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            y=['Canada', 'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
               'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec',
               'Repatriated travellers', 'Saskatchewan', 'Yukon'],
            labels={
                'date': 'Date',
                'value': 'Total Cases',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
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
            color_continuous_scale='reds',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':,0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Death Toll']), axis=-1),
            hovertemplate=hovertemplate
        )
        renamed_timeorder = df_timeorder.rename(
            columns={'numdeaths': 'Canada',
                     'numdeaths_Alberta': 'Alberta',
                     'numdeaths_British Columbia': 'British Columbia',
                     'numdeaths_Manitoba': 'Manitoba',
                     'numdeaths_New Brunswick': 'New Brunswick',
                     'numdeaths_Newfoundland and Labrador': 'Newfoundland and Labrador',
                     'numdeaths_Northwest Territories': 'Northwest Territories',
                     'numdeaths_Nova Scotia': 'Nova Scotia',
                     'numdeaths_Nunavut': 'Nunavut',
                     'numdeaths_Ontario': 'Ontario',
                     'numdeaths_Prince Edward Island': 'Prince Edward Island',
                     'numdeaths_Quebec': 'Quebec',
                     'numdeaths_Repatriated travellers': 'Repatriated travellers',
                     'numdeaths_Saskatchewan': 'Saskatchewan',
                     'numdeaths_Yukon': 'Yukon'}
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            y=['Canada', 'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
               'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec',
               'Repatriated travellers', 'Saskatchewan', 'Yukon'],
            labels={
                'date': 'Date',
                'value': 'Total Deaths',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
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
            color_continuous_scale='reds',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':,0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Test Count']), axis=-1),
            hovertemplate=hovertemplate
        )
        renamed_timeorder = df_timeorder.rename(
            columns={'numtested': 'Canada',
                     'numtested_Alberta': 'Alberta',
                     'numtested_British Columbia': 'British Columbia',
                     'numtested_Manitoba': 'Manitoba',
                     'numtested_New Brunswick': 'New Brunswick',
                     'numtested_Newfoundland and Labrador': 'Newfoundland and Labrador',
                     'numtested_Northwest Territories': 'Northwest Territories',
                     'numtested_Nova Scotia': 'Nova Scotia',
                     'numtested_Nunavut': 'Nunavut',
                     'numtested_Ontario': 'Ontario',
                     'numtested_Prince Edward Island': 'Prince Edward Island',
                     'numtested_Quebec': 'Quebec',
                     'numtested_Repatriated travellers': 'Repatriated travellers',
                     'numtested_Saskatchewan': 'Saskatchewan',
                     'numtested_Yukon': 'Yukon'}
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            y=['Canada', 'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
               'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec',
               'Repatriated travellers', 'Saskatchewan', 'Yukon'],
            labels={
                'date': 'Date',
                'value': 'Individuals Tested',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
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
            color_continuous_scale='reds',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':,0f'},
            zoom=2.5
        )
        fig_choropleth.update_traces(
            customdata=np.stack((df_map_CA['province'], df_map_CA['Recovery Count']), axis=-1),
            hovertemplate=hovertemplate
        )
        renamed_timeorder = df_timeorder.rename(
            columns={'numrecover': 'Canada',
                     'numrecover_Alberta': 'Alberta',
                     'numrecover_British Columbia': 'British Columbia',
                     'numrecover_Manitoba': 'Manitoba',
                     'numrecover_New Brunswick': 'New Brunswick',
                     'numrecover_Newfoundland and Labrador': 'Newfoundland and Labrador',
                     'numrecover_Northwest Territories': 'Northwest Territories',
                     'numrecover_Nova Scotia': 'Nova Scotia',
                     'numrecover_Nunavut': 'Nunavut',
                     'numrecover_Ontario': 'Ontario',
                     'numrecover_Prince Edward Island': 'Prince Edward Island',
                     'numrecover_Quebec': 'Quebec',
                     'numrecover_Repatriated travellers': 'Repatriated travellers',
                     'numrecover_Saskatchewan': 'Saskatchewan',
                     'numrecover_Yukon': 'Yukon'}
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            y=['Canada', 'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
               'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec',
               'Repatriated travellers', 'Saskatchewan', 'Yukon'],
            labels={
                'date': 'Date',
                'value': 'Cases Recovered',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
        )
    fig_choropleth.update_layout(margin={'r': 0, 'l': 0, 'b': 0, 't': 0})
    fig_ts.update_layout(margin={'r': 0, 'l': 0, 'b': 30, 't': 0},
                         legend_title_text=None)
    fig_ts.update_yaxes(type='linear' if yaxis_scale == 'Linear' else 'log')
    fig_ts.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig_choropleth, fig_ts


# ------------------------- WORLD ------------------------------
@app.callback([Output('case-count-country', 'children'),
               Output('total-cases-country', 'children'),
               Output('death-count-country', 'children'),
               Output('total-deaths-country', 'children'),
               Output('test-count-country', 'children'),
               Output('total-tests-country', 'children')],
              [Input('choropleth-map-world', 'hoverData')])
def show_daily_counts_world(hoverData):
    if hoverData:
        region_name = hoverData['points'][0]['hovertext']
    else:
        region_name = 'World'

    try:
        case_count = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'new_cases'].values[-1]))
    except (ValueError, IndexError):
        case_count = 'N/A'
    try:
        death_count = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'new_deaths'].values[-1]))
    except (ValueError, IndexError):
        death_count = 'N/A'
    try:
        test_count = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'new_tests'].values[-1]))
    except (ValueError, IndexError):
        test_count = 'N/A'

    try:
        total_cases = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'total_cases'].values[-1]))
    except (ValueError, IndexError):
        total_cases = 'N/A'
    try:
        total_deaths = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'total_deaths'].values[-1]))
    except (ValueError, IndexError):
        total_deaths = 'N/A'
    try:
        total_tests = '{:,}'.format(int(df_world.loc[df_world['location'] == region_name, 'total_tests'].values[-1]))
    except (ValueError, IndexError):
        total_tests = 'N/A'

    total_cases_country = [total_cases + " total cases in ", html.Br(), region_name]
    total_deaths_country = [total_deaths + " total deaths in ", html.Br(), region_name]
    total_tests_country = [total_tests + " total tested in ", html.Br(), region_name]

    return case_count, total_cases_country, death_count, total_deaths_country, test_count, total_tests_country


@app.callback([Output('choropleth-map-world', 'figure'),
               Output('timeseries-world', 'figure')],
              [Input('world-stat-dropdown', 'value'),
               Input('yaxis-scale-world-timeline', 'value'),
               Input('country-dropdown', 'value')])
def render_plots_world(dropdown, yaxis_scale, locations):
    fig_choropleth = px.choropleth_mapbox()
    world_removed = False
    if 'World' in locations:
        locations.remove('World')
        world_removed = True
    if dropdown == 'numtotalWorld':
        fig_choropleth = px.choropleth(
            df_map_world,
            color='Total Cases',
            locations='iso_code',
            locationmode='ISO-3',
            scope='world',
            hover_name='Country',
            hover_data={'iso_code': False, 'Total Cases': ':,0f'}
        )
        rename_map = {'total_cases_' + loc: loc for loc in locations}
        rename_map['total_cases'] = 'World'
        renamed_timeorder = df_timeorder_world.rename(
            columns=rename_map
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            y=['World'] + locations if world_removed else locations,
            labels={
                'date': 'Date',
                'value': 'Total Cases',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
        )
    elif dropdown == 'numdeathsWorld':
        fig_choropleth = px.choropleth(
            df_map_world,
            color='Death Toll',
            locations='iso_code',
            locationmode='ISO-3',
            scope='world',
            hover_name='Country',
            hover_data={'iso_code': False, 'Death Toll': ':,0f'}
        )
        rename_map = {'total_deaths_' + loc: loc for loc in locations}
        rename_map['total_deaths'] = 'World'
        renamed_timeorder = df_timeorder_world.rename(
            columns=rename_map
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            # y=['World']+locations,
            y=['World'] + locations if world_removed else locations,
            labels={
                'date': 'Date',
                'value': 'Total Deaths',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
        )
    elif dropdown == 'numtestedWorld':
        fig_choropleth = px.choropleth(
            df_map_world,
            color='Test Count',
            locations='iso_code',
            locationmode='ISO-3',
            scope='world',
            hover_name='Country',
            hover_data={'iso_code': False, 'Test Count': ':,0f'}
        )
        rename_map = {'total_tests_' + loc: loc for loc in locations}
        rename_map['total_tests'] = 'World'
        renamed_timeorder = df_timeorder_world.rename(
            columns=rename_map
        )
        fig_ts = px.line(
            renamed_timeorder, x='date',
            # y=['World']+locations,
            y=['World'] + locations if world_removed else locations,
            labels={
                'date': 'Date',
                'value': 'Individuals Tested',
                'variable': ' '
            },
            color_discrete_sequence=px.colors.qualitative.Light24,
            hover_name='variable',
            hover_data={'variable': False, 'value': ':,0f'}
        )
    fig_choropleth.update_layout(margin={'r': 0, 'l': 0, 'b': 0, 't': 0})
    fig_ts.update_layout(margin={'r': 0, 'l': 0, 'b': 30, 't': 0},
                         legend_title_text=None)
    fig_ts.update_yaxes(type='linear' if yaxis_scale == 'Linear' else 'log')
    fig_ts.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig_choropleth, fig_ts


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=False, port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
