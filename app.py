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
                    dcc.Graph(id='choropleth-map',  clear_on_unhover=True),
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
                html.H3('COVID-19 Timeline'),
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
            color_continuous_scale='emrld',
            hover_name='province',
            hover_data={'pr-id': False, 'Total Cases': ':.0f'},
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
            hover_data={'variable': False, 'value': ':.0f'}
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
            hover_data={'variable': False, 'value': ':.0f'}
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
            hover_data={'variable': False, 'value': ':.0f'}
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
            hover_data={'variable': False, 'value': ':.0f'}
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
