from dash import Dash, dcc, html, callback, Output, Input, dash_table
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from data import Data
from helper import create_config_dict
from dotenv import load_dotenv
import os
import dash_auth

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

def radio_items(title, id, options, value):
    buttons = html.Div([
        html.H6(title),
        dcc.RadioItems(options, value, id=id)
    ])
    return buttons


def table():
    df = data.get_position_info(config)
    table = dash_table.DataTable(df.to_dict('records'), 
                                 columns=[{'name': i, 'id': i} for i in df.columns],
                                 editable=False,
                                 id='table',
                                 style_cell={'textAlign': 'left'}
                                 )
    
    return html.Div([table])

def stop_string():
    stop_loss =  data.get_collateral_value() * 0.02
    string = '{0:.2f}'.format(-stop_loss)
    return 'Stop loss at: ' + string

app.layout = dbc.Container([
    html.Div(
        [
            html.Div(
                [
                    radio_items('Pairs', 'radio-selection',
                                sorted(list(config.keys())), sorted(list(config.keys()))[0]),
                    radio_items('Time View', 'time_view', [
                                72, 144, 216, 288, 360], 216),
                    radio_items('Lag', 'lag', [
                                24, 48, 72, 96, 120, 144, 168, 192], 144),
                    radio_items('Ticker Type', 'ticker_type', [
                                'mark', 'spot', 'trade'], 'trade'),
                    radio_items('Resolution', 'resolution', [
                                '15m', '30m', '1h', '4h', '12h', '1d'], '1h')
                ],
                style={'textAlign': 'left',
                       'display': 'flex',
                       'justify-content': 'space-evenly',
                       'align-items': 'flex-start',
                       'font-size': '0.75em',
                       },
            ),
            dcc.Graph(id='graph-spread', responsive=True,
                      style={'height': '65vh'}),
            html.H4(stop_string(), id='stop'),
            table()], 
    ),

    dcc.Interval(id='interval', interval=30000, n_intervals=0),
    dcc.Interval(id='interval2', interval=10000, n_intervals=0)
], style={'margin-top': 20, 'height': '100vh'})


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
    return update_pairs(value, interval, lag, ticker_type, resolution)


@callback(
    Output('table', 'data'),
    Input('interval2', 'n_intervals'),
)
def update_table(n_intervals):
    df = data.get_position_info(config)
    return df.to_dict('records')

@callback(
    Output('stop', 'children'),
    Input('interval2', 'n_intervals'),
)
def update_stop(n_intervals):
    return stop_string()

def update_pairs(value, interval, lag, ticker_type, resolution):
    entry = config[value]
    dff = data.create_pair_data(
        entry['pair_1'], entry['pair_2'], resolution, entry['beta'], interval, ticker_type, lag)
    x_axis_labels = list(data.create_axis_from_df(dff))
    fig = make_subplots(rows=3, cols=1, shared_xaxes=False,
                        vertical_spacing=0.05)
    # Add the lines
    fig.add_scatter(x=dff.index, y=dff['spread'],
                    row=2, col=1, showlegend=True, name='spread')
    fig.add_scatter(x=dff.index, y=dff['z'],
                    row=1, col=1, showlegend=True, name='z')
    fig.add_scatter(x=dff.index, y=dff['robust'],
                    row=1, col=1, showlegend=True, name='robust')

    # Add the horizontal lines
    fig.add_hline(0, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(2, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-2, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(3, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-3, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(1, row=1, col=1, line_dash='dash', line_color='grey')
    fig.add_hline(-1, row=1, col=1, line_dash='dash', line_color='grey')

    fig.update_xaxes(range=[x_axis_labels[0], x_axis_labels[-1]])
    fig.update_layout(title_text=f'Pair: {value}, Time View: {interval}, Spread Lag: {lag}, Resolution: {resolution}', title_font={
                      'size': 20, 'weight': 600})
    return fig


if __name__ == '__main__':
    app.run(debug=True)
