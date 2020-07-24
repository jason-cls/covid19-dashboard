import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

path_ca = os.path.join(os.getcwd(), 'data', 'covid19canada.csv')
df_can = pd.read_csv(path_ca)

app.layout = html.Div([
    html.H1('COVID-19 Dashboard '),

    dcc.Tabs(id='tabs-granular', value='tab-ca', children=[
        dcc.Tab(label='Canada', value='tab-ca'),
        dcc.Tab(label='International', value='tab-int'),
        dcc.Tab(label='Ontario', value='tab-on')
    ]),

    html.Div(id='tabs-content')


])


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