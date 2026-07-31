import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf2txt import roll_up_rbc_bank_transactions

class TestParser(unittest.TestCase):
    def test_date_change(self):
        date_lines = [
            "Your opening balance on December 20, 2024",
            "31 Dec",
            "Online Banking transfer - 5555",
            "1,000.00",
            "10,000.00",
            "1 Jan",
            "e-Transfer sent BUCKY BALLS",
            "300.00",
            "28,906.48",
        ]
        result_lines = roll_up_rbc_bank_transactions(date_lines)
        result_year = (result_lines[1].split('\t')[0].split(' '))[2]
        self.assertEqual(
            result_year, "2025"
        )


if __name__ == "__main__":
    unittest.main()
