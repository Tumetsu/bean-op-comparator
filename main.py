import subprocess
import csv
from io import StringIO


def read_beancount_ledger(file_path, start_date, end_date):
    result = subprocess.run(['bean-query', '-f', 'csv', file_path, 'select date, narration, account, position where account ~ ".:Käyttötili" and date >= {} and date <= {};'.format(start_date, end_date)], stdout=subprocess.PIPE)
    reader = csv.DictReader(StringIO(result.stdout.decode('utf-8')))

    contents = [row for row in reader]
    for row in contents:
        row['position'] = float(row['position'].replace('EUR', '').strip())

    return contents


def read_op_ledger(file_path):
    parsed = []
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            parsed.append({
                'date': row['Kirjauspäivä'],
                'position': float(row['Määrä\xa0 EUROA'].replace(',', '.')),
                'narration': row['Saaja/Maksaja']

            })

    return parsed


ledger_log = read_beancount_ledger('~/ledger/ledger.beancount', '2019-01-01', '2019-01-31')
op_log = read_op_ledger('./sample_data/op_ledger.csv')


