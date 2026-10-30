"""DoDoFin tests, on made-up data in a temp folder.

    python -m unittest discover -s tests -v
"""
import datetime
import os
import sqlite3
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import make_sample_data  # noqa: E402

FIXED_TODAY = datetime.date(2026, 1, 15)


class Demo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="dodofin-test-")
        cls.old = os.getcwd()
        os.chdir(cls.dir)
        rows = make_sample_data.build_rows(6, seed=11, today=FIXED_TODAY)
        cls.rows = rows
        make_sample_data.write_csv(rows, "sample/transactions.csv")
        make_sample_data.build_database("demo.db", "sample/transactions.csv")
        import db_utils
        cls.db_utils = db_utils
        cls.conn = db_utils.create_connection("demo.db")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        os.chdir(cls.old)

    def count(self, sql):
        return self.conn.execute(sql).fetchone()[0]

    def test_rows_are_deterministic_and_dated_before_today(self):
        again = make_sample_data.build_rows(6, seed=11, today=FIXED_TODAY)
        self.assertEqual(self.rows, again)
        self.assertTrue(all(r[0] < FIXED_TODAY.replace(day=1) for r in self.rows))
        self.assertEqual(sum(1 for r in self.rows if r[1].startswith("Paycheck")), 12)

    def test_import_keeps_every_row_and_flags_the_uncategorized(self):
        self.assertEqual(self.count("SELECT COUNT(*) FROM transactions"), len(self.rows))
        blank = sum(1 for r in self.rows if not r[3])
        self.assertGreater(blank, 0)
        self.assertEqual(self.count("SELECT COUNT(*) FROM transactions WHERE category_id IS NULL"), blank)
        self.assertEqual(self.count("SELECT COUNT(*) FROM transactions WHERE is_income = 1"), 12)

    def test_reimporting_the_same_file_adds_nothing(self):
        from csv_importer import import_csv
        before = self.count("SELECT COUNT(*) FROM transactions")
        import_csv(self.conn, "sample/transactions.csv")
        self.assertEqual(self.count("SELECT COUNT(*) FROM transactions"), before)

    def test_text_amounts_with_dollar_signs(self):
        from csv_importer import import_csv
        with open("money.csv", "w", encoding="utf-8") as fh:
            fh.write('Date,Description,Amount,Category\n2025-12-03,Test Hardware,"-$1,234.56",Home Repair\n')
        import_csv(self.conn, "money.csv")
        amt = self.conn.execute("SELECT amount FROM transactions WHERE description = 'Test Hardware'").fetchone()
        self.assertIsNotNone(amt)
        self.assertAlmostEqual(amt[0], 1234.56)

    def test_avalanche_never_costs_more_interest_than_snowball(self):
        import debt_manager
        _, snow = debt_manager.simulate_payoff(self.conn, "snowball", 700)
        _, aval = debt_manager.simulate_payoff(self.conn, "avalanche", 700)
        self.assertLessEqual(aval["total_interest"], snow["total_interest"])
        self.assertLess(aval["total_interest"], snow["total_interest"])  # the demo debts are set up to differ
        self.assertEqual(debt_manager.simulate_payoff(self.conn, "avalanche", 100), (None, None))  # below minimums

    def test_refuses_to_touch_a_real_finance_db(self):
        open("finance.db", "w").close()
        self.assertEqual(make_sample_data.main(["--db", "finance.db", "--csv", "sample/x.csv"]), 1)


if __name__ == "__main__":
    unittest.main()
