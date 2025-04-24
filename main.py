# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import dash_auth
import pandas as pd
from data import Data
from layout import radio_items, table, radio_card, pill, selection
from helper import create_config_dict, update_memory_store_value, stop_string, update_spread_fig, update_z_fig, cash_string

load_dotenv(override=True)

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

VALID_USERNAME_PASSWORD_PAIRS = {
    username: password
}

data = Data()
config = create_config_dict()
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

server = app.server

radio_controls = [
                radio_items('Pairs', 'pairs-selection',sorted(list(config.keys())), sorted(list(config.keys()))[0]),
                radio_items('Time View', 'time-view', [72, 144, 216, 288, 360], 216),
            ]

app.layout = [dbc.Container(
    [
        dcc.Store(id='memory-output'),
        dbc.Row([
            dbc.Col([dcc.Graph(id='graph-spread', config=dict(displayModeBar=False,  showAxisDragHandles=False))], lg=9),
            dbc.Col([radio_card(config)], lg=3),
        ], className='mt-3'),
        dbc.Row([
            dbc.Col([dcc.Graph(id='graph-z', config=dict(displayModeBar=False))], lg=9),
            dbc.Col(selection(sorted(list(config.keys()))[0], config), lg=3, id='selection'),
        ], className='mt-1'),
        dbc.Row([
            dbc.Col([
                pill('Cash', cash_string(data), 'cash')
            ], lg=2),
            dbc.Col([
                pill('Stop Loss', stop_string(data), 'stop')
            ], lg=2)
            
        ], justify='center', className='mt-1'),
        dbc.Row([
            dbc.Col([
                table(data, config)
            ], lg=6)
            
        ], justify='center', className='mt-3'),
    ], className='mh-100', fluid=True
),

dcc.Interval(id='interval-graph', interval=20000, n_intervals=0),
dcc.Interval(id='interval-stop', interval=5000, n_intervals=0)]


# Callback fro the memory store
@callback(
        Output('memory-output', 'data'),
        Input('pairs-selection', 'value'),
        Input('interval-graph', 'n_intervals')
)
def update_memory_store(pairs, n_intervals):
    return update_memory_store_value(pairs, data, config)

# Callbacks for updating spread graph
@callback(
    Output('graph-spread', 'figure'),
    Input('memory-output', 'data'),
    Input('time-view', 'value'),
)
def update_spread_graph(records, timeview):
    df = pd.DataFrame(records)
    df = df.tail(timeview)
    return update_spread_fig(df, data)

# Callbacks for updating z graph
@callback(
    Output('graph-z', 'figure'),
    Input('memory-output', 'data'),
    Input('time-view', 'value'),
)
def update_z_graph(records, timeview):
    df = pd.DataFrame(records)
    df = df.tail(timeview)
    pairs = df.columns[0][8:-3] + '/' + df.columns[1][8:-3]
    entry = config[pairs]
    return update_z_fig(df, data, entry['high_sigma'], entry['low_sigma'])

# Callbacks for table
@callback(
    Output('table', 'data'),
    Input('interval-stop', 'n_intervals'),
)
def update_table(n_intervals):
    df = data.get_position_info(config)
    return df.to_dict('records')

# Callback for stop
@callback(
    Output('stop', 'children'),
    Input('interval-stop', 'n_intervals'),
)
def update_stop(n_intervals):
    return stop_string(data)

# Callback for cash
@callback(
    Output('cash', 'children'),
    Input('interval-stop', 'n_intervals'),
)
def update_stop(n_intervals):
    return cash_string(data)

# Callback for settings
@callback(
    Output('selection', 'children'),
    Input('pairs-selection', 'value'),
)
def update_settings(value):
    return selection(value, config)

if __name__ == '__main__':
    app.run(debug=True)
