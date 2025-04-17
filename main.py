from dash import Dash, dcc, html, callback, Output, Input
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
                radio_items('Lag', 'lag', [192, 216, 240, 312], 312),
                radio_items('Ticker Type', 'ticker_type', ['mark', 'spot', 'trade'], 'trade'),
            ]

app.layout = [html.Div(
    [
        dcc.Store(id='memory-output'),
        html.Div(
            [
                html.Div(radio_controls, className='radio-div'),
                html.Div([
                    dcc.Graph(id='graph-spread', responsive=False),
                    dcc.Graph(id='graph-z', responsive=False),
                ], 
                className='graph-div')
            ],
            className='centre-div'
        ),
        html.H4(stop_string(data), id='stop'),
        table(data, config)
    ], className='main-div'
),

dcc.Interval(id='interval-graph', interval=30000, n_intervals=0),
dcc.Interval(id='interval-stop', interval=10000, n_intervals=0)]


# Callback fro the memory store
@callback(
        Output('memory-output', 'data'),
        Input('pairs-selection', 'value'),
        Input('lag', 'value'),
        Input('ticker_type', 'value'),
)
def update_memory_store(pairs, lag, ticker_type):
    return update_memory_store_value(pairs, lag, ticker_type, data, config)

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
def update_spread_graph(records, timeview):
    df = pd.DataFrame(records)
    df = df.tail(timeview)
    return update_z_fig(df, data)

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
