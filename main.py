from dash import Dash, dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import dash_auth
import pandas as pd
from data import Data
from layout import radio_items, table, stop_string, update_spread_fig, update_z_fig
from helper import create_config_dict, update_memory_store_value

load_dotenv(override=True)

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

VALID_USERNAME_PASSWORD_PAIRS = {
    username: password
}

data = Data()
config = create_config_dict()
app = Dash()
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

server = app.server

radio_controls = [
                radio_items('Pairs', 'pairs-selection',sorted(list(config.keys())), sorted(list(config.keys()))[0]),
                radio_items('Time View', 'time-view', [72, 144, 216, 288, 360], 216),
            ]

app.layout = [dbc.Container(
    [
        dcc.Store(id='memory-output'),
        html.Div(
            [
                html.Div([
                    dcc.Graph(id='graph-spread', config=dict(displayModeBar=False,  showAxisDragHandles=False), responsive=True),
                    html.Div(radio_controls, id='radio-div')
                    ],
                    className='row-div'),
                html.Div([
                    dcc.Graph(id='graph-z', config=dict(displayModeBar=False)),
                ], 
                className='row-div')
            ],
            id='centre-div'
        ),
        html.H6(stop_string(data), id='stop'),
        table(data, config)
    ], id='main-div'
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

# Callbacks for stop and table
@callback(
    Output('table', 'data'),
    Input('interval-stop', 'n_intervals'),
)
def update_table(n_intervals):
    df = data.get_position_info(config)
    return df.to_dict('records')


@callback(
    Output('stop', 'children'),
    Input('interval-stop', 'n_intervals'),
)
def update_stop(n_intervals):
    return stop_string(data)


if __name__ == '__main__':
    app.run(debug=True)
