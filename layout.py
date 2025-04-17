from dash import Dash, dcc, html, dash_table, no_update
import plotly.express as px
import pandas as pd

def radio_items(title, id, options, value):
    buttons = html.Div([
        html.H6(title),
        dcc.RadioItems(options, value, id=id)
    ])
    return buttons


def table(data_call, config):
    df = data_call.get_position_info(config)
    table = dash_table.DataTable(df.to_dict('records'), 
                                 columns=[{'name': i, 'id': i} for i in df.columns],
                                 editable=False,
                                 id='table',
                                 style_cell={'textAlign': 'left'}
                                 )
    
    return html.Div([table])

def stop_string(data_Call):
    stop_loss =  data_Call.get_collateral_value() * 0.02
    string = '{0:.2f}'.format(-stop_loss)
    return 'Stop loss at: ' + string



def update_spread_fig(df, data_call):
    if df is None:
        return no_update

    x_axis_labels = list(data_call.create_axis_from_df(df))
    fig = px.line(df, x='time', y='spread', title='spread')
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), title=None)
    fig.update_traces(line_color='blue', line_width=2)
    fig.update_xaxes(title='Spread', fixedrange=True, range=[x_axis_labels[0], x_axis_labels[-1]])
    fig.update_yaxes(side='right', title=None, fixedrange=True)
    return fig

def update_z_fig(df, data_call, high_sigma=2, low_sigma=-2):
    if df is None:
        return no_update
    
    x_axis_labels = list(data_call.create_axis_from_df(df))
    fig = px.line(df,  x='time', y='z', title=None)
    fig.add_hline(y=high_sigma, line_color='grey', opacity=0.75, line_dash='dash')
    fig.add_hline(y=low_sigma,  line_color='grey', opacity=0.75, line_dash='dash')
    fig.add_hline(y=0,  line_color='grey', opacity=0.75, line_dash='dash')
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_traces(line_color='red', line_width=2)
    fig.update_xaxes(title='Z',  fixedrange=True, range=[x_axis_labels[0], x_axis_labels[-1]])
    fig.update_yaxes(side='right', title=None, fixedrange=True)
    return fig