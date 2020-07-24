import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os


external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

path_ca = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
df_can = pd.read_csv(path_ca)

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
                            dcc.Tab(label='International', value='tab-int'),
                            dcc.Tab(label='Ontario', value='tab-on')
                        ]),
                    ),
                    width=6,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id='tabs-content'),
                    width=3
                )
            ]
        )
    ]
)


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-granular', 'value')])
def render_tab_content(tab):
    if tab == 'tab-ca':
        return html.Div([
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
        ])
    elif tab == 'tab-int':
        return html.Div([
            html.P('PLACEHOLDER TEXT WORLD')
        ])
    elif tab == 'tab-on':
        return html.Div([
            html.P('PLACEHOLDER TEXT ONTARIO')
        ])


if __name__ == '__main__':
    app.run_server(debug=True)