import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
import callbacks


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

if __name__ == '__main__':
    app.run_server(debug=True)
