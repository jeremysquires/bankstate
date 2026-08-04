import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf2txt import roll_up_rbc_bank_transactions, roll_up_bmo_bank_transactions, roll_up_card_transactions

class TestParser(unittest.TestCase):
    def test_date_change_bmo_bank(self):
        date_lines = [
            "For the period ending January 06, 2024",
            "Dec 31",
            "INTERAC e-Transfer Sent",
            "1,000.00",
            "10,000.00",
            "Jan 01",
            "INTERAC e-Transfer Sent",
            "300.00",
            "9,700.00",
            "Jan 06",
            "INTERAC e-Transfer Sent",
            "700.00",
            "9,000.00",
        ]
        result_lines = roll_up_bmo_bank_transactions(date_lines)
        start_year = (result_lines[1].split('\t')[0].split(' '))[2]
        end_year = (result_lines[2].split('\t')[0].split(' '))[2]
        continue_year = (result_lines[3].split('\t')[0].split(' '))[2]
        self.assertEqual(
            start_year, "2023"
        )
        self.assertEqual(
            end_year, "2024"
        )
        self.assertEqual(
            continue_year, "2024"
        )


    def test_month_jump_bmo_bank(self):
        date_lines = [
            "For the period ending May 06, 2024",
            "Sep 21",
            "INTERAC e-Transfer Sent",
            "1,000.00",
            "10,000.00",
            "Mar 01",
            "INTERAC e-Transfer Sent",
            "300.00",
            "9,700.00",
            "May 06",
            "INTERAC e-Transfer Sent",
            "700.00",
            "9,000.00",
        ]
        result_lines = roll_up_bmo_bank_transactions(date_lines)
        start_year = (result_lines[1].split('\t')[0].split(' '))[2]
        end_year = (result_lines[2].split('\t')[0].split(' '))[2]
        continue_year = (result_lines[3].split('\t')[0].split(' '))[2]
        self.assertEqual(
            start_year, "2023"
        )
        self.assertEqual(
            end_year, "2024"
        )
        self.assertEqual(
            continue_year, "2024"
        )


    def test_date_change_rbc_bank(self):
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


    def test_month_jumps_rbc_bank(self):
        date_lines = [
            "Your opening balance on September 20, 2024",
            "21 Sep",
            "Online Banking transfer - 5555",
            "1,000.00",
            "10,000.00",
            "1 Mar",
            "e-Transfer sent BUCKS FOR YOU",
            "300.00",
            "9,700.00",
            "6 Mar",
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


    def test_date_change_bmo_card(self):
        date_lines = [
            "Dec. 17, 2023 - Jan. 6, 2024",
            "Dec. 17",
            "Dec. 17",
            "Membership",
            "MyMembership",
            "3298749847539874",
            "100.00",
            "Jan. 1",
            "Jan. 3",
            "Food Court",
            "City",
            "Province",
            "9808938408093",
            "30.00",
            "Jan. 4",
            "Jan. 6",
            "GAS GAS GAS",
            "100.00"
        ]
        result_lines = roll_up_card_transactions(date_lines)
        start_year = (result_lines[1].split('\t')[0].split(' '))[2]
        end_year = (result_lines[2].split('\t')[0].split(' '))[2]
        continue_year = (result_lines[3].split('\t')[0].split(' '))[2]
        self.assertEqual(
            start_year, "2023"
        )
        self.assertEqual(
            end_year, "2024"
        )
        self.assertEqual(
            continue_year, "2024"
        )


    def test_date_change_rbc_card(self):
        date_lines = [
            "STATEMENT FROM DEC 17, 2025 TO JAN 6, 2026",
            "DEC 17",
            "DEC 17",
            "Membership",
            "MyMembership",
            "3298749847539874",
            "100.00",
            "JAN 1",
            "JAN 3",
            "Food Court City Province",
            "9808938408093",
            "30.00",
            "JAN 4",
            "JAN 6",
            "GAS GAS GAS",
            "100.00"
        ]
        result_lines = roll_up_card_transactions(date_lines)
        start_year = (result_lines[1].split('\t')[0].split(' '))[2]
        end_year = (result_lines[2].split('\t')[0].split(' '))[2]
        continue_year = (result_lines[3].split('\t')[0].split(' '))[2]
        self.assertEqual(
            start_year, "2025"
        )
        self.assertEqual(
            end_year, "2026"
        )
        self.assertEqual(
            continue_year, "2026"
        )


    def test_received_etransfers_rbc_bank(self):
        date_lines = [
            "Your opening balance on December 20, 2024",
            "Opening Balance",
            "11,000.00",
            "31 Dec",
            "Online Banking transfer - 5555",
            "ADDITIONAL_ID",
            "1,000.00",
            "10,000.00",
            "1 Jan",
            "e-Transfer sent BUCKS FOR YOU",
            "300.00",
            "9,700.00",
            "5 Jan",
            "e-Transfer received Friend of a Friend",
            "FriendID",
            "200.00",
            "9,900.00",
            "6 Jan",
            "e-Transfer sent MORE BUCKS FOR YOU",
            "700.00",
            "9,200.00",
        ]
        result_lines = roll_up_rbc_bank_transactions(date_lines)
        balances = [result_line.split('\t')[4] for result_line in result_lines]
        descriptions = [result_line.split('\t')[1] for result_line in result_lines]
        self.assertEqual(
            len(result_lines), 5
        )
        self.assertListEqual(
            balances, ["Balance","10,000.00","9,700.00","9,900.00","9,200.00"]
        )
        self.assertFalse(
            any([bool("ERR:BALANCE" in description) for description in descriptions])
        )


    def test_undated_rows_rbc_bank(self):
        date_lines = [
            "Your opening balance on December 20, 2024",
            "Opening Balance",
            "11,000.00",
            "31 Dec",
            "Online Banking transfer - 5555",
            "ADDITIONAL_ID",
            "1,000.00",
            "10,000.00",
            "1 Jan",
            "e-Transfer sent BUCKS FOR YOU",
            "300.00",
            "9,700.00",
            "e-Transfer received Friend of a Friend",
            "FriendID",
            "200.00",
            "9,900.00",
            "6 Jan",
            "e-Transfer sent MORE BUCKS FOR YOU",
            "700.00",
            "9,200.00",
        ]
        result_lines = roll_up_rbc_bank_transactions(date_lines)
        balances = [result_line.split('\t')[4] for result_line in result_lines]
        descriptions = [result_line.split('\t')[1] for result_line in result_lines]
        self.assertEqual(
            len(result_lines), 5
        )
        self.assertListEqual(
            balances, ["Balance","10,000.00","9,700.00","9,900.00","9,200.00"]
        )
        self.assertFalse(
            any([bool("ERR:BALANCE" in description) for description in descriptions])
        )


    def test_skip_balance_rbc_bank(self):
        date_lines = [
            "Your opening balance on December 20, 2024",
            "Opening Balance",
            "11,000.00",
            "31 Dec",
            "Online Banking transfer - 5555",
            "ADDITIONAL_ID",
            "1,000.00",
            "10,000.00",
            "1 Jan",
            "e-Transfer received BUCKS FOR YOU",
            "300.00",
            "e-Transfer received Friend of a Friend",
            "FriendID",
            "200.00",
            "10,500.00",
            "6 Jan",
            "e-Transfer sent MORE BUCKS FOR YOU",
            "700.00",
            "11,200.00",
        ]
        result_lines = roll_up_rbc_bank_transactions(date_lines)
        balances = [result_line.split('\t')[4] for result_line in result_lines]
        descriptions = [result_line.split('\t')[1] for result_line in result_lines]
        self.assertEqual(
            len(result_lines), 5
        )
        self.assertListEqual(
            balances, ["Balance","10,000.00","10,300.00","10,500.00","11,200.00"]
        )
        self.assertFalse(
            any([bool("ERR:BALANCE" in description) for description in descriptions])
        )


if __name__ == "__main__":
    unittest.main()
