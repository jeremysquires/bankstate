import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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

    def test_trim_parts_short(self):
        short_strings = "Any\tstring\tshorter"
        self.assertEqual(
            "\t".join(utils.trim_parts(short_strings.split("\t"))), short_strings
        )

    def test_trim_parts_long(self):
        long_strings = "01 Jan 9999	 2 of 2 Your RBC personal banking account statement From DATE to DATE Details of your account activity - continued Date Description Withdrawals ($) Deposits ($) Balance ($) Please check this Account Statement without delay and advise us of any error or omission within 45 days of the statement date. If you opted to receive cheque images, only images of the front of your cheques have been sent to you with this Account Statement. An image included on this Account Statement does not indicate that a cheque has been successfully processed as of the statement date. Please retain this statement for your records. TM Trademarks of Royal Bank of Canada. RBC and Royal Bank are registered trademarks of Royal Bank of Canada. ®Registered trade-mark of Royal Bank of Canada. Royal Trust Corporation of Canada and The Royal Trust Company are licensees of the trade-mark. Royal Bank of Canada GST Registration Number: Royal Trust Corporation of Canada GST Registration Number: The Royal Trust Company GST Registration Number:  MultiProduct rebate		9.99	99,999.99"
        desired_long_strings = "01 Jan 9999	MultiProduct rebate		9.99	99,999.99"
        self.assertEqual(
            "\t".join(utils.trim_parts(long_strings.split("\t"))), desired_long_strings
        )


if __name__ == "__main__":
    unittest.main()
