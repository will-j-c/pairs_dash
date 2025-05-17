from dash import Input, Output, dcc
import dash_bootstrap_components as dbc

from server import app

layout = dbc.Container([
    dcc.Location(id='url_index', refresh=True),
    dbc.Button('Go to login', id='link-button')
])


@app.callback(Output('url_index', 'pathname'),
              Input('link-button', 'n_clicks'))

def redirect(n_clicks):
    if n_clicks:
        return '/login'