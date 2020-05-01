import subprocess
import sys
import csv
from tabulate import tabulate
from io import StringIO
import datetime


def read_beancount_ledger(file_path, start_date, end_date):
    result = subprocess.run(['bean-query', '-f', 'csv', file_path, 'select date, narration, account, position where account ~ ".:Käyttötili" and date >= {} and date <= {};'.format(start_date, end_date)], stdout=subprocess.PIPE)
    reader = csv.DictReader(StringIO(result.stdout.decode('utf-8')))

    contents = [row for row in reader]
    try:
        for row in contents:
            row['position'] = float(row['position'].replace('EUR', '').strip())
            row['position_int'] = int(row['position'] * 100)
    except:
        print('Failed in reading the Beancount query results')
        print(contents)
        sys.exit(1)
    return contents


def read_op_ledger(file_path):
    parsed = []
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            position = float(row['Määrä\xa0 EUROA'].replace(',', '.'))
            date = datetime.datetime.strptime(row['Kirjauspäivä'], '%d.%m.%Y')
            parsed.append({
                'date': str(date.date()),
                'position': position,
                'position_int': int(position * 100),
                'narration': row['Saaja/Maksaja']
            })

    return parsed


def find_matching_entry_from(ledger, entry, strict):
    """
    Try to find a matching entry from the provided ledger. The algorithm is *really* naive. It considers any
    transaction with same price as a match. If strict mode is used, the algorithm also requires that dates
    of the transaction match along with its position.
    :param ledger:
    :param entry:
    :param: strict: If set true, will also require dates of the transaction to match
    :return:
    """
    for idx, row in enumerate(ledger):
        matching_position = row['position_int'] == entry['position_int']

        if strict:
            matching_date = row['date'] == entry['date']
            if matching_position and matching_date:
                return row, idx
        elif matching_position:
            return row, idx

    return None, None


def compare_ledgers(authorative, target, strict=False):
    """
    Runs a simple price based comparison between two ledgers. Source is considered as authorative ledger (for example
    a bank account report) and the target as the Beancount ledger.

    :param authorative:
    :param target:
    :param strict:
    :return:
    """
    report = {
        'strict': strict,
        'matching_transactions': [],
        'missing_transactions': []
    }

    for row in authorative:
        found_row, idx = find_matching_entry_from(target, row, strict)
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
    strict_mode = ''

    if report['strict']:
        strict_mode = 'in the strict mode'

    if len(report['missing_transactions']) == 0:
       exit(0)
    else:
        print(warning_color, 'No matches in ledger for transactions {}!\n'.format(strict_mode), end_color)
        print(tabulate(report['missing_transactions'], headers='keys'))
        exit(1)
