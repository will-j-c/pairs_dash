from dash import dcc, html, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dash_table.Format import Format


def radio_items(title, id, options, value):
    buttons = html.Div([
        html.H6(title),
        dcc.RadioItems(options, value, id=id)
    ])
    return buttons


def table(data_call, config):
    df = data_call.get_position_info(config)
    columns = [
        {'name': 'Position', 'id': 'Position'},
        {'name': 'Entry', 'id': 'Entry'},
        {'name': 'Entry Side', 'id': 'Entry Side'},
        {'name': 'P&L', 'id': 'P&L'},
        {'name': 'Est. Fee', 'id': 'Est. Fee'},
        {'name': 'Net P&L', 'id': 'Net P&L'},
    ]
    table = dash_table.DataTable(data=df.to_dict('records'),
                                 columns=columns,
                                 editable=False,
                                 id='table',
                                 style_cell={'textAlign': 'center'},
                                 style_header={'fontWeight': 'bolder'},
                                 style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Position'},
                                        'textAlign': 'left'
                                    },
                                ],
                                    style_data_conditional=[
                                    {
                                        'if': {
                                            'filter_query': '{P&L} > 0',
                                            'column_id': 'P&L'
                                        },
                                        'color': 'green'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{P&L} < 0',
                                            'column_id': 'P&L'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Net P&L} > 0',
                                            'column_id': 'Net P&L'
                                        },
                                        'color': 'green'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Net P&L} < 0',
                                            'column_id': 'Net P&L'
                                        },
                                        'color': 'red'
                                    },
                                ]
    )
    return html.Div([table])


def pill(title, value, id):
    card = dbc.Card([
        dbc.CardHeader([title], className='fw-bolder'),
        dbc.CardBody([
            value
        ], id=id)
    ], className='text-center')
    return card


def selection(pairs, config):
    entry = config[pairs]
    card = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(['Pairs: ']),
                dbc.Col(pairs)
            ]),
            dbc.Row([
                dbc.Col(['Beta: ']),
                dbc.Col(round(entry['beta'], 4))
            ]),
            dbc.Row([
                dbc.Col(['High: ']),
                dbc.Col(entry['high_sigma'])
            ]),
            dbc.Row([
                dbc.Col(['Low: ']),
                dbc.Col(entry['low_sigma'])
            ]),
            dbc.Row([
                dbc.Col(['Lag: ']),
                dbc.Col(entry['lag'])
            ]),
        ], className='fs-6')
    ], className='mt-3')
    return card


def radio_card(config):
    card = dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    'Pairs'
                ]),
                dbc.Col([
                    'View'
                ], width=4)
            ], className='fw-bolder')
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(sorted(list(config.keys())), sorted(
                        list(config.keys()))[0], id='pairs-selection'),
                ]),
                dbc.Col([
                    dcc.RadioItems([72, 144, 216, 288, 360, 480, 600],
                                   216, id='time-view')
                ], width=4, className='fs-6')
            ])
        ])], className='mt-3')
    return card
