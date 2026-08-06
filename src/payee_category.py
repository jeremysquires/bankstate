import argparse
from datetime import datetime
from typing import List, Tuple
import utils
import csv
import re
from functools import cache
import json
import os
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


def get_run_params() -> Tuple[str, str, str]:
    parser = argparse.ArgumentParser(
        prog="payee_categoryt.py",
        description="Converts bank statement TSV/CSVs to a common format and adds payees and categories",
        epilog=(
            f"Copyright (C) 2026 Jeremy Squires <jms@mailforce.net> "
            f"License: <https://opensource.org/licenses/MIT>"
        ),
    )
    parser.add_argument(
        "input",
        help="input is the path to a CSV/TSV bank statement",
    )
    parser.add_argument(
        "filetype",
        choices=["bmo_bank", "sco_visa"],
        help=(
            f"is the type of input bank statement: "
            f"bmo is the Bank of Montreal, "
            f"sco is the Scotiabank, "
            f"_bank is a bank current account statement, and "
            f"_visa is a VisaCard statement"
        ),
    )
    parser.add_argument(
        "output",
        help=f"output is the path to the CSV output file",
    )
    args = parser.parse_args()
    print(args.input, args.filetype, args.output, args.capture or "", args.format or "")
    return args.input, args.filetype, args.output, args.capture or "", args.format or ""


def get_csv(filename: str) -> List[str]:
    with open(filename, mode="r", encoding="utf-8") as file:
        delimiter = ","
        if filename.endswith("tsv"):
            delimiter = "\t"
        reader = csv.reader(file, delimiter=delimiter)
        rows = []
        for row in reader:
            rows.append(row)
    return rows


@cache
def get_category_patterns() -> dict[str, str]:
    # regex matches for specific payee patterns
    if os.path.exists(f"{SCRIPT_DIR}/category_patterns.json"):
        with open(f"{SCRIPT_DIR}/category_patterns.json", "r") as file:
            return json.load(file)
    return {
        "Transfer": " TF ",
        "Salary": " PAY",
        "Tax": "HST|GST|VAT",
        "Service": "Monthly fee|MultiProduct Rebate|FULL PLAN FEE REBATE|PREMIUM PLAN",
        "Insurance": "Insurance",
        "Investment": "Investment",
        "Cash withdrawal": "Cash",
    }


@cache
def get_payee_patterns() -> list[str]:
    # regex matches for specific payee patterns
    if os.path.exists(f"{SCRIPT_DIR}/payee_patterns.json"):
        with open(f"{SCRIPT_DIR}/payee_patterns.json", "r") as file:
            return json.load(file)
    return [
        "[\\*#]",
        "\\s\\d+\\s",
        "Direct Deposit, ",
        "Payroll Deposit ",
        "Online ",
        "Bill Payment",
        "Banking transfer - ",
        "Banking payment - ",
        "Misc Payment ",
        "INTERAC ",
        "e-Transfer Sent ",
        "e-Transfer Received ",
        "ETRNSFR SENT ",
        "ETRNSFR RECVD ",
    ]


def category_from_description(description: str) -> str:
    category_patterns = get_category_patterns()
    # TODO: if match multiple times, return most likely
    for key, value in category_patterns.items():
        p = re.compile(value, re.IGNORECASE)
        if re.search(p, description):
            return key
    return "Other"


def payee_from_description(description: str) -> str:
    payee_patterns = get_payee_patterns()
    payee_regex_string = "|".join(payee_patterns)
    p = re.compile(payee_regex_string, re.IGNORECASE)
    parts = re.split(p, description)
    parts = [part for part in parts if part is not None]
    if len(parts) > 0 and (payee := " ".join("".join(parts).split())):
        return payee
    return "Unknown"


def add_payee_and_category(rows: List[List[str]]) -> List[List[str]]:
    rows_added = [*(rows[0]), "Payee", "Category"]
    for row in rows[1:]:
        description = row[1]
        payee = payee_from_description(description)
        category = category_from_description(payee)
        rows_added.append([*row, payee, category])
    return rows_added


def map_bmo_bank_transactions(rows: List[List[str]]) -> List[List[str]]:
    roll_up_rows = [["Date", "Description", "Withdrawal", "Deposit", "Balance"]]
    return roll_up_rows


def map_scotia_visa_transactions(rows: List[List[str]]) -> List[List[str]]:
    roll_up_rows = [["Date", "Description", "Withdrawal", "Deposit", "Balance"]]
    return roll_up_rows


def output_rows(rows: List[List[str]], output: str) -> None:
    with open(output, mode="w", newline=None) as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def process():
    input, filetype, output = get_run_params()
    rows = get_csv(input)
    if filetype == "bmo_bank":
        # bank
        mapped_rows = map_bmo_bank_transactions(rows)
    elif filetype == "scotia_visa":
        # visa
        mapped_rows = map_scotia_visa_transactions(rows)
    else:
        # tsv input
        mapped_rows = rows
    payee_category_rows = add_payee_and_category(mapped_rows)
    output_rows(payee_category_rows, output)


if __name__ == "__main__":
    process()
