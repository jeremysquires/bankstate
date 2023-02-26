import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


class TestUtils(unittest.TestCase):

    def test_is_mon_dd_date(self):
        self.assertTrue(utils.is_mon_dd_date("Jan 05"))
        self.assertFalse(utils.is_mon_dd_date("Gak 05"))

    def test_is_date(self):
        self.assertTrue(utils.is_date("Jan 05"))
        self.assertFalse(utils.is_date("Gak 05"))

    def test_is_transaction_line(self):
        self.assertTrue(utils.is_transaction_line("Jan 05 blah blah"))
        self.assertFalse(utils.is_date("Gak 05 blah blah"))


if __name__ == '__main__':
    unittest.main()
