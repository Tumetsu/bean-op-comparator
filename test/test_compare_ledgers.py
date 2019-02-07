import pytest
from op_bean_compare import compare_ledgers, find_matching_entry_from


class TestFindMatchingEntry:
    @pytest.fixture()
    def ledger(self):
        return [
            {'date': '2019-01-01', 'position_int': 12},
            {'date': '2019-01-04', 'position_int': 14},
            {'date': '2019-01-14', 'position_int': 3},
            {'date': '2019-01-16', 'position_int': 3}
        ]

    def should_return_row_and_index_of_matching_entry(self, ledger):
        entry = {'date': '2019-01-04', 'position_int': 14}
        row, index = find_matching_entry_from(ledger, entry, False)
        assert row is not None
        assert index == 1

    def should_return_first_matching_entry(self, ledger):
        entry = {'date': '2019-01-04', 'position_int': 3}
        row, index = find_matching_entry_from(ledger, entry, False)
        assert row['date'] == '2019-01-14'
        assert index == 2

    def should_return_none_if_no_matching_entry_was_found(self, ledger):
        entry = {'date': '2019-01-04', 'position_int': 300}
        row, index = find_matching_entry_from(ledger, entry, False)
        assert row is None
        assert index is None

    class TestStrictMode:
        def should_return_row_and_index_of_matching_entry(self, ledger):
            entry = {'date': '2019-01-04', 'position_int': 14}
            row, index = find_matching_entry_from(ledger, entry, True)
            assert row is not None
            assert index == 1

        def should_return_none_if_entry_did_not_have_matching_position(self, ledger):
            entry = {'date': '2019-01-04', 'position_int': 30}
            row, index = find_matching_entry_from(ledger, entry, True)
            assert row is None
            assert index is None

        def should_return_none_if_entry_did_not_have_matching_date(self, ledger):
            entry = {'date': '2019-01-04', 'position_int': 3}
            row, index = find_matching_entry_from(ledger, entry, True)
            assert row is None
            assert index is None

class TestCompareLedgers:

    @pytest.fixture()
    def op_ledger(self):
        return [
            {'date': '2019-01-01', 'position_int': 12},
            {'date': '2019-01-04', 'position_int': 14},
            {'date': '2019-01-14', 'position_int': 3},
            {'date': '2019-01-16', 'position_int': 3}
        ]

    @pytest.fixture()
    def ledger(self):
        return [
            {'date': '2019-01-01', 'position_int': 12},
            {'date': '2019-01-04', 'position_int': 14},
            {'date': '2019-01-14', 'position_int': 3},
            {'date': '2019-01-16', 'position_int': 3}
        ]

    def should_report_nothing_missing_when_ledgers_match_in_non_strict_mode(self, ledger, op_ledger):
        report = compare_ledgers(op_ledger, ledger)
        assert len(report['matching_transactions']) == 4
        assert len(report['missing_transactions']) == 0


    def should_report_transactions_missing_from_the_ledger(self, ledger, op_ledger):
        missing_entry = {'date': '2019-01-16', 'position_int': 300}
        op_ledger.append(missing_entry)

        report = compare_ledgers(op_ledger, ledger)
        assert len(report['matching_transactions']) == 4
        assert len(report['missing_transactions']) == 1
        assert report['missing_transactions'][0] == missing_entry

    def should_report_transactions_missing_when_there_is_multiple_transactions_with_same_position(self, ledger, op_ledger):
        # When the matches are searched from the another ledger, the algorithm should recognize that while one of the following
        # transactions was found from the ledger, the subsequent two others weren't.
        missing_entries = [{'date': '2019-01-16', 'position_int': 3}, {'date': '2019-01-16', 'position_int': 3}]
        op_ledger += missing_entries

        report = compare_ledgers(op_ledger, ledger)
        assert len(report['matching_transactions']) == 4
        assert len(report['missing_transactions']) == 2
        assert report['missing_transactions'][0] == missing_entries[0]

    def should_not_report_transaction_missing_when_date_differs_in_the_non_strict_mode(self, ledger, op_ledger):
        op_ledger[0]['date'] = '2019-01-03'

        report = compare_ledgers(op_ledger, ledger)
        assert len(report['matching_transactions']) == 4
        assert len(report['missing_transactions']) == 0

    class TestStrictMode:
        def should_report_nothing_missing_when_ledgers_match_in_strict_mode(self, ledger, op_ledger):
            report = compare_ledgers(op_ledger, ledger, True)
            assert len(report['matching_transactions']) == 4
            assert len(report['missing_transactions']) == 0

        def should_report_transaction_missing_when_date_differs_in_the_strict_mode(self, ledger, op_ledger):
            op_ledger[0]['date'] = '2019-01-03'

            report = compare_ledgers(op_ledger, ledger, True)
            assert len(report['matching_transactions']) == 3
            assert len(report['missing_transactions']) == 1
            assert report['missing_transactions'][0] == op_ledger[0]
