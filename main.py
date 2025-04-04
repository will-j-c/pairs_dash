from dash import Dash, dcc, html, callback, Output, Input, clientside_callback
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from data import Data
from config import config

data = Data()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    html.Div(
        [
            html.Div(
                [
                    dcc.RadioItems(list(config.keys()), list(
                        config.keys())[0], id='radio-selection'),
                    dcc.RadioItems([72, 144, 216], 216, id='time_view'),
                    dcc.RadioItems([24, 48, 72, 96, 120, 144], 144, id='lag'),
                    dcc.RadioItems(['mark', 'spot', 'trade'],
                                   'trade', id='ticker_type'),
                ],
                style={'textAlign': 'left',
                       'display': 'flex',
                       'justify-content': 'space-evenly',
                       'align-items': 'flex-start'
                       },
            ),
            dcc.Graph(id='graph-spread', responsive=True, style={'height': '80vh'})],
        # style={'display': 'flex',
        #        'flex-direction': 'column',
        #        'align-items': 'center'
        #        },
    ),
    dcc.Interval(id='interval', interval=30000, n_intervals=0)
], style={'margin-top': 20})


@callback(
    Output('graph-spread', 'figure'),
    Input('radio-selection', 'value'),
    Input('interval', 'n_intervals'),
    Input('time_view', 'value'),
    Input('lag', 'value'),
    Input('ticker_type', 'value'),
)
def update_graph(value, n_intervals, interval, lag, ticker_type):
    return update_pairs(value, interval, lag, ticker_type)


def update_pairs(value, interval, lag, ticker_type):
    entry = config[value]
    dff = data.create_pair_data(
        entry['pair_1'], entry['pair_2'], '1h', entry['beta'], interval, ticker_type, lag)
    x_axis_labels = list(data.create_axis_from_df(dff))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05)
    fig.add_scatter(x=dff.index, y=dff['spread'],
                    row=1, col=1, showlegend=False, name='spread')
    fig.add_scatter(x=dff.index, y=dff['robust'],
                    row=2, col=1, showlegend=False, name='robust')
    fig.add_hline(0, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(2, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-2, row=2, col=1, line_dash='dash', line_color='grey')
    fig.update_xaxes(range=[x_axis_labels[0], x_axis_labels[-1]])
    return fig


if __name__ == '__main__':
    app.run(debug=True)
