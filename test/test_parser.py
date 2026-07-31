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
            "e-Transfer sent BUCKS FOR YOU",
            "300.00",
            "9,700.00",
            "6 Jan",
            "e-Transfer sent MORE BUCKS FOR YOU",
            "700.00",
            "9,000.00",
        ]
        result_lines = roll_up_rbc_bank_transactions(date_lines)
        start_year = (result_lines[1].split('\t')[0].split(' '))[2]
        end_year = (result_lines[2].split('\t')[0].split(' '))[2]
        continue_year = (result_lines[3].split('\t')[0].split(' '))[2]
        self.assertEqual(
            start_year, "2024"
        )
        self.assertEqual(
            end_year, "2025"
        )
        self.assertEqual(
            continue_year, "2025"
        )


if __name__ == "__main__":
    unittest.main()
