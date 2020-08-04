import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from app import df_world

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

world_locations = list(pd.unique(df_world['location']))

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
