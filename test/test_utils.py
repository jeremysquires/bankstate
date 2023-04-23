import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


class TestUtils(unittest.TestCase):

    def test_is_mon_dd_date(self):
        self.assertTrue(utils.is_mon_dd_date("Jan 05"))
        self.assertFalse(utils.is_mon_dd_date("Gak 05"))

    def test_is_mon_dot_dd_date(self):
        self.assertTrue(utils.is_mon_dot_dd_date("Jan. 05"))
        self.assertFalse(utils.is_mon_dot_dd_date("Jan 05"))
        self.assertFalse(utils.is_mon_dot_dd_date("Gak. 05"))

    def test_is_date(self):
        self.assertTrue(utils.is_date("Jan 05"))
        self.assertFalse(utils.is_date("Gak 05"))

    def test_is_format_date(self):
        self.assertTrue(utils.is_format_date("Jan. 05", "%b. %d"))
        self.assertTrue(utils.is_format_date("Jan 05, 2022", "%b %d, %Y"))
        self.assertFalse(utils.is_format_date("Jan 05, 20222", "%b %d, %Y"))

    def test_is_transaction_line(self):
        self.assertTrue(utils.is_transaction_line("Jan 05 blah blah"))
        self.assertFalse(utils.is_date("Gak 05 blah blah"))

# TODO: unit test is_currency, is_float, is_int and currency_to_float
    def test_is_currency(self):
        self.assertTrue(utils.is_currency("$5.00"))
        self.assertTrue(utils.is_currency("5.00"))
        self.assertFalse(utils.is_currency("$5"))
        self.assertTrue(utils.is_currency("5,000.00"))

    def test_is_float(self):
        self.assertTrue(utils.is_float("5.00"))
        self.assertFalse(utils.is_float("$5.00"))
        self.assertFalse(utils.is_float("5"))
        self.assertFalse(utils.is_float("5,000.00"))

    def test_is_int(self):
        self.assertFalse(utils.is_int("5.00"))
        self.assertFalse(utils.is_int("$5.00"))
        self.assertTrue(utils.is_int("5"))
        self.assertFalse(utils.is_int("5,000"))

    def test_currency_to_float(self):
        self.assertEqual(utils.currency_to_float("$5.00"), "5.00")
        self.assertEqual(utils.currency_to_float("5.00"), "5.00")
        self.assertEqual(utils.currency_to_float("$5"), None)
        self.assertEqual(utils.currency_to_float("5,000"), None)
        self.assertEqual(utils.currency_to_float("5,000.00"), "5000.00")

if __name__ == '__main__':
    unittest.main()
