import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from src.payee_category import category_from_description, payee_from_description


class TestPayeeCategory(unittest.TestCase):
    def test_generic_payee_from_description(self):
        descriptions = [
            "Payroll Deposit COMPANY",
            "e-Transfer sent AN INDIVIDUAL 55ID55",
            "Online Banking transfer Somebody - 1324",
            "INTERAC ETRNSFR SENT     CITY TAX          20260805DEFS",
            "MAGOO'S            CITY1 PROVINCE1",
            "MARKETPLACE*VENDOR WWW.MARKETPLACE.COM",
            "SOME STORE #00144 CITY PROVINCE",
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
            "SOME STORE",
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
            "#930 MARK'S           CITY1 PROVINCE1",  # Special rule for MARK'S
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
            "MARK'S",
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
        descriptions = [
            "Online Banking transfer - 1324",  # "(\\w) - (\\w)" pattern breaks others
            "BOOKSTORE 123           CITY1",  # BOOKSTORE not implemented
            "OUTER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP not implemented
            "INNER ROAD OTHERSHOP           CITY1 PROVINCE1",  # OTHERSHOP not implemented
            "ONLINESTORE 12345678 WWW.STORE.COM",  # ONLINESTORE not implemented
        ]
        payees = [
            "- 1324",
            "BOOKSTORE 123",
            "OUTER ROAD OTHERSHOP",
            "INNER ROAD OTHERSHOP",
            "ONLINESTORE 12345678 WWW.STORE.COM",
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
            "Tax",
            "Landscaping",
            "Utilities",
            "Salary",
            "Other",
            "Internet",
        ]
        for idx, description in enumerate(descriptions):
            category = category_from_description(description)
            self.assertEqual(category, categories[idx])


if __name__ == "__main__":
    unittest.main()
