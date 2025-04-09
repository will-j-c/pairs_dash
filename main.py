from dash import Dash, dcc, html, callback, Output, Input, clientside_callback
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from data import Data
from helper import create_config_dict

data = Data()
config = create_config_dict()
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

def radio_items(title, id, options, value):
    buttons = html.Div([
        html.H6(title),
        dcc.RadioItems(options, value, id=id)
    ])
    return buttons

app.layout = dbc.Container([
    html.Div(
        [
            html.Div(
                [
                    radio_items('Pairs', 'radio-selection', sorted(list(config.keys())), sorted(list(config.keys()))[0]),
                    radio_items('Time View', 'time_view', [72, 144, 216, 288, 360], 216),
                    radio_items('Robust Spread Lag', 'lag', [24, 48, 72, 96, 120, 144, 168, 192], 144),
                    radio_items('Ticker Type', 'ticker_type', ['mark', 'spot', 'trade'], 'trade'),
                    radio_items('Resolution', 'resolution', ['15m', '30m', '1h', '4h', '12h', '1d'], '1h')
                ],
                style={'textAlign': 'left',
                       'display': 'flex',
                       'justify-content': 'space-evenly',
                       'align-items': 'flex-start',
                       'font-size': '0.75em',
                       },
            ),
            dcc.Graph(id='graph-spread', responsive=True, style={'height': '70vh'})],
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
    Input('resolution', 'value'),
)
def update_graph(value, n_intervals, interval, lag, ticker_type, resolution):
    return update_pairs(value, interval, lag, ticker_type, resolution, sigma)


def update_pairs(value, interval, lag, ticker_type, resolution):
    entry = config[value]
    dff = data.create_pair_data(
        entry['pair_1'], entry['pair_2'], resolution, entry['beta'], interval, ticker_type, lag)
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
    fig.add_hline(3, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-3, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(1, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-1, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(1.5, row=2, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-1.5, row=2, col=1, line_dash='dash', line_color='grey')
    fig.update_xaxes(range=[x_axis_labels[0], x_axis_labels[-1]])
    fig.update_layout(title_text=f'Pair: {value}, Time View: {interval}, Spread Lag: {lag}, Resolution: {resolution}', title_font={'size': 20, 'weight': 600})
    return fig



if __name__ == '__main__':
    app.run(debug=True)
