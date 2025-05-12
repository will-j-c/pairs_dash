import csv
from pprint import pprint
import hashlib
import hmac
import base64
import urllib.parse
from dash import no_update
import plotly.express as px

def create_entries_list():
    entries = []
    with open('config/config.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # skip the first row
            if row[0] == 'pair_name':
                continue

            # Add the row to the entries
            entries.append(row)
    entries = sorted(entries, key=lambda entry: int(entry[5]), reverse=True)
    return entries

def create_unique_entries_list(entries):
    unique_entries = [entries[0]]
    for row in entries[1:]:
        pairs_1 = [entry[1] for entry in unique_entries]
        pairs_2 = [entry[2] for entry in unique_entries]
        if row[1] not in pairs_1 and row[1] not in pairs_2 and row[2] not in pairs_1 and row[2] not in pairs_2:
            unique_entries.append(row)
    return unique_entries


def create_config_dict():
    config_dict = {}
    entries = create_entries_list()
    unique_entries = create_unique_entries_list(entries)
    for entry in unique_entries:
        config_dict[entry[0]] = {
        'pair_1': f'PF_{entry[1]}',
        'pair_2': f'PF_{entry[2]}',
        'beta': float(entry[4]),
        'high_sigma': int(entry[6]),
        'low_sigma': int(entry[7]),
        'lag': int(entry[8])
        }
    return config_dict

def create_post_data(data):
    return urllib.parse.urlencode(data)


def authentication_function(post_data, endpoint, api_secret):

    # concatenate post data and enpoint
    concatenated_string = (post_data + endpoint)

    # hash the output
    sha256_hash_result = hashlib.sha256(
        concatenated_string.encode('utf8')).digest()

    # base decode the api secret
    decoded_api_seccret = base64.b64decode(api_secret)

    # use decoded secret as key for hmac
    hmac_sha512 = hmac.new(decoded_api_seccret,
                           sha256_hash_result, hashlib.sha512).digest()
    APISign = base64.b64encode(hmac_sha512).decode()

    return APISign


def get_headers(api_key, authent):
    return {
        'Accept': 'application/json',
        'APIKey': api_key,
        'Authent': authent
    }

def update_memory_store_value(value, data_call, config):
     entry = config[value]
     df = data_call.create_pair_data(entry['pair_1'], entry['pair_2'], '1h', entry['beta'], 'trade', entry['lag'])
     return df.to_dict('records')

def stop_string(data_call):
    stop_loss =  data_call.get_collateral_value() * 0.02
    string = '{0:.2f}'.format(-stop_loss)
    return string

def cash_string(data_call):
    cash =  data_call.get_collateral_value()
    string = '{0:.2f}'.format(cash)
    return string

def update_spread_fig(df, data_call):
    if df is None:
        return no_update

    x_axis_labels = list(data_call.create_axis_from_df(df))
    fig = px.line(df, x='time', y='spread', title='spread')
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), title=None, font_family='Arial, Helvetica, sans-serif')
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
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), font_family='Arial, Helvetica, sans-serif')
    fig.update_traces(line_color='red', line_width=2)
    fig.update_xaxes(title='Z',  fixedrange=True, range=[x_axis_labels[0], x_axis_labels[-1]])
    fig.update_yaxes(side='right', title=None, fixedrange=True)
    return fig

if __name__ == '__main__':
    pprint(create_config_dict())