import csv
from pprint import pprint

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

if __name__ == '__main__':
    pprint(create_config_dict())