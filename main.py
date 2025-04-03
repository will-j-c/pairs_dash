from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from data import Data
from config import config

data = Data()

app = Dash()

app.layout = [
    dcc.RadioItems(list(config.keys()), list(
        config.keys())[0], id='radio-selection'),
    dcc.Dropdown([72, 144, 216], 72, id='dropdown'),
    dcc.Graph(id='graph-spread', responsive=True,
              style={'width': '90vh', 'height': '80vh'}),
    dcc.Interval(id='interval', interval=30000, n_intervals=0)
]

@callback(
    Output('graph-spread', 'figure'),
    Input('radio-selection', 'value'),
    Input('interval', 'n_intervals'),
    Input('dropdown', 'value')
)
def update_graph(value, n_intervals, interval):
    return update_pairs(value, interval)


def update_pairs(value, interval):
    entry = config[value]
    dff = data.create_pair_data(entry['pair_1'], entry['pair_2'], '1h', entry['beta'], interval, 'mark', entry['lag'])
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    fig.add_scatter(x=dff.index, y=dff['spread'],
                    row=1, col=1, showlegend=False, name='spread')
    fig.add_scatter(x=dff.index, y=dff['robust'],
                    row=2, col=1, showlegend=False, name='robust')
    fig.add_hline(0, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(2, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-2, row=2, col=1, line_dash='dash', line_color='grey')
    return fig


if __name__ == '__main__':
    app.run(debug=True)
