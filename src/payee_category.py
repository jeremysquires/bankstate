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
        prog="payee_category.py",
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
    parser.add_argument(
        "--balance",
        "-b",
        help=(f"balance before first transaction"),
        default=None,
    )
    args = parser.parse_args()
    print(args.input, args.filetype, args.output, args.balance or "")
    return args.input, args.filetype, args.output, args.balance or ""


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
    return {}


@cache
def get_payee_patterns() -> list[str]:
    # regex matches for specific payee patterns
    if os.path.exists(f"{SCRIPT_DIR}/payee_patterns.json"):
        with open(f"{SCRIPT_DIR}/payee_patterns.json", "r") as file:
            return json.load(file)
    return []


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


def map_header_to_indexes(row: list[str]) -> dict:
    header_to_indexes = {}
    for idx, header in enumerate(row):
        header_to_indexes[header] = idx
    return header_to_indexes


def map_bmo_bank_transactions(rows: List[List[str]], balance: str) -> List[List[str]]:
    # "First Bank Card", "Transaction Type", "Date Posted", "Transaction Amount", Description
    header_to_indexes = map_header_to_indexes(rows[0])
    # remove [CW] transaction type prefixes from descriptions
    p = re.compile(r"\[..\]")
    roll_up_rows = [
        ["Date", "Description", "Withdrawal", "Deposit", "Balance", "Payee", "Category"]
    ]
    for row in rows[1:]:
        dateposted = datetime.strptime(
            row[header_to_indexes["Date Posted"]], "%Y%m%d"
        ).strftime("%d %b, %Y")
        description = p.sub("", row[header_to_indexes["Description"]])
        amount = row[header_to_indexes["Transaction Amount"]]
        deposit = amount if amount >= 0.0 else None
        withdrawal = -1.0 * amount if amount < 0.0 else None
        balance = balance + amount if balance else None
        roll_up_rows.append(
            [
                dateposted,
                description,
                withdrawal,
                deposit,
                balance,
                payee_from_description(description),
                category_from_description(description),
            ]
        )
    return roll_up_rows


def map_scotia_visa_transactions(rows: List[List[str]]) -> List[List[str]]:
    roll_up_rows = [["Date", "Description", "Withdrawal", "Deposit", "Balance"]]
    return roll_up_rows


def output_rows(rows: List[List[str]], output: str) -> None:
    with open(output, mode="w", newline=None) as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def process():
    input, filetype, output, balance = get_run_params()
    rows = get_csv(input)
    if filetype == "bmo_bank":
        # bank
        mapped_rows = map_bmo_bank_transactions(rows, balance)
    elif filetype == "sco_visa":
        # visa
        mapped_rows = map_scotia_visa_transactions(rows, balance)
    else:
        # tsv input
        mapped_rows = rows
    payee_category_rows = add_payee_and_category(mapped_rows)
    output_rows(payee_category_rows, output)


if __name__ == "__main__":
    process()
