from op_bean_compare import read_op_ledger


class TestOPLedger:

    def should_convert_op_format_to_a_new_format(self):
        data = read_op_ledger('./test/data/op_ledger.csv')
        row = data[0]

        assert row['date'] == '2019-01-02'
        assert row['position'] == -51.34
        assert row['position_int'] == -5134
        assert row['narration'] is not None
        assert len(data) == 33
