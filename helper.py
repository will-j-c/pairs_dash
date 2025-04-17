import csv
from pprint import pprint
import hashlib
import hmac
import base64
import urllib.parse

def create_entries_list():
    entries = []
    with open('results.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # skip the first row
            if row[0] == 'pair_name':
                continue

            # Add the row to the entries
            entries.append(row)

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

def update_memory_store_value(value, lag, ticker_type, data_call, config):
     entry = config[value]
     df = data_call.create_pair_data(entry['pair_1'], entry['pair_2'], '1h', entry['beta'], ticker_type, lag)
     return df.to_dict('records')



if __name__ == '__main__':
    pprint(create_config_dict())