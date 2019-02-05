import subprocess
import csv
from tabulate import tabulate
from io import StringIO


def read_beancount_ledger(file_path, start_date, end_date):
    result = subprocess.run(['bean-query', '-f', 'csv', file_path, 'select date, narration, account, position where account ~ ".:Käyttötili" and date >= {} and date <= {};'.format(start_date, end_date)], stdout=subprocess.PIPE)
    reader = csv.DictReader(StringIO(result.stdout.decode('utf-8')))

    contents = [row for row in reader]
    for row in contents:
        row['position'] = float(row['position'].replace('EUR', '').strip())
        row['position_int'] = int(row['position'] * 100)

    return contents


def read_op_ledger(file_path):
    parsed = []
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            position = float(row['Määrä\xa0 EUROA'].replace(',', '.'))
            parsed.append({
                'date': row['Kirjauspäivä'],
                'position': position,
                'position_int': int(position * 100),
                'narration': row['Saaja/Maksaja']
            })

    return parsed


def find_matching_entry_from(ledger, entry):
    """
    Try to find a matching entry from the provided ledger. The algorithm is *really* naive. It considers any
    transaction with same price as a match. We could improve this if we could rely on dates but the Beancount
    ledger dates might differ from bank statement which reports all purchases as business days.
    :param ledger:
    :param entry:
    :return:
    """
    for idx, row in enumerate(ledger):
        if row['position_int'] == entry['position_int']:
            return row, idx

    return None, None


def compare_ledgers(authorative, target):
    """
    Runs a simple price based comparison between two ledgers. Source is considered as authorative ledger (for example
    a bank account report) and the target as the Beancount ledger.

    :param authorative:
    :param target:
    :return:
    """
    report = {
        'matching_transactions': [],
        'missing_transactions': []
    }

    for row in authorative:
        found_row, idx = find_matching_entry_from(target, row)
        row.pop('position_int')  # We do not need this key anymore so remove it from cluttering the reports etc. later

        if found_row is not None:
            target.remove(found_row)
            report['matching_transactions'].append(row)
        else:
            report['missing_transactions'].append(row)

    return report


def print_comparison_report(report):
    warning_color = '\033[93m'
    end_color = '\033[0m'

    if len(report['missing_transactions']) == 0:
       exit(0)
    else:
        print(warning_color, 'No match in ledger for transactions!\n', end_color)
        print(tabulate(report['missing_transactions'], headers='keys'))
        exit(1)


ledger_log = read_beancount_ledger('~/ledger/ledger.beancount', '2019-01-01', '2019-01-31')
op_log = read_op_ledger('./sample_data/op_ledger.csv')

comparison_report = compare_ledgers(op_log, ledger_log)
print_comparison_report(comparison_report)
