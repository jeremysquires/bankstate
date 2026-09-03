import os
import sys
import unittest
import locale

locale.setlocale(locale.LC_NUMERIC, "")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from src.payee_category import (
    category_from_description,
    payee_from_description,
    map_bmo_bank_transactions,
    map_scotia_visa_transactions,
    map_tsv_transactions,
)


class TestPayeeCategory(unittest.TestCase):
    def test_generic_payee_from_description(self):
        descriptions = [
            "Payroll Deposit COMPANY",
            "e-Transfer sent AN INDIVIDUAL 55ID55",
            "Online Banking transfer Somebody - 1324",
            "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
            "MAGOO'S            CITY1 PROVINCE1",
            "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
            "INTERAC e-Transfer Sent Neighborhood Lawn Care",
            "Online Bill Payment, POWER COMPANY",
            "Direct Deposit, JOB INC. PAY/PAY",
            "USD999.00@1.000000000 COMPANY PRODUCTS & SERVICES 123456789 AA",
        ]
        payees = [
            "COMPANY",
            "AN INDIVIDUAL 55ID55",
            "Somebody - 1324",
            "CITY TAX",
            "MAGOO'S",
            "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
            "Neighborhood Lawn Care",
            "POWER COMPANY",
            "JOB INC. PAY/PAY",
            "COMPANY PRODUCTS & SERVICES 123456789 AA",
        ]
        for idx, description in enumerate(descriptions):
            payee = payee_from_description(description)
            self.assertEqual(payee, payees[idx])

    def test_special_payee_from_description(self):
        descriptions = [
            "AMZN Mktp CA*J999B9K99 WWW.AMAZON.CAON",
            "LinkedIn 6367341474     LINKEDIN.COM IRL",
            "Amazon.ca*A99AA9A99        AMAZON.CA ON",
            "SHELL C99999            CITY PROVINCE",
            "Online Banking transfer - 1324",  # "(\\w) - (\\w)" pattern breaks others
            "BOOKSTORE 123           CITY1",  # BOOKSTORE not implemented
            "OUTER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP not implemented
            "INNER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP not implemented
            "ONLINESTORE 12345678 WWW.STORE.COM",  # ONLINESTORE not implemented
        ]
        payees = [
            "AMZN Mktp CA",
            "LinkedIn",
            "Amazon.ca",
            "SHELL",
            "- 1324",
            "BOOKSTORE 123",
            "OUTER ROAD OTHERSHOP",
            "INNER ROAD OTHERSHOP",
            "ONLINESTORE 12345678 WWW.STORE.COM",
        ]
        for idx, description in enumerate(descriptions):
            payee = payee_from_description(description)
            self.assertEqual(payee, payees[idx])

    def test_malfunctioning_payee_from_description(self):
        # TODO: fix these ... https://github.com/jeremysquires/bankstate/issues/51
        descriptions = [
            "Online Banking transfer - 1324",  # "(\\w) - (\\w)" pattern breaks others
            "BOOKSTORE 123           CITY1",  # BOOKSTORE expected
            "OUTER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP expected
            "INNER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP expected
            "ONLINESTORE 12345678 WWW.STORE.COM",  # ONLINESTORE expected
            "SOME STORE #00144 CITY PROVINCE",  # SOME STORE expected
            "SOME STORE #00144      CITY PROVINCE",  # SOME STORE expected
            "#930 MARK'S           CITY1 PROVINCE1",  # MARK'S expected
        ]
        payees = [
            "- 1324",
            "BOOKSTORE 123",
            "OUTER ROAD OTHERSHOP",
            "INNER ROAD OTHERSHOP",
            "ONLINESTORE 12345678 WWW.STORE.COM",
            "SOME STORE CITY PROVINCE",
            "SOME STORE CITY PROVINCE",
            "MARK'S CITY1 PROVINCE1",
        ]
        for idx, description in enumerate(descriptions):
            payee = payee_from_description(description)
            self.assertEqual(payee, payees[idx])

    def test_generic_category_from_description(self):
        descriptions = [
            "Payroll Deposit COMPANY",
            "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
            "INTERAC e-Transfer Sent Neighborhood Lawn Care",
            "Online Bill Payment, POWER COMPANY",
            "Direct Deposit, JOB INC. PAY/PAY",
            "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
            "Online Bill Payment, COMMS COMPANY",
        ]
        categories = [
            "Salary",
            "Taxes",
            "Landscaping",
            "Electricity",
            "Salary",
            "Other",
            "Internet",
        ]
        for idx, description in enumerate(descriptions):
            category = category_from_description(description)
            self.assertEqual(category, categories[idx])

    def test_map_bmo_bank_transactions(self):
        rows_bmo_bank = [
            [
                "First Bank Card",
                "Transaction Type",
                "Date Posted",
                "Transaction Amount",
                "Description",
            ],
            ["111", "CREDIT", "20260101", "1000.00", "[DN]Payroll Deposit COMPANY"],
            [
                "111",
                "DEBIT",
                "20260101",
                "-1000.00",
                "[CW]INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
            ],
            [
                "111",
                "DEBIT",
                "20260101",
                "-100.00",
                "[CW]INTERAC e-Transfer Sent Neighborhood Lawn Care",
            ],
            [
                "111",
                "DEBIT",
                "20260101",
                "-100.00",
                "[CW]Online Bill Payment, POWER COMPANY",
            ],
            [
                "111",
                "CREDIT",
                "20260101",
                "1000.00",
                "[DN]Direct Deposit, JOB INC. PAY/PAY",
            ],
            [
                "111",
                "DEBIT",
                "20260101",
                "-100.00",
                "[CW]MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
            ],
            [
                "111",
                "DEBIT",
                "20260101",
                "-100.00",
                "[CW]Online Bill Payment, COMMS COMPANY",
            ],
        ]
        rows_expected = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
                "Payee",
                "Category",
            ],
            [
                "01 Jan 2026",
                "Payroll Deposit COMPANY",
                "",
                "1000.00",
                "2000.00",
                "COMPANY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1000.00",
                "",
                "1000.00",
                "CITY TAX",
                "Taxes",
            ],
            [
                "01 Jan 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
                "Neighborhood Lawn Care",
                "Landscaping",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
                "POWER COMPANY",
                "Electricity",
            ],
            [
                "01 Jan 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1000.00",
                "1800.00",
                "JOB INC. PAY/PAY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1700.00",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "Other",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1600.00",
                "COMMS COMPANY",
                "Internet",
            ],
        ]
        rows_out = map_bmo_bank_transactions(rows_bmo_bank, "1000.00")
        self.assertListEqual(rows_expected, rows_out)

    def test_map_scotia_visa_transactions(self):
        rows_scotia_visa = [
            [
                "Filter",
                "Date",
                "Description",
                "Sub-description",
                "Status",
                "Type of Transaction",
                "Amount",
            ],
            [
                "All available transactions (up to 2 years), From date=2026-01-01",
                "2026-01-01",
                "Payroll Deposit COMPANY",
                "City",
                "posted",
                "Credit",
                "-1000",
            ],
            [
                "",
                "2026-01-01",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "City",
                "posted",
                "Debit",
                "1000",
            ],
            [
                "",
                "2026-01-01",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "City",
                "posted",
                "Debit",
                "100.00",
            ],
            [
                "",
                "2026-01-01",
                "Online Bill Payment, POWER COMPANY",
                "City",
                "posted",
                "Debit",
                "100.00",
            ],
            [
                "",
                "2026-01-01",
                "Direct Deposit, JOB INC. PAY/PAY",
                "City",
                "posted",
                "Credit",
                "-1000",
            ],
            [
                "",
                "2026-01-01",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "City",
                "posted",
                "Debit",
                "100.00",
            ],
            [
                "",
                "2026-01-01",
                "Online Bill Payment, COMMS COMPANY",
                "City",
                "posted",
                "Debit",
                "100.00",
            ],
        ]
        rows_expected = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
                "Payee",
                "Category",
            ],
            [
                "01 Jan 2026",
                "Payroll Deposit COMPANY",
                "",
                "1000.00",
                "2000.00",
                "COMPANY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1000.00",
                "",
                "1000.00",
                "CITY TAX",
                "Taxes",
            ],
            [
                "01 Jan 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
                "Neighborhood Lawn Care",
                "Landscaping",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
                "POWER COMPANY",
                "Electricity",
            ],
            [
                "01 Jan 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1000.00",
                "1800.00",
                "JOB INC. PAY/PAY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1700.00",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "Other",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1600.00",
                "COMMS COMPANY",
                "Internet",
            ],
        ]
        rows_out = map_scotia_visa_transactions(rows_scotia_visa, "1000.00")
        self.assertListEqual(rows_expected, rows_out)

    def test_map_tsv_transactions(self):
        rows_tsv = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
            ],
            [
                "01 Jan 2026",
                "Payroll Deposit COMPANY",
                "",
                "1000.00",
                "2000.00",
            ],
            [
                "01 Jan 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1000.00",
                "",
                "1000.00",
            ],
            [
                "01 Jan 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
            ],
            [
                "01 Jan 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1000.00",
                "1800.00",
            ],
            [
                "01 Jan 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1700.00",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1600.00",
            ],
        ]
        rows_expected = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
                "Payee",
                "Category",
            ],
            [
                "01 Jan 2026",
                "Payroll Deposit COMPANY",
                "",
                "1000.00",
                "2000.00",
                "COMPANY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1000.00",
                "",
                "1000.00",
                "CITY TAX",
                "Taxes",
            ],
            [
                "01 Jan 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
                "Neighborhood Lawn Care",
                "Landscaping",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
                "POWER COMPANY",
                "Electricity",
            ],
            [
                "01 Jan 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1000.00",
                "1800.00",
                "JOB INC. PAY/PAY",
                "Salary",
            ],
            [
                "01 Jan 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1700.00",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "Other",
            ],
            [
                "01 Jan 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1600.00",
                "COMMS COMPANY",
                "Internet",
            ],
        ]
        rows_out = map_tsv_transactions(rows_tsv)
        self.assertListEqual(rows_expected, rows_out)

    def test_locale_map_tsv_transactions(self):
        rows_tsv = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
            ],
            [
                "01 Jan, 2026",
                "Payroll Deposit COMPANY",
                "",
                "1,000.00",
                "2,000.00",
            ],
            [
                "01 Jan, 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1,000.00",
                "",
                "1,000.00",
            ],
            [
                "01 Jan, 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
            ],
            [
                "01 Jan, 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
            ],
            [
                "01 Jan, 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1,000.00",
                "1,800.00",
            ],
            [
                "01 Jan, 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1,700.00",
            ],
            [
                "01 Jan, 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1,600.00",
            ],
        ]
        rows_expected = [
            [
                "Date",
                "Description",
                "Withdrawal",
                "Deposit",
                "Balance",
                "Payee",
                "Category",
            ],
            [
                "01 Jan, 2026",
                "Payroll Deposit COMPANY",
                "",
                "1000.00",
                "2000.00",
                "COMPANY",
                "Salary",
            ],
            [
                "01 Jan, 2026",
                "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
                "1000.00",
                "",
                "1000.00",
                "CITY TAX",
                "Taxes",
            ],
            [
                "01 Jan, 2026",
                "INTERAC e-Transfer Sent Neighborhood Lawn Care",
                "100.00",
                "",
                "900.00",
                "Neighborhood Lawn Care",
                "Landscaping",
            ],
            [
                "01 Jan, 2026",
                "Online Bill Payment, POWER COMPANY",
                "100.00",
                "",
                "800.00",
                "POWER COMPANY",
                "Electricity",
            ],
            [
                "01 Jan, 2026",
                "Direct Deposit, JOB INC. PAY/PAY",
                "",
                "1000.00",
                "1800.00",
                "JOB INC. PAY/PAY",
                "Salary",
            ],
            [
                "01 Jan, 2026",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "100.00",
                "",
                "1700.00",
                "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
                "Other",
            ],
            [
                "01 Jan, 2026",
                "Online Bill Payment, COMMS COMPANY",
                "100.00",
                "",
                "1600.00",
                "COMMS COMPANY",
                "Internet",
            ],
        ]
        rows_out = map_tsv_transactions(rows_tsv)
        self.assertListEqual(rows_expected, rows_out)


if __name__ == "__main__":
    unittest.main()
