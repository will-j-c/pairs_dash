from dash import Dash, dcc, html, callback, Output, Input, dash_table

def radio_items(title, id, options, value):
    buttons = html.Div([
        html.H6(title),
        dcc.RadioItems(options, value, id=id)
    ])
    return buttons


def table(data, config):
    df = data.get_position_info(config)
    table = dash_table.DataTable(df.to_dict('records'), 
                                 columns=[{'name': i, 'id': i} for i in df.columns],
                                 editable=False,
                                 id='table',
                                 style_cell={'textAlign': 'left'}
                                 )
    
    return html.Div([table])

def stop_string(data):
    stop_loss =  data.get_collateral_value() * 0.02
    string = '{0:.2f}'.format(-stop_loss)
    return 'Stop loss at: ' + string